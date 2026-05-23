import unittest
from src.db.backend.memory import Database
from src.db.tui import TUI


class TestTUI(unittest.TestCase):
    """Тесты для класса TUI"""

    def setUp(self):
        """Очищаем БД перед каждым тестом и создаём TUI"""
        self.db = Database()
        self.tui = TUI(db=self.db)

    def tearDown(self):
        """Очищаем после каждого теста"""
        self.tui = None
        self.db = None

    def _mock_input(self, inputs):
        """Вспомогательный метод для подмены input"""
        self.inputs = inputs
        self.input_index = 0
        self.original_input = __builtins__["input"]
        __builtins__["input"] = self._mock_input_func

    def _mock_input_func(self, prompt=""):
        """Функция-заглушка для input"""
        if self.input_index < len(self.inputs):
            value = self.inputs[self.input_index]
            self.input_index += 1
            return value
        return ""

    def _restore_input(self):
        """Восстанавливаем оригинальный input"""
        __builtins__["input"] = self.original_input

    # ===== Тесты создания таблиц =====

    def test_create_new_table_success(self):
        """Тест успешного создания таблицы"""
        self._mock_input(["students", "id name age"])
        self.tui._create_new_table()
        self._restore_input()
        self.assertIn("students", self.db.list_tables())

    def test_create_new_table_empty_name(self):
        """Тест создания таблицы с пустым именем"""
        self._mock_input([""])
        self.tui._create_new_table()
        self._restore_input()
        self.assertEqual(self.db.list_tables(), [])

    def test_create_new_table_no_columns(self):
        """Тест создания таблицы без колонок"""
        self._mock_input(["test", ""])
        self.tui._create_new_table()
        self._restore_input()
        self.assertEqual(self.db.list_tables(), [])

    def test_create_new_table_duplicate(self):
        """Тест создания дубликата таблицы"""
        self.db.create_table("students", ["id", "name"])
        self._mock_input(["students", "id name age"])
        self.tui._create_new_table()
        self._restore_input()

    # ===== Тесты выбора таблицы =====

    def test_select_table_by_number(self):
        """Тест выбора таблицы по номеру"""
        self.db.create_table("students", ["id"])
        self.db.create_table("teachers", ["id"])
        self._mock_input(["1"])
        self.tui._select_table()
        self._restore_input()
        self.assertEqual(self.tui._current_table, "students")

    def test_select_table_by_name(self):
        """Тест выбора таблицы по имени"""
        self.db.create_table("students", ["id"])
        self._mock_input(["students"])
        self.tui._select_table()
        self._restore_input()
        self.assertEqual(self.tui._current_table, "students")

    def test_select_table_no_tables(self):
        """Тест выбора таблицы когда таблиц нет"""
        self._mock_input(["1"])
        self.tui._select_table()
        self._restore_input()
        self.assertIsNone(self.tui._current_table)

    # ===== Тесты показа таблиц =====

    def test_show_tables_empty(self):
        """Тест показа таблиц когда БД пуста"""
        self.tui._show_tables()

    def test_show_tables_with_data(self):
        """Тест показа таблиц с данными"""
        self.db.create_table("students", ["id", "name"])
        self.db.create_table("teachers", ["id"])
        self.tui._show_tables()

    def test_show_current_table_info_no_table(self):
        """Тест показа информации без выбранной таблицы"""
        self.tui._show_current_table_info()

    def test_show_current_table_info_success(self):
        """Тест показа информации о текущей таблице"""
        self.db.create_table("students", ["id", "name"])
        self.tui._current_table = "students"
        self.tui._show_current_table_info()

    # ===== Тесты добавления записей =====

    def test_add_record_success(self):
        """Тест успешного добавления записи"""
        self.db.create_table("students", ["id", "name"])
        self.tui._current_table = "students"
        self._mock_input(["1", "John"])
        self.tui._add_record()
        self._restore_input()
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], ("1", "John"))

    def test_add_record_no_table(self):
        """Тест добавления записи без выбранной таблицы"""
        self._mock_input(["1", "John"])
        self.tui._add_record()
        self._restore_input()

    def test_add_record_table_not_found(self):
        """Тест добавления записи в несуществующую таблицу"""
        self.tui._current_table = "ghost"
        self._mock_input(["1", "John"])
        self.tui._add_record()
        self._restore_input()
        self.assertIsNone(self.tui._current_table)

    # ===== Тесты показа записей =====

    def test_show_all_records_success(self):
        """Тест показа всех записей"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.db.insert_record("students", (2, "Jane"))
        self.tui._current_table = "students"
        self.tui._show_all_records()

    def test_show_all_records_no_table(self):
        """Тест показа записей без выбранной таблицы"""
        self.tui._show_all_records()

    # ===== Тесты поиска =====

    def test_find_records_success(self):
        """Тест поиска записей по фильтру"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.db.insert_record("students", (2, "Jane"))
        self.db.insert_record("students", (3, "John"))
        self.tui._current_table = "students"
        self._mock_input(["name=John"])
        self.tui._find_records()
        self._restore_input()

    def test_find_records_no_filters(self):
        """Тест поиска без фильтров"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.db.insert_record("students", (2, "Jane"))
        self.tui._current_table = "students"
        self._mock_input([""])
        self.tui._find_records()
        self._restore_input()

    def test_find_records_invalid_filter(self):
        """Тест поиска с некорректным фильтром"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.tui._current_table = "students"
        self._mock_input(["name"])
        self.tui._find_records()
        self._restore_input()

    # ===== Тесты очистки таблицы =====

    def test_clear_table_success(self):
        """Тест очистки таблицы"""
        self.db.create_table("students", ["id"])
        self.db.insert_record("students", (1,))
        self.db.insert_record("students", (2,))
        self.tui._current_table = "students"
        self._mock_input(["д"])
        self.tui._clear_table()
        self._restore_input()
        self.assertEqual(len(self.db.select_records("students")), 0)

    def test_clear_table_cancel(self):
        """Тест отмены очистки таблицы"""
        self.db.create_table("students", ["id"])
        self.db.insert_record("students", (1,))
        self.tui._current_table = "students"
        self._mock_input(["н"])
        self.tui._clear_table()
        self._restore_input()
        self.assertEqual(len(self.db.select_records("students")), 1)

    # ===== Тесты переименования таблиц =====

    def test_rename_table_success(self):
        """Тест переименования таблицы"""
        self.db.create_table("old", ["id"])
        self.tui._current_table = "old"
        self._mock_input(["new"])
        self.tui._rename_table()
        self._restore_input()
        self.assertIn("new", self.db.list_tables())
        self.assertNotIn("old", self.db.list_tables())
        self.assertEqual(self.tui._current_table, "new")

    def test_rename_table_same_name(self):
        """Тест переименования в то же имя"""
        self.db.create_table("test", ["id"])
        self.tui._current_table = "test"
        self._mock_input(["test"])
        self.tui._rename_table()
        self._restore_input()
        self.assertIn("test", self.db.list_tables())

    def test_rename_table_no_name(self):
        """Тест переименования с пустым именем"""
        self.db.create_table("test", ["id"])
        self.tui._current_table = "test"
        self._mock_input([""])
        self.tui._rename_table()
        self._restore_input()
        self.assertIn("test", self.db.list_tables())

    def test_rename_table_duplicate(self):
        """Тест переименования таблицы в существующее имя"""
        self.db.create_table("t1", ["col"])
        self.db.create_table("t2", ["col"])
        self.tui._current_table = "t1"
        self._mock_input(["t2"])
        self.tui._rename_table()
        self._restore_input()
        # Таблица не должна быть переименована
        self.assertIn("t1", self.db.list_tables())
        self.assertIn("t2", self.db.list_tables())
        self.assertEqual(self.tui._current_table, "t1")

    # ===== Тесты удаления таблиц =====

    def test_delete_table_success(self):
        """Тест удаления таблицы"""
        self.db.create_table("test", ["id"])
        self.tui._current_table = "test"
        self._mock_input(["test", "д"])
        self.tui._delete_table()
        self._restore_input()
        self.assertNotIn("test", self.db.list_tables())
        self.assertIsNone(self.tui._current_table)

    def test_delete_table_empty_name(self):
        """Тест удаления с пустым именем"""
        self.db.create_table("test", ["id"])
        self._mock_input([""])
        self.tui._delete_table()
        self._restore_input()

    def test_delete_table_not_found(self):
        """Тест удаления несуществующей таблицы"""
        self.db.create_table("test", ["id"])
        self._mock_input(["ghost"])
        self.tui._delete_table()
        self._restore_input()

    # ===== Тесты переименования колонок =====

    def test_rename_column_success(self):
        """Тест переименования колонки"""
        self.db.create_table("students", ["old", "other"])
        self.tui._current_table = "students"
        self._mock_input(["old", "new"])
        self.tui._rename_column()
        self._restore_input()
        columns = self.db.get_columns("students")
        self.assertIn("new", columns)
        self.assertNotIn("old", columns)

    def test_rename_column_empty_old(self):
        """Тест переименования колонки с пустым старым именем"""
        self.db.create_table("students", ["name"])
        self.tui._current_table = "students"
        self._mock_input([""])
        self.tui._rename_column()
        self._restore_input()
        columns = self.db.get_columns("students")
        self.assertEqual(columns, ["name"])

    def test_rename_column_empty_new(self):
        """Тест переименования колонки с пустым новым именем"""
        self.db.create_table("students", ["name"])
        self.tui._current_table = "students"
        self._mock_input(["name", ""])
        self.tui._rename_column()
        self._restore_input()
        columns = self.db.get_columns("students")
        self.assertEqual(columns, ["name"])

    def test_rename_column_not_found(self):
        """Тест переименования несуществующей колонки"""
        self.db.create_table("students", ["name"])
        self.tui._current_table = "students"
        self._mock_input(["age", "newage"])
        self.tui._rename_column()
        self._restore_input()
        columns = self.db.get_columns("students")
        self.assertEqual(columns, ["name"])

    def test_rename_column_duplicate(self):
        """Тест переименования колонки в существующее имя"""
        self.db.create_table("students", ["name", "age"])
        self.tui._current_table = "students"
        self._mock_input(["name", "age"])
        self.tui._rename_column()
        self._restore_input()
        columns = self.db.get_columns("students")
        self.assertEqual(columns, ["name", "age"])  # не изменилось

    # ===== Тесты обновления записей =====

    def test_update_records_all(self):
        """Тест обновления всех записей по фильтру"""
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", ("1", "John", "20"))
        self.db.insert_record("students", ("2", "Jane", "22"))
        self.db.insert_record("students", ("3", "John", "25"))
        self.tui._current_table = "students"

        self._mock_input(["name=John", "all", "д", "age=30"])
        self.tui._update_records()
        self._restore_input()

        records = self.db.select_records("students")
        johns = [r for r in records if r[1] == "John"]
        for record in johns:
            self.assertEqual(record[2], "30")

    def test_update_records_selected(self):
        """Тест обновления выбранных записей"""
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", ("1", "John", "20"))
        self.db.insert_record("students", ("2", "Jane", "22"))
        self.db.insert_record("students", ("3", "John", "25"))
        self.tui._current_table = "students"
        self._mock_input(["name=John", "1", "д", "age=30"])
        self.tui._update_records()
        self._restore_input()
        records = self.db.select_records("students")
        self.assertEqual(records[0][2], "30")
        self.assertEqual(records[1][2], "22")
        self.assertEqual(records[2][2], "25")

    def test_update_records_cancel(self):
        """Тест отмены обновления"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.db.insert_record("students", (2, "Jane"))
        self.tui._current_table = "students"
        self._mock_input(["", "all", "name=Peter", "н"])
        self.tui._update_records()
        self._restore_input()
        records = self.db.select_records("students")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0][1], "John")
        self.assertEqual(records[1][1], "Jane")

    def test_update_records_no_matches(self):
        """Тест обновления когда нет записей под фильтр"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.tui._current_table = "students"
        self._mock_input(["name=Ghost"])
        self.tui._update_records()
        self._restore_input()

    def test_update_records_no_updates(self):
        """Тест обновления без указания что обновлять"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.tui._current_table = "students"

        self._mock_input(["", "all", "д", ""])
        self.tui._update_records()
        self._restore_input()

        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "John")

    def test_update_records_invalid_input(self):
        """Тест обновления с некорректным вводом номеров"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.db.insert_record("students", (2, "Jane"))
        self.tui._current_table = "students"
        self._mock_input(["", "abc", ""])
        self.tui._update_records()
        self._restore_input()
        records = self.db.select_records("students")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0][1], "John")
        self.assertEqual(records[1][1], "Jane")

    def test_update_records_unknown_field(self):
        """Тест обновления с неизвестным полем"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.tui._current_table = "students"
        self._mock_input(["", "all", "д", "agge=30"])
        self.tui._update_records()
        self._restore_input()
        # Запись не должна измениться
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "John")

    # ===== Тесты удаления по фильтру =====

    def test_delete_by_filter_all(self):
        """Тест удаления всех записей по фильтру"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", ("1", "John"))
        self.db.insert_record("students", ("2", "Jane"))
        self.db.insert_record("students", ("3", "John"))
        self.tui._current_table = "students"
        self._mock_input(["name=John", "all", "д"])
        self.tui._delete_by_filter()
        self._restore_input()
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        names = [r[1] for r in records]
        self.assertIn("Jane", names)
        self.assertNotIn("John", names)

    def test_delete_by_filter_selected(self):
        """Тест удаления выбранных записей"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", ("1", "John"))
        self.db.insert_record("students", ("2", "Jane"))
        self.db.insert_record("students", ("3", "John"))
        self.tui._current_table = "students"
        self._mock_input(["name=John", "1", "д"])
        self.tui._delete_by_filter()
        self._restore_input()
        records = self.db.select_records("students")
        self.assertEqual(len(records), 2)
        names = [r[1] for r in records]
        self.assertIn("Jane", names)
        self.assertIn("John", names)

    def test_delete_by_filter_cancel(self):
        """Тест отмены удаления"""
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John"))
        self.tui._current_table = "students"
        self._mock_input(["name=John", "all", "н"])
        self.tui._delete_by_filter()
        self._restore_input()
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "John")

    def test_delete_by_filter_no_filters(self):
        """Тест удаления без фильтров"""
        self.db.create_table("students", ["id"])
        self.tui._current_table = "students"
        self._mock_input([""])
        self.tui._delete_by_filter()
        self._restore_input()

    # ===== Тесты сортировки =====

    def test_sort_records_success_ascending(self):
        """Тест успешной сортировки по возрастанию"""
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 25))
        self.db.insert_record("students", (2, "Alice", 20))
        self.db.insert_record("students", (3, "Bob", 22))
        self.tui._current_table = "students"

        self._mock_input(["age", "1"])
        self.tui._sort_records()
        self._restore_input()

    def test_sort_records_success_descending(self):
        """Тест успешной сортировки по убыванию"""
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 25))
        self.db.insert_record("students", (2, "Alice", 20))
        self.db.insert_record("students", (3, "Bob", 22))
        self.tui._current_table = "students"

        self._mock_input(["age", "2"])
        self.tui._sort_records()
        self._restore_input()

    def test_sort_records_no_table(self):
        """Тест сортировки без выбранной таблицы"""
        self._mock_input(["age", "1"])
        self.tui._sort_records()
        self._restore_input()

    def test_sort_records_table_not_found(self):
        """Тест сортировки в несуществующей таблице"""
        self.tui._current_table = "ghost"
        self._mock_input(["age", "1"])
        self.tui._sort_records()
        self._restore_input()
        self.assertIsNone(self.tui._current_table)

    def test_sort_records_empty_column(self):
        """Тест сортировки с пустым названием колонки"""
        self.db.create_table("students", ["id", "name", "age"])
        self.tui._current_table = "students"

        self._mock_input([""])
        self.tui._sort_records()
        self._restore_input()

    def test_sort_records_invalid_column(self):
        """Тест сортировки по несуществующей колонке"""
        self.db.create_table("students", ["id", "name", "age"])
        self.tui._current_table = "students"

        self._mock_input(["ghost", "1"])
        self.tui._sort_records()
        self._restore_input()

    def test_sort_records_empty_table(self):
        """Тест сортировки пустой таблицы"""
        self.db.create_table("students", ["id", "name", "age"])
        self.tui._current_table = "students"

        self._mock_input(["age", "1"])
        self.tui._sort_records()
        self._restore_input()

    # ===== Тесты run =====

    def test_run_exit(self):
        """Тест выхода из программы"""
        self._mock_input(["0"])
        self.tui.run()
        self._restore_input()

    def test_run_invalid_command(self):
        """Тест неверной команды"""
        self._mock_input(["invalid", "0"])
        self.tui.run()
        self._restore_input()

    def test_menu_choice_91(self):
        """Тест выбора пункта 9.1 (удаление по фильтру)"""
        self.db.create_table("test", ["col"])
        self.db.insert_record("test", ("1",))
        self.tui._current_table = "test"
        self._mock_input(["9.1", "col=1", "all", "д", "0"])
        self.tui.run()
        self._restore_input()
        self.assertEqual(len(self.db.select_records("test")), 0)

    def test_menu_choice_92(self):
        """Тест выбора пункта 9.2 (очистка таблицы)"""
        self.db.create_table("test", ["col"])
        self.db.insert_record("test", ("1",))
        self.tui._current_table = "test"
        self._mock_input(["9.2", "д", "0"])
        self.tui.run()
        self._restore_input()
        self.assertEqual(len(self.db.select_records("test")), 0)

    def test_menu_choice_13(self):
        """Тест выбора пункта 13 (сортировка)"""
        self.db.create_table("test", ["col"])
        self.db.insert_record("test", (2,))
        self.db.insert_record("test", (1,))
        self.tui._current_table = "test"

        self._mock_input(["13", "col", "1", "0"])
        self.tui.run()
        self._restore_input()


if __name__ == "__main__":
    unittest.main()
