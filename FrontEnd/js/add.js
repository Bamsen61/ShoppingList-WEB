// Add page logic

let itemToDelete = null;

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

    li.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      itemToDelete = item;
      document.getElementById("deleteItemName").textContent = `Delete '${item.Name}'?`;
      document.getElementById("deleteDialog").classList.remove("hidden");
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

function closeDeleteDialog() {
  document.getElementById("deleteDialog").classList.add("hidden");
  itemToDelete = null;
}

async function confirmDelete() {
  if (!itemToDelete) return;
  await fetch(`${API_BASE}/item`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: itemToDelete.id })
  });
  closeDeleteDialog();
  location.reload();
}
