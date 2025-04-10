// Main page logic

document.addEventListener("DOMContentLoaded", async () => {
  applySavedFontSize();

  // Load the saved person or default to "Morten"
  const person = getFromStorage("person", "Morten");
  document.getElementById("personSelector").value = person;

  const shop = getFromStorage("shop", "");
  document.getElementById("shopName").textContent = shop || "Select shop";

  const items = await fetchItems(shop);
  const list = document.getElementById("itemList");
  list.innerHTML = "";

  items.sort((a, b) => a.Name.localeCompare(b.Name));

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

    li.addEventListener("click", async () => {
      await markItemAsBought(item.id);
      li.remove();
    });

    list.appendChild(li);
  });
});

function updatePerson() {
  const person = document.getElementById("personSelector").value;
  saveToStorage("person", person); // Save the selected person to local storage
}

async function fetchItems(shop) {
  const res = await fetch(`${API_BASE}/all-items`);
  const items = await res.json();

  if (shop.toLowerCase() === "all") {
    // Return all items with Buy = True
    return items.filter(item => item.Buy === true);
  }

  // Return items filtered by shop and Buy = True
  return items.filter(item => item.Buy === true && item.Shop.toLowerCase() === shop.toLowerCase());
}

async function markItemAsBought(itemId) {
  await fetch(`${API_BASE}/item/remove`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: itemId })
  });
}
