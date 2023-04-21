from abc import ABC, abstractmethod
from .note import Note


class DataBase(ABC):
    """ Database Interface """
    @staticmethod
    @abstractmethod
    def get_grouped_notes() -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_attached_group_notes(group_title: str) -> list[str]:
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
    def check_group(group_title) -> int | None:
        pass

    @staticmethod
    @abstractmethod
    def check_note(note_title: str) -> Note | None:
        pass

    @staticmethod
    @abstractmethod
    def create_group(group_title: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def update_group(group_title: str, new_group_title: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def delete_group(group_title: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def create_note(group_title: str, note_title: str, note_text: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def update_note(note_title: str, text: str, option: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def delete_note(note_title: str) -> None:
        pass

