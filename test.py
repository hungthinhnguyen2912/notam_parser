from parser_notam_package.parser_notam_package import NOTAMParser

cc = NOTAMParser()

sample1 = """
B1974/25 NOTAMN 
Q) LFBB/QACAH/IV/BO /AE/000/020/4449N00031E009 
A) LFBE B) 2505260000 C) 2506012300 
E) CTR 'BERGERAC' SKED : - MON-FRI : 0600-1800  - SAT : 0700-1010   1130-1700 - SUN : 0645-1000   1120-1645 POSSIBLE 1HR EXTENSION FOR SKED COMMERCIAL FLIGHTS. OUTSIDE THESE SKED, CTR DOWNGRADED TO G AND AD CTL NOT PROVIDED. 
CREATED: 11 May 2025 07:46:00  SOURCE: EUECYIYN
"""

result = cc.parse_notam(sample1)
print(cc.print_result(result))
###
print("===========================")
# state
state = cc.parse_state(sample1)
print(state)
# id
id = cc.parse_notam_id(sample1)
print(id)
# Notam type
type = cc.parse_notam_type(sample1)
print(type)
# FIR
fir = cc.parse_fir(sample1)
print(fir)
#Notam code (Q code)
q_code = cc.parse_notam_code(sample1)
print(q_code)
# Entity
entity = cc.parse_entity(sample1)
print(entity)
# Category area
c_area = cc.parse_category_area(sample1)
print(c_area)
# sub category area
sub_area = cc.parse_sub_category_area(sample1)
print(sub_area)
# subject
subject = cc.parse_subject(sample1)
print(subject)
# status
status = cc.parse_status(sample1)
print(status)
# condition
condition = cc.parse_condition(sample1)
print(condition)
# modifier
modifier = cc.parse_modifier(sample1)
print(modifier)
# area affected
aa = cc.parse_area_affected(sample1)
print(aa)
# location
location = cc.parse_location(sample1)
print(location)
#ValidTill and Valid from (B,C line)
valid_till,valid_from = cc.parse_dates(sample1)
print(valid_till)
print(valid_from)
# Schedule (D line)
schedule = cc.parse_schedule(sample1)
print(schedule)
# Body (E line)
body = cc.parse_body(sample1)
print(body)
# Lower limit, Upper limit (F line, G line)
low_limit,up_limit = cc.parse_limits(sample1)
print(low_limit)
print(up_limit)









