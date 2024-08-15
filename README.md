# FFXIV Profit Craft
## Overview
What started as a small idea turned into a rabbit hole, as they often do.  
FFXIV Profit Craft is a tool designed to assist players of Final Fantasy XIV in optimizing their crafting strategies for profit. By leveraging data from XIVAPI and Universalis, this tool helps users determine the most profitable items to craft by comparing market prices and ingredient costs.  

## Features
- Recipe Search: Uses XIVAPI to search for recipes that meet specific criteria (e.g., item level, category).
- Ingredient Mapping: Maps recipe ingredients using data from TeamCraft's recipes-ingredient-lookup.json.
- Ingredient Price Analysis: Checks if ingredients themselves have recipes, retrieves their sub-ingredient information, and calculates the total cost.
- Price Fetching: Retrieves current market prices for items and ingredients from Universalis, using both aggregated and detailed price data.
- Profit Calculation: Compares the market price of the crafted item against the cost of ingredients, including sub-ingredients where applicable, to determine profit margins.
- Data Storage: Saves the fetched data into a JSON file for future use and reference.
- Result Sorting: Sorts items based on price markup to highlight the most profitable crafting opportunities.
- Final Output: Displays the top items along with detailed information about their ingredients and potential profits.

## How It Works
Search for Recipes:
- The tool queries XIVAPI to find recipes that match the specified criteria.

Map Ingredients:
- Matches the recipe IDs against TeamCraft's recipes-ingredient-lookup.json to retrieve ingredient details.
   
Price Fetching:
- For each item and its ingredients, the tool fetches market prices from Universalis, first trying to get aggregated prices, and if necessary, fetching detailed prices.  
- The tool prioritizes HQ (high-quality) prices and falls back to NQ (normal-quality) prices if needed.
  
Profit Calculation:
- The tool calculates the total cost of ingredients and compares it to the market price of the crafted item, considering both direct ingredient costs and potential sub-ingredient costs.
  
Data Storage:
- All data, including prices and recipe information, is saved into a JSON file for future use.
  
Sorting and Output:
- The tool sorts the items by their markup percentage, displaying the most profitable items first.  

## Installation and Usage
### Prerequisites
Python 3.x
requests library (install via pip install requests)  

### Installation
1. Clone the repository:
```bash
git clone https://github.com/Spaceboy86/FFXIV_Profit_Craft.git
cd FFXIV_Profit_Craft
```
2. Install the required dependencies:
```bash
pip install requests
```
### Usage
Currently the option to use stored data or request to fetch new data is hardcoded  
```python
use_cached_data = True
```

Run the script:
```bash
python main.py
```
The tool will fetch the required data, process it, and display the top crafting opportunities based on profit margins.

### Example Output
```plaintext
Item Name: Roast Rroneek - ID: 44092 - Price: 4269
Total Ingredient Price: 6644 - Difference Markup %: -35.74%
Ingredients:
  - Turali Corn Oil (ID: 43976) - Price: 956 - Amount: 1
  - Rroneek Chuck (ID: 44106) - Price: 1299 - Amount: 1
  - Yyasulani Garlic (ID: 43985) - Price: 485 - Amount: 2
  - White Pepper (ID: 43986) - Price: 550 - Amount: 2
  - Night Vinegar (ID: 27843) - Price: 799 - Amount: 1
  - Fire Crystal (ID: 8) - Price: 110 - Amount: 8
  - Water Crystal (ID: 13) - Price: 80 - Amount: 8
```
## Configuration
### Worlds and Data Centers
The script is currently configured to fetch data for the materia data centre:  
{'Ravana': 21, 'Bismarck': 22, 'Sephirot': 86, 'Sophia': 87, 'Zurvan': 88}  
This can be edited for other worlds, but there will be support for selecting different data centres and world selection. 

### Contributing
Feel free to submit pull requests or report issues on GitHub. Contributions are welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Thanks to XIVAPI and Universalis for providing the APIs that power this tool.  
Special thanks to the developers of FFXIV TeamCraft for their recipes-ingredient-lookup.json data.  

## Third-Party Resources

This project includes the `recipes-ingredient-lookup.json` file, sourced from the [FFXIV Teamcraft project](https://github.com/ffxiv-teamcraft/ffxiv-teamcraft). This file is used for crafting recipe data and is not modified by this project.

You can find the original file [here](https://github.com/ffxiv-teamcraft/ffxiv-teamcraft/blob/staging/libs/data/src/lib/json/recipes-ingredient-lookup.json).


## To-Do
- [ ] Add support for more data centers.  
      - Select Data centre, Select world from returned data centre. 
- [ ] Add support for multiple Job selection for item search.  
      - Depenent on selected Job, can "," separate Jobs from return list. "cul, alc, arm"  
      - results will specify crafting method 
