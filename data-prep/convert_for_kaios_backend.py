import re
import json

import json_stream
from json_stream_to_standard_types import to_standard_types

# fat, carbs, protein, caffeine, alcohol
stupid_foods = [
    "NOT A DESCRIPTIVE ITEM".lower(),
    "OREO MINI BISCUITS VANILLA 150 GR".lower(),
]
stupid_upcs = [
    '713733769433',
]
stupid_servings = [
    re.compile('Guideline amount per fl oz of beverage', re.IGNORECASE),
    re.compile('Quantity not specified', re.IGNORECASE),
    re.compile('Guideline amount per cup of hot cereal', re.IGNORECASE),
    re.compile('N/A', re.IGNORECASE),
    re.compile('GRM', re.IGNORECASE),
]
servings_fix_these_phrases = [
    {'find': re.compile(r'^(\d+)(g|gr|oz|onz|ml)$', re.IGNORECASE), 'replace': r'\1 \2'},
    {'find': re.compile(r'oz serving.*', re.IGNORECASE), 'replace': 'oz'},
    {'find': re.compile(r'\s+', re.IGNORECASE), 'replace': ' '},
    {'find': re.compile(r'\bz\b$', re.IGNORECASE), 'replace': 'oz'},
    {'find': re.compile(r'1 % COOKIES', re.IGNORECASE), 'replace': '1 cookie'},
    {'find': re.compile(r'2 ~3TSP', re.IGNORECASE), 'replace': '3 tsp'},
    {'find': re.compile(r'2\.1 /2"" SLICES', re.IGNORECASE), 'replace': '2 half-inch slices'},
    {'find': re.compile(r'4/0.48 Bites', re.IGNORECASE), 'replace': '4 bites'},

    {'find': re.compile(r'\d+\s*[\'\"]*\s*x\s*\d+\s*[\'\"]*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'[(\[][^)]+[)\]]', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'(\d+)th\b', re.IGNORECASE), 'replace': r'\1'},
    {'find': re.compile(r'about\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'~\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'Null\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'About\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'Approx\.*\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'Seasons 2 tacos', re.IGNORECASE), 'replace': '2 tsp. mix'},
    {'find': re.compile(r'onz', re.IGNORECASE), 'replace': 'oz'},
    {'find': re.compile(r'oza', re.IGNORECASE), 'replace': 'fl oz'},
    {'find': re.compile(r'\[([^]]+)]', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\bdia[.]*\b', re.IGNORECASE), 'replace': 'diameter'},
    {'find': re.compile(r'"+', re.IGNORECASE), 'replace': '"'},
    {'find': re.compile(r'^1 \[$', re.IGNORECASE), 'replace': '1 packet'},
    {'find': re.compile(r'\u00BC', re.IGNORECASE), 'replace': '1/4'},
    {'find': re.compile(r'[^\u0020-\u007E]', re.IGNORECASE), 'replace': ''},

]
stupid_brands = [
    "Not A Branded Item".lower(),
    "N/A".lower(),
]
needs_more_info_brands = [
    'Farmland'.lower()
]
brand_fixes = {
    "Psst...": "P$$t...",
    "Psst": "P$$t...",
    "Kellogg Company Us": "Kellogg Company",
}
serving_fixes = {
    "Piecesq": "pieces",
    "Stick | Null": "stick",
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

leading_range_regex = re.compile(r"^(\d+)\s*-\s*(\d+)\b\s*([^(]*)")
leading_irregular_fraction_regex = re.compile(r"^(\d+)[\s\-]+(\d+[\\/]\d+)\s+([^(]*)")
leading_fraction_regex = re.compile(r"^(\d+\s*[\\/]\s*\d+)\s*([^(]*)")
leading_numbers_regex = re.compile(r"^(\d*[,.]?\d+)\b\s*([^(]*)")
apostrophe_s = re.compile(r"'S")
whitespace = re.compile(r"\s+")
acai_berry = re.compile(r"AA BERRY", re.IGNORECASE)
two_as = re.compile(r"\ba{2}\b", re.IGNORECASE)

def my_titlecase(input_string):
    output = input_string
    output = re.sub(apostrophe_s, "'s", output.title())
    output = re.sub(whitespace, " ", output)
    output = re.sub(acai_berry, "Acai Berry", output)
    output = re.sub(two_as, "AA", output)
    return output

def parse_portion(q, p):
    q, p = inner_parse_portion(q, p)
    p = p.strip("- ()|'\",.+/~}{][;")
    if not p:
        p = 'count'
    return q, p

def inner_parse_portion(q, p):
    for bad_thing in servings_fix_these_phrases:
        p = bad_thing['find'].sub(bad_thing['replace'], p)
    output = leading_irregular_fraction_regex.match(p)
    if output:
        return float(output.group(1)) + eval(output.group(2).replace('\\', '/')), output.group(3).strip()
    output = leading_range_regex.match(p)
    if output:
        return (float(output.group(1)) + float(output.group(2))) / 2.0, output.group(3).strip()
    output = leading_fraction_regex.match(p)
    if output:
        return eval(output.group(1).replace('\\', '/')), output.group(2).strip()
    output = leading_numbers_regex.match(p)
    if output:
        return float(output.group(1).replace(',', '.')), output.group(2).strip()
    return q, p

def write_servings(input_servings: set):
    with open("servings.jsonl", "w") as servings_file:
        for unique_serving in sorted(input_servings):
            servings_file.write(unique_serving + '\n')

def is_portion_stupid(input_text):
    for stupid_serving in stupid_servings:
        if stupid_serving.findall(input_text):
            return True
    return False


unique_servings = set()
count = 0

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
                if is_portion_stupid(portion_name):
                    continue
                quantity = 1
                quantity, portion_name = parse_portion(quantity, portion_name)
                portion_grams = portion['gramWeight']
                ratio = portion_grams / 100.0
                serving = { 'name': portion_name, 'quantity': quantity }
                for key in serving_100g.keys():
                    if key in serving:
                        continue
                    serving[key] = round(serving_100g[key] * ratio, 2)
                servings.append(serving)
            servings.append(serving_100g)

            for serving in servings:
                unique_servings.add(serving['name'])

            json_line = json.dumps({'name': my_titlecase(item['description']), 'servings': servings})
            output_file.write(json_line + "\n")
            count = count + 1
            if count > 10000:
                count = 0
                write_servings(unique_servings)
    with open("../data/FoodData_Central_branded_food_json_2025-04-24.json", 'r') as file:
        raw_data = json_stream.load(file)
        for item_stream in raw_data["BrandedFoods"]:
            item = to_standard_types(item_stream)
            upc = item['gtinUpc']
            if upc in stupid_upcs:
                continue
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
                quantity, portion_name = parse_portion(quantity, portion_name)
                if not is_portion_stupid(portion_name):
                    serving = { 'name': portion_name, 'quantity': quantity, **household_serving }
                    servings.append(serving)

            if 'servingSizeUnit' in item:
                portion_name = item['servingSizeUnit']
                if not is_portion_stupid(portion_name):
                    quantity = item['servingSize']
                    quantity, portion_name = parse_portion(quantity, portion_name)

                    serving = { 'name': portion_name, 'quantity': quantity, **household_serving }
                    servings.append(serving)

            any_grams = False
            for serving in servings:
                if serving['name'].lower() == 'g':
                    any_grams = True
            if not any_grams:
                servings.append(serving_100g)

            for serving in servings:
                unique_servings.add(serving['name'])

            name = item['description']
            if 'subbrandName' in item and item['subbrandName'] and item['subbrandName'].lower() not in stupid_brands:
                if item['subbrandName'].lower() not in name.lower():
                    name = item['subbrandName'] + " " + name
                if item['brandName'].lower() not in name.lower() and item['brandName'].lower() not in stupid_brands:
                    name = item['brandName'] + " " + name
            elif 'brandName' in item and item['brandName'].lower() in needs_more_info_brands:
                name = item['brandOwner'] + " " + item['brandName'] + " " + name
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
            json_line = json.dumps({'name': name, 'servings': servings, 'upc': upc})
            output_file.write(json_line + "\n")
            count = count + 1
            if count > 10000:
                write_servings(unique_servings)
                count = 0

write_servings(unique_servings)
