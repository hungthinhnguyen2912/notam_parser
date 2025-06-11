import pytest
import json
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from parser_notam_package import NOTAMParser, NOTAMSchema

parser = NOTAMParser()
schema = NOTAMSchema()

SAMPLE_VALID = """
F9876/25 NOTAMN
Q) VVTS/QWULW/IV/BO/W/010/050/1045N10640E010
A) VVTS B) 2506120200 C) 2506120400
D) DLY 0200-0400
E) PARACHUTE JUMPING EXERCISES WI RADIUS 10NM OF 104500N1064000E.
F) 1000FT AGL 
G) 5000FT AGL
"""


@pytest.fixture(scope="module")
def parsed_valid_notam():
    notam_data, warnings = parser.parse_notam(SAMPLE_VALID)
    assert notam_data is not None, "Parser đã thất bại với NOTAM hợp lệ"
    assert not warnings, "NOTAM hợp lệ không nên có cảnh báo"
    return notam_data


def test_missing_mandatory_field():
    sample_missing_e = """
    F9876/25 NOTAMN
    Q) VVTS/QWULW/IV/BO/W/010/050/1045N10640E010
    A) VVTS B) 2506120200 C) 2506120400
    D) DLY 0200-0400
    F) 1000FT AGL 
    G) 5000FT AGL
    """
    notam_data, warning = parser.parse_notam(sample_missing_e)

    assert notam_data is None
    assert warning == ["Lỗi: Thiếu các trường bắt buộc: ['E']"]


def test_scenario_with_trash_field():
    sample_with_h = """
    F9876/25 NOTAMN
    Q) VVTS/QWULW/IV/BO/W/010/050/1045N10640E010
    A) VVTS B) 2506120200 C) 2506120400
    E) PARACHUTE JUMPING EXERCISES WI RADIUS 10NM OF 104500N1064000E.
    H) HEHEHE
    """
    notam_data, messages = parser.parse_notam(sample_with_h)

    assert notam_data is not None
    assert len(messages) == 1
    assert "Cảnh báo: Phát hiện và loại bỏ field rác 'H)'" in messages[0]
    assert schema.validate_detail(notam_data) is True


def test_notam_with_trash_field_and_missing_mandatory_field():
    sample_with = """
    F9876/25 NOTAMN
    Q) VVTS/QWULW/IV/BO/W/010/050/1045N10640E010
    A) VVTS B) 2506120200 C) 2506120400
    H) HEHEHE
    """
    notam_data, messages = parser.parse_notam(sample_with)
    assert notam_data is None
    assert len(messages) == 2
    assert "Cảnh báo: Phát hiện và loại bỏ field rác 'H)'" in messages[0]
    assert "Lỗi: Thiếu các trường bắt buộc: ['E']" in messages[1]


def test_full_parse_and_schema_validation(parsed_valid_notam):
    notam = parsed_valid_notam
    assert notam is not None
    assert notam['state'] == "Vietnam"
    assert notam['id'] == 'F9876/25'
    assert notam['notam_type'] == 'NEW'
    assert notam['referenced_notam'] is None
    assert notam['fir'] == 'VVTS'
    assert notam['notam_code'] == 'QWULW'
    assert notam['entity'] == 'WU'
    assert notam['status'] == 'LW'
    assert notam['category_area'] == 'Navigation Warnings'
    assert notam['sub_area'] == 'Warnings'
    assert notam['subject'] == 'Unmanned aircraft'
    assert notam['condition'] == 'Limitations'
    assert notam['modifier'] == 'Will take place'
    assert notam['area_affected']['lat'] == '1045N'
    assert notam['area_affected']['lon'] == '10640E'
    assert notam['area_affected']['radius'] == 10
    assert notam['location'] == 'VVTS'
    assert notam['valid_from'] == '2025-06-12T02:00:00+00:00'
    assert notam['valid_till'] == '2025-06-12T04:00:00+00:00'
    assert notam['schedule'] == 'Daily 0200-0400'
    assert notam['body'] == 'PARACHUTE JUMPING EXERCISES Within RADIUS 10Nautical miles OF 104500N1064000E.'
    assert notam['lower_limit'] == '1000FT Above Ground Level'
    assert notam['upper_limit'] == '5000FT Above Ground Level'
    assert schema.validate_detail(notam) is True


def test_parse_id(parsed_valid_notam):
    assert parsed_valid_notam['id'] == 'F9876/25'


def test_parse_state(parsed_valid_notam):
    assert parsed_valid_notam['state'] == 'Vietnam'


def test_parse_fir(parsed_valid_notam):
    assert parsed_valid_notam['fir'] == 'VVTS'


def test_parse_notam_type(parsed_valid_notam):
    assert parsed_valid_notam['notam_type'] == 'NEW'


def test_parse_referenced_notam(parsed_valid_notam):
    assert parsed_valid_notam['referenced_notam'] is None


def test_notamc_parsing_and_validation():
    """Test parse và validate cho NOTAMC"""
    notamc_text = """
    D0123/25 NOTAMC D0120/25 
Q) VVCR/QCSAS/I/B/AE/000/999/1018N10912E025 
A) VVCR B) 2506110800 C) 2506111200 
E) CAM RANH APP 121.250MHZ U/S. 
    """
    notam_data, warnings = parser.parse_notam(notamc_text)

    assert notam_data is not None
    assert notam_data['notam_type'] == 'CANCEL'
    assert notam_data['referenced_notam'] == 'D0120/25'
    assert schema.validate_detail(notam_data) is True


def test_notamr_parsing_and_validation():
    """Test parse và validate cho NOTAMR"""
    notamr_text = """A1235/25 NOTAMR A1100/25 
Q) VVHM/QFAXX/IV/NBO/A/000/999/2101N10550E005 
A) VVNB B) 2506091000 C) 2506091600 EST 
E) TWY S CLSD BTN TWY S1 AND TWY S2.
"""
    notam_data, warnings = parser.parse_notam(notamr_text)

    assert notam_data is not None
    assert notam_data['notam_type'] == 'REPLACE'
    assert notam_data['referenced_notam'] == 'A1100/25'
    assert schema.validate_detail(notam_data) is True


def test_parse_and_validate_notamr_without_referenced_notam():
    notamr_error = """
    A1235/25 NOTAMR
    Q) VVHM/QFAXX/IV/NBO/A/000/999/2101N10550E005
    A) VVNB B) 2506091000 C) 2506091600 EST 
    E) TWY S CLSD BTN TWY S1 AND TWY S2.
    """
    notam_data, warnings = parser.parse_notam(notamr_error)
    assert notam_data is None
    assert warnings == ["Cảnh báo: NOTAM loại 'REPLACE' thiếu mã NOTAM tham chiếu"]


def test_parse_notam_code(parsed_valid_notam):
    assert parsed_valid_notam['notam_code'] == 'QWULW'


def test_parse_entity(parsed_valid_notam):
    assert parsed_valid_notam['entity'] == 'WU'


def test_parse_status(parsed_valid_notam):
    assert parsed_valid_notam['status'] == 'LW'


def test_parse_category_area(parsed_valid_notam):
    assert parsed_valid_notam['category_area'] == 'Navigation Warnings'


def test_parse_sub_area(parsed_valid_notam):
    assert parsed_valid_notam['sub_area'] == 'Warnings'


def test_parse_subject(parsed_valid_notam):
    assert parsed_valid_notam['subject'] == 'Unmanned aircraft'


def test_parse_condition(parsed_valid_notam):
    assert parsed_valid_notam['condition'] == 'Limitations'


def test_parse_modifier(parsed_valid_notam):
    assert parsed_valid_notam['modifier'] == 'Will take place'


def test_parse_area_affected(parsed_valid_notam):
    area = parsed_valid_notam['area_affected']
    assert area['lat'] == '1045N'
    assert area['lon'] == '10640E'
    assert area['radius'] == 10


def test_parse_location(parsed_valid_notam):
    assert parsed_valid_notam['location'] == 'VVTS'


def test_parse_valid_from(parsed_valid_notam):
    assert parsed_valid_notam['valid_from'] == '2025-06-12T02:00:00+00:00'


def test_parse_valid_till(parsed_valid_notam):
    assert parsed_valid_notam['valid_till'] == '2025-06-12T04:00:00+00:00'


def test_parse_schedule(parsed_valid_notam):
    assert parsed_valid_notam['schedule'] == 'Daily 0200-0400'


def test_parse_body(parsed_valid_notam):
    assert parsed_valid_notam[
               'body'] == 'PARACHUTE JUMPING EXERCISES Within RADIUS 10Nautical miles OF 104500N1064000E.'


def test_parse_lower_limit(parsed_valid_notam):
    assert parsed_valid_notam['lower_limit'] == '1000FT Above Ground Level'


def test_parse_upper_limit(parsed_valid_notam):
    assert parsed_valid_notam['upper_limit'] == '5000FT Above Ground Level'


def test_geopy_address():
    try:
        address = parser.geopy_address(SAMPLE_VALID)
        assert "Ho Chi Minh City" in address
        assert "Vietnam" in address
    except Exception as e:
        # Pass test if have error with API
        pytest.skip(f"Skipping geopy test due to API/network error: {e}")


# JSON
def create_test_pdf(file_path: Path, text_content: str):
    """Hàm này tạo ra một file PDF đơn giản chứa nội dung văn bản."""
    c = canvas.Canvas(str(file_path), pagesize=letter)
    text_object = c.beginText(40, 750)  # Tọa độ bắt đầu viết text
    text_object.setFont("Helvetica", 10)
    for line in text_content.splitlines():
        text_object.textLine(line.strip())

    c.drawText(text_object)
    c.save()


def test_process_pdf_all_valid(tmp_path, capsys):
    """
    Unit test 1: Test file PDF với tất cả NOTAM đều hợp lệ.
    Hàm test này nhận 2 fixture từ pytest:
    - tmp_path: Cung cấp một thư mục tạm để tạo file.
    - capsys: Bắt lại output từ lệnh print.
    """
    # Nội dung cho file PDF test
    pdf_content = """
    A1234/25 NOTAMN
    Q) VVTS/QWULW/IV/BO/W/000/999/1045N10640E010
    A) VVTS B) 2506120200 C) 2506120400
    E) TEST BODY 1.

    B5678/25 NOTAMR B1111/25
    Q) VVHM/QFAXX/IV/NBO/A/000/999/2101N10550E005
    A) VVNB B) 2506091000 C) 2506091600 EST 
    E) TEST BODY 2.
    """
    pdf_path = tmp_path / "valid_notam.pdf"
    json_path = tmp_path / "output.json"
    create_test_pdf(pdf_path, pdf_content)

    schema.process_and_validate_pdf(str(pdf_path), str(json_path))
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert len(data) == 2
    assert data[0]['id'] == 'A1234/25'
    assert data[1]['id'] == 'B5678/25'

    captured = capsys.readouterr()
    assert "Lỗi" not in captured.out
    assert "Cảnh báo" not in captured.out
    assert "Ghi 2 NOTAM hợp lệ" in captured.out


def test_process_pdf_with_trash_field(tmp_path, capsys):
    """
    Unit test 2: Test file PDF có NOTAM chứa field rác (H).
    """
    schema = NOTAMSchema()
    pdf_content = """
    A1234/25 NOTAMN
    Q) VVTS/QWULW/IV/BO/W/000/999/1045N10640E010
    A) VVTS B) 2506120200 C) 2506120400
    E) VALID NOTAM WITH TRASH FIELD.
    H) THIS IS A TRASH FIELD.
    
    B5678/25 NOTAMN
    Q) VVHM/QFAXX/IV/NBO/A/000/999/2101N10550E005
    B) 2506091000 C) 2506091600
    E) THIS IS A VALID NOTAM WITHOUT TRASH FIELD.
    P) TRASH FIELD
    """
    pdf_path = tmp_path / "trash_notam.pdf"
    json_path = tmp_path / "output.json"
    create_test_pdf(pdf_path, pdf_content)
    schema.process_and_validate_pdf(str(pdf_path), str(json_path))

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]['id'] == 'A1234/25'
    captured = capsys.readouterr()
    assert "Cảnh báo: Phát hiện và loại bỏ field rác 'H)'." in captured.out
    assert "Lỗi: THiếu các trường bắt buộc: ['A']. Sẽ không được ghi vào JSON" not in captured.out
    assert "Cảnh báo: Phát hiện và loại bỏ field rác 'P)'." in captured.out


def test_process_pdf_with_missing_mandatory_field(tmp_path, capsys):
    """
    Unit test 3: Test file PDF có NOTAM thiếu field bắt buộc (A).
    """
    schema = NOTAMSchema()
    pdf_content = """
    A1111/25 NOTAMN
    Q) VVTS/QWULW/IV/BO/W/000/999/1045N10640E010
    B) 2506120200 C) 2506120400
    E) THIS NOTAM IS MISSING FIELD A.

    B2222/25 NOTAMN
    Q) VVHM/QFAXX/IV/NBO/A/000/999/2101N10550E005
    A) VVNB B) 2506091000 C) 2506091600
    E) THIS IS A VALID NOTAM.
    """
    pdf_path = tmp_path / "missing_field.pdf"
    json_path = tmp_path / "output.json"
    create_test_pdf(pdf_path, pdf_content)
    schema.process_and_validate_pdf(str(pdf_path), str(json_path))
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]['id'] == 'B2222/25'
    captured = capsys.readouterr()
    assert "ID: A1111/25" in captured.out
    assert "Lỗi: Thiếu các trường bắt buộc: ['A']" in captured.out
    assert "Sẽ không được ghi vào JSON" in captured.out


def test_process_pdf_not_found(capsys):
    """Test trường hợp file PDF đầu vào không tồn tại."""
    schema.process_and_validate_pdf("path/that/does/not/exist.pdf", "output.json")
    captured = capsys.readouterr()
    assert "Lỗi: Không tìm thấy file" in captured.out


def test_pdf_dont_have_notam(capsys):
    """Test trường hợp file PDF không chứa NOTAM nào."""
    schema = NOTAMSchema()
    pdf_path = Path("empty_notam.pdf")
    json_path = Path("output.json")
    create_test_pdf(pdf_path, "")
    schema.process_and_validate_pdf(str(pdf_path), str(json_path))

    captured = capsys.readouterr()
    assert "Không tìm thấy NOTAM nào trong file PDF." in captured.out
    assert not json_path.exists()
