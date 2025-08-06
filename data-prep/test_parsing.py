import re
from titlecase import titlecase

leading_numbers_regex = re.compile(r"^(\d+\.?\d*)\s+([^(]+)")
print(leading_numbers_regex.match("1 tablespoon"))
result = leading_numbers_regex.match("1.25 slice (4-3/8\" dia x 1/10\" thick) (1 oz)")
print(result.group(1), result.group(2).strip())
print("WELCH'S, CONCORD GRAPE SPREAD, GRAPE".title())
print(titlecase("WELCH'S, CONCORD GRAPE SPREAD, GRAPE"))