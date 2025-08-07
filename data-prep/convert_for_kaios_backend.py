import re
import json
import json_stream
from titlecase import titlecase
from json_stream_to_standard_types import to_standard_types

# fat, carbs, protein, caffeine, alcohol
stupid_foods = [
    "NOT A DESCRIPTIVE ITEM".lower(),
]
stupid_servings = [
    'Guideline amount per fl oz of beverage'.lower(),
    'Quantity not specified'.lower(),
    'Guideline amount per cup of hot cereal'.lower(),
    'N/A'.lower(),
    'GRM'.lower(),
]
stupid_brands = [
    "Not A Branded Item".lower(),
    "N/A".lower(),
]
brand_fixes = {
    "Psst...": "P$$t...",
    "Psst": "P$$t...",
    "Kellogg Company Us": "Kellogg Company",
}
macros = {
    'Total lipid (fat)': 'fat',
    'Carbohydrate, by difference': 'carbohydrates',
    'Protein': 'protein',
    'Energy': 'calories',
    'Alcohol, ethyl': 'alcohol',
    'Fatty acids, total saturated': 'saturatedFat',
    'not-present-1': 'transFat',
    'Cholesterol': 'cholesterol',
    'Sodium, Na': 'sodium',
    'Fiber, total dietary': 'fiber',
    'Total Sugars': 'sugars',
    'Vitamin D (D2 + D3)': 'vitaminD',
    'Calcium, Ca': 'calcium',
    'Iron, Fe': 'iron',
    'Potassium, K': 'potassium',
    'not-present-2': 'addedSugar',
}

leading_numbers_regex = re.compile(r"^(\d+\.?\d*)\s+([^(]+)")
apostrophe_s = re.compile(r"'S")
whitespace = re.compile(r"\s+")
acai_berry = re.compile(r"AA BERRY", re.IGNORECASE)
two_as = re.compile(r"\ba{2}\b", re.IGNORECASE)

def my_titlecase(input_string):
    # AA BERRY
    output = input_string
    output = re.sub(apostrophe_s, "'s", output.title())
    output = re.sub(whitespace, " ", output)
    output = re.sub(acai_berry, "Acai Berry", output)
    output = re.sub(two_as, "AA", output)
    return output

with open("output_my_titlecase.jsonl", "w") as output_file:
    with open("../data/surveyDownload.json", 'r') as file:
        raw_data = json_stream.load(file)
        for item_stream in raw_data["SurveyFoods"]:
            item = to_standard_types(item_stream)
            serving_100g = {'name': 'g', 'quantity': 100.0}
            for nutrient in item['foodNutrients']:
                if nutrient['nutrient']['name'] in macros.keys():
                    serving_100g[macros[nutrient['nutrient']['name']]] = nutrient['amount']
            servings = []
            for portion in item['foodPortions']:
                portion_name = portion['portionDescription']
                if portion_name in stupid_servings:
                    continue
                quantity = 1
                result = leading_numbers_regex.match(portion_name)
                if result:
                    quantity = float(result.group(1))
                    portion_name = result.group(2).strip()
                portion_grams = portion['gramWeight']
                ratio = portion_grams / 100.0
                serving = { 'name': portion_name, 'quantity': quantity }
                for key in serving_100g.keys():
                    if key in serving:
                        continue
                    serving[key] = round(serving_100g[key] * ratio, 2)
                servings.append(serving)
            servings.append(serving_100g)
            json_line = json.dumps({'name': my_titlecase(item['description']), 'servings': servings})
            output_file.write(json_line + "\n")
    with open("../data/FoodData_Central_branded_food_json_2025-04-24.json", 'r') as file:
        raw_data = json_stream.load(file)
        for item_stream in raw_data["BrandedFoods"]:
            item = to_standard_types(item_stream)
            if item['description'].lower() in stupid_foods:
                continue
            skip = False
            for stupid_food in stupid_foods:
                if stupid_food in item['description'].lower():
                    skip = True
                    break
            if skip:
                continue
            serving_100g = {'name': 'g', 'quantity': 100.0}
            for nutrient in item['foodNutrients']:
                if nutrient['nutrient']['name'] in macros.keys():
                    serving_100g[macros[nutrient['nutrient']['name']]] = nutrient['amount']

            servings = []

            household_serving = {}
            for key in macros.values():
                if key in item['labelNutrients']:
                    household_serving[key] = item['labelNutrients'][key]['value']

            if 'householdServingFullText' in item:
                portion_name = my_titlecase(item['householdServingFullText'])
                quantity = 1
                result = leading_numbers_regex.match(portion_name)
                if result:
                    quantity = float(result.group(1))
                    portion_name = result.group(2).strip()

                if portion_name.lower() not in stupid_servings:
                    if portion_name.lower() == 'onz':
                        portion_name = 'oz'
                    elif portion_name.lower() == 'oza':
                        portion_name = 'fl oz'

                    serving = { 'name': portion_name, 'quantity': quantity, **household_serving }
                    servings.append(serving)

            if 'servingSizeUnit' in item:
                portion_name = item['servingSizeUnit']
                if portion_name.lower() not in stupid_servings:
                    quantity = item['servingSize']

                    serving = { 'name': portion_name, 'quantity': quantity, **household_serving }
                    servings.append(serving)

            any_grams = False
            for serving in servings:
                if serving['name'].lower() == 'g':
                    any_grams = True
            if not any_grams:
                servings.append(serving_100g)

            name = item['description']
            if 'subbrandName' in item and item['subbrandName'] and item['subbrandName'].lower() not in stupid_brands:
                if item['subbrandName'].lower() not in name.lower():
                    name = item['subbrandName'] + " " + name
                if item['brandName'].lower() not in name.lower() and item['brandName'].lower() not in stupid_brands:
                    name = item['brandName'] + " " + name
            elif 'brandName' in item and item['brandName'] and item['brandName'].lower() not in stupid_brands:
                if item['brandName'].lower() not in name.lower():
                    name = item['brandName'] + " " + name
            elif 'brandOwner' in item and item['brandOwner'] and item['brandOwner'].lower() not in stupid_brands:
                if item['brandOwner'].lower() not in name.lower():
                    name = item['brandOwner'] + " " + name
            name = my_titlecase(name)
            for key, value in brand_fixes.items():
                if key in name:
                    name = name.replace(key, value)
            json_line = json.dumps({'name': name, 'servings': servings})
            output_file.write(json_line + "\n")
