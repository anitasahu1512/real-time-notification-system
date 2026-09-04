
const API_URL = "https://real-time-notification-system-1-c4jm.onrender.com";
const WS_URL = "wss://real-time-notification-system-1-c4jm.onrender.com/ws";

function getToken() {
    return localStorage.getItem("access_token");
}

const token = getToken();

if (!token) {
    window.location.href = "login.html";
}

const notificationsContainer =
    document.getElementById("notifications");

const notificationCount =
    document.getElementById("notificationCount");

const connectionStatus =
    document.getElementById("connectionStatus");

const headerStatus =
    document.getElementById("headerStatus");

const statusDot =
    document.getElementById("statusDot");

const notificationTitle =
    document.getElementById("notificationTitle");

const pageTitle =
    document.getElementById("pageTitle");

const notificationPage =
    document.getElementById("notificationPage");

const profilePage =
    document.getElementById("profilePage");

const settingsPage =
    document.getElementById("settingsPage");

let notifications = [];
let currentFilter = "all";
let socket;


// API authorization

function authHeaders() {
    return {
        "Authorization": `Bearer ${getToken()}`
    };
}


// Handle expired token

function handleUnauthorized(response) {
    if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "login.html";
        return true;
    }

    return false;
}


// Load notifications

async function loadNotifications() {
    try {
        const response = await fetch(
            `${API_URL}/notifications`,
            {
                headers: authHeaders()
            }
        );

        if (handleUnauthorized(response)) {
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load notifications");
        }

        notifications = await response.json();

        displayNotifications();

    } catch (error) {
        console.error(error);

        if (notificationsContainer) {
            notificationsContainer.innerHTML = `
                <div class="error">
                    Unable to load notifications.
                    Please try again.
                </div>
            `;
        }
    }
}


// Display notifications

function displayNotifications() {
    if (!notificationsContainer) {
        return;
    }

    notificationsContainer.innerHTML = "";

    const unreadCount = notifications.filter(
        notification => !notification.is_read
    ).length;

    if (notificationCount) {
        notificationCount.textContent = unreadCount;
    }

    let filteredNotifications = notifications;

    if (currentFilter === "unread") {
        filteredNotifications = notifications.filter(
            notification => !notification.is_read
        );
    }

    if (currentFilter === "read") {
        filteredNotifications = notifications.filter(
            notification => notification.is_read
        );
    }

    if (filteredNotifications.length === 0) {
        notificationsContainer.innerHTML = `
            <div class="empty">
                No notifications found.
            </div>
        `;
        return;
    }

    filteredNotifications.forEach(notification => {
        const notificationElement =
            document.createElement("div");

        notificationElement.className = "notification";

        if (!notification.is_read) {
            notificationElement.classList.add("unread");
        }

        const icon =
            document.createElement("div");

        icon.className = "notification-icon";
        icon.textContent = "🔔";

        const content =
            document.createElement("div");

        content.className = "notification-content";

        const title =
            document.createElement("h3");

        title.textContent = "Notification";

        const message =
            document.createElement("p");

        message.textContent =
            notification.message;

        const time =
            document.createElement("div");

        time.className = "notification-time";

        time.textContent =
            formatDate(notification.created_at);

        content.appendChild(title);
        content.appendChild(message);
        content.appendChild(time);

        const actions =
            document.createElement("div");

        actions.className = "notification-actions";

        const readButton =
            document.createElement("button");

        readButton.textContent =
            notification.is_read
                ? "✓ Read"
                : "Mark read";

        readButton.disabled =
            notification.is_read;

        readButton.addEventListener(
            "click",
            () => markAsRead(notification.id)
        );

        const deleteButton =
            document.createElement("button");

        deleteButton.textContent = "🗑";

        deleteButton.addEventListener(
            "click",
            () => deleteNotification(notification.id)
        );

        actions.appendChild(readButton);
        actions.appendChild(deleteButton);

        notificationElement.appendChild(icon);
        notificationElement.appendChild(content);
        notificationElement.appendChild(actions);

        if (!notification.is_read) {
            const dot =
                document.createElement("span");

            dot.className = "unread-dot";
            dot.textContent = "●";

            notificationElement.appendChild(dot);
        }

        notificationsContainer.appendChild(
            notificationElement
        );
    });
}


// Format date

function formatDate(dateString) {
    if (!dateString) {
        return "";
    }

    const date = new Date(dateString);

    return date.toLocaleString();
}


// Mark notification as read

async function markAsRead(id) {
    if (!id) {
        console.error("Notification ID missing");
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/notifications/${id}/read`,
            {
                method: "PATCH",
                headers: authHeaders()
            }
        );

        if (handleUnauthorized(response)) {
            return;
        }

        if (!response.ok) {
            throw new Error(
                "Failed to mark notification as read"
            );
        }

        await loadNotifications();

    } catch (error) {
        console.error(error);
    }
}


// Delete notification

async function deleteNotification(id) {
    if (!id) {
        console.error("Notification ID missing");
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/notifications/${id}`,
            {
                method: "DELETE",
                headers: authHeaders()
            }
        );

        if (handleUnauthorized(response)) {
            return;
        }

        if (!response.ok) {
            throw new Error(
                "Failed to delete notification"
            );
        }

        await loadNotifications();

    } catch (error) {
        console.error(error);
    }
}


// Mark all as read

const markAllButton =
    document.getElementById("markAllButton");

if (markAllButton) {
    markAllButton.addEventListener(
        "click",
        async function () {

            const unreadNotifications =
                notifications.filter(
                    notification => !notification.is_read
                );

            for (const notification of unreadNotifications) {
                await markAsRead(notification.id);
            }

            await loadNotifications();
        }
    );
}


// Clear all notifications

const clearAllButton =
    document.getElementById("clearAllButton");

if (clearAllButton) {
    clearAllButton.addEventListener(
        "click",
        async function () {

            if (notifications.length === 0) {
                return;
            }

            const confirmed =
                confirm(
                    "Are you sure you want to delete all notifications?"
                );

            if (!confirmed) {
                return;
            }

            for (const notification of notifications) {
                await deleteNotification(notification.id);
            }

            await loadNotifications();
        }
    );
}


// Sidebar navigation

document
    .querySelectorAll(".nav-item[data-filter]")
    .forEach(button => {

        button.addEventListener(
            "click",
            function () {

                document
                    .querySelectorAll(".nav-item")
                    .forEach(item => {
                        item.classList.remove("active");
                    });

                button.classList.add("active");

                const filter =
                    button.dataset.filter;

                showPage(filter);
            }
        );
    });


// Show selected page

function showPage(filter) {
    if (notificationPage) {
        notificationPage.style.display = "none";
    }

    if (profilePage) {
        profilePage.style.display = "none";
    }

    if (settingsPage) {
        settingsPage.style.display = "none";
    }

    if (
        filter === "all" ||
        filter === "all-notifications"
    ) {
        if (notificationPage) {
            notificationPage.style.display = "block";
        }

        currentFilter = "all";

        if (notificationTitle) {
            notificationTitle.textContent =
                filter === "all"
                    ? "Notifications"
                    : "All Notifications";
        }

        if (pageTitle) {
            pageTitle.textContent =
                filter === "all"
                    ? "Real-Time Notifications"
                    : "All Notifications";
        }

        displayNotifications();

        return;
    }

    if (filter === "unread") {
        if (notificationPage) {
            notificationPage.style.display = "block";
        }

        currentFilter = "unread";

        if (notificationTitle) {
            notificationTitle.textContent =
                "Unread Notifications";
        }

        if (pageTitle) {
            pageTitle.textContent =
                "Unread Notifications";
        }

        displayNotifications();

        return;
    }

    if (filter === "read") {
        if (notificationPage) {
            notificationPage.style.display = "block";
        }

        currentFilter = "read";

        if (notificationTitle) {
            notificationTitle.textContent =
                "Read Notifications";
        }

        if (pageTitle) {
            pageTitle.textContent =
                "Read Notifications";
        }

        displayNotifications();

        return;
    }

    if (filter === "profile") {
        if (profilePage) {
            profilePage.style.display = "block";
        }

        if (pageTitle) {
            pageTitle.textContent = "Profile";
        }

        return;
    }

    if (filter === "settings") {
        if (settingsPage) {
            settingsPage.style.display = "block";
        }

        if (pageTitle) {
            pageTitle.textContent = "Settings";
        }
    }
}


// Logout

const logoutButton =
    document.getElementById("logoutButton");

if (logoutButton) {
    logoutButton.addEventListener(
        "click",
        function () {

            localStorage.removeItem(
                "access_token"
            );

            if (socket) {
                socket.close();
            }

            window.location.href =
                "login.html";
        }
    );
}


// WebSocket connection

function connectWebSocket() {
    const currentToken = getToken();

    if (!currentToken) {
        return;
    }

    socket = new WebSocket(
        `${WS_URL}?token=${encodeURIComponent(currentToken)}`
    );

    socket.onopen = function () {
        console.log("WebSocket connected");

        if (connectionStatus) {
            connectionStatus.textContent =
                "Connected";
        }

        if (headerStatus) {
            headerStatus.textContent =
                "Connected";
        }

        if (statusDot) {
            statusDot.textContent = "●";
        }
    };

    socket.onmessage = function (event) {
        console.log("New notification:", event.data);

        try {
            const notification = JSON.parse(event.data);

            console.log("Notification object:", notification);

            // Refresh notification list
            loadNotifications();

            // Play sound
            const soundToggle =
                document.getElementById("soundToggle");

            if (soundToggle && soundToggle.checked) {
                playNotificationSound();
            }

            // Browser notification
            showBrowserNotification(notification);

        } catch (error) {
            console.error(
                "Failed to process WebSocket notification:",
                error
            );
        }
    };

    socket.onclose = function () {
        console.log("WebSocket disconnected");

        if (connectionStatus) {
            connectionStatus.textContent = "Disconnected";
        }

        if (headerStatus) {
            headerStatus.textContent = "Disconnected";
        }

        if (statusDot) {
            statusDot.textContent = "●";
        }

        if (getToken()) {
            setTimeout(connectWebSocket, 3000);
        }
    };

    socket.onerror = function (error) {
        console.error(
            "WebSocket error:",
            error
        );
    };
}


// Browser notification

function showBrowserNotification(notification) {
    if (
        "Notification" in window &&
        Notification.permission === "granted"
    ) {
        new Notification(
            "NotifyHub",
            {
                body: notification.message
            }
        );
    }
}


// Enable browser notifications

const browserNotificationButton =
    document.getElementById(
        "browserNotificationButton"
    );

if (browserNotificationButton) {
    browserNotificationButton.addEventListener(
        "click",
        async function () {

            if (!("Notification" in window)) {
                alert(
                    "Browser notifications are not supported."
                );

                return;
            }

            const permission =
                await Notification.requestPermission();

            if (permission === "granted") {
                this.textContent = "Enabled";
            }
        }
    );
}


// Notification sound

function playNotificationSound() {
    const AudioContext =
        window.AudioContext ||
        window.webkitAudioContext;

    if (!AudioContext) {
        return;
    }

    const audioContext =
        new AudioContext();

    const oscillator =
        audioContext.createOscillator();

    const gain =
        audioContext.createGain();

    oscillator.connect(gain);
    gain.connect(audioContext.destination);

    oscillator.frequency.value = 700;
    gain.gain.value = 0.08;

    oscillator.start();

    oscillator.stop(
        audioContext.currentTime + 0.15
    );
}


// Initial load

loadNotifications();

connectWebSocket();