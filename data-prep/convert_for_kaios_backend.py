import re
import json
import json_stream
from titlecase import titlecase
from json_stream_to_standard_types import to_standard_types

# fat, carbs, protein, caffeine, alcohol
stupid_servings = [
    'Guideline amount per fl oz of beverage',
    'Quantity not specified',
    'Guideline amount per cup of hot cereal'
]
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
with open("output2.jsonl", "w") as output_file:
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
            json_line = json.dumps({'name': titlecase(item['description']), 'servings': servings})
            output_file.write(json_line + "\n")
