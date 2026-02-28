laptop_selection = []
total = 0

# ─── Pricing Data ───────────────────────────────────────────
laptop_prices = {
    "Lenovo IdeaPad Slim 3 (14-inch)": 25.00,
    "Lenovo ThinkPad E16 (16-inch)": 30.00,
    "Lenovo V15 Gen 5 (15.6-inch)": 22.00,
    "Lenovo IdeaPad Slim 5i (16-inch)": 35.00,
    "Lenovo IdeaPad 5i 2-in-1 (14-inch)": 35.00,
    "Lenovo LOQ 15IRX9 (15.6-inch)": 40.00,
    "Lenovo ThinkPad X1 Carbon Gen 12 (14-inch)": 50.00,
    "Lenovo Yoga 7i 2-in-1 Gen 9 (14-inch)": 48.00,
    "Lenovo Legion Pro 5i Gen 9 (16-inch)": 55.00,
    "Lenovo IdeaPad 1 (Budget)": 18.00,
    "Lenovo IdeaPad Slim 5 (Mid-Range)": 35.00,
    "Lenovo ThinkPad X1 Carbon (Premium)": 55.00,
    "Dell Inspiron 15 3530 (i3)": 24.00,
    "Dell Vostro 3420": 22.00,
    "Dell Latitude 3540": 28.00,
    "Dell Inspiron 15 3530 (i5)": 32.00,
    "Dell Inspiron 14 (5440)": 34.00,
    "Dell Latitude 3450": 36.00,
    "Dell XPS 13 (9345/9350)": 55.00,
    "Dell Inspiron 14 Plus (7440)": 50.00,
    "Dell Alienware m16 R2": 65.00,
    "Dell Inspiron 15 3535 (AMD Ryzen 3)": 22.00,
    "Dell Vostro 3535 (AMD Ryzen 3)": 20.00,
    "Dell Inspiron 14 3435 (AMD Ryzen 3)": 22.00,
    "Dell G15 Ryzen Edition (Ryzen 5)": 42.00,
    "Dell Inspiron 14 5435 (Ryzen 5)": 35.00,
    "Dell Vostro 5635 (Ryzen 5)": 36.00,
    "Dell XPS 14 (AMD Ryzen 7)": 58.00,
    "Dell Alienware m16 R2 (AMD)": 65.00,
    "MacBook Air M2 (13-inch)": 60.00,
}

# ─── Billing ────────────────────────────────────────────────
def billing(laptop_name):
    global total
    print("\n--- BILLING SECTION ---")

    try:
        days = int(input("Enter number of rental days: "))
    except:
        print("Invalid input. Defaulting to 1 day.")
        days = 1

    price = laptop_prices.get(laptop_name, 30.00)
    cost = price * days
    total += cost

    laptop_selection.append({
        "Laptop": laptop_name,
        "Days": days,
        "Cost": cost
    })

    print(f"Rate : ${price}/day")
    print(f"Days : {days}")
    print(f"Cost : ${cost}")
    print(f"Running Total: ${total}")
    print("--------------------------------")

# ─── Helper ────────────────────────────────────────────────
def show_laptop(name, specs):
    print(f"\nSelected: {name}")
    print("Specifications:")
    for s in specs:
        print(" -", s)
    billing(name)

# ─── LENOVO ────────────────────────────────────────────────
def lenovo_menu():
    print("\n--- LENOVO ---")
    print("1. Intel i3")
    print("2. Intel i5")
    print("3. Intel i7")
    print("4. Budget Range")

    try:
        c = int(input("Choice: "))
    except:
        print("Invalid.")
        return

    match c:
        case 1:
            show_laptop("Lenovo IdeaPad Slim 3 (14-inch)", [
                "Intel i3 13th Gen",
                "8GB RAM, 512GB SSD",
                "14-inch FHD"
            ])
        case 2:
            show_laptop("Lenovo IdeaPad Slim 5i (16-inch)", [
                "Intel i5 13th Gen",
                "16GB RAM, 512GB SSD",
                "16-inch IPS"
            ])
        case 3:
            show_laptop("Lenovo Legion Pro 5i Gen 9 (16-inch)", [
                "Intel i7 14th Gen",
                "RTX 4070 GPU",
                "16-inch WQXGA"
            ])
        case 4:
            show_laptop("Lenovo IdeaPad 1 (Budget)", [
                "Ryzen 3 / Celeron",
                "8GB RAM",
                "Basic student use"
            ])
        case _:
            print("Invalid choice.")

# ─── DELL ───────────────────────────────────────────────────
def dell_menu():
    print("\n--- DELL ---")
    print("1. Intel i3")
    print("2. Intel i5")
    print("3. Intel i7")
    print("4. AMD Ryzen 3")
    print("5. AMD Ryzen 5")
    print("6. AMD Ryzen 7")

    try:
        c = int(input("Choice: "))
    except:
        print("Invalid.")
        return

    match c:
        case 1:
            show_laptop("Dell Inspiron 15 3530 (i3)", [
                "Intel i3 13th Gen",
                "8GB RAM, 512GB SSD"
            ])
        case 2:
            show_laptop("Dell Inspiron 15 3530 (i5)", [
                "Intel i5 13th Gen",
                "16GB RAM, 1TB SSD"
            ])
        case 3:
            show_laptop("Dell XPS 13 (9345/9350)", [
                "Intel Ultra 7",
                "OLED Display"
            ])
        case 4:
            show_laptop("Dell Inspiron 15 3535 (AMD Ryzen 3)", [
                "Ryzen 3 7320U",
                "8GB RAM, 256GB SSD"
            ])
        case 5:
            show_laptop("Dell G15 Ryzen Edition (Ryzen 5)", [
                "Ryzen 5 7600H",
                "RTX 4060",
                "165Hz Display"
            ])
        case 6:
            show_laptop("Dell XPS 14 (AMD Ryzen 7)", [
                "Ryzen 7 8840HS",
                "2.8K OLED"
            ])
        case _:
            print("Invalid choice.")

# ─── MAIN MENU ─────────────────────────────────────────────
def main():
    global total

    while True:
        print("\n=== LAPTOP RENTAL SYSTEM ===")
        print("1. Lenovo")
        print("2. Dell")
        print("3. Checkout & Exit")

        try:
            choice = int(input("Enter choice: "))
        except:
            print("Invalid input.")
            continue

        match choice:
            case 1:
                lenovo_menu()
            case 2:
                dell_menu()
            case 3:
                print("\n--- FINAL BILL ---")
                for item in laptop_selection:
                    print(item)
                print("Total Amount: $", total)
                print("Thank you.")
                break
            case _:
                print("Invalid choice.")

main()