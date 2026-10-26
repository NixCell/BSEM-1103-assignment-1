"""
Product Inventory Monitor
PROG211 - Object-Oriented Programming 1

Expected profit = (selling price per unit - cost per unit) * quantity.
This is an estimate before other business expenses and taxes.
"""


class Product:
    """Parent class for all products."""

    STATUSES = ("Active", "Discontinued")

    def __init__(self, name, category, unit_cost, selling_price, quantity, status="Active"):
        self._name = self._validate_name(name, "Product name")
        self._category = self._validate_name(category, "Product group")
        self.unit_cost = unit_cost
        self.selling_price = selling_price
        self.quantity = quantity
        self.status = status

    @staticmethod
    def _validate_name(value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} cannot be empty.")
        return value.strip()

    @property
    def name(self):
        return self._name

    @property
    def category(self):
        return self._category

    @property
    def unit_cost(self):
        return self._unit_cost

    @unit_cost.setter
    def unit_cost(self, value):
        value = validate_money(value, "Cost")
        self._unit_cost = value

    @property
    def selling_price(self):
        return self._selling_price

    @selling_price.setter
    def selling_price(self, value):
        value = validate_money(value, "Selling price")
        self._selling_price = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        self._quantity = validate_quantity(value, allow_zero=True)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in self.STATUSES:
            raise ValueError("Choose a valid product status.")
        self._status = value

    @property
    def total_cost(self):
        return self.unit_cost * self.quantity

    @property
    def total_selling_value(self):
        return self.selling_price * self.quantity

    @property
    def expected_profit(self):
        return (self.selling_price - self.unit_cost) * self.quantity

    def describe(self):
        """Subclasses can override this method (polymorphism)."""
        return f"{self.name} ({self.category})"

    def display_info(self):
        print_product(self)


class FoodProduct(Product):
    """Example product subclass for food items."""

    def describe(self):
        return f"{super().describe()} - food product"


class GeneralProduct(Product):
    """Product subclass for all other product groups."""

    def describe(self):
        return f"{super().describe()} - general product"


def validate_money(value, label):
    """Accept only numeric amounts that are zero or greater."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number.")
    if value < 0:
        raise ValueError(f"{label} cannot be negative.")
    return round(float(value), 2)


def validate_quantity(value, allow_zero=False):
    """Accept only whole-number quantities."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Quantity must be a whole number.")
    minimum = 0 if allow_zero else 1
    if value < minimum:
        raise ValueError(f"Quantity must be at least {minimum}.")
    return value


class ProductInventory:
    """Stores product groups and their products in dictionaries."""

    total_products_created = 0

    def __init__(self):
        # Structure: {category_name: {product_name: Product object}}
        self._groups = {}

    @property
    def groups(self):
        return self._groups

    @classmethod
    def get_total_products_created(cls):
        return cls.total_products_created

    @staticmethod
    def is_valid_status(status):
        return status in Product.STATUSES

    def add_group(self, group_name):
        group_name = Product._validate_name(group_name, "Product group")
        existing = self._find_group_name(group_name)
        if existing:
            return existing
        self._groups[group_name] = {}
        return group_name

    def _find_group_name(self, name):
        for existing in self._groups:
            if existing.casefold() == name.casefold():
                return existing
        return None

    def _find_product(self, category, product_name):
        group_key = self._find_group_name(category)
        if group_key is None:
            return None
        for existing_name, product in self._groups[group_key].items():
            if existing_name.casefold() == product_name.casefold():
                return product
        return None

    def add_product(self, category, name, unit_cost, selling_price, quantity, status):
        """Create a product, or add quantity to a matching existing product."""
        category = self.add_group(category)
        name = Product._validate_name(name, "Product name")
        quantity = validate_quantity(quantity)
        unit_cost = validate_money(unit_cost, "Cost")
        selling_price = validate_money(selling_price, "Selling price")
        if not self.is_valid_status(status):
            raise ValueError("Choose a valid product status.")

        existing = self._find_product(category, name)
        if existing is not None:
            # Do not create duplicate entries for an already-recorded product.
            existing.quantity += quantity
            # A discontinued item stays discontinued until the user changes it.
            print(f"Added {quantity} unit(s) to existing product '{existing.name}'.")
            print("The existing product's cost, selling price and status were kept.")
            return existing, False

        product_class = FoodProduct if category.casefold() in {"food", "foods", "groceries"} else GeneralProduct
        product = product_class(name, category, unit_cost, selling_price, quantity, status)
        self._groups[category][name] = product
        ProductInventory.total_products_created += 1
        print(f"Product '{name}' was recorded in group '{category}'.")
        return product, True

    def get_group_products(self, category):
        group_key = self._find_group_name(category)
        return self._groups.get(group_key, {}) if group_key else {}

    def all_products(self):
        for group_name, products in self._groups.items():
            for product in products.values():
                yield group_name, product

    def display_group(self, category):
        products = self.get_group_products(category)
        if not products:
            print("There are no products recorded in this group yet.")
            return
        print(f"\n=== PRODUCTS IN {category.upper()} ===")
        for number, product in enumerate(products.values(), start=1):
            print(f"\nProduct {number}: {product.describe()}")
            product.display_info()

    def display_all(self):
        if not self._groups or not any(self._groups.values()):
            print("No products have been recorded yet.")
            return
        grand_quantity = 0
        grand_cost = 0.0
        grand_selling = 0.0
        grand_profit = 0.0
        for group_name, products in self._groups.items():
            print(f"\n{'=' * 65}\nGROUP: {group_name}\n{'=' * 65}")
            if not products:
                print("No products in this group yet.")
                continue
            for product in products.values():
                product.display_info()
                print("-" * 65)
                grand_quantity += product.quantity
                grand_cost += product.total_cost
                grand_selling += product.total_selling_value
                grand_profit += product.expected_profit
        print("\n=============== INVENTORY TOTALS ===============")
        print(f"Number of product types : {sum(len(p) for p in self._groups.values())}")
        print(f"Total quantity of units : {grand_quantity}")
        print(f"Total cost value        : {grand_cost:.2f}")
        print(f"Total selling value     : {grand_selling:.2f}")
        print(f"Total expected profit   : {grand_profit:.2f}")


def print_product(product):
    print(f"Product name       : {product.name}")
    print(f"Product group      : {product.category}")
    print(f"Unit cost          : {product.unit_cost:.2f}")
    print(f"Selling price      : {product.selling_price:.2f}")
    print(f"Quantity in stock  : {product.quantity}")
    print(f"Status             : {product.status}")
    print(f"Total cost amount  : {product.total_cost:.2f}")
    print(f"Total sales value  : {product.total_selling_value:.2f}")
    print(f"Expected profit    : {product.expected_profit:.2f}")


def choose_from_list(title, options, allow_create=False):
    """Display numbered options and reject invalid selections."""
    options = list(options)
    while True:
        print(f"\n{title}")
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")
        if allow_create:
            print(f"{len(options) + 1}. Create a new one")
        print("0. Cancel / go back")
        raw = input("Choose an option: ").strip()
        if not raw.isdigit():
            print("Invalid input. Enter one of the listed numbers.")
            continue
        choice = int(raw)
        if choice == 0:
            return None
        if 1 <= choice <= len(options):
            return options[choice - 1]
        if allow_create and choice == len(options) + 1:
            return "__CREATE_NEW__"
        print("That option is not on the list. Try again.")


def input_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def input_money(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value < 0:
                print("Amount cannot be negative. Try again.")
                continue
            return round(value, 2)
        except ValueError:
            print("Enter a valid number, for example 150 or 150.50.")


def input_quantity(prompt, minimum=1):
    while True:
        raw = input(prompt).strip()
        try:
            # Reject decimals, signs and other non-integer text.
            if not raw.isdigit():
                raise ValueError
            value = int(raw)
            if value < minimum:
                print(f"Quantity must be at least {minimum}.")
                continue
            return value
        except ValueError:
            print("Enter a valid whole number.")


def record_product(inventory):
    group_names = list(inventory.groups.keys())
    category = choose_from_list("Choose a product group", group_names, allow_create=True)
    if category is None:
        return
    if category == "__CREATE_NEW__":
        category = input_nonempty("Enter the name of the new product group: ")
        existing_group = inventory._find_group_name(category)
        if existing_group:
            category = existing_group
            print(f"The group '{category}' already exists. It will be reused.")
        else:
            inventory.add_group(category)
            print(f"Created product group '{category}'.")

    existing_products = inventory.get_group_products(category)
    product_choice = choose_from_list(
        f"Choose a product in '{category}' or create a new product",
        existing_products.keys(), allow_create=True
    )
    if product_choice is None:
        return

    if product_choice != "__CREATE_NEW__":
        product = existing_products[product_choice]
        print(f"Selected existing product: {product.name}")
        amount = input_quantity("How many additional units are being added? ")
        product.quantity += amount
        print(f"Added {amount} unit(s). New quantity: {product.quantity}.")
        print("Existing cost, selling price and status remain unchanged.")
        return

    name = input_nonempty("Enter the product name: ")
    # If the same name already exists, add stock rather than making a duplicate.
    duplicate = inventory._find_product(category, name)
    if duplicate:
        amount = input_quantity("This product already exists. How many units should be added? ")
        duplicate.quantity += amount
        print(f"Added {amount} unit(s). New quantity: {duplicate.quantity}.")
        return

    cost = input_money("Enter the cost per unit: ")
    selling_price = input_money("Enter the selling price per unit: ")
    while selling_price < cost:
        print("Warning: selling price is below cost, so each sale would make a loss.")
        confirm = choose_from_list("Keep this loss-making price?", ("Yes, keep it", "No, enter price again"))
        if confirm is None or confirm == "No, enter price again":
            selling_price = input_money("Enter the selling price per unit: ")
        else:
            break
    quantity = input_quantity("Enter the quantity being added: ")
    status = choose_from_list("Choose product status", Product.STATUSES)
    if status is None:
        print("Product recording cancelled.")
        return
    try:
        inventory.add_product(category, name, cost, selling_price, quantity, status)
    except ValueError as error:
        print(f"Could not record product: {error}")


def view_products(inventory):
    options = list(inventory.groups.keys())
    if not options:
        print("No product groups exist yet.")
        return
    options.append("All groups and products")
    choice = choose_from_list("Choose which products to view", options)
    if choice is None:
        return
    if choice == "All groups and products":
        inventory.display_all()
    else:
        inventory.display_group(choice)


def update_product_status(inventory):
    available = [(group, product) for group, product in inventory.all_products()]
    if not available:
        print("No products have been recorded yet.")
        return
    labels = [f"{product.name} (Group: {group}, status: {product.status})" for group, product in available]
    selected = choose_from_list("Choose a product to update", labels)
    if selected is None:
        return
    product = available[labels.index(selected)][1]
    new_status = choose_from_list("Choose the new status", Product.STATUSES)
    if new_status is not None:
        product.status = new_status
        print(f"Status for '{product.name}' updated to {new_status}.")


def main():
    inventory = ProductInventory()
    print("=" * 58)
    print("       PRODUCT INVENTORY MONITOR")
    print("=" * 58)
    print("Money values are shown in the same currency you enter.\n")

    while True:
        print("\nMAIN MENU")
        print("1. Record a product / add stock")
        print("2. View products and totals")
        print("3. View products in one group")
        print("4. Update a product's status")
        print("5. Show total number of product types")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            record_product(inventory)
        elif choice == "2":
            inventory.display_all()
        elif choice == "3":
            view_products(inventory)
        elif choice == "4":
            update_product_status(inventory)
        elif choice == "5":
            print(f"Total product types recorded: {ProductInventory.get_total_products_created()}")
        elif choice == "0":
            print("Thank you for using Product Inventory Monitor.")
            break
        else:
            print("Invalid choice. Please select one of the listed menu options.")


if __name__ == "__main__":
    main()
