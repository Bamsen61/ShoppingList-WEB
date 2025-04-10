// Logic for additem.html

document.addEventListener("DOMContentLoaded", () => {
  applySavedFontSize();
});

async function submitItem() {
  const Name = document.getElementById("itemName").value.trim();
  const Shop = document.getElementById("itemShop").value.trim();
  const AddedBy = getFromStorage("AddedBy", "anonymous");

  if (!Name || !Shop) {
    alert("Name and Shop are required.");
    return;
  }

  await fetch(`${API_BASE}/item/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Name, Shop, AddedBy })
  });

  window.location.href = "index.html";
}

function cancelAdd() {
  window.location.href = "index.html";
}
