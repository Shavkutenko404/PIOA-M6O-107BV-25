from abc import ABC, abstractmethod
from typing import Any


class Database(ABC):
    """Абстрактный интерфейс базы данных"""

    @abstractmethod
    def create_table(self, table_name: str, columns: list[str]) -> None:
        """Создаёт таблицу"""
        pass

    @abstractmethod
    def list_tables(self) -> list[str]:
        """Возвращает список всех таблиц"""
        pass

    @abstractmethod
    def get_columns(self, table_name: str) -> list[str]:
        """Возвращает список колонок таблицы"""
        pass

    @abstractmethod
    def insert_record(self, table_name: str, record: tuple[Any, ...]) -> None:
        """Добавляет запись"""
        pass

    @abstractmethod
    def select_records(self, table_name: str, **filters: Any) -> list[tuple[Any, ...]]:
        """Возвращает записи по фильтру"""
        pass

    @abstractmethod
    def update_records(
        self, table_name: str, updates: dict[str, Any], **filters: Any
    ) -> int:
        """Обновляет записи по фильтру"""
        pass

    @abstractmethod
    def delete_records(self, table_name: str, **filters: Any) -> int:
        """Удаляет записи по фильтру"""
        pass

    @abstractmethod
    def clear_table(self, table_name: str) -> None:
        """Очищает все записи в таблице"""
        pass

    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы"""
        pass

    @abstractmethod
    def rename_table(self, old_name: str, new_name: str) -> None:
        """Переименовывает таблицу (бросает исключение при ошибке)"""
        pass

    @abstractmethod
    def rename_column(self, table_name: str, old_column: str, new_column: str) -> None:
        """Переименовывает колонку (бросает исключение при ошибке)"""
        pass

    @abstractmethod
    def delete_table(self, table_name: str) -> None:
        """Удаляет таблицу полностью"""
        pass

    @abstractmethod
    def get_all_info(self) -> dict[str, tuple[list[str], int]]:
        """Возвращает информацию обо всех таблицах"""
        pass

    @abstractmethod
    def sort_records(
        self, table_name: str, column: str, reverse: bool = False
    ) -> list[tuple[Any, ...]]:
        """Сортирует записи по указанной колонке"""
        pass
