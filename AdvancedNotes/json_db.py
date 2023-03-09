"""
The class that manages the Json database
Notes are loaded at the moment the program starts.
During the operation of the program, interaction with them is carried out as with a regular dictionary.
After user's commands this dictionary changes and instantly dumps in the .json file
"""

from datetime import datetime
from pydantic import ValidationError

from databases.json_impl.json_view import Groups, Group, Note
from databases.json_impl.config import JSON_PATH
from databases.idatabase import DataBase
from settings.colors import ERROR_COLOR, TEXT_COLOR, GROUP_COLOR

from exceptions.json_errors import *


class DataBaseJsonImp(DataBase):
    """ Object for storing notes """
    __notes = Groups(groups_list=[])

    @staticmethod
    def _change_groups_list(function):
        """ Decorator for accessing the list of groups """
        def wrapper(*args):
            notes = DataBaseJsonImp.__get_notes()
            DataBaseJsonImp.__set_notes(function(notes, *args))
            DataBaseJsonImp.__dump_json()

        return wrapper

    @staticmethod
    def _change_notes_list(function):
        """ Decorator for finding and changing a group """
        def wrapper(*args):
            notes = DataBaseJsonImp.__get_notes()
            for index, group in enumerate(notes.groups_list):
                if group.name == args[0]:
                    notes.groups_list[index] = function(group, *args)
                    break
            DataBaseJsonImp.__set_notes(notes)
            DataBaseJsonImp.__dump_json()

        return wrapper

    # loads notes data in list from the .json file
    @staticmethod
    def load_json() -> None:
        """ Loads json dictionary in the program from .json file """
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
        """ Dumps json dictionary from the program to the .json file """
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
    def get_attached_group_notes(group_name: str) -> list[str]:
        """
        :return: List of notes of attached group for the autocompletion
        :return: An empty list if the attached group is empty
        """
        for group in DataBaseJsonImp.__get_notes().groups_list:
            if group.name == group_name:
                return [f"{note.title}" for note in group.notes_list]
        return []

    @staticmethod
    def get_grouped_notes() -> list[str]:
        """
        :return: List of notes divided into groups.

        Cosmetic method.
        Group names are highlighted.
        Empty groups are highlighted too.
        """
        column = []
        for group in DataBaseJsonImp.__get_notes().groups_list:
            # Painting group name
            column.append(f"{GROUP_COLOR}Group: {group.name}{TEXT_COLOR}")
            # if group is empty
            if not DataBaseJsonImp.select_attached_group_notes(group.name):
                column.append(ERROR_COLOR + "empty group" + TEXT_COLOR)
            else:
                for note in group.notes_list:
                    column.append(f"{note.note_id + 1}. {note.title}")
            column.append("")
        return column[:-1]

    @staticmethod
    def get_all_groups() -> list[str]:
        """
        :return: List of all groups from database
        """
        return [f"{index + 1}. {group.name}" for index, group in enumerate(DataBaseJsonImp.__get_notes().groups_list)]

    @staticmethod
    def get_all_notes() -> list[str]:
        """
        :return: List of all notes from database
        """
        return [note.title for group in DataBaseJsonImp.__get_notes().groups_list for note in group.notes_list]

    @staticmethod
    def check_group(group_name: str) -> int:
        """ Check existence of the group in database """
        for group in DataBaseJsonImp.__get_notes().groups_list:
            if group.name == group_name:
                return 1
        return 0

    @staticmethod
    def check_note(note_name: str) -> Note | int:
        """ Check existence of the note in database """
        for group in DataBaseJsonImp.__get_notes().groups_list:
            for note in group.notes_list:
                if note.title == note_name:
                    return note
        return 0

    @staticmethod
    @_change_groups_list
    def create_group(notes: Groups, group_name: str) -> Groups:
        notes.groups_list.append(Group(name=group_name, notes_list=[]))
        return notes

    @staticmethod
    @_change_groups_list
    def delete_group(notes: Groups, group_name: str) -> Groups:
        for index, group in enumerate(notes.groups_list):
            if group.name == group_name:
                notes.groups_list.pop(index)
                return notes

    @staticmethod
    @_change_notes_list
    def rename_group(group: Group, _: str, new_group_name: str) -> Group:
        group.name = new_group_name
        return group

    @staticmethod
    @_change_notes_list
    def create_note(group: Group, group_name: str, title: str, text: str) -> Group:
        group.notes_list.append(Note(
            note_id=len(DataBaseJsonImp.select_attached_group_notes(group_name)),
            creation_date=datetime.now(),
            last_change_date=datetime.now(),
            title=title,
            text=text,
        ))
        return group

    @staticmethod
    @_change_notes_list
    def update_note(group: Group, _: str, note_id: int, text: str, option: str) -> Group:
        """
        :param option: 'title' or 'text'
        Change note title or text according the option
        """
        if option == "title":
            group.notes_list[note_id].title = text
        else:
            group.notes_list[note_id].text = text
        group.notes_list[note_id].last_change_date = datetime.now()
        return group

    @staticmethod
    @_change_notes_list
    def delete_note(group: Group, _: str, note_id: int) -> Group:
        group.notes_list.pop(note_id)
        return group

