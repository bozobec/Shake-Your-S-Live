window.addEventListener("DOMContentLoaded", async () => {
  const publishableKey = "pk_live_Y2xlcmsucmFzdC5ndXJ1JA"; // the prod key

  const script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/@clerk/clerk-js@5.111.0/dist/clerk.browser.js";
  script.async = true;
  script.setAttribute("data-clerk-publishable-key", publishableKey);

  script.addEventListener("load", async () => {
    await Clerk.load();
    const header = document.getElementById("clerk-header");
    const bridge = document.getElementById("login-state-bridge");

    // Helper: update Dash dcc.Store + UI
    async function updateAppState() {
      const user = Clerk.user;
      const isLoggedIn = !!user;

      // Get billing info from Clerk/Stripe
      const hasFreePlan = isLoggedIn ? Clerk.session.checkAuthorization({ plan: 'free_user' }) : false;
      const hasProPlan = isLoggedIn ? Clerk.session.checkAuthorization({ plan: 'pro_user' }) : false;

      // ✅ Push to Dash including billing info
      dash_clientside.set_props("login-state-bridge", {
        children: JSON.stringify({
          logged_in: isLoggedIn,
          user_id: user ? user.id : null,
          has_free_plan: hasFreePlan,
          has_pro_plan: hasProPlan,
        })
      });

      // 2️⃣ Update header UI
      header.innerHTML = "";
      if (isLoggedIn) {
        const userButtonWrapper = document.createElement("div");
        userButtonWrapper.id = "clerk-user-button-wrapper";
        userButtonWrapper.style.display = "flex";
        userButtonWrapper.style.alignItems = "center"; // center vertically
        userButtonWrapper.style.height = "100%";       // match navbar height

        const userButtonContainer = document.createElement("div");
        userButtonContainer.id = "clerk-user-button";
        userButtonWrapper.appendChild(userButtonContainer);

        header.appendChild(userButtonWrapper);
        Clerk.mountUserButton(userButtonContainer);

        // remove extra sign-in button
        const extra = document.getElementById("clerk-extra-signin");
        if (extra) extra.innerHTML = "";
      } else {
        const btn = document.createElement("button");
        btn.id = "sign-in-btn";
        btn.className = "btn btn-outline-light btn-sm";
        btn.textContent = "Sign In";
        btn.addEventListener("click", () => {
            posthog.capture("sign_in_clicked"); // posthog event
            posthog.capture("sign_in_modal_opened"); //posthog event
            Clerk.openSignIn();
            });
        header.appendChild(btn);
      }
          // --- Second button ---
        const extra = document.getElementById("clerk-extra-signin");
        if (extra) {
        extra.innerHTML = ""; // clear previous
        const extraBtn = document.createElement("button");
        extraBtn.textContent = "Ranking";
        extraBtn.className = "btn btn-primary";   // choose your style
        extraBtn.addEventListener("click", () => {
            posthog.capture("sign_in_clicked", { location: "ranking-button" }); // posthog event
            posthog.capture("sign_in_modal_opened"); //posthog event
            Clerk.openSignIn();
        });
        extra.appendChild(extraBtn);
        }
    }

        // ✨ Billing: Function to mount pricing table
    function mountPricingTable(elementId) {
      const pricingTableDiv = document.getElementById(elementId);
      if (pricingTableDiv) {
        Clerk.mountPricingTable(pricingTableDiv);
      }
    }

    // ✨ Billing: Function to check if user has a plan
    function checkPlan(planName) {
      if (!Clerk.session) return false;
      return Clerk.session.checkAuthorization({ plan: planName });
    }

    // ✨ Billing: Function to check if user has a feature
    function checkFeature(featureName) {
      if (!Clerk.session) return false;
      return Clerk.session.checkAuthorization({ feature: featureName });
    }

    // Make functions available globally for Dash callbacks
    window.clerkBilling = {
      mountPricingTable,
      checkPlan,
      checkFeature
    };

    // Initial check
    await updateAppState();

    // React to login/logout changes
    Clerk.addListener(() => updateAppState());

    // Optionally get session token if needed
    const token = await Clerk.session?.getToken();
    if (token) {
      console.log("Session token:", token);
    }
  });

  document.body.appendChild(script);
});
