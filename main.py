import requests
import json

# Define the world mapping
worlds = {'Ravana': 21, 'Bismarck': 22, 'Sephirot': 86, 'Sophia': 87, 'Zurvan': 88}
data_centers = {'Light': [21, 22, 86, 87, 88]}
processed_ingredients = set()
recipe_list = []


# Price fetching functions
def fetchAggregatedPrices(itemID, worldID, name):
    url = f"https://universalis.app/api/v2/aggregated/{worldID}/{itemID}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching aggregated prices for item {itemID}: {response.status_code}")
        return {"itemAvgPrice": None, "itemLowest": None, "itemLowestWorld": None}

    try:
        itemResponse = response.json()
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response for item {itemID}")
        return {"itemAvgPrice": None, "itemLowest": None, "itemLowestWorld": None}

    if 'results' not in itemResponse or not itemResponse['results']:
        return {"itemAvgPrice": None, "itemLowest": None, "itemLowestWorld": None}

    result = itemResponse['results'][0]

    def get_price_data(data):
        minListing_world = data.get("minListing", {}).get("world", {}).get("price")
        averageSalePrice_world = data.get("averageSalePrice", {}).get("world", {}).get("price")
        recentPurchase_world = data.get("recentPurchase", {}).get("world", {}).get("price")

        minListing_dc = data.get("minListing", {}).get("dc", {}).get("price")
        minListing_region = data.get("minListing", {}).get("region", {}).get("price")

        itemAvgPrice = minListing_world or averageSalePrice_world or recentPurchase_world or minListing_dc or minListing_region

        itemLowestWorldId = data.get("minListing", {}).get("world", {}).get("worldId") or \
                            data.get("recentPurchase", {}).get("world", {}).get("worldId") or \
                            data.get("averageSalePrice", {}).get("world", {}).get("worldId") or \
                            data.get("minListing", {}).get("dc", {}).get("worldId") or \
                            data.get("minListing", {}).get("region", {}).get("worldId")

        return itemAvgPrice, itemLowestWorldId

    itemAvgPrice, itemLowestWorldId = get_price_data(result.get("hq", {}))
    if not itemAvgPrice:
        itemAvgPrice, itemLowestWorldId = get_price_data(result.get("nq", {}))

    itemLowestWorld = None
    if itemLowestWorldId in worlds.values():
        itemLowestWorld = list(worlds.keys())[list(worlds.values()).index(itemLowestWorldId)]

    return {"itemAvgPrice": itemAvgPrice, "itemLowest": itemAvgPrice, "itemLowestWorld": itemLowestWorld}


def fetchDetailedPrices(itemID, worldID, name):
    url = f"https://universalis.app/api/v2/{worldID}/{itemID}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching detailed prices for item {itemID}: {response.status_code}")
        return {"itemAvgPrice": None, "itemLowest": None, "itemLowestWorld": None}

    try:
        itemResponse = response.json()
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response for item {itemID}")
        return {"itemAvgPrice": None, "itemLowest": None, "itemLowestWorld": None}

    listings = itemResponse.get("listings", [])
    if not listings:
        print(f"No listings found for item {itemID} in world {worldID}")
        return {"itemAvgPrice": None, "itemLowest": None, "itemLowestWorld": None}

    pricesHQ = [listing['pricePerUnit'] for listing in listings if listing['hq']]
    pricesNQ = [listing['pricePerUnit'] for listing in listings if not listing['hq']]

    if pricesHQ:
        itemAvgPrice = sum(pricesHQ) / len(pricesHQ)
        itemLowest = min(pricesHQ)
    elif pricesNQ:
        itemAvgPrice = sum(pricesNQ) / len(pricesNQ)
        itemLowest = min(pricesNQ)
    else:
        return {"itemAvgPrice": None, "itemLowest": None, "itemLowestWorld": None}

    itemLowestWorldId = listings[0].get('worldID')
    itemLowestWorld = None
    if itemLowestWorldId in worlds.values():
        itemLowestWorld = list(worlds.keys())[list(worlds.values()).index(itemLowestWorldId)]

    return {"itemAvgPrice": itemAvgPrice, "itemLowest": itemLowest, "itemLowestWorld": itemLowestWorld}


def itemPriceGetter(itemID, worldID, name):
    url_aggregated = f"https://universalis.app/api/v2/aggregated/{worldID}/{itemID}"
    url_current = f"https://universalis.app/api/v2/{worldID}/{itemID}"

    response = requests.get(url_aggregated)
    if response.status_code == 200:
        itemResponse = response.json()
        if 'results' in itemResponse and itemResponse['results']:
            result = itemResponse['results'][0]

            def get_price_data(data, world=True):
                if world:
                    return data.get("minListing", {}).get("world", {}).get("price") or \
                        data.get("averageSalePrice", {}).get("world", {}).get("price") or \
                        data.get("recentPurchase", {}).get("world", {}).get("price")
                return data.get("minListing", {}).get("dc", {}).get("price") or \
                    data.get("minListing", {}).get("region", {}).get("price")

            # HQ Prices
            itemAvgPrice = get_price_data(result.get("hq", {}), world=True)
            if not itemAvgPrice:
                itemAvgPrice = get_price_data(result.get("hq", {}), world=False)
            if not itemAvgPrice:
                itemAvgPrice = get_price_data(result.get("nq", {}), world=True)
            if not itemAvgPrice:
                itemAvgPrice = get_price_data(result.get("nq", {}), world=False)
            if not itemAvgPrice:
                print(f"No HQ or NQ data available for item {itemID}")

            # Lowest World ID for HQ
            itemLowestWorldId = result.get("hq", {}).get("minListing", {}).get("world", {}).get("worldId") or \
                                result.get("nq", {}).get("minListing", {}).get("world", {}).get("worldId")
            itemLowestWorld = list(worlds.keys())[
                list(worlds.values()).index(itemLowestWorldId)] if itemLowestWorldId in worlds.values() else None

            if itemAvgPrice:
                return {"itemAvgPrice": itemAvgPrice, "itemLowest": itemAvgPrice, "itemLowestWorld": itemLowestWorld}

    # Fallback to current prices if aggregated doesn't return a price
    response = requests.get(url_current)
    if response.status_code == 200:
        itemResponse = response.json()
        if 'listings' in itemResponse and itemResponse['listings']:
            minPriceHQ = min([listing['pricePerUnit'] for listing in itemResponse['listings'] if listing['hq']],
                             default=None)
            avgPriceHQ = sum([listing['pricePerUnit'] for listing in itemResponse['listings'] if listing['hq']]) / len(
                [listing['pricePerUnit'] for listing in itemResponse['listings'] if listing['hq']]) if [
                listing['pricePerUnit'] for listing in itemResponse['listings'] if listing['hq']] else None
            minPriceNQ = min([listing['pricePerUnit'] for listing in itemResponse['listings']], default=None)
            avgPriceNQ = sum([listing['pricePerUnit'] for listing in itemResponse['listings']]) / len(
                [listing['pricePerUnit'] for listing in itemResponse['listings']]) if [listing['pricePerUnit'] for
                                                                                       listing in itemResponse[
                                                                                           'listings']] else None
            if minPriceHQ:
                return {"itemAvgPrice": minPriceHQ, "itemLowest": minPriceHQ, "itemLowestWorld": worldID}
            if avgPriceHQ:
                return {"itemAvgPrice": avgPriceHQ, "itemLowest": avgPriceHQ, "itemLowestWorld": worldID}
            if minPriceNQ:
                return {"itemAvgPrice": minPriceNQ, "itemLowest": minPriceNQ, "itemLowestWorld": worldID}
            if avgPriceNQ:
                return {"itemAvgPrice": avgPriceNQ, "itemLowest": avgPriceNQ, "itemLowestWorld": worldID}
    print(f"Error fetching prices for item {itemID}")
    return {"itemAvgPrice": None, "itemLowest": None, "itemLowestWorld": None}


def fetch_item_prices(recipe_map, world_id, ingredient_prices):
    data_storage = []

    for recipe in recipe_map:
        item_id = recipe['item_id']
        item_name = recipe['item_name']
        ingredients = recipe['ingredients']
        yields = recipe['yields']

        total_ingredient_cost = 0
        ingredient_data = []

        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id not in ingredient_prices:
                ingredient_prices[ingredient_id] = itemPriceGetter(ingredient_id, world_id, ingredient['name'])
            ingredient_info = ingredient_prices[ingredient_id]
            avg_price = ingredient_info.get('itemAvgPrice', 0)

            ingredient_data.append({
                "name": ingredient['name'],
                "id": ingredient_id,
                "avg_price": avg_price,
                "lowest_price": ingredient_info.get('itemLowest'),
                "lowest_world": ingredient_info.get('itemLowestWorld')
            })

            total_ingredient_cost += avg_price * ingredient['amount']

        recipe_price_data = itemPriceGetter(item_id, world_id, item_name)
        avg_price = recipe_price_data['itemAvgPrice'] or 0
        lowest_price = recipe_price_data['itemLowest'] or 0
        lowest_world = recipe_price_data['itemLowestWorld'] or 'Unknown'

        data_storage.append({
            "item_name": item_name,
            "item_id": item_id,
            "item_avg_price": avg_price,
            "item_lowest_price": lowest_price,
            "item_lowest_world": lowest_world,
            "total_ingredient_cost": total_ingredient_cost / yields,
            "markup": ((avg_price - total_ingredient_cost / yields) / (
                    total_ingredient_cost / yields)) * 100 if total_ingredient_cost > 0 else 0,
            "ingredients": ingredient_data
        })

    return data_storage


# Utility functions
def load_data_from_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def save_data_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def search_items():
    try:
        url = "https://beta.xivapi.com/api/1/search?sheets=Recipe&query=ItemResult.ItemSearchCategory=45%20ItemResult.LevelItem%3E=680"
        response = requests.get(url)
        if response.status_code == 504:
            print("504 @ search_items")
            return search_items()
        else:
            data = response.json()
            filtered_data = [item['row_id'] for item in data['results']]
            return filtered_data
    except Exception as e:
        print(f"An error occurred: {e}")


def get_item_names(item_ids):
    try:
        item_ids_str = ','.join(map(str, item_ids))
        url = f"https://beta.xivapi.com/api/1/sheet/Item?rows={item_ids_str}&columns=Name"
        response = requests.get(url)
        data = response.json()
        if 'rows' not in data:
            print(f"Unexpected response format: {data}")
            return {}
        item_names = {item['row_id']: item['fields']['Name'] for item in data['rows']}
        return item_names
    except Exception as e:
        print(f"An error occurred while fetching item names: {e}")
        return {}


# Main recipe processing functions
def get_recipe_for_item(recipe_id, world_id):
    recipe_url = f"https://beta.xivapi.com/api/1/sheet/Recipe/{recipe_id}"
    recipe_response = requests.get(recipe_url)
    recipe_details = recipe_response.json()

    recipe_item_id = recipe_details['fields']['ItemResult']['value']
    recipe_item_name = recipe_details['fields']['ItemResult']['fields']['Name']
    ingredient_data = []
    print(f"Processing item: {recipe_item_name} (ID: {recipe_item_id})")

    for x, ingredient in enumerate(recipe_details['fields']['Ingredient']):
        ingredient_id = ingredient['value']
        if ingredient_id <= 0:
            continue

        amount_ingredient = recipe_details['fields']['AmountIngredient'][x]

        item_url = f"https://beta.xivapi.com/api/1/sheet/Item/{ingredient_id}"
        item_response = requests.get(item_url)
        item_details = item_response.json()
        ingredient_name = item_details['fields'].get('Name', 'Unknown')

        price_data = itemPriceGetter(ingredient_id, world_id, ingredient_name)
        avg_price = price_data['itemAvgPrice'] or 0
        lowest_price = price_data['itemLowest'] or 0
        lowest_world = price_data['itemLowestWorld'] or 'Unknown'

        ingredient_data.append({
            "amount": amount_ingredient,
            "name": ingredient_name,
            "id": ingredient_id,
            "avg_price": avg_price,
            "lowest_price": lowest_price,
            "lowest_world": lowest_world
        })

    amount_result = recipe_details['fields'].get("AmountResult", 1)
    total_ingredient_cost = sum(
        ing['avg_price'] * ing['amount'] for ing in ingredient_data if ing['avg_price'] is not None)
    price_per_item = total_ingredient_cost / amount_result

    price_data = itemPriceGetter(recipe_item_id, world_id, recipe_item_name)
    avg_price = price_data['itemAvgPrice'] or 0
    lowest_price = price_data['itemLowest'] or 0
    lowest_world = price_data['itemLowestWorld'] or 'Unknown'

    return {
        "item_id": recipe_item_id,
        "item_name": recipe_item_name,
        "item_avg_price": avg_price,
        "item_lowest_price": lowest_price,
        "item_lowest_world": lowest_world,
        "total_ingredient_cost": total_ingredient_cost,
        "markup": ((
                               avg_price - total_ingredient_cost) / total_ingredient_cost) * 100 if total_ingredient_cost > 0 else 0,
        "ingredients": ingredient_data
    }


def calculate_price_differences(data_storage):
    for item in data_storage:
        total_ingredient_cost = sum(
            ingredient['avg_price'] * ingredient['amount'] for ingredient in item['ingredients'])
        item['total_ingredient_cost'] = total_ingredient_cost
        item_avg_price = item.get('item_avg_price') or 0
        if item_avg_price:
            item['markup'] = ((
                                          item_avg_price - total_ingredient_cost) / total_ingredient_cost) * 100 if total_ingredient_cost > 0 else 0


def sort_items_by_markup(data_storage):
    sorted_items = sorted(data_storage, key=lambda x: x['markup'], reverse=True)
    for item in sorted_items:
        print(f"\nItem Name: {item['item_name']} - ID: {item['item_id']} - Price: {item['item_avg_price']}")
        print(f"Total Ingredient Price: {item['total_ingredient_cost']} - Difference Markup %: {item['markup']}")
        print("Ingredients:")
        for ingredient in item['ingredients']:
            print(
                f"  - {ingredient['name']} (ID: {ingredient['id']}) - Price: {ingredient['avg_price']} - Amount: {ingredient['amount']}")
            if 'subingredients' in ingredient:
                print("    Subingredients:")
                for subingredient in ingredient['subingredients']:
                    print(
                        f"      - {subingredient['name']} (ID: {subingredient['id']}) - Price: {subingredient['avg_price']} - Amount: {subingredient['amount']}")


def display_final_output(data_storage):
    for item in data_storage:
        print(f"Item Name: {item['item_name']} - ID: {item['item_id']} - Price: {item['item_avg_price']}")
        print(f"Total Ingredient Price: {item['total_ingredient_cost']} - Difference Markup %: {item['markup']}%")
        print("Ingredients:")
        for ingredient in item["ingredients"]:
            print(f"  - {ingredient['name']} (ID: {ingredient['id']}) - Price: {ingredient['avg_price']} - Amount: {ingredient['amount']} ")
            if "subingredients" in ingredient:
                for subingredient in ingredient["subingredients"]:
                    print(
                        f"      - {subingredient['name']} (ID: {subingredient['id']}) - Price: {subingredient['avg_price']}")
        print()


def recipe_mapper(recipe_mapping):
    found_recipes = []

    recipe_list = search_items()
    item_ids = set()

    for recipe_id in recipe_list:
        recipe_id_str = str(recipe_id)
        if recipe_id_str in recipe_mapping['recipes']:
            recipe_data = recipe_mapping['recipes'][recipe_id_str]
            item_id = recipe_data["itemId"]
            ingredients = [{"id": ing["id"], "amount": ing["amount"]} for ing in recipe_data["ingredients"]]
            yields = recipe_data["yields"]
            extracted_recipe = {
                "item_id": item_id,
                "ingredients": ingredients,
                "yields": yields
            }
            found_recipes.append(extracted_recipe)
            item_ids.add(item_id)
            for ing in ingredients:
                item_ids.add(ing["id"])

    item_names = get_item_names(item_ids)

    for recipe in found_recipes:
        recipe['item_name'] = item_names.get(recipe['item_id'], 'Unknown Item')
        for ingredient in recipe['ingredients']:
            ingredient['name'] = item_names.get(ingredient['id'], 'Unknown Ingredient')

    return found_recipes


def idlist(recipes_data):
    item_ids = set()
    for recipe in recipes_data:
        item_ids.add(recipe['item_id'])
        for ingredient in recipe['ingredients']:
            item_ids.add(ingredient['id'])

    item_ids_str = ','.join(map(str, item_ids))
    print(item_ids_str)


# Main function
if __name__ == '__main__':
    world_name = 'Ravana'
    world_id = worlds.get(world_name)

    use_cached_data = True
    filename = "item_data.json"

    recipe_map = load_data_from_json('recipes-ingredient-lookup.json')
    mapper_out = recipe_mapper(recipe_map)
    idlist(mapper_out)

    item_ids = {recipe['item_id'] for recipe in mapper_out}
    for recipe in mapper_out:
        for ingredient in recipe['ingredients']:
            item_ids.add(ingredient['id'])

    item_names = get_item_names(item_ids)
    print(f"Fetched item names: {item_names}")

    data_storage = []

    if not use_cached_data or not data_storage:
        recipe_list = search_items()
        for recipe_id in recipe_list:
            item_data = get_recipe_for_item(recipe_id, world_id)
            if item_data:
                data_storage.append(item_data)

        save_data_to_json(data_storage, filename)

    calculate_price_differences(data_storage)
    sort_items_by_markup(data_storage)
    display_final_output(data_storage)
