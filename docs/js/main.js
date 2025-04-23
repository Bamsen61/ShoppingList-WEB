// Main page logic

document.addEventListener("DOMContentLoaded", async () => {
  applySavedFontSize();

  // Load the saved person or default to "Morten"
  const person = getFromStorage("person", "Morten");
  document.getElementById("personSelector").value = person;

  const shop = getFromStorage("shop", "");
  document.getElementById("shopName").textContent = shop || "Select shop";

  let currentItems = await fetchItems(shop);
  renderItemList(currentItems);

  // Fetch and store the initial state string
  let lastStateString = null;
  let lastFetchedState = null;
  try {
    const stateRes = await fetch(`${API_BASE}/statestring`);
    const stateData = await stateRes.json();
    lastStateString = stateData.state;
    lastFetchedState = stateData.state;
    // Update debug section
    if (document.getElementById("lastStateString")) {
      document.getElementById("lastStateString").textContent = lastStateString;
      document.getElementById("currentStateString").textContent = stateData.state;
    }
  } catch (e) {
    lastStateString = null;
    lastFetchedState = null;
  }

  // Periodically check if the state string has changed
  setInterval(async () => {
    try {
      const stateRes = await fetch(`${API_BASE}/statestring`);
      const stateData = await stateRes.json();
      // Update debug section
      if (document.getElementById("lastStateString")) {
        document.getElementById("lastStateString").textContent = lastStateString;
        document.getElementById("currentStateString").textContent = stateData.state;
      }
      if (stateData.state !== lastStateString) {
        lastStateString = stateData.state;
        const newItems = await fetchItems(shop);
        currentItems = newItems;
        renderItemList(currentItems);
      }
    } catch (e) {
      // Optionally handle error
    }
  }, 4000); // 4 seconds
});

function renderItemList(items) {
  const list = document.getElementById("itemList");
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

    li.addEventListener("click", async () => {
      await markItemAsBought(item.id);
      li.remove();
    });

    list.appendChild(li);
  });
}

function areItemListsEqual(listA, listB) {
  if (listA.length !== listB.length) return false;
  for (let i = 0; i < listA.length; i++) {
    if (
      listA[i].id !== listB[i].id ||
      listA[i].Name !== listB[i].Name ||
      listA[i].Shop !== listB[i].Shop
    ) {
      return false;
    }
  }
  return true;
}

function updatePerson() {
  const person = document.getElementById("personSelector").value;
  saveToStorage("person", person); // Save the selected person to local storage
}

async function fetchItems(shop) {
  // Use fetchWithAuth to include the token in the request
  // const response = await fetchWithAuth(`${API_BASE}/all-items`);
  const response = await fetchWithAuth(`${API_BASE}/itemstobuy`);
  const items = await response.json();

  if (shop.toLowerCase() === "all" || shop.toLowerCase() === "alle") {
    // Return all items with Buy = True
    return items.filter(item => item.Buy === true);
  }

  // Return items filtered by shop and Buy = True
  return items.filter(item => item.Buy === true && item.Shop.toLowerCase() === shop.toLowerCase());
}

async function markItemAsBought(itemId) {
  const BoughtBy = getFromStorage("person", "Anonymous"); // Retrieve the selected person from local storage

  await fetchWithAuth(`${API_BASE}/item/markitemasbought`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: itemId, BoughtBy }) // Include BoughtBy in the request
  });
}
