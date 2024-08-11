# FFXIV Profit Craft
What started as a small idea turned into a rabbit holes, as they often do.  

Currently it will:  
- Use the XIVAPI to search for the correct sheet for all item recipes that meet the criteria
- Check the receipeID's against TeamCraft's recipes_ingredient_lookup json to retrieve the ingredients itemID, amount required, amount produced
- Check if the ingredient has recipes, if they do, return it's receipe information 
- Check for the item, ingredients, subingredients prices with the universalis
- Store all the data into a json 
- Compare the item's prices vs the ingredients price as well as if it has subingredients and if crafting via subingredients is cheaper
- Sort the items based on price markup
- return X results with markup
