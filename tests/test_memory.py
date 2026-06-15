import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.table import Table
from src.db.backend.errors import (
    TableNotFoundError,
    ColumnNotFoundError,
    DuplicateTableError,
    EmptyTableNameError,
    EmptyColumnsError,
    InvalidRecordLengthError,
    RecordNotFoundError,
    InvalidColumnNameError,
)


class TestDatabase(unittest.TestCase):
    """Тесты для класса Database (управление таблицами)"""

    def setUp(self):
        """Создаем чистую БД перед каждым тестом"""
        self.db = MemoryDatabase()

    def test_create_table_success(self):
        """Успешное создание таблицы"""
        table = self.db.create_table("students", ["id", "name", "age"])
        self.assertIsInstance(table, Table)
        self.assertEqual(table.name, "students")
        self.assertEqual(table.columns, ["id", "name", "age"])
        self.assertIn("students", self.db.list_tables())

    def test_create_table_duplicate(self):
        """Создание таблицы с существующим именем"""
        self.db.create_table("students", ["id", "name"])
        with self.assertRaises(DuplicateTableError):
            self.db.create_table("students", ["id", "name", "age"])

    def test_create_table_empty_name(self):
        """Создание таблицы с пустым именем"""
        with self.assertRaises(EmptyTableNameError):
            self.db.create_table("", ["id"])

    def test_create_table_no_columns(self):
        """Создание таблицы без колонок"""
        with self.assertRaises(EmptyColumnsError):
            self.db.create_table("test", [])

    def test_create_table_duplicate_columns(self):
        """Создание таблицы с повторяющимися названиями колонок"""
        with self.assertRaises(InvalidColumnNameError) as context:
            self.db.create_table("students", ["id", "name", "id"])
        self.assertEqual(
            str(context.exception), "Названия колонок не должны повторяться"
        )

    def test_list_tables_empty(self):
        """Список таблиц когда БД пуста"""
        self.assertEqual(self.db.list_tables(), [])

    def test_list_tables_with_data(self):
        """Список таблиц с данными"""
        self.db.create_table("t1", ["col1"])
        self.db.create_table("t2", ["col1"])
        tables = self.db.list_tables()
        self.assertEqual(len(tables), 2)
        self.assertIn("t1", tables)
        self.assertIn("t2", tables)

    def test_get_table_exists(self):
        """Получение существующей таблицы"""
        self.db.create_table("students", ["id", "name"])
        table = self.db.get_table("students")
        self.assertIsInstance(table, Table)
        self.assertEqual(table.name, "students")

    def test_get_table_not_exists(self):
        """Получение несуществующей таблицы"""
        table = self.db.get_table("ghost")
        self.assertIsNone(table)

    def test_delete_table_success(self):
        """Успешное удаление таблицы"""
        self.db.create_table("test", ["col"])
        self.db.delete_table("test")
        self.assertNotIn("test", self.db.list_tables())

    def test_delete_table_not_exists(self):
        """Удаление несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.delete_table("ghost")

    def test_rename_table_success(self):
        """Успешное переименование таблицы"""
        self.db.create_table("old", ["col"])
        self.db.rename_table("old", "new")
        self.assertNotIn("old", self.db.list_tables())
        self.assertIn("new", self.db.list_tables())
        table = self.db.get_table("new")
        self.assertEqual(table.name, "new")

    def test_rename_table_not_exists(self):
        """Переименование несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.rename_table("ghost", "new")

    def test_rename_table_to_existing(self):
        """Переименование в существующее имя"""
        self.db.create_table("t1", ["col"])
        self.db.create_table("t2", ["col"])
        with self.assertRaises(DuplicateTableError):
            self.db.rename_table("t1", "t2")

    def test_rename_table_empty_name(self):
        """Переименование с пустым именем"""
        self.db.create_table("test", ["col"])
        with self.assertRaises(EmptyTableNameError):
            self.db.rename_table("test", "")

    def test_get_all_info_empty(self):
        """Информация о всех таблицах когда БД пуста"""
        info = self.db.get_all_info()
        self.assertEqual(info, {})

    def test_get_all_info_with_tables(self):
        """Информация о всех таблицах с данными"""
        self.db.create_table("t1", ["id", "name"])
        self.db.create_table("t2", ["title"])

        table = self.db.get_table("t1")
        table.add_record((1, "test"))

        info = self.db.get_all_info()
        self.assertEqual(len(info), 2)
        self.assertIn("t1", info)
        self.assertIn("t2", info)

        columns_t1, count_t1 = info["t1"]
        self.assertEqual(columns_t1, ["id", "name"])
        self.assertEqual(count_t1, 1)

        columns_t2, count_t2 = info["t2"]
        self.assertEqual(columns_t2, ["title"])
        self.assertEqual(count_t2, 0)

    def test_table_exists(self):
        """Проверка существования таблицы"""
        self.db.create_table("test", ["col"])
        self.assertTrue(self.db.table_exists("test"))
        self.assertFalse(self.db.table_exists("ghost"))

    def test_get_columns_table_not_found(self):
        """Получение колонок несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.get_columns("ghost")

    def test_clear_table_not_found(self):
        """Очистка несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.clear_table("ghost")

    def test_insert_record_table_not_found(self):
        """Добавление записи в несуществующую таблицу"""
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("ghost", (1, "test"))

    def test_select_records_table_not_found(self):
        """Чтение записей из несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("ghost")

    def test_update_records_table_not_found(self):
        """Обновление записей в несуществующей таблице"""
        with self.assertRaises(TableNotFoundError):
            self.db.update_records("ghost", {"col": "val"})

    def test_delete_records_table_not_found(self):
        """Удаление записей из несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.delete_records("ghost")

    def test_get_record_by_index_table_not_found(self):
        """Получение записи по индексу из несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.get_record_by_index("ghost", 0)

    def test_delete_record_by_index_table_not_found(self):
        """Удаление записи по индексу из несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.delete_record_by_index("ghost", 0)

    def test_update_record_by_index_table_not_found(self):
        """Обновление записи по индексу в несуществующей таблице"""
        with self.assertRaises(TableNotFoundError):
            self.db.update_record_by_index("ghost", 0, {})

    def test_sort_records_database(self):
        """Сортировка записей через Database"""
        self.db.create_table("students", ["id", "name", "age"])
        table = self.db.get_table("students")
        table.add_record((1, "John", 25))
        table.add_record((2, "Alice", 20))
        table.add_record((3, "Bob", 22))

        result = self.db.sort_records("students", "age", reverse=False)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][2], 20)
        self.assertEqual(result[1][2], 22)
        self.assertEqual(result[2][2], 25)

    def test_sort_records_table_not_found(self):
        """Сортировка в несуществующей таблице"""
        with self.assertRaises(TableNotFoundError):
            self.db.sort_records("ghost", "age", reverse=False)


class TestTable(unittest.TestCase):
    """Тесты для класса Table (работа с записями)"""

    def setUp(self):
        """Создаем чистую таблицу перед каждым тестом"""
        self.table = Table("students", ["id", "name", "age"])

    def test_table_initialization(self):
        """Проверка инициализации таблицы"""
        self.assertEqual(self.table.name, "students")
        self.assertEqual(self.table.columns, ["id", "name", "age"])
        self.assertEqual(len(self.table.records), 0)
        self.assertEqual(self.table.records, [])

    def test_add_record_success(self):
        """Успешное добавление записи"""
        record = (1, "John", 20)
        self.table.add_record(record)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0], record)

    def test_add_record_wrong_length(self):
        """Добавление записи неверной длины"""
        record = (1, "John")
        with self.assertRaises(InvalidRecordLengthError):
            self.table.add_record(record)

    def test_add_multiple_records(self):
        """Добавление нескольких записей"""
        records = [(1, "John", 20), (2, "Jane", 22), (3, "Bob", 25)]
        for rec in records:
            self.table.add_record(rec)
        self.assertEqual(len(self.table.records), 3)
        self.assertEqual(self.table.records, records)

    def test_get_records_no_filters(self):
        """Чтение всех записей без фильтров"""
        records = [(1, "John", 20), (2, "Jane", 22), (3, "Bob", 25)]
        for rec in records:
            self.table.add_record(rec)
        result = self.table.get_records()
        self.assertEqual(result, records)

    def test_get_records_with_filter(self):
        """Чтение с фильтром по одному полю"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        self.table.add_record((3, "John", 25))
        result = self.table.get_records(name="John")
        self.assertEqual(len(result), 2)
        self.assertIn((1, "John", 20), result)
        self.assertIn((3, "John", 25), result)

    def test_get_records_multiple_filters(self):
        """Чтение с несколькими фильтрами"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        self.table.add_record((3, "John", 25))
        result = self.table.get_records(name="John", age=20)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (1, "John", 20))

    def test_get_records_filter_not_found(self):
        """Фильтр не дает результатов"""
        self.table.add_record((1, "John", 20))
        result = self.table.get_records(name="Ghost")
        self.assertEqual(result, [])

    def test_get_records_invalid_column(self):
        """Фильтр по несуществующей колонке вызывает ошибку"""
        self.table.add_record((1, "John", 20))
        with self.assertRaises(ColumnNotFoundError) as context:
            self.table.get_records(phone="123")
        self.assertIn("Неизвестная колонка: 'phone'", str(context.exception))

    def test_update_records_no_filters(self):
        """Обновление всех записей (без фильтра)"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        updated = self.table.update_records({"age": 30})
        self.assertEqual(updated, 2)
        records = self.table.records
        self.assertEqual(records[0], (1, "John", 30))
        self.assertEqual(records[1], (2, "Jane", 30))

    def test_update_records_with_filter(self):
        """Обновление записей по фильтру"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        self.table.add_record((3, "John", 25))
        updated = self.table.update_records({"age": 99}, name="John")
        self.assertEqual(updated, 2)
        john_records = self.table.get_records(name="John")
        for rec in john_records:
            self.assertEqual(rec[2], 99)
        jane_record = self.table.get_records(name="Jane")[0]
        self.assertEqual(jane_record[2], 22)

    def test_update_records_multiple_fields(self):
        """Обновление нескольких полей одновременно"""
        self.table.add_record((1, "John", 20))
        updated = self.table.update_records({"name": "Jonathan", "age": 21})
        self.assertEqual(updated, 1)
        record = self.table.records[0]
        self.assertEqual(record, (1, "Jonathan", 21))

    def test_update_records_no_matches(self):
        """Обновление когда нет записей под фильтр"""
        self.table.add_record((1, "John", 20))
        updated = self.table.update_records({"age": 30}, name="Ghost")
        self.assertEqual(updated, 0)
        self.assertEqual(self.table.records[0], (1, "John", 20))

    def test_update_records_unknown_field_raises_error(self):
        """Обновление с неизвестным полем вызывает ошибку"""
        self.table.add_record((1, "John", 20))
        with self.assertRaises(ColumnNotFoundError) as context:
            self.table.update_records({"agge": 30})
        self.assertIn("agge", str(context.exception))
        self.assertIn("Доступные поля", str(context.exception))

    def test_update_records_unknown_fields_list(self):
        """Обновление с несколькими неизвестными полями"""
        self.table.add_record((1, "John", 20))
        with self.assertRaises(ColumnNotFoundError) as context:
            self.table.update_records({"agge": 30, "phonne": "123"})
        self.assertIn("agge, phonne", str(context.exception))

    def test_delete_records_no_filters(self):
        """Удаление всех записей"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        deleted = self.table.delete_records()
        self.assertEqual(deleted, 2)
        self.assertEqual(len(self.table.records), 0)

    def test_delete_records_with_filter(self):
        """Удаление записей по фильтру"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        self.table.add_record((3, "John", 25))
        deleted = self.table.delete_records(name="John")
        self.assertEqual(deleted, 2)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0], (2, "Jane", 22))

    def test_delete_records_no_matches(self):
        """Удаление когда нет записей под фильтр"""
        self.table.add_record((1, "John", 20))
        deleted = self.table.delete_records(name="Ghost")
        self.assertEqual(deleted, 0)
        self.assertEqual(len(self.table.records), 1)

    def test_delete_records_multiple_filters(self):
        """Удаление с несколькими фильтрами"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "John", 25))
        self.table.add_record((3, "Jane", 20))
        deleted = self.table.delete_records(name="John", age=20)
        self.assertEqual(deleted, 1)
        self.assertEqual(len(self.table.records), 2)
        self.assertIn((2, "John", 25), self.table.records)
        self.assertIn((3, "Jane", 20), self.table.records)

    def test_clear_table(self):
        """Очистка всех записей"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        self.table.clear()
        self.assertEqual(len(self.table.records), 0)
        self.assertEqual(self.table.records, [])

    def test_rename_column_success(self):
        """Успешное переименование колонки"""
        self.table.rename_column("name", "full_name")
        self.assertIn("full_name", self.table.columns)
        self.assertNotIn("name", self.table.columns)

    def test_rename_column_not_exists(self):
        """Переименование несуществующей колонки"""
        with self.assertRaises(ColumnNotFoundError):
            self.table.rename_column("ghost", "new")

    def test_rename_column_to_existing_raises_error(self):
        """Переименование в существующее имя вызывает ошибку"""
        with self.assertRaises(ColumnNotFoundError) as context:
            self.table.rename_column("name", "age")
        self.assertEqual(str(context.exception), "Колонка 'age' уже существует")

    def test_get_record_by_index(self):
        """Получение записи по индексу"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        record = self.table.get_record_by_index(0)
        self.assertEqual(record, (1, "John", 20))
        record = self.table.get_record_by_index(1)
        self.assertEqual(record, (2, "Jane", 22))

    def test_get_record_by_index_not_found(self):
        """Получение несуществующей записи по индексу"""
        self.table.add_record((1, "John", 20))
        with self.assertRaises(RecordNotFoundError):
            self.table.get_record_by_index(5)

    def test_delete_record_by_index(self):
        """Удаление записи по индексу"""
        self.table.add_record((1, "John", 20))
        self.table.add_record((2, "Jane", 22))
        self.table.delete_record_by_index(0)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0], (2, "Jane", 22))

    def test_delete_record_by_index_not_found(self):
        """Удаление несуществующей записи по индексу"""
        self.table.add_record((1, "John", 20))
        with self.assertRaises(RecordNotFoundError):
            self.table.delete_record_by_index(5)

    def test_update_record_by_index(self):
        """Обновление записи по индексу"""
        self.table.add_record((1, "John", 20))
        self.table.update_record_by_index(0, {"name": "Jonathan", "age": 21})
        self.assertEqual(self.table.records[0], (1, "Jonathan", 21))

    def test_update_record_by_index_not_found(self):
        """Обновление несуществующей записи по индексу"""
        self.table.add_record((1, "John", 20))
        with self.assertRaises(RecordNotFoundError):
            self.table.update_record_by_index(5, {"name": "Jonathan"})

    def test_update_record_by_index_unknown_field_raises_error(self):
        """Обновление по индексу с неизвестным полем вызывает ошибку"""
        self.table.add_record((1, "John", 20))
        with self.assertRaises(ColumnNotFoundError):
            self.table.update_record_by_index(0, {"agge": 30})

    def test_sort_records_by_column_ascending(self):
        """Сортировка по колонке по возрастанию"""
        self.table.add_record((1, "John", 25))
        self.table.add_record((2, "Alice", 20))
        self.table.add_record((3, "Bob", 22))
        result = self.table.sort_records("age", reverse=False)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], (2, "Alice", 20))
        self.assertEqual(result[1], (3, "Bob", 22))
        self.assertEqual(result[2], (1, "John", 25))

    def test_sort_records_by_column_descending(self):
        """Сортировка по колонке по убыванию"""
        self.table.add_record((1, "John", 25))
        self.table.add_record((2, "Alice", 20))
        self.table.add_record((3, "Bob", 22))
        result = self.table.sort_records("age", reverse=True)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], (1, "John", 25))
        self.assertEqual(result[1], (3, "Bob", 22))
        self.assertEqual(result[2], (2, "Alice", 20))

    def test_sort_records_by_string_column(self):
        """Сортировка по строковой колонке"""
        self.table.add_record((1, "John", 25))
        self.table.add_record((2, "Alice", 20))
        self.table.add_record((3, "Bob", 22))
        result = self.table.sort_records("name", reverse=False)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], (2, "Alice", 20))
        self.assertEqual(result[1], (3, "Bob", 22))
        self.assertEqual(result[2], (1, "John", 25))

    def test_sort_records_column_not_found(self):
        """Сортировка по несуществующей колонке"""
        self.table.add_record((1, "John", 25))
        with self.assertRaises(ColumnNotFoundError):
            self.table.sort_records("ghost", reverse=False)

    def test_sort_records_empty_table(self):
        """Сортировка пустой таблицы"""
        result = self.table.sort_records("age", reverse=False)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
