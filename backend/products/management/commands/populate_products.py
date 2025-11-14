from django.core.management.base import BaseCommand
from products.models import Category, Product
from django.contrib.auth import get_user_model
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populates categories and products for tech and medicine'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Step 1: Create categories
        categories = [
            "Laptops", "Smartphones", "Medical Devices", "Medicines", "Headphones", "Wearables"
        ]

        category_objects = []

        for category_name in categories:
            category = Category.objects.create(name=category_name)
            category_objects.append(category)
            self.stdout.write(f"Created category: {category_name}")

        # Step 2: Create products
        users = User.objects.all()
        if not users:
            raise ValueError("No users found. Please create a user first.")

        sample_descriptions = [
            "High performance, portable, and stylish.",
            "The latest model with cutting-edge features.",
            "Top-rated for comfort and clarity.",
            "A revolutionary medical device to improve health.",
            "Effective medicine for fast relief.",
            "An advanced wearable with health tracking."
        ]

        for _ in range(50):
            seller = random.choice(users)
            category = random.choice(category_objects)

            product_name = f"{category.name} Product {random.randint(1, 100)}"
            product_slug = product_name.lower().replace(" ", "-")
            price = Decimal(random.randint(100, 1000))  # Random price between 100 and 1000
            stock = random.randint(1, 100)  # Random stock count
            description = random.choice(sample_descriptions)
            
            # Create product
            product = Product.objects.create(
                seller=seller,
                category=category,
                name=product_name,
                slug=product_slug,
                description=description,
                price=price,
                stock=stock,
                is_active=True
            )
            self.stdout.write(f"Created product: {product.name} in {category.name}")

        self.stdout.write("Finished populating categories and products.")
