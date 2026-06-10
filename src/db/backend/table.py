from typing import Any
from .errors import InvalidRecordLengthError, ColumnNotFoundError, RecordNotFoundError


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

    def delete_records_by_indexes(self, indexes: list[int]) -> int:
        """Удаляет записи по списку индексов"""
        deleted = 0
        for idx in sorted(indexes, reverse=True):
            if 0 <= idx < len(self.records):
                del self.records[idx]
                deleted += 1
        return deleted

    def sort_records(self, column: str, reverse: bool = False) -> list[tuple[Any, ...]]:
        """Сортирует записи по указанной колонке"""
        if column not in self.columns:
            raise ColumnNotFoundError(f"Колонка '{column}' не найдена")

        col_idx = self.columns.index(column)
        return sorted(self.records, key=lambda record: record[col_idx], reverse=reverse)
