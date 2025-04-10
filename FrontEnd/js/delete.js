let itemToDelete = null;

document.addEventListener("DOMContentLoaded", async () => {
  applySavedFontSize();

  const res = await fetch(`${API_BASE}/all-items`);
  const items = await res.json();

  const list = document.getElementById("deleteList");
  list.innerHTML = "";

  items.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item.Name;

    li.addEventListener("click", () => {
      itemToDelete = item;
      document.getElementById("confirmText").textContent = `Are you sure you want to delete '${item.Name}'?`;
      document.getElementById("confirmDialog").classList.remove("hidden");
    });

    list.appendChild(li);
  });
});

function closeConfirmDialog() {
  document.getElementById("confirmDialog").classList.add("hidden");
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