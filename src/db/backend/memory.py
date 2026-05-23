from typing import Any
from .errors import (
    TableNotFoundError,
    ColumnNotFoundError,
    DuplicateTableError,
    EmptyTableNameError,
    EmptyColumnsError,
    InvalidRecordLengthError,
    RecordNotFoundError,
    InvalidColumnNameError,
)


class Table:
    """Класс для представления одной таблицы"""

    def __init__(self, name: str, columns: list[str]):
        self.name = name
        self.columns = columns.copy()
        self.records: list[tuple[Any, ...]] = []

    def add_record(self, record: tuple[Any, ...]) -> None:
        """Добавляет запись в таблицу"""
        if len(record) != len(self.columns):
            raise InvalidRecordLengthError(
                f"Запись должна содержать {len(self.columns)} полей"
            )
        self.records.append(record)

    def get_records(self, **filters: Any) -> list[tuple[Any, ...]]:
        """Возвращает записи по фильтру"""
        if not filters:
            return self.records.copy()

        result = []
        for record in self.records:
            if self._matches_filters(record, filters):
                result.append(record)
        return result

    def _matches_filters(self, record: tuple, filters: dict) -> bool:
        """Проверяет, соответствует ли запись фильтрам"""
        for key, value in filters.items():
            if key not in self.columns:
                return False
            idx = self.columns.index(key)
            if record[idx] != value:
                return False
        return True

    def update_records(self, updates: dict[str, Any], **filters: Any) -> int:
        """Обновляет записи по фильтру"""
        # Проверяем, что все поля для обновления существуют
        invalid_keys = [k for k in updates.keys() if k not in self.columns]
        if invalid_keys:
            raise ColumnNotFoundError(
                f"Неизвестное поле: {', '.join(invalid_keys)}. "
                f"Доступные поля: {self.columns}"
            )

        updated = 0
        for i, record in enumerate(self.records):
            if self._matches_filters(record, filters):
                record_list = list(record)
                for key, value in updates.items():
                    idx = self.columns.index(key)
                    record_list[idx] = value
                self.records[i] = tuple(record_list)
                updated += 1
        return updated

    def update_records_by_indexes(
        self, indexes: list[int], updates: dict[str, Any]
    ) -> int:
        """Обновляет записи по списку индексов"""
        # Проверяем, что все поля для обновления существуют
        invalid_keys = [k for k in updates.keys() if k not in self.columns]
        if invalid_keys:
            raise ColumnNotFoundError(
                f"Неизвестное поле: {', '.join(invalid_keys)}. "
                f"Доступные поля: {self.columns}"
            )

        updated = 0
        for idx in sorted(indexes, reverse=True):
            if 0 <= idx < len(self.records):
                record_list = list(self.records[idx])
                for key, value in updates.items():
                    col_idx = self.columns.index(key)
                    record_list[col_idx] = value
                self.records[idx] = tuple(record_list)
                updated += 1
        return updated

    def delete_records(self, **filters: Any) -> int:
        """Удаляет записи по фильтру"""
        if not filters:
            count = len(self.records)
            self.records.clear()
            return count

        to_keep = []
        deleted = 0
        for record in self.records:
            if self._matches_filters(record, filters):
                deleted += 1
            else:
                to_keep.append(record)

        self.records = to_keep
        return deleted

    def delete_records_by_indexes(self, indexes: list[int]) -> int:
        """Удаляет записи по списку индексов"""
        deleted = 0
        for idx in sorted(indexes, reverse=True):
            if 0 <= idx < len(self.records):
                del self.records[idx]
                deleted += 1
        return deleted

    def clear(self) -> None:
        """Очищает все записи"""
        self.records.clear()

    def rename_column(self, old_name: str, new_name: str) -> None:
        """Переименовывает колонку"""
        if old_name not in self.columns:
            raise ColumnNotFoundError(f"Колонка '{old_name}' не найдена")
        if new_name in self.columns:
            raise ColumnNotFoundError(f"Колонка '{new_name}' уже существует")

        idx = self.columns.index(old_name)
        self.columns[idx] = new_name

    def get_record_by_index(self, index: int) -> tuple[Any, ...]:
        """Возвращает запись по индексу"""
        if 0 <= index < len(self.records):
            return self.records[index]
        raise RecordNotFoundError(f"Запись с индексом {index} не найдена")

    def delete_record_by_index(self, index: int) -> None:
        """Удаляет запись по индексу"""
        if 0 <= index < len(self.records):
            del self.records[index]
        else:
            raise RecordNotFoundError(f"Запись с индексом {index} не найдена")

    def update_record_by_index(self, index: int, updates: dict[str, Any]) -> None:
        """Обновляет запись по индексу"""
        if not (0 <= index < len(self.records)):
            raise RecordNotFoundError(f"Запись с индексом {index} не найдена")

        # Проверяем, что все поля для обновления существуют
        invalid_keys = [k for k in updates.keys() if k not in self.columns]
        if invalid_keys:
            raise ColumnNotFoundError(
                f"Неизвестное поле: {', '.join(invalid_keys)}. "
                f"Доступные поля: {self.columns}"
            )

        record_list = list(self.records[index])
        for key, value in updates.items():
            col_idx = self.columns.index(key)
            record_list[col_idx] = value
        self.records[index] = tuple(record_list)

    def record_count(self) -> int:
        """Количество записей в таблице"""
        return len(self.records)

    def sort_records(self, column: str, reverse: bool = False) -> list[tuple[Any, ...]]:
        """Сортирует записи по указанной колонке"""
        if column not in self.columns:
            raise ColumnNotFoundError(f"Колонка '{column}' не найдена")

        col_idx = self.columns.index(column)
        return sorted(self.records, key=lambda record: record[col_idx], reverse=reverse)


class Database:
    """Класс для управления базой данных (коллекцией таблиц)"""

    def __init__(self):
        self._tables: dict[str, Table] = {}

    def create_table(self, name: str, columns: list[str]) -> Table:
        """Создает новую таблицу"""
        name = name.strip()

        if not name:
            raise EmptyTableNameError("Имя таблицы не может быть пустым")

        if not columns:
            raise EmptyColumnsError("Таблица должна содержать хотя бы одну колонку")

        if len(columns) != len(set(columns)):
            raise InvalidColumnNameError("Названия колонок не должны повторяться")

        if name in self._tables:
            raise DuplicateTableError(f"Таблица '{name}' уже существует")

        table = Table(name, columns.copy())
        self._tables[name] = table
        return table

    def list_tables(self) -> list[str]:
        """Возвращает список всех таблиц"""
        return list(self._tables.keys())

    def get_table(self, name: str) -> Table | None:
        """Возвращает таблицу по имени"""
        return self._tables.get(name)

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

    def rename_column(self, table_name: str, old_column: str, new_column: str) -> None:
        """Переименовывает колонку"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.rename_column(old_column, new_column)

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

    def update_records_by_indexes(
        self, table_name: str, indexes: list[int], updates: dict[str, Any]
    ) -> int:
        """Обновляет записи по списку индексов"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.update_records_by_indexes(indexes, updates)

    def delete_records(self, table_name: str, **filters: Any) -> int:
        """Удаляет записи по фильтру"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.delete_records(**filters)

    def delete_records_by_indexes(self, table_name: str, indexes: list[int]) -> int:
        """Удаляет записи по списку индексов"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.delete_records_by_indexes(indexes)

    def get_record_by_index(self, table_name: str, index: int) -> tuple[Any, ...]:
        """Возвращает запись по индексу"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.get_record_by_index(index)

    def delete_record_by_index(self, table_name: str, index: int) -> None:
        """Удаляет запись по индексу"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.delete_record_by_index(index)

    def update_record_by_index(
        self, table_name: str, index: int, updates: dict[str, Any]
    ) -> None:
        """Обновляет запись по индексу"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.update_record_by_index(index, updates)

    def sort_records(
        self, table_name: str, column: str, reverse: bool = False
    ) -> list[tuple[Any, ...]]:
        """Сортирует записи в таблице по указанной колонке"""
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.sort_records(column, reverse)
