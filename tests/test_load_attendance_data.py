import pytest
import app
from app.attendance import add_bonus_score, find_student, Student, load_attendance_data, add_attendance_data

def test_load_attendace_data(mocker):
    mock_data = "Alice Mon\nBob Tue\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_data))

    mock_add = mocker.patch("app.attendance.add_attendance_data")

    load_attendance_data()

    mock_add.assert_any_call("Alice", "Mon")
    mock_add.assert_any_call("Bob", "Tue")
    assert mock_add.call_count == 2

def test_load_attendance_data_invalid_line(mocker):
    # 잘못된 데이터 (공백 없는 라인)
    mock_data = "InvalidLine\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_data))
    mocker.patch("app.attendance.add_attendance_data")

    with pytest.raises(ValueError, match="Invalid input format"):
        load_attendance_data()

def test_load_attendance_data_file_not_found(mocker):
    # open() 호출 시 FileNotFoundError 발생하도록 설정
    mocker.patch("builtins.open", side_effect=FileNotFoundError)

    with pytest.raises(ValueError, match="attendance_weekday_500.txt을 찾을 수 없습니다."):
        load_attendance_data()

def test_add_attendance_new_student_normal_day(mocker):
    # find_student은 없다고 응답 -> 신규 생성 흐름
    mocker.patch("app.attendance.find_student", return_value=None)
    # 전역 students 리스트를 테스트용으로 격리
    mocker.patch("app.attendance.students", [])

    add_attendance_data("Alice", "monday")

    # students에 1명 추가되었는지 확인
    assert len(app.attendance.students) == 1
    s = app.attendance.students[0]
    assert s.name == "Alice"
    # 월요일: 기본 +1, 보너스 없음
    assert s.total_score == 1
    # 출석 카운트
    assert s.attendance["monday"] == 1


def test_add_attendance_existing_student_weekend(mocker):
    # 기존 학생 준비
    existing = Student(name="Bob", total_score=10, grade="NORMAL", attendance={})
    # find_student은 기존 학생을 반환
    mocker.patch("app.attendance.find_student", return_value=existing)
    # 전역 students = [existing] 로 고정
    mocker.patch("app.attendance.students", [existing])

    add_attendance_data("Bob", "saturday")

    # 새로 append 되지 않아야 함
    assert len(app.attendance.students) == 1
    s = app.attendance.students[0]
    assert s is existing
    # 토요일: 기본 +1 + 주말 보너스 +1 => +2
    assert s.total_score == 12
    assert s.attendance["saturday"] == 1


def test_add_attendance_wednesday_bonus(mocker):
    # 신규 생성 흐름으로 수요일 보너스 확인
    mocker.patch("app.attendance.find_student", return_value=None)
    mocker.patch("app.attendance.students", [])

    add_attendance_data("Carol", "wednesday")

    s = app.attendance.students[0]
    # 수요일: 기본 +1 + 보너스 +2 => +3
    assert s.total_score == 3
    assert s.attendance["wednesday"] == 1

def test_find_student_found(mocker):
    # 준비: students 리스트에 Alice 있음
    s1 = Student(name="Alice", total_score=10, grade="NORMAL", attendance={})
    s2 = Student(name="Bob", total_score=5, grade="NORMAL", attendance={})

    mocker.patch("app.attendance.students", [s1, s2])

    result = find_student("Alice")
    assert result is s1
    assert result.name == "Alice"
    assert result.total_score == 10


def test_find_student_not_found(mocker):
    # 준비: students 리스트에 Charlie 없음
    s1 = Student(name="Alice", total_score=10, grade="NORMAL", attendance={})
    mocker.patch("app.attendance.students", [s1])

    result = find_student("Charlie")
    assert result is None

def test_add_bonus_score_wednesday_bonus(mocker):
    s = Student(name="Alice", total_score=50, grade="NORMAL", attendance={"wednesday": 10})
    mocker.patch("app.attendance.students", [s])

    add_bonus_score()

    assert s.total_score == 60  # +10 보너스


def test_add_bonus_score_weekend_bonus(mocker):
    s = Student(name="Bob", total_score=70, grade="NORMAL", attendance={"saturday": 6, "sunday": 5})
    mocker.patch("app.attendance.students", [s])

    add_bonus_score()

    assert s.total_score == 80  # +10 보너스


def test_add_bonus_score_no_bonus(mocker):
    s = Student(name="Charlie", total_score=30, grade="NORMAL", attendance={"wednesday": 5, "saturday": 4, "sunday": 3})
    mocker.patch("app.attendance.students", [s])

    add_bonus_score()

    assert s.total_score == 30  # 보너스 없음