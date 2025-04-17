// Logic for additemtodatabase.html

document.addEventListener("DOMContentLoaded", () => {
  applySavedFontSize(); // Apply the saved font size to the body
});

async function submitItem() {
  const Name = document.getElementById("itemName").value.trim();
  const Shop = document.getElementById("itemShop").value.trim();
  const AddedBy = getFromStorage("person", "Anonymous"); // Retrieve the selected person from local storage

  if (!Name || !Shop) {
    alert("Name and Shop are required.");
    return;
  }

  // Send the item data to the backend
  // await fetch(`${API_BASE}/item/add`, {
  await fetchWithAuth(`${API_BASE}/item/additemtodatabase`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Name, Shop, AddedBy }) // Include AddedBy in the request
  });

  window.location.href = "index.html"; // Redirect to the main page
}

function cancelAdd() {
  window.location.href = "index.html";
}
