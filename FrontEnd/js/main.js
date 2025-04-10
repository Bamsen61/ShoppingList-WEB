// Main page logic

document.addEventListener("DOMContentLoaded", async () => {
  applySavedFontSize();

  const shop = getFromStorage("shop", "");
  document.getElementById("shopName").textContent = shop || "Select shop";

  const items = await fetchItems(shop);
  const list = document.getElementById("itemList");
  list.innerHTML = "";

  items.sort((a, b) => a.Name.localeCompare(b.Name));

  items.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item.Name;
    li.addEventListener("click", async () => {
      await markItemAsBought(item.id);
      li.remove();
    });
    list.appendChild(li);
  });
});
