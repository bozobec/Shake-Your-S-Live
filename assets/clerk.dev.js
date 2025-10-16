window.addEventListener("DOMContentLoaded", async () => {
  const publishableKey = "pk_test_aGFwcHktc2t5bGFyay03My5jbGVyay5hY2NvdW50cy5kZXYk"; // your real key

  const script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js";
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

      // ✅ Directly push to Dash — no need for hidden div polling!
      dash_clientside.set_props("login-state-bridge", {
        children: JSON.stringify({
          logged_in: isLoggedIn,
          user_id: user ? user.id : null,
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
      } else {
        const btn = document.createElement("button");
        btn.id = "sign-in-btn";
        btn.className = "btn btn-outline-light btn-sm";
        btn.textContent = "Sign In";
        btn.addEventListener("click", () => Clerk.openSignIn());
        header.appendChild(btn);
      }
    }

    // Initial check
    await updateAppState();

    // React to login/logout changes
    Clerk.addListener(() => updateAppState());

    // Optionally get session token if needed
    const token = await Clerk.session?.getToken({ template: "dash-api" });
    if (token) {
      console.log("Session token:", token);
    }
  });

  document.body.appendChild(script);
});
