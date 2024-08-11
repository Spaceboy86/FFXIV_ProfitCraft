import requests
import json

# Define the world mapping
worlds = {'Ravana': 21, 'Bismarck': 22, 'Sephirot': 86, 'Sophia': 87, 'Zurvan': 88}

def itemPriceGetter(itemID, worldID):
    # Get the item's price information
    url = f"https://universalis.app/api/v2/aggregated/{worldID}/{itemID}"
    response = requests.get(url)
    itemResponse = response.json()
    result = itemResponse.get("results", [])[0] if itemResponse.get("results") else {}

    nqData = result.get("nq", {})
    hqData = result.get("hq", {})
    minListing = nqData.get("minListing", {})
    dc = minListing.get("dc", {})
    if nqData is None:
        nqData = hqData
    itemAvgPrice = minListing.get("dc", {}).get("price")
    itemLowest = minListing.get("dc", {}).get("price")
    itemLowestWorldId = minListing.get("dc", {}).get("worldId")

    # Find the world name if the world ID is found
    itemLowestWorld = None
    if itemLowestWorldId in worlds.values():
        itemLowestWorld = list(worlds.keys())[list(worlds.values()).index(itemLowestWorldId)]

    return itemAvgPrice, itemLowest, itemLowestWorld


def get_recipe_for_item(item_id, world_id):
    item_url = f"https://xivapi.com/Item/{item_id}?pretty=1"
    item_response = requests.get(item_url)

    # Check if the response is valid JSON
    try:
        item_data = item_response.json()
    except json.JSONDecodeError:
        print(f"Invalid JSON response for item ID: {item_id}")
        return None

    item_name = item_data.get("Name", "Unknown Item")
    item_avg_price, item_lowest_price, item_lowest_world = itemPriceGetter(item_id, world_id)

    item_results = item_data.get("GameContentLinks", {}).get("Recipe", {}).get("ItemResult", [])
    if not item_results:
        print(f"No recipe found for item ID {item_id}")
        return {
            "item_id": item_id,
            "item_name": item_name,
            "item_avg_price": item_avg_price,
            "item_lowest_price": item_lowest_price,
            "item_lowest_world": item_lowest_world,
            "ingredients": []
        }

    recipe_id = item_results[0]
    recipe_url = f"https://xivapi.com/Recipe/{recipe_id}?pretty=1"
    recipe_response = requests.get(recipe_url)

    # Check if the response is valid JSON
    try:
        recipe_data = recipe_response.json()
    except json.JSONDecodeError:
        print(f"Invalid JSON response for recipe ID: {recipe_id}")
        return None

    ingredient_data = []
    i = 0
    total_ingredient_cost = 0
    while True:
        AmountIngredient = f"AmountIngredient{i}"
        ItemIngredient = f"ItemIngredient{i}"
        itemTargetID = f"{ItemIngredient}TargetID"

        if AmountIngredient not in recipe_data:
            break

        ingredient_amount = recipe_data.get(AmountIngredient)
        item_ingredient_data = recipe_data.get(ItemIngredient, {})
        ingredient_name = item_ingredient_data.get("Name", "Unknown") if item_ingredient_data else "Unknown"
        ingredient_ID = recipe_data.get(itemTargetID)

        avg_price, lowest_price, lowest_world = itemPriceGetter(ingredient_ID, world_id) if ingredient_ID else (None, None, None)

        if ingredient_name != "Unknown" and ingredient_ID:
            ingredient_data.append({
                "amount": ingredient_amount,
                "name": ingredient_name,
                "id": ingredient_ID,
                "avg_price": avg_price,
                "lowest_price": lowest_price,
                "lowest_world": lowest_world
            })
            total_ingredient_cost += avg_price * ingredient_amount

        i += 1

    amount_result = recipe_data.get("AmountResult", 1)
    price_per_item = total_ingredient_cost / amount_result

    return {
        "item_id": item_id,
        "item_name": item_name,
        "item_avg_price": item_avg_price,
        "item_lowest_price": item_lowest_price,
        "item_lowest_world": item_lowest_world,
        "ingredients": ingredient_data,
        "price_per_item": price_per_item
    }


def check_and_store_subingredients(item_data, world_id):
    # This function will check if the ingredients have recipes and store the relevant data
    subingredients_data = []
    for ingredient in item_data['ingredients']:
        ingredient_id = ingredient.get("id")
        if ingredient_id:
            subingredient_data = get_recipe_for_item(ingredient_id, world_id)
            # If subingredients are found, store the data
            if subingredient_data:
                subingredients_data.append({
                    "ingredient": ingredient,
                    "subingredients": subingredient_data
                })
    return subingredients_data


def search_items():
    url = "https://xivapi.com/search?filters=ItemSearchCategory.ID=45,LevelItem%3E680,ItemKind.ID=5,Recipes!"
    print(f"Search URL: {url}")
    response = requests.get(url)
    data = response.json()
    filtered_data = {"Results": [item for item in data.get('Results', []) if 'crystal' not in item.get('Name', '').lower()]}
    return filtered_data


def save_data_to_json(data, filename="item_data.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def load_data_from_json(filename="item_data.json"):
    with open(filename, "r") as f:
        return json.load(f)


def sort_items_by_markup(item_data):
    sorted_items = sorted((item for item in item_data if "markup" in item), key=lambda x: x["markup"], reverse=True)
    top_3_items = sorted_items

    for item in top_3_items:
        print(f"\nItem Name: {item['item_name']}")
        print(f"Item Price: {item['item_avg_price']}")
        print(f"Markup Percentage: {item['markup']}%")
        print(f"Total Ingredient Cost: {item['total_ingredient_cost']}")
        print("Ingredients:")
        for ingredient in item["ingredients"]:
            if "is_cheaper_with_subingredients" in ingredient and ingredient["is_cheaper_with_subingredients"]:
                print(f"  - Amount: {ingredient['amount']}, Name: {ingredient['name']}, Avg Price: {ingredient['avg_price']} (Subingredient)")
                for subingredient in ingredient["subingredients"]:
                    print(f"      - Amount: {subingredient['amount']}, Name: {subingredient['name']}, Avg Price: {subingredient['avg_price']}")
            else:
                print(f"  - Amount: {ingredient['amount']}, Name: {ingredient['name']}, Avg Price: {ingredient['avg_price']} (Item Ingredient)")



def calculate_price_differences(item_data):
    for item in item_data:
        total_ingredient_cost = 0
        for ingredient in item["ingredients"]:
            is_cheaper_with_subingredients = ingredient.get("is_cheaper_with_subingredients", False)
            if is_cheaper_with_subingredients:
                total_ingredient_cost += ingredient.get("subingredient_avg_price", 0) * ingredient["amount"]
            else:
                total_ingredient_cost += ingredient.get("avg_price", 0) * ingredient["amount"]

        item["total_ingredient_cost"] = total_ingredient_cost
        item_avg_price = item.get("item_avg_price")
        if item_avg_price is not None:
            item["markup"] = ((item_avg_price - total_ingredient_cost) / total_ingredient_cost) * 100 \
                if total_ingredient_cost > 0 else 0

if __name__ == '__main__':
    # Example world name
    world_name = 'Ravana'
    world_id = worlds.get(world_name)

    # Load or fetch new data
    use_cached_data = True
    filename = "item_data.json"

    if use_cached_data:
        data_storage = load_data_from_json(filename)
        if not data_storage:
            data_storage = []
    else:
        data_storage = []

    # Fetch new data if not using cached data
    if not use_cached_data or not data_storage:
        items_data = search_items()
        print(f"Items fetched: {len(items_data.get('Results', []))}")
        for item in items_data.get('Results', []):
            item_id = item.get('ID')
            item_name = item.get('Name')
            print(f"Processing item: {item_name} (ID: {item_id})")
            item_data = get_recipe_for_item(item_id, world_id)
            if item_data:
                # check_and_store_subingredients(item_data, world_id)
                data_storage.append(item_data)

        save_data_to_json(data_storage, filename)

    calculate_price_differences(data_storage)
    sort_items_by_markup(data_storage)
