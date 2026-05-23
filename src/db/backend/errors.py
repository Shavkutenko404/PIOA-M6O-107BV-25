class TableError(Exception):
    """Базовый класс для ошибок таблиц"""

    pass


# Исключения для работы с таблицами (оценка 3)
class StudentTableError(TableError):
    """Базовый класс для ошибок таблицы Student"""

    pass


class InvalidAgeError(StudentTableError):
    """Ошибка: некорректный возраст"""

    pass


class DuplicateIDError(StudentTableError):
    """Ошибка: дубликат ID"""

    pass


# Дополнительные исключения для оценки 5 (ООП)
class TableNotFoundError(TableError):
    """Ошибка: таблица не найдена"""

    pass


class ColumnNotFoundError(TableError):
    """Ошибка: колонка не найдена"""

    pass


class DuplicateTableError(TableError):
    """Ошибка: таблица с таким именем уже существует"""

    pass


class EmptyTableNameError(TableError):
    """Ошибка: имя таблицы не может быть пустым"""

    pass


class EmptyColumnsError(TableError):
    """Ошибка: таблица должна содержать хотя бы одну колонку"""

    pass


class InvalidRecordLengthError(TableError):
    """Ошибка: длина записи не соответствует количеству колонок"""

    pass


class RecordNotFoundError(TableError):
    """Ошибка: запись с указанным индексом не найдена"""

    pass


class InvalidColumnNameError(TableError):
    """Ошибка: недопустимое название колонки (повторяющиеся имена)"""

    pass
