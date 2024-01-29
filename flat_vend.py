import requests
import csv
from tqdm import tqdm
import time

# Define your API URL and access token
url = "https://your_domain.vendhq.com/api/2.0/products"
headers = {
    "authorization": "Bearer your_token"
}

# Initialize an empty list to store all product data
all_products = []

# Define a function to flatten nested JSON while maintaining hierarchy
def flatten_json(y):
    """Recursively flattens a nested JSON structure with hierarchical field names."""
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# Start with an 'after' value of 0 for the first page
after = 0

# Initialize a progress bar
total_pages = None
progress_bar = None

while True:
    params = {"after": after}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad requests

        data = response.json()
        products = data.get("data", [])
        if products:
            all_products.extend(products)
            after = data["version"]["max"]  # Get the 'max' version for the next page
            if total_pages is None:
                total_pages = data["version"]["max"]
                progress_bar = tqdm(total=total_pages, desc="Fetching Products", unit="page")

        else:
            print("No more products to fetch.")
            break

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        break

    if progress_bar:
        progress_bar.update(1)
    time.sleep(1)  # Sleep for 1 second to avoid hitting rate limits

if progress_bar:
    progress_bar.close()

# Check if any products were fetched
if all_products:
    flattened_products = [flatten_json(product) for product in all_products]

    for product in flattened_products:
        if 'sku' in product:
            product['sku'] = str(product['sku'])

    all_keys = set()
    for product in flattened_products:
        all_keys.update(product.keys())

    headers = sorted(list(all_keys))

    with open("p13.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for product in flattened_products:
            writer.writerow(product)

    print("Data saved to p13.csv")
else:
    print("No data to save")

