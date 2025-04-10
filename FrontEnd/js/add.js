// Add page logic

document.addEventListener("DOMContentLoaded", async () => {
  applySavedFontSize();
  const shop = getFromStorage("shop", "");

  const res = await fetch(`${API_BASE}/all-items`);
  const items = await res.json();
  const filtered = items.filter(i => !i.Buy);
  filtered.sort((a, b) => a.Name.localeCompare(b.Name));

  const list = document.getElementById("addList");
  list.innerHTML = "";

  filtered.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item.Name;

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
