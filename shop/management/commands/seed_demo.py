from decimal import Decimal
from django.core.management.base import BaseCommand
from shop.models import Category, Product

PRODUCTS = [
    ("Everyday Backpack", "Bags", "A clean, durable backpack for work and weekends.", "1499.00", 24, True, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85"),
    ("Studio Headphones", "Electronics", "Comfortable over-ear headphones for focused listening.", "3299.00", 16, True, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85"),
    ("Minimal Ceramic Mug", "Home", "A tactile ceramic mug for your daily coffee ritual.", "499.00", 60, True, "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85"),
    ("Everyday Sneakers", "Fashion", "Versatile sneakers built for daily movement.", "2499.00", 18, False, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=85"),
    ("Desk Lamp", "Home", "Warm, adjustable light for a calmer workspace.", "1799.00", 13, False, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=85"),
    ("Classic Wristwatch", "Accessories", "A timeless dial with a clean, understated profile.", "4599.00", 9, True, "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=900&q=85"),
    ("Wireless Speaker", "Electronics", "Compact sound with a modern portable design.", "2199.00", 21, False, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=85"),
    ("Linen Tote", "Bags", "Lightweight everyday carry-all with a natural finish.", "699.00", 31, False, "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=900&q=85"),
]

class Command(BaseCommand):
    help = "Create illustrative demo categories and products. Replace all demo data before launch."

    def handle(self, *args, **options):
        categories = {}
        for _, category_name, *_ in PRODUCTS:
            categories[category_name], _ = Category.objects.get_or_create(name=category_name)
        for name, category_name, description, price, stock, featured, image_url in PRODUCTS:
            Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": categories[category_name],
                    "description": description,
                    "price": Decimal(price),
                    "stock": stock,
                    "is_featured": featured,
                    "image_url": image_url,
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Demo catalog seeded. These are sample products; replace before launch."))
