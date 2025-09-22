import pytest
import app
from app.attendance import main, print_member_info, get_remove_member, update_member_grade, add_bonus_score, \
    find_student, Student, load_attendance_data, add_attendance_data, Normal, Silver, Gold, StudentRegistry


def test_main_calls_pipeline_in_order(mocker):
    calls = []

    mocker.patch("app.attendance.load_attendance_data",
                           side_effect=lambda: calls.append("load"))
    mocker.patch("app.attendance.add_bonus_score",
                           side_effect=lambda: calls.append("bonus"))
    mocker.patch("app.attendance.update_member_grade",
                           side_effect=lambda: calls.append("grade"))
    mocker.patch("app.attendance.print_member_info",
                           side_effect=lambda: calls.append("print"))
    mocker.patch("app.attendance.get_remove_member",
                           side_effect=lambda: calls.append("remove"))

    main()

    # 호출 순서까지 보장
    assert calls == ["load", "bonus", "grade", "print", "remove"]


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

def test_add_attendance_new_student_normal_day():
    repo = StudentRegistry()
    repo._items = []

    add_attendance_data("Alice", "monday")

    items = repo.all()
    assert len(items) == 1
    s = items[0]
    assert s.name == "Alice"
    assert s.total_score == 1          # 월요일: 기본 +1
    assert s.attendance["monday"] == 1


def test_add_attendance_existing_student_weekend(mocker):
    repo = StudentRegistry()
    existing = Student(name="Bob", total_score=10, grade=Normal(), attendance={})
    repo._items = [existing]
    add_attendance_data("Bob", "saturday")

    # 새로 append 되지 않아야 함
    items = repo.all()
    assert len(items) == 1
    s = items[0]
    assert s is existing
    # 토요일: 기본 +1 + 주말 보너스 +1 => +2
    assert s.total_score == 12
    assert s.attendance["saturday"] == 1


def test_add_attendance_wednesday_bonus(mocker):
    # 신규 생성 흐름으로 수요일 보너스 확인
    repo = StudentRegistry()
    repo._items = []
    add_attendance_data("Carol", "wednesday")

    items = repo.all()
    s = items[0]
    # 수요일: 기본 +1 + 보너스 +2 => +3
    assert s.total_score == 3
    assert s.attendance["wednesday"] == 1

def test_find_student_found(mocker):
    # 준비: students 리스트에 Alice 있음
    s1 = Student(name="Alice", total_score=10, grade=Normal(), attendance={})
    s2 = Student(name="Bob", total_score=5, grade=Normal(), attendance={})
    repo = StudentRegistry()
    repo._items = [s1, s2]

    result = find_student("Alice")
    assert result is s1
    assert result.name == "Alice"
    assert result.total_score == 10


def test_find_student_not_found(mocker):
    # 준비: students 리스트에 Charlie 없음
    s = Student(name="Alice", total_score=10, grade=Normal(), attendance={})
    repo = StudentRegistry()
    repo._items = [s]

    result = find_student("Charlie")
    assert result is None

def test_add_bonus_score_wednesday_bonus(mocker):
    s = Student(name="Alice", total_score=50, grade=Normal(), attendance={"wednesday": 10})
    repo = StudentRegistry()
    repo._items = [s]

    add_bonus_score()

    assert s.total_score == 60  # +10 보너스


def test_add_bonus_score_weekend_bonus(mocker):
    s = Student(name="Bob", total_score=70, grade=Normal(), attendance={"saturday": 6, "sunday": 5})
    repo = StudentRegistry()
    repo._items = [s]

    add_bonus_score()

    assert s.total_score == 80  # +10 보너스


def test_add_bonus_score_no_bonus(mocker):
    s = Student(name="Charlie", total_score=30, grade=Normal(), attendance={"wednesday": 5, "saturday": 4, "sunday": 3})
    repo = StudentRegistry()
    repo._items = [s]

    add_bonus_score()

    assert s.total_score == 30  # 보너스 없음

def test_update_member_grade_gold(mocker):
    s = Student(name="Alice", total_score=55, grade=Normal(), attendance={})
    repo = StudentRegistry()
    repo._items = [s]

    update_member_grade()

    assert s.grade.name() == "GOLD"


def test_update_member_grade_silver(mocker):
    s = Student(name="Bob", total_score=35, grade=Normal(), attendance={})
    repo = StudentRegistry()
    repo._items = [s]

    update_member_grade()

    assert s.grade.name() == "SILVER"


def test_update_member_grade_normal(mocker):
    s = Student(name="Charlie", total_score=20, grade=Normal(), attendance={})
    repo = StudentRegistry()
    repo._items = [s]

    update_member_grade()

    assert s.grade.name() == "NORMAL"  # 바뀌지 않음

def test_print_member_info(mocker, capsys):
    s1 = Student(name="Alice", total_score=40, grade=Silver(), attendance={})
    s2 = Student(name="Bob", total_score=60, grade=Gold(), attendance={})
    repo = StudentRegistry()
    repo._items = [s1, s2]

    print_member_info()
    captured = capsys.readouterr()

    # 두 학생의 출력이 포함되어야 함
    assert "NAME : Alice, POINT : 40, GRADE : SILVER" in captured.out
    assert "NAME : Bob, POINT : 60, GRADE : GOLD" in captured.out

def test_get_remove_member_removes_correct_student(mocker, capsys):
    # Alice는 NORMAL + 수요일 0 + 주말 0 → 제거 대상
    s1 = Student(name="Alice", total_score=10, grade=Normal(), attendance={})
    # Bob은 SILVER → 제거 대상 아님
    s2 = Student(name="Bob", total_score=40, grade=Silver(), attendance={"wednesday": 0})
    # Carol은 NORMAL이지만 일요일 출석 있음 → 제거 대상 아님
    s3 = Student(name="Carol", total_score=5, grade=Normal(), attendance={"sunday": 2})

    repo = StudentRegistry()
    repo._items = [s1, s2, s3]

    get_remove_member()
    captured = capsys.readouterr()

    # 헤더 출력 확인
    assert "Removed player" in captured.out
    assert "==============" in captured.out

    # Alice만 출력되어야 함
    assert "Alice" in captured.out
    assert "Bob" not in captured.out
    assert "Carol" not in captured.out