from parser_notam_package import NOTAMParser
from parser_notam_package.json_schema_notam import NOTAMSchema

schema = NOTAMSchema()
parser = NOTAMParser()
sample1 = """
B0899/25 NOTAMN
Q) VVTS/QRTCA/IV/BO/W/000/100/1045N10640E025
A) VVTS B) 2506102300 C) 2506110400
E) TEMPO RESTRICTED AREA ACT DUE TO MILITARY EXERCISE.
F) SFC G) FL100
"""

notam_json = parser.to_json(sample1)
print(notam_json)
notam_print = parser.print_result(sample1)
print(notam_print)

if schema.validate_detail(parser.parse_notam(sample1)):
    print("Valid")
else:
    print("Invalid")

address = parser.geopy_address(sample1)
print(address)

created = parser.parse_created(sample1)
print(created)

valid_from , valid_till = parser.parse_dates(sample1)
print(valid_from)
print(valid_till)