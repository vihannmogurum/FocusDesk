laptops = {
    "windows": {
        "dell": 60000,
        "hp": 55000,
        "lenovo": 52000,
        "asus": 58000
    },

    "mac": {
        "macbook air": 95000,
        "macbook pro": 140000
    }
}

cart = {}

print("!!!!!! LAPTOP STORE !!!!!")

while True:
    os = input("Choose OS (windows/mac) or type 'done' to stop: ").lower()

    if os == "done":
        break

    if os not in laptops:
        print("Invalid OS")
        continue

    print("\nAvailable laptops:")
    for name, price in laptops[os].items():
        print(name, ":", price)

    model = input("Enter laptop model: ").lower()

    if model not in laptops[os]:
        print("Model not available")
        continue

    ram = input("Enter RAM (8GB / 16GB / 32GB): ")
    storage = input("Enter Storage (256GB / 512GB / 1TB): ")

    quantity = int(input("Enter quantity: "))

    key = model + " | " + ram + " | " + storage

    if key in cart:
        cart[key]["qty"] += quantity
    else:
        cart[key] = {
            "price": laptops[os][model],
            "qty": quantity
        }

print("\nYour Cart:")
for item, data in cart.items():
    print(item, ":", data["qty"])


while True:
    print("\n1. Update Quantity / Remove Item")
    print("2. Checkout")

    choice = input("Enter choice: ")

    if choice == "1":

        item = input("Enter item name exactly: ")

        if item in cart:

            new_qty = int(input("Enter new quantity: "))

            if new_qty > 0:
                cart[item]["qty"] = new_qty
                print("Quantity updated")

            elif new_qty == 0:
                del cart[item]
                print("Item removed")

        else:
            print("Item not in cart")

    elif choice == "2":
        break

    else:
        print("Invalid choice")


if not cart:
    print("Cart empty")
else:
    print("\n------ BILL ------")

    total = 0

    for item, data in cart.items():

        price = data["price"]
        qty = data["qty"]

        item_total = price * qty
        total += item_total

        print(item, qty, "x", price, "=", item_total)

    print("------------------")
    print("Total =", total)
    print("Thank you for shopping!")