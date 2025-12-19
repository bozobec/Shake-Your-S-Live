"""
Clientside functions are executed by the client browser so that no round trips are needed. They are javascript
"""


# Clientside callback for smooth scrolling and scroll spy
CLIENTSIDE_CALLBACK_SMOOTH_SCROLLING = """
    function(n_clicks_list) {
        // Use a persistent key to ensure listeners are only added once per page load.
        // This is often more reliable than checking n_clicks, especially for listeners.
        if (window.__scrollListenersAttached) {
            return window.dash_clientside.no_update;
        }

        const mainContent = document.getElementById('main-content');
        // Ensure this selector targets your links correctly
        const links = document.querySelectorAll('[id^="link-section-"]'); 
        const sections = document.querySelectorAll('[id^="section-"]'); 

        // --- 1. Attach Scroll Spy Listener ---
        function updateActiveLink() {
            // ... (Your original scroll spy logic, and the PostHog logic)
            // ... (This part seems okay as it relates to the scroll event)

            // Re-inserting the PostHog tracking logic here for completeness:
            let currentSectionId = '';
            const scrollPosition = mainContent.scrollTop + 200; 

            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;

                if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                    currentSectionId = section.id;
                }
            });

            // PostHog Tracking Logic (Ensure window.posthog exists on your page)
            if (currentSectionId && currentSectionId !== window.lastTrackedSection) {
                const urlParams = new URLSearchParams(window.location.search);
                const companyName = urlParams.get('company') || 'None Selected';

                if (window.posthog) {
                    console.log(`[POSTHOG DEBUG] Attempting to capture: Section Viewed for section ${currentSectionId}`)
                    
                    window.posthog.capture('Section Viewed', {
                        section_name: currentSectionId.replace('section-', ''), 
                        company_name: companyName,
                        scroll_transition: 'enter',
                    });
                }
                window.lastTrackedSection = currentSectionId;
            }

            // Scroll Spy logic (Style update)
            links.forEach(link => {
                const linkTarget = link.getAttribute('href').substring(1);
                if (linkTarget === currentSectionId) {
                    link.style.backgroundColor = '#953AF6';
                    link.style.fontWeight = '600';
                    link.style.color = '#FFFFFF';
                } else {
                    link.style.backgroundColor = 'transparent';
                    link.style.fontWeight = 'normal';
                    link.style.color = '#495057';
                }
            });
        }

        // Attach scroll listener once
        if (mainContent) {
            mainContent.addEventListener('scroll', updateActiveLink);
            updateActiveLink(); // Initial run
        }

        // --- 2. Attach Click Listeners (The fix is ensuring this runs) ---
        links.forEach(link => {
            // Ensure link is a valid DOM element
            if (link && !link.hasAttribute('data-click-listener')) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();

                    // Verify targetId is correct
                    const targetId = this.getAttribute('href').substring(1); 
                    const targetElement = document.getElementById(targetId);

                    if (targetElement && mainContent) {
                        const targetPosition = targetElement.offsetTop - 70;
                        mainContent.scrollTo({ 
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    }
                });
                link.setAttribute('data-click-listener', 'true');
            }
        });

        // Mark listeners as attached to prevent duplication on subsequent updates
        window.__scrollListenersAttached = true; 

        return window.dash_clientside.no_update;
    }
    """
# Callback displaying the pricing table on the pricing page
CLIENTSIDE_CALLBACK_PRICING_DISPLAY = """
    function(id_table, pathname) {
        // Only mount if we're on the pricing page
        if (pathname === '/pricing') {
            const container = document.getElementById('pricing-table-container');

            // --- New/Modified Logic Starts Here ---
            if (container) {
                // Function to attempt mounting
                function tryMountClerk() {
                    if (window.Clerk) {
                        // Clear previous content to avoid duplicates
                        container.innerHTML = '';
                        // Mount the pricing table
                        window.Clerk.mountPricingTable(container);
                        return true; // Successfully mounted
                    }
                    return false; // Clerk not ready yet
                }

                // Try mounting immediately
                if (!tryMountClerk()) {
                    // If not ready, poll every 50ms until Clerk is available
                    const maxAttempts = 100; // Max 5 seconds
                    let attempts = 0;
                    const intervalId = setInterval(() => {
                        if (tryMountClerk() || attempts >= maxAttempts) {
                            clearInterval(intervalId); // Stop the interval
                        }
                        attempts++;
                    }, 50);
                }
            }
        }
        return window.dash_clientside.no_update;
    }
    """
CLIENTSIDE_CALLBACK_SCROLL_CAPTURE = """
    function() {
        const aside = document.querySelector('[class*="AppShellAside"]');

        if (aside && !aside.hasAttribute('data-scroll-fixed')) {
            aside.addEventListener('wheel', function(e) {
                // Check if aside content is scrollable
                const isScrollable = this.scrollHeight > this.clientHeight;

                if (!isScrollable) {
                    // If not scrollable, don't capture the scroll
                    e.preventDefault();
                    // Pass scroll to main content
                    const mainContent = document.getElementById('main-content');
                    if (mainContent) {
                        mainContent.scrollTop += e.deltaY;
                    }
                }
            });
            aside.setAttribute('data-scroll-fixed', 'true');
        }

        return window.dash_clientside.no_update;
    }
    """