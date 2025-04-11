// Shared utility functions

const API_BASE = "http://127.0.0.1:5000"; // Adjust if hosted elsewhere

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
