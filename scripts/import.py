import os
import sys
import django
import csv
import logging

# Add the project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'widget_store.settings')

# Initialize Django
django.setup()

# Import models and settings after setup
from store.models import Product, Category
from django.conf import settings
from django.utils.text import slugify

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_products_from_csv(file_path):
    """
    Import products from a tab-limited CSV file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Create a DictReader with the tab character as the delimiter
            reader = csv.DictReader(file, delimiter='\t')
            
            for row in reader:
                logger.info("Processing row: %s", row)
                # Get or create the Category object
                category, created = Category.objects.get_or_create(name=row['category'])
                
                # Generate slug
                slug = slugify(row['sku'])

                # Create the Product object
                product = Product(
                    name= None,
                    sku=row['sku'],
                    category=category,
                    price=None,  # Ensure price is optional
                    description=row['description'] if row['description'] else '',  # Ensure description is optional
                    image= None,  # Ensure image is optional
                    slug=slug,
                    quantity=None,  # Convert to int and ensure optional
                    manufacturer=row['manufacturer'] if row['manufacturer'] else '',  # Ensure manufacturer is optional
                    condition=None,  # Ensure condition is optional
                )
                product.save()
                logger.info("Saved product: %s", product.name)
    except FileNotFoundError:
        logger.error("The file '%s' was not found.", file_path)
    except Exception as e:
        logger.error("An error occurred: %s", e)

if __name__ == "__main__":
    # Path to your CSV file
    csv_file_path = 'scripts/productstest.csv'
    import_products_from_csv(csv_file_path)
