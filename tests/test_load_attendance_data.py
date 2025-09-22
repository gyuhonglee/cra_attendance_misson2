import pytest
from attendance import load_attendance_data

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
    mocker.patch("your_module.add_attendance_data")

    with pytest.raises(ValueError, match="Invalid input format"):
        load_attendance_data()

def test_load_attendance_data_file_not_found(mocker):
    # open() 호출 시 FileNotFoundError 발생하도록 설정
    mocker.patch("builtins.open", side_effect=FileNotFoundError)

    with pytest.raises(ValueError, match="attendance_weekday_500.txt을 찾을 수 없습니다."):
        load_attendance_data()