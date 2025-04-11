let itemToDelete = null;

document.addEventListener("DOMContentLoaded", async () => {
  applySavedFontSize();

  const res = await fetch(`${API_BASE}/all-items`);
  const items = await res.json();

  const list = document.getElementById("deleteList");
  list.innerHTML = "";

  items.forEach(item => {
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

    li.addEventListener("click", () => {
      itemToDelete = item;
      document.getElementById("confirmText").textContent = `Are you sure you want to delete '${item.Name}'?`;
      document.getElementById("confirmDialog").classList.remove("hidden"); // Show dialog
    });

    list.appendChild(li);
  });
});

function closeConfirmDialog() {
  document.getElementById("confirmDialog").classList.add("hidden"); // Hide dialog
  itemToDelete = null;
}

async function confirmDelete() {
  if (!itemToDelete) return;

  await fetch(`${API_BASE}/item`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: itemToDelete.id })
  });

  closeConfirmDialog();
  location.reload();
}

function goToMainPage() {
  window.location.href = "index.html";
}