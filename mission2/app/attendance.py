from abc import ABC, abstractmethod
from dataclasses import dataclass, field

class Grade(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

class Normal(Grade):
    def name(self): return "NORMAL"

class Silver(Grade):
    def name(self): return "SILVER"

class Gold(Grade):
    def name(self): return "GOLD"


@dataclass
class Student:
    name: str
    grade: Grade = field(default_factory=Normal)
    total_score: int = 0
    attendance: dict = field(default_factory=dict)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class StudentRegistry(metaclass=Singleton):
    def __init__(self):
        self._items: list[Student] = []

    # 리스트 유틸
    def add(self, s: Student) -> None:
        self._items.append(s)

    def all(self) -> list[Student]:
        return list(self._items)  # 복사본 반환(외부 변형 방지용)

    def find(self, name: str) -> Student | None:
        return next((x for x in self._items if x.name == name), None)

# --- 사용 예 ---
repo = StudentRegistry()
repo.add(Student(name="Alice"))
repo2 = StudentRegistry()
assert repo is repo2  # 같은 인스턴스!


def print_member_info():
    students = StudentRegistry().all()
    for student in students:
        print(f"NAME : {student.name}, POINT : {student.total_score}, GRADE : {student.grade.name()}")

def get_remove_member():
    students = StudentRegistry().all()
    print("\nRemoved player")
    print("==============")
    for student in students:
        if student.grade.name() == 'NORMAL' and student.attendance.get("wednesday", 0) == 0 \
                and student.attendance.get("sunday", 0) + student.attendance.get("saturday", 0) == 0:
            print(student.name)

def update_member_grade():
    students = StudentRegistry().all()
    for student in students:
        if student.total_score >= 50:
            student.grade = Gold()
        elif student.total_score >= 30:
            student.grade = Silver()

def add_bonus_score():
    students = StudentRegistry().all()
    for student in students:
        if student.attendance.get("wednesday", 0)>= 10:
            student.total_score += 10
        if student.attendance.get("sunday", 0) + student.attendance.get("saturday", 0) >= 10:
            student.total_score += 10

def find_student(name):
    students = StudentRegistry().all()
    for student in students:
        if student.name == name:
            return student
    return None

def add_attendance_data(name, day_of_week):
    student = StudentRegistry().find(name)
    if not student:
        student = Student(name=name,grade=Normal(), total_score=0, attendance={})
        StudentRegistry().add(student)

    student.total_score += 1
    if day_of_week == "wednesday":
        student.total_score += 2
    if day_of_week == "saturday" or day_of_week == "sunday":
        student.total_score += 1
    student.attendance[day_of_week] = student.attendance.get(day_of_week, 0) + 1

def load_attendance_data():
    input_file_name = "../attendance_weekday_500.txt"
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

def main():
    load_attendance_data()
    add_bonus_score()
    update_member_grade()
    print_member_info()
    get_remove_member()



if __name__ == "__main__":
    main()
