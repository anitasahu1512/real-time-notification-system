const API_URL = "https://real-time-notification-system-1-c4jm.onrender.com";

const existingToken = localStorage.getItem("access_token");

if (existingToken) {
    window.location.href = "index.html";
}

const loginForm = document.getElementById("loginForm");
const loginButton = document.getElementById("loginButton");
const errorMessage = document.getElementById("errorMessage");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    errorMessage.textContent = "";
    loginButton.disabled = true;
    loginButton.textContent = "Logging in...";

    try {
        const formData = new URLSearchParams();

        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed");
        }

        localStorage.setItem("access_token", data.access_token);

        window.location.href = "index.html";

    } catch (error) {
        console.error("Login error:", error);
        errorMessage.textContent = error.message;
    }

    loginButton.disabled = false;
    loginButton.textContent = "Login";
});