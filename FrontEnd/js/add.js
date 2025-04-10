// Add page logic

document.addEventListener("DOMContentLoaded", async () => {
  applySavedFontSize();

  const res = await fetch(`${API_BASE}/all-items`);
  const items = await res.json();

  const list = document.getElementById("addList");
  list.innerHTML = "";

  // Filter out items where Buy is True
  const filteredItems = items.filter(item => item.Buy !== true);

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

    li.addEventListener("click", async () => {
      await fetch(`${API_BASE}/item/buy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: item.id })
      });
      li.remove();
    });

    list.appendChild(li);
  });
});

function showAddItemDialog() {
  window.location.href = "additem.html";
}

function closeAddDialog() {
  document.getElementById("addDialog").classList.add("hidden");
}

function goToShopPage() {
  window.location.href = "index.html";
}
