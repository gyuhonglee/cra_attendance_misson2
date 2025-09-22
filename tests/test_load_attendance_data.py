import pytest
from attendance import Student, load_attendance_data, add_attendance_data

def test_load_attendace_data(mocker):
    mock_data = "Alice Mon\nBob Tue\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_data))

    mock_add = mocker.patch("attendance.add_attendance_data")

    load_attendance_data()

    mock_add.assert_any_call("Alice", "Mon")
    mock_add.assert_any_call("Bob", "Tue")
    assert mock_add.call_count == 2

def test_load_attendance_data_invalid_line(mocker):
    # 잘못된 데이터 (공백 없는 라인)
    mock_data = "InvalidLine\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_data))
    mocker.patch("attendance.add_attendance_data")

    with pytest.raises(ValueError, match="Invalid input format"):
        load_attendance_data()

def test_load_attendance_data_file_not_found(mocker):
    # open() 호출 시 FileNotFoundError 발생하도록 설정
    mocker.patch("builtins.open", side_effect=FileNotFoundError)

    with pytest.raises(ValueError, match="attendance_weekday_500.txt을 찾을 수 없습니다."):
        load_attendance_data()

def test_add_attendance_new_student_normal_day(mocker):
    # find_student은 없다고 응답 -> 신규 생성 흐름
    mocker.patch("attendance.find_student", return_value=None)
    # 전역 students 리스트를 테스트용으로 격리
    mocker.patch("attendance.students", [])

    add_attendance_data("Alice", "monday")

    # students에 1명 추가되었는지 확인
    assert len(__import__("attendance").students) == 1
    s = __import__("attendance").students[0]
    assert s.name == "Alice"
    # 월요일: 기본 +1, 보너스 없음
    assert s.total_score == 1
    # 출석 카운트
    assert s.attendance["monday"] == 1


def test_add_attendance_existing_student_weekend(mocker):
    # 기존 학생 준비
    existing = Student(name="Bob", total_score=10, grade="NORMAL", attendance={})
    # find_student은 기존 학생을 반환
    mocker.patch("attendance.find_student", return_value=existing)
    # 전역 students = [existing] 로 고정
    mocker.patch("attendance.students", [existing])

    add_attendance_data("Bob", "saturday")

    # 새로 append 되지 않아야 함
    assert len(__import__("attendance").students) == 1
    s = __import__("attendance").students[0]
    assert s is existing
    # 토요일: 기본 +1 + 주말 보너스 +1 => +2
    assert s.total_score == 12
    assert s.attendance["saturday"] == 1


def test_add_attendance_wednesday_bonus(mocker):
    # 신규 생성 흐름으로 수요일 보너스 확인
    mocker.patch("attendance.find_student", return_value=None)
    mocker.patch("attendance.students", [])

    add_attendance_data("Carol", "wednesday")

    s = __import__("attendance").students[0]
    # 수요일: 기본 +1 + 보너스 +2 => +3
    assert s.total_score == 3
    assert s.attendance["wednesday"] == 1