from parser_notam_package import NOTAMParser
from parser_notam_package.json_schema_notam import NOTAMSchema

schema = NOTAMSchema()
parser = NOTAMParser()
sample1 = """
P1429/25 NOTAMN 
Q) LFFF/QOBCE/IV/M  /A /000/999/4947N00439E005 
A) LFQV B) 2504301600 C) 2604271600 
E) CRANE OPR CLOSE TO 'CHARLEVILLE MEZIERES (HMEZ)' HLP  RDL : 82/3.07NM ARP LFQV PSN : 494731.319''N / 0044315.941''E HEIGHT : 136FT  ELEV :857FT LIGHTING : NIGHT 
CREATED: 25 Apr 2025 14:49:00  SOURCE: EUECYIYN
"""
sample_error = """
P1429/25 NOTAMN 
Q) LFFF/QOBCE/IV/M  /A /000/999/4947N00439E005 
A) LFQV B) 2504301600 C) 2604271600 
E) CRANE OPR CLOSE TO 'CHARLEVILLE MEZIERES (HMEZ)' HLP  
RDL : 82/3.07NM ARP LFQV PSN : 494731.319''N / 0044315.941''E 
HEIGHT : 136FT  ELEV :857FT LIGHTING : NIGHT 
Schedule: 25 0800-1600 
CREATED: 25 Apr 2025 14:49:00  SOURCE: EUECYIYN
"""

# notam_json = parser.to_json(sample1)
# print(notam_json)


notam_json_error = {
    'state': 'France',
    'id': None,
    'notam_type': 'NEW',
    'fir': 'LFFF',
    'notam_code': 'QOBCE',
    'entity': 'OB',
    'status': 'CE',
    'category_area': 'Other Information',
    'sub_area': 'Other Information',
    'subject': 'Obstacle',
    'condition': 'Changes',
    'modifier': 'Erected',
    'area_affected': {'lat': '4947N', 'long': '00439E', 'radius': "5"},
    'location': 'LFQV',
    'valid_from': 202504301600,
    'valid_till': None,
    'schedule': 'None',
    'body': 'test body',
    'lower_limit': 'None',
    'upper_limit': 'None'
}

if schema.validate_detail(notam_json_error):
    print("NOTAM valid schema.")
else:
    print("NOTAM invalid")

notam_missing_value_json = {
    'state': 'France',
    'notam_type': 'NEW',
    'fir': 'LFFF',
    'notam_code': 'QOBCE',
    'entity': 'OB',
    'status': 'CE',
    'category_area': 'Other Information',
    'sub_area': 'Other Information',
    'subject': 'Obstacle',
    'condition': 'Changes',
    'modifier': 'Erected',
    'area_affected': {'lat': '4947N', 'long': '00439E', 'radius': "5"},
    'location': 'LFQV',
    'valid_from': 202504301600,
    'valid_till': "None",
    'schedule': 'None',
    'body': 'test body',
    'lower_limit': 'None',
    'upper_limit': 'None'
}

n = schema.missing_value_notam(notam_missing_value_json)
print(n)

if schema.validate_detail(n):
    print("NOTAM valid schema.")
else:
    print("NOTAM invalid")