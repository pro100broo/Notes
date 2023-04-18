"""
The class that manages the Json database
Notes are loaded at the moment the program starts.
During the operation of the program, interaction with them is carried out as with a regular dictionary.
After user's commands this dictionary changes and instantly dumps in the .json file
"""

from datetime import datetime
from pydantic import ValidationError

from databases.json_impl.json_view import Groups, Group, Note
from databases.idatabase import DataBase
from settings.colors import ERROR_COLOR, TEXT_COLOR, GROUP_COLOR
from settings.config import JSON_PATH

from exceptions.json_errors import *


class DataBaseJsonImp(DataBase):
    """ Object for storing notes """
    __notes = Groups(groups_list=[])

    @staticmethod
    def _get_groups(function):
        def wrapper(*args):
            DataBaseJsonImp.__set_notes(function(*args, DataBaseJsonImp.__get_notes()))
            DataBaseJsonImp.__dump_json()

        return wrapper

    @staticmethod
    def _find_group_by_group_name(function):
        def wrapper(*args):
            notes = DataBaseJsonImp.__get_notes()
            for index, group in enumerate(notes.groups_list):
                if group.title == args[0]:
                    notes.groups_list[index] = function(*args, group)
                    break
            DataBaseJsonImp.__set_notes(notes)
            DataBaseJsonImp.__dump_json()

        return wrapper

    # loads notes data in list from the .json file
    @staticmethod
    def load_json() -> None:
        try:
            with open(JSON_PATH, "r") as file:
                # If .json file is empty, the following exception raises
                if not (text := file.read()):
                    raise EmptyJsonFileError
                DataBaseJsonImp.__set_notes(Groups.parse_raw(text))
        except FileNotFoundError:
            raise JsonLoadingError
        except ValidationError:
            raise JsonReadingError

    # saves notes data in the .json file
    @staticmethod
    def __dump_json() -> None:
        try:
            with open(JSON_PATH, "w") as file:
                file.write(DataBaseJsonImp.__get_notes().json())
        except FileNotFoundError | ValidationError:
            raise JsonDumpingError

    @staticmethod
    def __set_notes(notes: Groups) -> None:
        DataBaseJsonImp.__notes = notes

    @staticmethod
    def __get_notes() -> Groups:
        return DataBaseJsonImp.__notes

    @staticmethod
    def get_attached_group_notes(group_title: str) -> list[str]:
        """
        :return: List of notes of attached group for the autocompletion
        :return: An empty list if the attached group is empty
        """
        for group in DataBaseJsonImp.__get_notes().groups_list:
            if group.title == group_title:
                return [f"{note.title}" for note in group.notes_list]

    @staticmethod
    def get_grouped_notes() -> list[str]:
        """
        Cosmetic method.
        Group names are highlighted.
        Empty groups are highlighted too.

        :return: List of notes divided into groups.
        """
        column = []
        for group in DataBaseJsonImp.__get_notes().groups_list:
            # Painting group name
            column.append(f"{GROUP_COLOR}Group: {group.title}{TEXT_COLOR}")
            # if group is empty
            if DataBaseJsonImp.get_attached_group_notes(group.title):
                for index, note in enumerate(group.notes_list, start=1):
                    column.append(f"{index}. {note.title}")
            else:
                column.append(ERROR_COLOR + "empty group" + TEXT_COLOR)
            column.append("")
        return column[:-1]

    @staticmethod
    def get_all_groups() -> list[str]:
        """
        :return: List of all groups from database
        """
        return [group.title for group in DataBaseJsonImp.__get_notes().groups_list]

    @staticmethod
    def get_all_notes() -> list[str]:
        """
        :return: List of all notes from database
        """
        return [note.title for group in DataBaseJsonImp.__get_notes().groups_list for note in group.notes_list]

    @staticmethod
    def check_group(group_title: str) -> int:
        for group in DataBaseJsonImp.__get_notes().groups_list:
            if group.title == group_title:
                return 1

    @staticmethod
    def check_note(note_title: str) -> Note | int:
        for group in DataBaseJsonImp.__get_notes().groups_list:
            for note in group.notes_list:
                if note.note_id == note_title:
                    return note

    @staticmethod
    @_get_groups
    def create_group(group_title: str, notes: Groups) -> Groups:
        notes.groups_list.append(Group(title=group_title, notes_list=[]))
        return notes

    @staticmethod
    @_find_group_by_group_name
    def update_group(group_title: str, new_group_title: str, group: Group) -> Group:
        group.title = new_group_title
        return group

    @staticmethod
    @_get_groups
    def delete_group(group_title: str, notes: Groups) -> Groups:
        for index, group in enumerate(notes.groups_list):
            if group.title == group_title:
                notes.groups_list.pop(index)
                return notes

    @staticmethod
    @_find_group_by_group_name
    def create_note(group_title: str, note_title: str, note_text: str, group: Group) -> Group:
        group.notes_list.append(Note(
            note_id=note_title,
            creation_date=datetime.now(),
            last_change_date=datetime.now(),
            title=note_title,
            text=note_text,
        ))
        return group

    @staticmethod
    @_change_group
    def update_note(group_title: str, note_id: int, note_text: str, option: str, group: Group) -> Group:
        if option == "title":
            group.notes_list[note_id].title = note_text
            group.notes_list[note_id].note_id = note_text
        else:
            group.notes_list[note_id].text = note_text
        group.notes_list[note_id].last_change_date = datetime.now()
        return group

    @staticmethod
    @_change_group
    def delete_note(group_title: str, note_id: int, group: Group) -> Group:
        for index, note in enumerate(group.notes_list):
            if note.note_id == note_id:
                group.notes_list.pop(index)
                return group



