import json

from my_parser.notam_parser import NOTAMParser


def main():
    notam = NOTAMParser()
    sample = """
    P1344/25 NOTAMN
Q) LFEE/QOBCE/IV/M /A /000/999/4709N00458E005
A) LFGZ B) 2504210600 C) 2505301600
E) MOBILE CRANE NEAR AD NUITS ST GEORGES RDL/D : 283/0.5NM ARP LFGZ
NUITS SAINT GEORGES PSN : 470839N 0045723E HGT : 78FT ELEV: 889FT
LGT : DAY
CREATED: 17 Apr 2025 14:50:00
SOURCE: EUECYIYN
    """
    print(sample)
    result = notam.parse_notam(sample)
    print('======Output======')
    print(notam.format_output(result))
    print('=====JSON=====')
    print(json.dumps(result,indent=4, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()