// Shared utility functions

// Determine the API base URL based on the environment
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = isLocal ? "http://127.0.0.1:8080" : "https://shoppinglist-backend.fly.dev"; // Use local or production URL

// Automatically set a debug token when running locally
if (isLocal) {
  saveToStorage("authToken", "debug-token");
}

function getFromStorage(key, defaultValue) {
  return localStorage.getItem(key) || defaultValue; // Retrieve the value or use the default
}

function saveToStorage(key, value) {
  localStorage.setItem(key, value); // Save the value to local storage
}

function setToStorage(key, value) {
  localStorage.setItem(key, value);
}

function updateFontSize() {
  const size = document.getElementById("fontSize").value;
  document.body.setAttribute("data-font-size", size);
  setToStorage("fontSize", size);
}

function applySavedFontSize() {
  const saved = getFromStorage("fontSize", "16");
  document.body.setAttribute("data-font-size", saved); // Set the font size on the body
  const selector = document.getElementById("fontSize");
  if (selector) selector.value = saved;
}

function changeShop() {
  const newShop = prompt("Enter shop name:", getFromStorage("shop"));
  if (newShop) {
    setToStorage("shop", newShop);
    location.reload();
  }
}

function goToAddPage() {
  window.location.href = "add.html";
}

async function fetchItems(shop) {
  const response = await fetch(`${API_BASE}/items?shop=${encodeURIComponent(shop)}`);
  return await response.json();
}

async function markItemAsBought(id) {
  await fetch(`${API_BASE}/item/remove`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id })
  });
}

async function fetchWithAuth(url, options = {}) {
  const token = getFromStorage("authToken", null);
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  options.headers = {
    ...options.headers,
    Authorization: token,
  };

  const response = await fetch(url, options);
  if (response.status === 401) {
    // Try to parse error for session expiration
    try {
      const data = await response.clone().json();
      if (data && data.error && data.error.toLowerCase().includes("session expired")) {
        alert("Session expired. Please log in again.");
      } else {
        alert("Unauthorized. Please log in again.");
      }
    } catch {
      alert("Session expired or unauthorized. Please log in again.");
    }
    localStorage.removeItem("authToken");
    window.location.href = "login.html";
  }
  return response;
}
