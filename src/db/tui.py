from src.db.backend.errors import (
    TableNotFoundError,
    ColumnNotFoundError,
    DuplicateTableError,
    EmptyColumnsError,
    EmptyTableNameError,
    RecordNotFoundError,
    InvalidColumnNameError,
)
from src.db.backend.memory import MemoryDatabase
from src.db.backend.file import FileDatabase


class TUI:
    """Класс для текстового пользовательского интерфейса"""

    def __init__(self, db=None):
        """Инициализация интерфейса"""
        self._current_table: str | None = None
        if db is None:
            self._db = self._select_database_type()
        else:
            self._db = db

    def _select_database_type(self):
        """Выбор типа базы данных"""
        print("\n=== Выбор типа базы данных ===")
        print("1. In-memory (данные не сохраняются)")
        print("2. File database (данные сохраняются в папку 'data/'")
        choice = input("Выберите (1/2): ").strip()

        if choice == "2":
            print("✓ Используется файловая база данных")
            return FileDatabase()
        else:
            print("✓ Используется in-memory база данных")
            return MemoryDatabase()

    # ... остальные методы (run, _print_menu и т.д.)

    def run(self) -> None:
        """Главный цикл программы"""
        print("\n=== Добро пожаловать в систему управления БД ===")

        while True:
            if self._current_table:
                print(f"\n🔹 Текущая таблица: {self._current_table}")
            self._print_menu()

            action = input("Выберите действие: ").strip()

            if action == "1":
                self._create_new_table()
            elif action == "2":
                self._select_table()
            elif action == "3":
                self._show_tables()
            elif action == "4":
                self._show_current_table_info()
            elif action == "5":
                self._add_record()
            elif action == "6":
                self._show_all_records()
            elif action == "7":
                self._find_records()
            elif action == "8":
                self._update_records()
            elif action in ("9.1", "91"):
                self._delete_by_filter()
            elif action in ("9.2", "92"):
                self._clear_table()
            elif action == "10":
                self._delete_table()
            elif action == "11":
                self._rename_table()
            elif action == "12":
                self._rename_column()
            elif action == "13":
                self._sort_records()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")

    def _print_menu(self) -> None:
        """Отображает меню программы"""
        print("\n=== Система управления базами данных ===")
        print("1. Создать новую таблицу")
        print("2. Выбрать текущую таблицу")
        print("3. Показать все таблицы")
        print("4. Показать информацию о текущей таблице")
        print("5. Добавить запись")
        print("6. Показать все записи")
        print("7. Найти записи по фильтру")
        print("8. Обновить записи по фильтру")
        print("9. Удалить записи:")
        print("   9.1. Удалить по фильтру")
        print("   9.2. Очистить всю таблицу")
        print("10. Удалить таблицу")
        print("11. Переименовать текущую таблицу")
        print("12. Переименовать колонку")
        print("13. Сортировать записи")
        print("0. Выход")

    def _create_new_table(self) -> None:
        """Создание новой таблицы с колонками"""
        print("\n--- Создание новой таблицы ---")

        table_name = input("Введите имя таблицы: ").strip()
        if not table_name:
            print("✗ Имя таблицы не может быть пустым")
            return

        print("Введите названия колонок через пробел")
        columns_input = input("Колонки: ").strip().split()

        if not columns_input:
            print("✗ Нужно указать хотя бы одну колонку")
            return

        try:
            self._db.create_table(table_name, columns_input)
            print(f"✓ Таблица '{table_name}' создана")
        except (
            DuplicateTableError,
            EmptyTableNameError,
            EmptyColumnsError,
            InvalidColumnNameError,
        ) as e:
            print(f"✗ Ошибка: {e}")

    def _select_table(self) -> None:
        """Выбор текущей таблицы"""
        tables = self._db.list_tables()
        if not tables:
            print("📭 Нет созданных таблиц")
            return

        print("\nДоступные таблицы:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")

        while True:
            choice = input("\nВыберите таблицу (номер или имя): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(tables):
                    self._current_table = tables[idx]
                    print(f"✓ Текущая таблица: {self._current_table}")
                    return
            elif choice in tables:
                self._current_table = choice
                print(f"✓ Текущая таблица: {self._current_table}")
                return
            print("Неверный выбор. Попробуйте снова.")

    def _show_tables(self) -> None:
        """Показать все таблицы"""
        tables = self._db.list_tables()

        if not tables:
            print("📭 Нет созданных таблиц")
            return

        print("\n📋 Список всех таблиц:")
        for table_name in tables:
            try:
                columns = self._db.get_columns(table_name)
                records = self._db.select_records(table_name)
                print(f"   • {table_name}: {len(records)} записей, колонки: {columns}")
            except Exception as e:
                print(f"   • {table_name}: ошибка - {e}")
        print()

    def _show_current_table_info(self) -> None:
        """Показать информацию о текущей таблице"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        columns = self._db.get_columns(self._current_table)
        records = self._db.select_records(self._current_table)
        print(f"\n📋 Текущая таблица: {self._current_table}")
        print(f"   Колонки: {columns}")
        print(f"   Записей: {len(records)}")

    def _add_record(self) -> None:
        """Добавление записи в текущую таблицу"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        columns = self._db.get_columns(self._current_table)

        print(f"\n--- Добавление записи в таблицу '{self._current_table}' ---")
        print(f"Колонки: {columns}")

        values = []
        for col in columns:
            val = input(f"{col}: ").strip()
            while val == "":
                print(f"❌ Поле '{col}' не может быть пустым. Введите значение.")
                val = input(f"{col}: ").strip()
            values.append(val)

        try:
            self._db.insert_record(self._current_table, tuple(values))
            print("✓ Запись добавлена")
        except Exception as e:
            print(f"✗ Не удалось добавить запись: {e}")

    def _show_all_records(self) -> None:
        """Показать все записи текущей таблицы"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        records = self._db.select_records(self._current_table)
        columns = self._db.get_columns(self._current_table)

        if not records:
            print("📭 Записей нет")
            return

        print(f"\n--- Записи таблицы '{self._current_table}' ---")
        print(f"Колонки: {columns}")
        for i, record in enumerate(records, 1):
            print(f"{i}. {record}")

    def _find_records(self) -> None:
        """Поиск записей по фильтру"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        print(f"\n--- Поиск в таблице '{self._current_table}' ---")
        print("Введите фильтры в формате колонка=значение")
        print("(несколько фильтров через пробел, Enter = все записи)")
        filter_str = input("→ ").strip()

        filters = {}
        if filter_str:
            for item in filter_str.split():
                if "=" in item:
                    key, val = item.split("=", 1)
                    key = key.strip()
                    val = val.strip()

                    if key and val:
                        filters[key] = val
                    else:
                        print(f"⚠️ Пропущен некорректный фильтр: {item}")

        try:
            records = self._db.select_records(self._current_table, **filters)
            if not records:
                print("🔍 Записей не найдено")
                return
            print(f"\nНайдено записей: {len(records)}")
            for i, record in enumerate(records, 1):
                print(f"{i}. {record}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def _update_records(self) -> None:
        """Обновление записей по фильтру"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        print(f"\n--- Обновление записей в таблице '{self._current_table}' ---")

        print("Введите ФИЛЬТР для поиска записей (колонка=значение)")
        filter_str = input("Фильтр → ").strip()

        filters = {}
        if filter_str:
            for item in filter_str.split():
                if "=" in item:
                    key, val = item.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    filters[key] = val

        try:
            all_records_with_indexes = list(
                enumerate(self._db.select_records(self._current_table))
            )

            found_records_with_indexes = [
                (idx, record)
                for idx, record in all_records_with_indexes
                if all(
                    str(record[self._db.get_columns(self._current_table).index(k)]) == v
                    for k, v in filters.items()
                )
                or not filters
            ]

            found_records = [record for _, record in found_records_with_indexes]

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return

        if not found_records:
            print("🔍 Записей не найдено")
            return

        print(f"\nНайдено {len(found_records)} записей:")
        for i, record in enumerate(found_records, 1):
            print(f"{i}. {record}")

        print("\nВыберите записи для обновления (номера через пробел, 'all' - все):")
        choice = input("→ ").strip().lower()

        if not choice:
            print("❌ Обновление отменено")
            return

        selected_real_indexes = []
        if choice == "all":
            selected_real_indexes = [idx for idx, _ in found_records_with_indexes]
        else:
            for num in choice.split():
                try:
                    idx_in_found = int(num) - 1
                    if 0 <= idx_in_found < len(found_records_with_indexes):
                        selected_real_indexes.append(
                            found_records_with_indexes[idx_in_found][0]
                        )
                    else:
                        print(f"⚠️ Номер {num} вне диапазона")
                except ValueError:
                    print(f"⚠️ Некорректный номер: {num}")

        selected_real_indexes = sorted(set(selected_real_indexes), reverse=True)

        if not selected_real_indexes:
            print("❌ Не выбрано ни одной записи")
            return

        print(f"\nВыбрано {len(selected_real_indexes)} записей для обновления:")
        for real_idx in selected_real_indexes:
            record = next(
                (r for i, r in all_records_with_indexes if i == real_idx), None
            )
            if record:
                print(f"  • {record}")

        confirm = input("\nВы уверены? (д/н): ").strip().lower()
        if confirm not in ("д", "yes", "y", "да"):
            print("Обновление отменено")
            return

        print("\nВведите ЧТО обновлять (колонка=значение)")
        updates_str = input("Обновления → ").strip()

        updates = {}
        if updates_str:
            for item in updates_str.split():
                if "=" in item:
                    key, val = item.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    updates[key] = val

        if not updates:
            print("✗ Нет данных для обновления")
            return

        try:
            updated = self._db.update_records_by_indexes(
                self._current_table, selected_real_indexes, updates
            )
            print(f"✓ Обновлено {updated} из {len(selected_real_indexes)} записей")
        except (ColumnNotFoundError, RecordNotFoundError) as e:
            print(f"✗ Ошибка: {e}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def _delete_by_filter(self) -> None:
        """Удаление записей по фильтру"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        print(
            f"\n--- Удаление записей по фильтру из таблицы '{self._current_table}' ---"
        )
        print("Введите фильтры в формате колонка=значение")
        print("(несколько фильтров через пробел)")
        filter_str = input("→ ").strip()

        if not filter_str:
            print("✗ Нужно указать хотя бы один фильтр")
            return

        filters = {}
        for item in filter_str.split():
            if "=" in item:
                key, val = item.split("=", 1)
                key = key.strip()
                val = val.strip()
                if key and val:
                    filters[key] = val
                else:
                    print(f"⚠️ Пропущен некорректный фильтр: {item}")

        if not filters:
            print("✗ Нет корректных фильтров для удаления")
            return

        try:
            all_records_with_indexes = list(
                enumerate(self._db.select_records(self._current_table))
            )

            found_records_with_indexes = [
                (idx, record)
                for idx, record in all_records_with_indexes
                if all(
                    str(record[self._db.get_columns(self._current_table).index(k)]) == v
                    for k, v in filters.items()
                )
            ]

            to_delete = [record for _, record in found_records_with_indexes]

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return

        if not to_delete:
            print("🔍 Записей, соответствующих фильтру, не найдено")
            return

        print(f"\nНайдено {len(to_delete)} записей:")
        for i, record in enumerate(to_delete, 1):
            print(f"{i}. {record}")

        print("\nВыберите записи для удаления (номера через пробел, 'all' - все):")
        choice = input("→ ").strip().lower()

        if not choice:
            print("❌ Удаление отменено")
            return

        selected_real_indexes = []
        if choice == "all":
            selected_real_indexes = [idx for idx, _ in found_records_with_indexes]
        else:
            for num in choice.split():
                try:
                    idx_in_found = int(num) - 1
                    if 0 <= idx_in_found < len(found_records_with_indexes):
                        selected_real_indexes.append(
                            found_records_with_indexes[idx_in_found][0]
                        )
                    else:
                        print(f"⚠️ Номер {num} вне диапазона")
                except ValueError:
                    print(f"⚠️ Некорректный номер: {num}")

        selected_real_indexes = sorted(set(selected_real_indexes), reverse=True)

        if not selected_real_indexes:
            print("❌ Не выбрано ни одной записи")
            return

        print(f"\nВыбрано {len(selected_real_indexes)} записей для удаления:")
        for real_idx in selected_real_indexes:
            record = next(
                (r for i, r in all_records_with_indexes if i == real_idx), None
            )
            if record:
                print(f"  • {record}")

        confirm = input("\nВы уверены? (д/н): ").strip().lower()
        if confirm not in ("д", "yes", "y", "да"):
            print("Удаление отменено")
            return

        try:
            deleted = self._db.delete_records_by_indexes(
                self._current_table, selected_real_indexes
            )
            print(f"✓ Удалено {deleted} из {len(selected_real_indexes)} записей")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def _clear_table(self) -> None:
        """Очистить всю таблицу"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        records = self._db.select_records(self._current_table)
        count = len(records)

        if count == 0:
            print("📭 Таблица уже пуста")
            return

        print(f"\n--- Очистка таблицы '{self._current_table}' ---")
        print(f"Будет удалено {count} записей")
        confirm = input("Вы уверены? (д/н): ").strip().lower()

        if confirm in ("д", "yes", "y", "да"):
            try:
                self._db.clear_table(self._current_table)
                print(f"✓ Таблица '{self._current_table}' очищена")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        else:
            print("Очистка отменена")

    def _rename_table(self) -> None:
        """Переименование текущей таблицы"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        print(f"\n--- Переименование таблицы '{self._current_table}' ---")
        new_name = input("Введите новое имя таблицы: ").strip()

        if not new_name:
            print("✗ Имя не может быть пустым")
            return

        if new_name == self._current_table:
            print("✗ Новое имя совпадает со старым")
            return

        try:
            self._db.rename_table(self._current_table, new_name)
            self._current_table = new_name
            print(f"✓ Таблица переименована в '{new_name}'")
        except (TableNotFoundError, DuplicateTableError, EmptyTableNameError) as e:
            print(f"✗ {e}")

    def _delete_table(self) -> None:
        """Удаление таблицы"""
        tables = self._db.list_tables()
        if not tables:
            print("📭 Нет созданных таблиц")
            return

        print("\n--- Удаление таблицы ---")
        print("Доступные таблицы:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")

        table_name = input("Введите имя таблицы для удаления: ").strip()
        if not table_name:
            print("✗ Имя таблицы не может быть пустым")
            return

        if table_name not in tables:
            print(f"❌ Таблица '{table_name}' не найдена")
            return

        confirm = (
            input(f"Вы уверены, что хотите удалить таблицу '{table_name}'? (д/н): ")
            .strip()
            .lower()
        )
        if confirm in ("д", "yes", "y", "да"):
            try:
                self._db.delete_table(table_name)
                if self._current_table == table_name:
                    self._current_table = None
                    print("⚠️ Текущая таблица сброшена")
                print(f"✓ Таблица '{table_name}' удалена")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        else:
            print("Удаление отменено")

    def _rename_column(self) -> None:
        """Переименование колонки в текущей таблице"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        columns = self._db.get_columns(self._current_table)

        print(f"\n--- Переименование колонки в таблице '{self._current_table}' ---")
        print(f"Существующие колонки: {columns}")

        old_name = input("Введите старое название колонки: ").strip()
        if not old_name:
            print("✗ Имя не может быть пустым")
            return

        if old_name not in columns:
            print(f"✗ Колонка '{old_name}' не найдена")
            return

        new_name = input("Введите новое название колонки: ").strip()
        if not new_name:
            print("✗ Имя не может быть пустым")
            return

        if new_name in columns:
            print(f"✗ Колонка '{new_name}' уже существует")
            return

        try:
            self._db.rename_column(self._current_table, old_name, new_name)
            print("✓ Колонка переименована")
        except (TableNotFoundError, ColumnNotFoundError) as e:
            print(f"✗ {e}")

    def _sort_records(self) -> None:
        """Сортировка записей текущей таблицы"""
        if not self._current_table:
            print("⚠️ Сначала выберите таблицу (пункт 2)")
            return

        if not self._db.table_exists(self._current_table):
            print(f"❌ Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return

        columns = self._db.get_columns(self._current_table)

        print(f"\n--- Сортировка таблицы '{self._current_table}' ---")
        print(f"Доступные колонки: {columns}")

        column = input("Введите название колонки для сортировки: ").strip()
        if not column:
            print("✗ Сортировка отменена")
            return

        if column not in columns:
            print(f"✗ Колонка '{column}' не найдена")
            return

        print("Порядок сортировки:")
        print("1. По возрастанию")
        print("2. По убыванию")
        order = input("Выберите (1/2): ").strip()

        reverse = order == "2"

        try:
            records = self._db.sort_records(self._current_table, column, reverse)
            if not records:
                print("📭 Записей нет")
                return

            print(
                f"\n--- Отсортированные записи по колонке '{column}' {'(убывание)' if reverse else '(возрастание)'} ---"
            )
            for i, record in enumerate(records, 1):
                print(f"{i}. {record}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")


def run() -> None:
    """Точка входа для совместимости с __main__.py"""
    tui = TUI()
    tui.run()
