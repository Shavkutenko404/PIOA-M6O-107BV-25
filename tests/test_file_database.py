import tempfile
import unittest

from src.db.backend.file import FileDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    DuplicateTableError,
    EmptyTableNameError,
    EmptyColumnsError,
    InvalidRecordLengthError,
    ColumnNotFoundError,
    InvalidColumnNameError,  # добавить
)


class TestFileDatabase(unittest.TestCase):
    """Тесты для файловой базы данных"""

    def setUp(self):
        """Создаём временную директорию для каждого теста"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = FileDatabase(self.temp_dir.name)

    def tearDown(self):
        """Удаляем временную директорию после теста"""
        self.temp_dir.cleanup()

    def test_create_table_success(self):
        """Успешное создание таблицы"""
        self.db.create_table("students", ["id", "name", "age"])
        self.assertTrue(self.db.table_exists("students"))
        self.assertIn("students", self.db.list_tables())
        self.assertEqual(self.db.get_columns("students"), ["id", "name", "age"])

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
        """Создание таблицы с повторяющимися колонками"""
        with self.assertRaises(InvalidColumnNameError):
            self.db.create_table("test", ["a", "b", "a"])

    def test_insert_record_success(self):
        """Успешное добавление записи"""
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", ("1", "John", "20"))
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], ("1", "John", "20"))

    def test_insert_record_wrong_length(self):
        """Добавление записи неверной длины"""
        self.db.create_table("students", ["id", "name", "age"])
        with self.assertRaises(InvalidRecordLengthError):
            self.db.insert_record("students", ("1", "John"))

    def test_select_records_with_filter(self):
        """Чтение с фильтром"""
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", ("1", "John", "20"))
        self.db.insert_record("students", ("2", "Jane", "22"))
        self.db.insert_record("students", ("3", "John", "25"))

        records = self.db.select_records("students", name="John")
        self.assertEqual(len(records), 2)

    def test_update_records(self):
        """Обновление записей"""
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", ("1", "John", "20"))
        self.db.insert_record("students", ("2", "Jane", "22"))

        updated = self.db.update_records("students", {"age": "30"})
        self.assertEqual(updated, 2)

        records = self.db.select_records("students")
        self.assertEqual(records[0][2], "30")
        self.assertEqual(records[1][2], "30")

    def test_delete_records(self):
        """Удаление записей"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", ("1", "John"))
        self.db.insert_record("students", ("2", "Jane"))

        deleted = self.db.delete_records("students", name="John")
        self.assertEqual(deleted, 1)

        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Jane")

    def test_data_persists_between_instances(self):
        """Данные сохраняются между разными экземплярами"""
        db1 = FileDatabase(self.temp_dir.name)
        db1.create_table("students", ["id", "name"])
        db1.insert_record("students", ("1", "John"))

        db2 = FileDatabase(self.temp_dir.name)
        self.assertTrue(db2.table_exists("students"))
        records = db2.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], ("1", "John"))

    def test_rename_table(self):
        """Переименование таблицы"""
        self.db.create_table("old", ["id"])
        self.db.rename_table("old", "new")
        self.assertIn("new", self.db.list_tables())
        self.assertNotIn("old", self.db.list_tables())

    def test_rename_column(self):
        """Переименование колонки"""
        self.db.create_table("students", ["old", "other"])
        self.db.insert_record("students", ("1", "value"))

        self.db.rename_column("students", "old", "new")

        columns = self.db.get_columns("students")
        self.assertIn("new", columns)
        self.assertNotIn("old", columns)

    def test_table_not_found(self):
        """Ошибка при обращении к несуществующей таблице"""
        with self.assertRaises(TableNotFoundError):
            self.db.get_columns("ghost")

        with self.assertRaises(TableNotFoundError):
            self.db.select_records("ghost")

        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("ghost", ("1",))

    def test_rename_column_not_found(self):
        """Переименование несуществующей колонки"""
        self.db.create_table("students", ["name"])
        with self.assertRaises(ColumnNotFoundError):
            self.db.rename_column("students", "ghost", "new")

    def test_delete_table(self):
        """Удаление таблицы"""
        self.db.create_table("test", ["col"])
        self.db.insert_record("test", ("1",))
        self.db.delete_table("test")
        self.assertFalse(self.db.table_exists("test"))


if __name__ == "__main__":
    unittest.main()
