from typing import Any
from .database import Database
from .table import Table
from .errors import (
    TableNotFoundError,
    ColumnNotFoundError,
    DuplicateTableError,
    EmptyTableNameError,
    EmptyColumnsError,
    InvalidColumnNameError,
)


class MemoryDatabase(Database):
    """База данных в оперативной памяти"""

    def __init__(self):
        self._tables: dict[str, Table] = {}

    def create_table(self, name: str, columns: list[str]) -> None:
        """Создаёт новую таблицу"""
        name = name.strip()

        if not name:
            raise EmptyTableNameError("Имя таблицы не может быть пустым")

        if not columns:
            raise EmptyColumnsError("Таблица должна содержать хотя бы одну колонку")

        if len(columns) != len(set(columns)):
            raise InvalidColumnNameError("Названия колонок не должны повторяться")

        if name in self._tables:
            raise DuplicateTableError(f"Таблица '{name}' уже существует")

        self._tables[name] = Table(name, columns)

    def list_tables(self) -> list[str]:
        """Возвращает список всех таблиц"""
        return list(self._tables.keys())

    def get_columns(self, name: str) -> list[str]:
        """Возвращает список колонок таблицы"""
        table = self._tables.get(name)
        if not table:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        return table.columns.copy()

    def delete_table(self, name: str) -> None:
        """Удаляет таблицу полностью"""
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        del self._tables[name]

    def clear_table(self, name: str) -> None:
        """Очищает все записи в таблице"""
        table = self._tables.get(name)
        if not table:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        table.clear()

    def rename_table(self, old_name: str, new_name: str) -> None:
        """Переименовывает таблицу"""
        old_name = old_name.strip()
        new_name = new_name.strip()

        if not old_name or not new_name:
            raise EmptyTableNameError("Имя таблицы не может быть пустым")

        if old_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{old_name}' не найдена")

        if new_name in self._tables:
            raise DuplicateTableError(f"Таблица '{new_name}' уже существует")

        table = self._tables.pop(old_name)
        table.name = new_name
        self._tables[new_name] = table
        # убрал return True

    def rename_column(
        self, table_name: str, old_column: str, new_column: str
    ) -> None:  # убрал -> bool
        """Переименовывает колонку"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.rename_column(old_column, new_column)  # теперь None

    def table_exists(self, name: str) -> bool:
        """Проверяет существование таблицы"""
        return name in self._tables

    def get_all_info(self) -> dict[str, tuple[list[str], int]]:
        """Возвращает информацию обо всех таблицах"""
        result = {}
        for name, table in self._tables.items():
            result[name] = (table.columns.copy(), len(table.records))
        return result

    def insert_record(self, table_name: str, record: tuple[Any, ...]) -> None:
        """Добавляет запись"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.add_record(record)

    def select_records(self, table_name: str, **filters: Any) -> list[tuple[Any, ...]]:
        """Возвращает записи по фильтру"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.get_records(**filters)

    def update_records(
        self, table_name: str, updates: dict[str, Any], **filters: Any
    ) -> int:
        """Обновляет записи по фильтру"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.update_records(updates, **filters)

    def delete_records(self, table_name: str, **filters: Any) -> int:
        """Удаляет записи по фильтру"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.delete_records(**filters)

    def get_record_by_index(self, table_name: str, index: int) -> tuple[Any, ...]:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.get_record_by_index(index)

    def delete_record_by_index(
        self, table_name: str, index: int
    ) -> None:  # убрал -> bool
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.delete_record_by_index(index)  # теперь None

    def update_record_by_index(
        self, table_name: str, index: int, updates: dict[str, Any]
    ) -> None:  # убрал -> bool
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.update_record_by_index(index, updates)  # теперь None

    def sort_records(
        self, table_name: str, column: str, reverse: bool = False
    ) -> list[tuple[Any, ...]]:
        """Сортирует записи в таблице по указанной колонке"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.sort_records(column, reverse)
