import requests
import json

def build_category_tree(categories):
    tree = {}
    parent_map = {cat['id']: cat for cat in categories}

    # Initialize each category in the tree
    for cat in categories:
        cat_id = cat['id']
        tree[cat_id] = {
            'name': cat['name'],
            'children': [],
            'parent_category_id': cat.get('parent_category_id')
        }

    # Assign children to their respective parents
    for cat in categories:
        parent_id = cat['parent_category_id']
        if parent_id and parent_id in parent_map:
            tree[parent_id]['children'].append(cat['id'])

    return tree

def print_category_tree(tree, parent_id=None, level=0):
    if parent_id is None:
        for cat_id, cat in tree.items():
            if not cat['parent_category_id']:
                print_category_tree(tree, cat_id)
    else:
        parent = tree[parent_id]
        print('    ' * level + parent['name'])
        for child_id in parent['children']:
            print_category_tree(tree, child_id, level + 1)

# API URL and headers
api_url = "https://your_domain.vendhq.com/api/2.0/product_categories"
api_headers = {"authorization": "Bearer your_token"}

# Fetch data from API
try:
    response = requests.get(api_url, headers=api_headers)
    if response.status_code == 200:
        response_json = response.json()
        print("[INFO] API response received successfully.")

        # Access the nested 'data' within 'data'
        if "data" in response_json and "data" in response_json["data"]:
            nested_data = response_json["data"]["data"]

            if "categories" in nested_data:
                categories = nested_data["categories"]
                print(f"[INFO] Found {len(categories)} categories.")

                # Build and print the category tree
                category_tree = build_category_tree(categories)
                print_category_tree(category_tree)
            else:
                print("[ERROR] 'categories' key not found in the nested 'data'.")
        else:
            print("[ERROR] Nested 'data' key not found in the response.")
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
except requests.exceptions.RequestException as e:
    print(f"[ERROR] Request failed: {e}")
