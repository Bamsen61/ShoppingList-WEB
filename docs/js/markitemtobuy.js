// Add page logic

document.addEventListener("DOMContentLoaded", async () => {
  applySavedFontSize();

  // Fetch all items from the backend
  const res = await fetchWithAuth(`${API_BASE}/all-items`);
  const items = await res.json();

  const list = document.getElementById("addList");
  list.innerHTML = "";

  // Filter out items where Buy is True
  const filteredItems = items.filter(item => item.Buy !== true);
  filteredItems.sort((a, b) => a.Name.localeCompare(b.Name));
  
  filteredItems.forEach(item => {
    const li = document.createElement("li");
    li.classList.add("item-row");

    const nameSpan = document.createElement("span");
    nameSpan.classList.add("item-name");
    nameSpan.textContent = item.Name;

    const shopSpan = document.createElement("span");
    shopSpan.classList.add("item-shop");
    shopSpan.textContent = item.Shop;

    li.appendChild(nameSpan);
    li.appendChild(shopSpan);

    // Add click event listener to mark item to buy
    li.addEventListener("click", async () => {
      await MarkItemToBuy(item.id, li);
    });

    list.appendChild(li);
  });
});

// Mark an item to be bought (set Buy to true)
async function MarkItemToBuy(itemId, liElement) {
  await fetchWithAuth(`${API_BASE}/item/markitemtobuy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: itemId }) // Send the item id in the request body
  });
  liElement.remove(); // Remove the item from the list after marking it as to buy
}

function showAddItemDialog() {
  window.location.href = "additemtodatabase.html";
}

function closeAddDialog() {
  document.getElementById("addDialog").classList.add("hidden");
}

function goToShopPage() {
  window.location.href = "index.html";
}
