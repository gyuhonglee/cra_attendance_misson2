from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    grade : str
    total_score: int = 0
    attendance: dict = field(default_factory=dict)

students: list[Student] = []

def find_student(name):
    for student in students:
        if student.name == name:
            return student
    return None

def load_attendance_data():
    input_file_name = "attendance_weekday_500.txt"
    try:
        with open(input_file_name, encoding='utf-8') as f:
            for line in f:
                try:
                    name, day_of_week = line.strip().split()
                    add_attendance_data(name, day_of_week)
                except ValueError:
                    raise ValueError(f"Invalid input format: {line}")
    except FileNotFoundError:
        raise ValueError(f"{input_file_name}을 찾을 수 없습니다.")

def add_attendance_data(name, day_of_week):
    student = find_student(name)
    if not student:
        student = Student(name=name, total_score=0, grade="NORMAL", attendance={})
        students.append(student)

    student.total_score += 1
    if day_of_week == "wednesday" :
        student.total_score += 2
    if day_of_week == "saturday" or day_of_week == "sunday" :
        student.total_score += 1
    student.attendance[day_of_week] = student.attendance.get(day_of_week, 0) + 1

def add_bonus_score():
    for student in students:
        if student.attendance.get("wednesday", 0)>= 10:
            student.total_score += 10
        if student.attendance.get("sunday", 0) + student.attendance.get("saturday", 0) >= 10:
            student.total_score += 10

def update_member_grade():
    for student in students:
        if student.total_score>= 50:
            student.grade = "GOLD"
        elif student.total_score>= 30:
            student.grade = "SILVER"

def print_member_info():
    for student in students:
        print(f"NAME : {student.name}, POINT : {student.total_score}, GRADE : {student.grade}")

def get_remove_member():
    print("\nRemoved player")
    print("==============")
    for student in students:
        if student.grade == 'NORMAL' and student.attendance.get("wednesday", 0) == 0 \
                and student.attendance.get("sunday", 0) + student.attendance.get("saturday", 0) == 0:
            print(student.name)

def main():
    load_attendance_data()
    add_bonus_score()
    update_member_grade()
    print_member_info()
    get_remove_member()

if __name__ == "__main__":
    main()
