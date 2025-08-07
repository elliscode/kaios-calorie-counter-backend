import re
from titlecase import titlecase

leading_numbers_regex = re.compile(r"^(\d+\.?\d*)\s+([^(]+)")
print(leading_numbers_regex.match("1 tablespoon"))
result = leading_numbers_regex.match("1.25 slice (4-3/8\" dia x 1/10\" thick) (1 oz)")
print(result.group(1), result.group(2).strip())
print("WELCH'S, CONCORD GRAPE SPREAD, GRAPE".title())
print(titlecase("WELCH'S, CONCORD GRAPE SPREAD, GRAPE"))
print(titlecase("DIGIORNO DIGIORNO Croissant Crust Pepperoni 6.5in 10x9oz Carton"))

print('testy' in 'testicle')

print(titlecase('GENERAL MILLS SALES INC. Food Should Taste Good Guacamole Tortilla Chips'))
print(re.sub(re.compile(r"a{2}", re.IGNORECASE), "AA", "Grade Aa Eggs"))
