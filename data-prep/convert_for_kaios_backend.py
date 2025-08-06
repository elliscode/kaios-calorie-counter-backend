import re
import json
import json_stream
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

results = []
with open("../data/surveyDownload.json", 'r') as file:
    data = json_stream.load(file)
    for item_stream in data["SurveyFoods"]:
        item = to_standard_types(item_stream)
        servings = []
        for portion in item['foodPortions']:
            portion_name = portion['portionDescription']
            if portion_name in stupid_servings:
                continue
            portion_name = re.sub(r"^1\s+", "", portion_name)
            portion_grams = portion['gramWeight']
            ratio = portion_grams / 100.0
            print(item['description'] + ": " + str(portion_grams) + "g (" + portion_name + ")")
            serving = { 'name': portion_name }
            for nutrient in item['foodNutrients']:
                if nutrient['nutrient']['name'] in macros.keys():
                    serving[macros[nutrient['nutrient']['name']]] = nutrient['amount'] * ratio
            servings.append(serving)
        results.append({'name': item['description'], 'servings': servings})
        if len(results) > 10:
            break
print(json.dumps(results))