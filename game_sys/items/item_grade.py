from enum import Enum, auto
class ItemGrade(Enum):
    ONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
@classmethod
def get_all_grades(cls):
    """
    Returns a list of all item grades.
    """
    return [member for member in cls]
@classmethod
def get_grade_by_value(cls, value):
    """
    Returns the ItemGrade corresponding to the given value.
    If no matching grade is found, returns None.
    """
    for grade in cls:
        if grade.value == value:
            return grade
    return None
