import os
import requests
import pandas as pd
from playwright.sync_api import sync_playwright

def search_and_download_image(query, file_name):
    """
    Search DuckDuckGo for an image and download the first result.
    """
    try:
        with sync_playwright() as p:
            # Launch a headless browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to DuckDuckGo image search
            page.goto(f"https://duckduckgo.com/?q={query}&t=h_&iax=images&ia=images")
            
            # Wait for images to load
            page.wait_for_selector("tile--img__img  js-lazyload")
            
            # Get the first image URL
            image_url = page.query_selector("tile--img__img  js-lazyload" ).get_attribute("src")
            if not image_url:
                print(f"No images found for query: {query}")
                return False
            
            # Ensure the URL is complete
            if not image_url.startswith("http"):
                image_url = "https:" + image_url
            
            # Download the image
            image_data = requests.get(image_url).content
            with open(file_name, "wb") as f:
                f.write(image_data)
            
            print(f"Image saved: {file_name}")
            return True
    except Exception as e:
        print(f"Failed to download image for {query}. Error: {e}")
        return False

def main(csv_file):
    # Determine the directory where the script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Load the CSV file
    data = pd.read_csv(csv_file)
    
    for _, row in data.iterrows():
        sku = row['SKU']
        description = row['Product Description']
        manufacturer = row['Manufacturer']
        
        # Construct search query and file name
        query = f"{sku} {description} {manufacturer}"
        file_name = os.path.join(script_directory, f"{sku}_{manufacturer}.jpg".replace(" ", "_"))
        
        # Search and download the image
        search_and_download_image(query, file_name)

if __name__ == "__main__":
    # Input CSV file
    csv_file = "products.csv"  # Update this to your actual CSV file path
    main(csv_file)
