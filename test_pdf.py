from parser_notam_package.json_schema_notam import NOTAMSchema

schema = NOTAMSchema()


input_path = r"D:\AAA\parser_notam_package\notam_error.pdf"
output = 'valid_notam_error.json'

schema.process_and_validate_pdf(input_path,output)