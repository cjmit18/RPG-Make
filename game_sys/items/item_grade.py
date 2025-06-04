from enum import Enum
class ItemGrade(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
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
