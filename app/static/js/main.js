document.addEventListener("DOMContentLoaded", function () {
    const socket = io();

    // ----------------- مدیریت پیام‌ها -----------------

    // اضافه کردن پیام به صفحه
    function addMessage(message) {
        const messagesDiv = document.getElementById("chat-messages");
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");
        messageDiv.textContent = message;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // ارسال پیام
    document.getElementById("send-message-form")?.addEventListener("submit", function (e) {
        e.preventDefault();
        const messageContent = document.getElementById("message-content").value;

        fetch("/api/messages", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("token")}`,
            },
            body: JSON.stringify({ content: messageContent }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    addMessage(`[You]: ${messageContent}`);
                    document.getElementById("message-content").value = "";
                } else {
                    alert(data.error || "Error sending message.");
                }
            })
            .catch((err) => console.error(err));
    });

    // گوش دادن به پیام‌های جدید از سرور
    socket.on("new_message", function (data) {
        addMessage(`[User ${data.sender_id}]: ${data.content}`);
    });

    // ----------------- مدیریت فایل‌ها -----------------

    // اضافه کردن فایل به لیست فایل‌ها
    function addFileToList(filename) {
        const fileList = document.getElementById("uploaded-files");
        const listItem = document.createElement("li");
        listItem.innerHTML = `
            <span>${filename}</span>
            <button class="btn delete-btn" data-filename="${filename}">Delete</button>
        `;
        fileList.appendChild(listItem);

        // افزودن عملکرد حذف فایل به دکمه
        listItem.querySelector(".delete-btn").addEventListener("click", function () {
            deleteFile(filename);
        });
    }

    // حذف فایل
    function deleteFile(filename) {
        fetch(`/api/delete/${filename}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`,
            },
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    alert("File deleted successfully!");
                    const fileList = document.getElementById("uploaded-files");
                    const fileItem = Array.from(fileList.children).find(
                        (item) => item.querySelector(".delete-btn").dataset.filename === filename
                    );
                    fileItem.remove();
                } else {
                    alert(data.error || "Error deleting file.");
                }
            })
            .catch((err) => console.error(err));
    }

    // آپلود فایل
    document.getElementById("upload-file-form")?.addEventListener("submit", function (e) {
        e.preventDefault();
        const fileInput = document.getElementById("file-input");
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        fetch("/api/upload", {
            method: "POST",
            body: formData,
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`,
            },
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    alert("File uploaded successfully!");
                    addFileToList(fileInput.files[0].name);
                    fileInput.value = "";
                } else {
                    alert(data.error || "Error uploading file.");
                }
            })
            .catch((err) => console.error(err));
    });

    // ----------------- مدیریت توکن -----------------

    // بررسی ورود و ذخیره توکن
    document.getElementById("login-form")?.addEventListener("submit", function (e) {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.token) {
                    localStorage.setItem("token", data.token);
                    window.location.href = "/chat";
                } else {
                    alert(data.error || "Login failed.");
                }
            })
            .catch((err) => console.error(err));
    });

    // ثبت‌نام و ذخیره توکن
    document.getElementById("register-form")?.addEventListener("submit", function (e) {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        fetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    alert("Registration successful! Please login.");
                    window.location.href = "/auth/login";
                } else {
                    alert(data.error || "Registration failed.");
                }
            })
            .catch((err) => console.error(err));
    });
});
