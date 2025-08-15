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
    '3173282219297',
    '8435070421486',
]
bad_servings_upcs = {
    '697658692796': '1 bar',
    '031142105209': '1 Tablespoons',
    '00016000363489': '1 roll',
    '00846675010339': '1 bar',
    '00019320001925': '2 packages',
    '00012546012249': '1 stick',
    '00044000009663': '2 cookies',
    '00012546012256': '1 stick',
    '751106000240': '1 piece',
    '829262004263': '1 oat bar',
    '076064051265': '1 cake',
    '748703280311': '1 sope',
    '859977002056': '30 g',
    '860002410807': '1 cookie',
    '722252238078': '1 brownie',
    '835871130057': '1 bag',
    '850029742067': '1 can',
    '842595106626': '1 can',
    '646670532207': '1 fillet',
    '026883221059': '30 g',
    '047792012361': '1/3 cup',
    '011141087478': '1 shell',
    '041331036139': '2 sardines',
    '012900043186': '1 shell',
    '038000123443': '1 waffle',
    '644216323593': '1 semita',
    '850000428058': '1 slice',
    '710069107236': '1 smore',
    '711381313329': '1/12 dry mix',
    '711381312247': '1/9 dry mix',
    '070896163745': '1/19 kit',
    '070896163790': '1/27 kit',
    '710069008205': '1 piece',
    '855024004042': '2 bars',
    '071429035065': '2 olives',
    '045255118476': '2 half-inch slices',
    '086700005163': '2 rolls',
    '10693392005189': '2 bowties',
    '7506244300744': '3 pops',
    '778367517515': '3 canes',
    '041466004782': '3 bon bons',
    '038000256035': '3 waffles',
    '038000017148': '3 waffles',
    '720379504359': '3 count',
    '00030800000658': '3 pops',
    '850808005253': '10 pieces',
    '030223033547': '1 sandwich',
    '012265074641': '1 cookie',
    '077890421727': '3/4 inch slice',
    '077890419977': '1.25 inch slice',
    '077890395905': '1.25 inch slice',
    '077890352434': '1.25 inch slice',
    '711381310090': '1 fl oz',
    '711381326992': '1 fl oz',
    '711381310076': '1 fl oz',
    '850681003018': '1 link',
    '077890371275': '3/4 inch slice',
    '079621002571': '1 pan fried slice',
    '018000486557': '3 fl oz',
    '807444790418': '4 oz, raw',
    '0041501008324': '2 taco shells',
    '0039000008051': '2 taco shells',
    '0710069806511': '2 Tablespoons',
    '0710069806528': '2 Tablespoons',
    '0710069806504': '2 Tablespoons',
    '866176000011': '2 slices',
    '7503022525016': '2 slices',
    '078935005124': '2 slices',
}
stupid_servings = [
    re.compile('Guideline amount per fl oz of beverage', re.IGNORECASE),
    re.compile('Quantity not specified', re.IGNORECASE),
    re.compile('Guideline amount per cup of hot cereal', re.IGNORECASE),
    re.compile('N/A', re.IGNORECASE),
    re.compile('None', re.IGNORECASE),
    re.compile(r'^\(.*', re.IGNORECASE),  # leading parenthesis are STUPID
    re.compile(r'^0+\D.*', re.IGNORECASE),  # zero values are STUPID
]
ignore_parsing_servings = [
    re.compile(r'with\s+\d', re.IGNORECASE),
]
servings_fix_these_phrases = [
    {'find': re.compile(r'\u00BC', re.IGNORECASE), 'replace': '1/4'},
    {'find': re.compile(r'[^\u0020-\u007E]', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'^\s+', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\s+$', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\s+', re.IGNORECASE), 'replace': ' '},
    {'find': re.compile(r'^About\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'^Abt\.\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'^Per\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'^~', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\s*\|.*$', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\\(\D)', re.IGNORECASE), 'replace': r'\1'},
    {'find': re.compile(r'^[+\-]\s*', re.IGNORECASE), 'replace': r''},
    {'find': re.compile(r'^App?r?o?xi?m?a?t?e?l?y?\.?\s*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\(.*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\bz\.?$', re.IGNORECASE), 'replace': 'oz'},
    {'find': re.compile(r'\bonz\.?$', re.IGNORECASE), 'replace': 'oz'},
    {'find': re.compile(r'\boza\.?$', re.IGNORECASE), 'replace': 'fl oz'},
    {'find': re.compile(r'/$', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'/.*\)$', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'(, |-)About.*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r', \d+ .*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'[,.] per cont?a?i?n?e?r?\.?.*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\s*"+\s*', re.IGNORECASE), 'replace': '" '},
    {'find': re.compile(r'\[Image of an? ([^]]+)]', re.IGNORECASE), 'replace': r'\1'},
    {'find': re.compile(r'children.*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'([0-9])\s*gr?a?m?s?\.?\s*$', re.IGNORECASE), 'replace': r'\1 g'},
    {'find': re.compile(r'^gr?a?m?s?\.?$', re.IGNORECASE), 'replace': 'g'},
    {'find': re.compile(r',?\s+\[?Makes?.*$', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'Makes.*', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\\\s*(\d)', re.IGNORECASE), 'replace': r'/\1'},
    {'find': re.compile(r',?\s+\[?Contains.*$', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'^[01]+$', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r',?(\s*)frozen.*', re.IGNORECASE), 'replace': r'\1Frozen'},
    {'find': re.compile(r"\s*'{2,}\s*", re.IGNORECASE), 'replace': r'" '},
    {'find': re.compile(r"\s+fl?u?i?d?\.?\s*ou?n?c?e?s?z?\.?", re.IGNORECASE), 'replace': r' fl oz'},
    {'find': re.compile(r"\s+oz\.?", re.IGNORECASE), 'replace': r' oz'},
    {'find': re.compile(r",?\s+NF?S\s+.*$", re.IGNORECASE), 'replace': r''},
    {'find': re.compile(r"\s+(pieces|pcs|pc's|pc)[,.)]*(\s*)", re.IGNORECASE), 'replace': r' pieces\2'},
    {'find': re.compile(r"\s+Container.?\.?(\s*)", re.IGNORECASE), 'replace': r' container '},
    {'find': re.compile(r"^(\d+)\s+,\s+(\D)", re.IGNORECASE), 'replace': r'\1 \2'},
#     {'find': re.compile(r"^1\s*[\-),%.\s:*]+", re.IGNORECASE), 'replace': '1 '},
    {'find': re.compile(r'^\s+', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\s+$', re.IGNORECASE), 'replace': ''},
    {'find': re.compile(r'\s+', re.IGNORECASE), 'replace': ' '},
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

# chat GPT sucks ass
# def parse_portion(quantity_v, portion_string):
#     # Helper: parse fractions like "1 3/4" or "3/4"
#     def parse_fraction(s):
#         s = s.strip()
#         if ' ' in s:
#             whole, frac = s.split(' ', 1)
#             return float(whole) + parse_fraction(frac)
#         if '/' in s:
#             num, den = s.split('/')
#             try:
#                 return float(num) / float(den)
#             except ValueError:
#                 return None
#         try:
#             return float(s)
#         except ValueError:
#             return None
#
#     if not portion_string or not portion_string.strip():
#         return None, "serving"
#
#     # Take only first portion before parentheses or commas
#     first_part = portion_string.split('(')[0].split(',')[0].strip()
#
#     # Extract quantity (fraction or decimal)
#     match = re.match(r'^\s*([\d\s\/\.]+)\s*(.*)$', first_part)
#     if not match:
#         return None, "serving"
#
#     qty_str, portion_v = match.groups()
#     quantity_v = parse_fraction(qty_str)
#
#     # Clean portion text
#     portion_v = portion_v.strip()
#     portion_v = re.sub(r'^[^\w]+|[^\w]+$', '', portion_v)  # remove leading/trailing symbols
#
#     if not portion_v or not re.search(r'[A-Za-z]', portion_v):
#         portion_v = "serving"
#
#     return quantity_v, portion_v

decimal_regex = re.compile(r'^(\d*\.\d+)(.*)$', re.IGNORECASE)

def parse_portion(q:float, p:str):
    for phrase in servings_fix_these_phrases:
        p = phrase['find'].sub(phrase['replace'], p)
    if not p:
        p = 'serving'
    for phrase in ignore_parsing_servings:
        if phrase.findall(p):
            return q, p
    return actually_parse(q, p)

def actually_parse(q:float, p:str):
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
            if upc in bad_servings_upcs.keys():
                item['householdServingFullText'] = bad_servings_upcs[upc]
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
