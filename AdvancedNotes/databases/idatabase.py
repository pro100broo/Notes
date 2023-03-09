"""
Database Abstract class
I am planning to add a support of the PostgreSQL and MongoDB with a common interface
"""


from abc import ABC, abstractmethod
from .json_impl.json_view import Note, Group, Groups


class DataBase(ABC):

    @staticmethod
    @abstractmethod
    def get_attached_group_notes(group_name: str) -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_grouped_notes() -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_all_groups() -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_all_notes() -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def check_group(group_name: str) -> int:
        pass

    @staticmethod
    @abstractmethod
    def check_note(note_name: str) -> Note | int:
        pass

    @staticmethod
    @abstractmethod
    def create_group(notes: Groups, group_name: str) -> Groups:
        pass

    @staticmethod
    @abstractmethod
    def delete_group(notes: Groups, group_name: str) -> Groups:
        pass

    @staticmethod
    @abstractmethod
    def rename_group(group: Group, _: str, new_group_name: str) -> Group:
        pass

    @staticmethod
    @abstractmethod
    def create_note(group: Group, group_name: str, title: str, text: str) -> Group:
        pass

    @staticmethod
    @abstractmethod
    def update_note(group: Group, _: str, note_id: int, text: str, option: str) -> Group:
        pass

    @staticmethod
    @abstractmethod
    def delete_note(group: Group, _: str, note_id: int) -> Group:
        pass

