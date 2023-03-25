"""
Main application class. Manages all main processes of the program.
User's commands handling processed in the -while- loop.
Validation errors handling processed in the decorators.
To access a group of notes or individual notes and change/read them,
you need to pin them with the 'select' command.
Application supports commands autocompletion and multiline text editor.
Navigation in autocompletion and text redactor with keyboard arrows.
"""

import os
import pyperclip
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard

from view import View
from databases.json_db import DataBaseJsonImp
from custom_input import CustomInput
from databases.json_impl.json_view import Note
from databases.json_impl.config import JSON_PATH
from settings.commands import MAIN_COMMANDS, GROUPS_COMMANDS, NOTES_COMMANDS
from settings.colors import TEXT_COLOR, STATUS_COLOR
from settings.config import LINE_SYMBOL

from exceptions.json_errors import *


class App:
    __attached_group = None
    __attached_note = None

    @staticmethod
    def _screen_cleaner(function):
        """ Cosmetic decorator. Cleans app screen before and after using a text editor """
        def wrapper(title):
            os.system('cls' if os.name == 'nt' else 'clear')
            if status_message := function(title):
                os.system('cls' if os.name == 'nt' else 'clear')
                view.print_status_message(status_message)
        return wrapper

    @staticmethod
    def _delete_confirmation(function):
        def wrapper(title):
            view.print_error_message(f"\nAre you sure to delete this [Y/N]?{TEXT_COLOR}")
            suggestion = input(LINE_SYMBOL).lower()
            if suggestion == "y":
                function(title)
            else:
                view.print_status_message("\nThe deletion was rejected")
        return wrapper

    @staticmethod
    def _empty_title(function):
        def wrapper(title):
            if not title:
                view.print_error_message("Title shouldn't be empty")
            else:
                function(title)
        return wrapper

    @staticmethod
    def _wrong_group_title(function):
        def wrapper(*args):
            """
            :param args: args[0] -> The name of the group
            """
            if not database.check_group(args[0]):
                view.print_error_message(f"Group title: '{args[0]}' doesn't exists")
            else:
                function(*args)
        return wrapper

    @staticmethod
    def _wrong_note_title(function):
        def wrapper(note_title):
            if not database.get_attached_group_notes(group_title := App.get_attached_group()):
                view.print_error_message(f"Group: '{group_title}' is empty")
            elif not (database.check_note(note_title)):
                view.print_error_message(f"Note title: '{note_title}' doesn't exists")
            else:
                function(note_title)
        return wrapper

    @staticmethod
    def _group_title_duplication(function):
        def wrapper(group_title):
            if not database.check_group(group_title):
                function(group_title)
            else:
                view.print_error_message(f"Group title: '{group_title}' already exists")
        return wrapper

    @staticmethod
    def _note_title_duplication(function):
        def wrapper(note_title):
            if not database.check_note(note_title):
                function(note_title)
            else:
                view.print_error_message(f"Note title: '{note_title}' already exists")
        return wrapper

    @staticmethod
    def _group_not_selected(function):
        def wrapper(title):
            if App.get_attached_group():
                function(title)
            else:
                view.print_error_message(f"Group doesn't selected")
        return wrapper

    @staticmethod
    def _note_not_selected(function):
        def wrapper(*args):
            """ This decorator calls the following function with 'Note' type object instead of 'str' type """
            if note := App.get_attached_note():
                function(*args, note) if args else function(note)
            else:
                view.print_error_message(f"Note doesn't selected")
        return wrapper

    @staticmethod
    def main_loop() -> int:
        view.print_text("\nWelcome to MyNotes!\nEnter 'help' option to show context menu")
        while True:
            try:
                view.print_attached_group_and_note(App.get_attached_group(), App.get_attached_note())
                command = input_handler.command_input(database.get_all_groups(),
                                                      database.get_attached_group_notes(App.get_attached_group()))
                match command.split():

                    # Main menu commands
                    case "help", :
                        view.print_table("Main commands:", MAIN_COMMANDS["commands"], MAIN_COMMANDS["descriptions"])
                    case "cls", :
                        os.system('cls' if os.name == 'nt' else 'clear')
                    case "help", "groups":
                        view.print_table("Groups commands:", GROUPS_COMMANDS["commands"],
                                         GROUPS_COMMANDS["descriptions"])
                    case "help", "notes":
                        view.print_table("Notes commands:", NOTES_COMMANDS["commands"], NOTES_COMMANDS["descriptions"])
                    case "quit", :
                        return 0

                    # Groups navigation commands
                    case "groups", :
                        view.print_table_with_pointer("Groups", database.get_all_groups(), App.get_attached_group())
                    case "group", "select", *group_title:
                        App.group_select(" ".join(group_title))

                    # Groups editing commands
                    case "group", "create", *group_title:
                        App.group_create(" ".join(group_title))

                    case "group", "rename", *group_title:
                        App.group_rename(" ".join(group_title))

                    case "group", "delete", *group_title:
                        App.group_delete(" ".join(group_title))

                    # Notes navigation commands
                    case "notes", :
                        view.print_table_with_pointer("Notes", database.get_grouped_notes(),
                                                      note.title if (note := App.get_attached_note()) else "")

                    case "note", "select", *note_title:
                        App.note_select(" ".join(note_title))

                    case "note", "read":
                        App.note_read()

                    case "note", "info":
                        App.note_info()

                    case "note", "copy":
                        App.note_copy()

                    # Notes editing commands
                    case "note", "create", *note_title:
                        App.note_create(" ".join(note_title))

                    case "note", "edit", "text":
                        App.note_edit_text()

                    case "note", "edit", "title":
                        App.note_edit_title()

                    case "note", "delete":
                        App.note_delete()

                    case _:
                        view.print_error_message("Wrong command, try again")

            # Exceptions catching
            except JsonDumpingError:
                view.print_error_message("Can't dump .json file")
            except JsonReadingError:
                view.print_error_message("Can't load .json file. Check it's integrity")
            except KeyboardInterrupt:
                view.print_error_message("Ctrl+C hotkey was intercepted. Use 'quit' option to close the program!")

    @staticmethod
    def __set_attached_group(group_title: str | None) -> None:
        App.__attached_group = group_title

    @staticmethod
    def get_attached_group() -> str:
        return App.__attached_group

    @staticmethod
    def __set_attached_note(note: Note | None) -> None:
        App.__attached_note = note

    @staticmethod
    def get_attached_note() -> Note | None:
        return App.__attached_note

    @staticmethod
    @_empty_title
    @_wrong_group_title
    def group_select(group_title) -> None:
        App.__set_attached_group(group_title)
        App.__set_attached_note(None)

    @staticmethod
    @_empty_title
    @_group_title_duplication
    def group_create(group_title: str) -> None:
        database.create_group(group_title)
        App.__set_attached_group(group_title)
        App.__set_attached_note(None)
        view.print_status_message(f"\nNew group: {group_title} was successfully created")

    @staticmethod
    @_empty_title
    @_wrong_group_title
    @_screen_cleaner
    def group_rename(group_title: str) -> str:
        if new_group_title := App.title_input(group_title):
            database.rename_group(group_title, new_group_title)
            App.__set_attached_group(new_group_title)
            return f"\nGroup title was successfully changed: {group_title} -> {new_group_title}"

    @staticmethod
    @_empty_title
    @_wrong_group_title
    @_delete_confirmation
    def group_delete(group_title: str) -> None:
        database.delete_group(group_title)
        App.__set_attached_group(None)
        view.print_status_message(f"\nGroup: '{group_title}' was successfully deleted")

    @staticmethod
    @_empty_title
    @_group_not_selected
    @_wrong_note_title
    def note_select(note_title: str) -> None:
        App.__set_attached_note(database.check_note(note_title))

    @staticmethod
    @_note_not_selected
    def note_read(note: Note) -> None:
        view.print_note(note.title, note.text)

    @staticmethod
    @_note_not_selected
    def note_info(note: Note) -> None:
        view.print_note_info(note)

    @staticmethod
    @_note_not_selected
    def note_copy(note: Note) -> None:
        """ Copies text of the attached note in the system clipboard """
        view.print_text(f"\n{STATUS_COLOR}Note's text was copied in the global clipboard!!!")
        pyperclip.copy(note.text)

    @staticmethod
    @_empty_title
    @_group_not_selected
    @_note_title_duplication
    @_screen_cleaner
    def note_create(note_title) -> str:
        note_text = input_handler.text_editor()
        database.create_note(App.get_attached_group(), note_title, note_text)
        App.note_select(note_title)
        return f"Note: '{note_title}' was successfully created!"

    @staticmethod
    @_note_not_selected
    @_screen_cleaner
    def note_edit_text(note: Note) -> str:
        new_text = input_handler.text_editor(buffered_text=note.text)
        database.update_note(App.get_attached_group(), note.note_id, new_text, "text")
        return "Note text was successfully changed!"

    @staticmethod
    @_note_not_selected
    @_screen_cleaner
    def note_edit_title(note: Note) -> str:
        if new_note_title := App.title_input(note.title):
            database.update_note(App.get_attached_group(), note.note_id, new_note_title, "title")
            return "Note title was successfully changed!"

    @staticmethod
    @_note_not_selected
    @_delete_confirmation
    def note_delete(note: Note) -> None:
        database.delete_note(App.get_attached_group(), note.note_id)
        App.__set_attached_note(None)
        view.print_status_message(f"Note: '{note.title}' was successfully deleted!")

    @staticmethod
    def title_input(title: str) -> str:
        """ Method for validation note or group of notes title input """
        if not (new_title := input_handler.text_editor(buffered_text=title, multiline=False)):
            os.system('cls' if os.name == 'nt' else 'clear')
            view.print_error_message("title shouldn't be empty")
        else:
            return new_title

    @staticmethod
    def create_json_file() -> None:
        """
        Method calls before the first launching of the app.
        Automatically generates an empty .json file with basic content
        """
        view.print_text("\nProgram keeps data in the json format."
                        "\nCould I create .json file in the chosen path [Y/N]?"
                        "\nAttention! Existing .json file will be overwritten:")
        action = input(LINE_SYMBOL).lower()
        match action:
            case "y":
                try:
                    with open(JSON_PATH, "w") as file:
                        # Initialisation of the database view
                        file.write('{"groups_list": [{"name": "Home", "notes_list": []}]}')
                except PermissionError:
                    view.print_error_message("Your operating system refused to create the file."
                                             f"\nChange the settings or create an empty{STATUS_COLOR} mynotes.json"
                                             f"{TEXT_COLOR} file in the specified path")
                else:
                    view.print_status_message("\nJson file was successfully created! You should reboot the program")
            case "n":
                pass
            case _:
                view.print_error_message("Wrong command, try again")

    @staticmethod
    def fill_empty_json_file() -> None:
        """
        Method calls if json file is empty.
        Automatically fills an empty .json file with basic content
        """
        view.print_error_message("\nIt looks like your .json file is empty!"
                                 "\nCould I initialize database in it to start work [Y/N]?"
                                 "\nAttention! Existing .json file will be overwritten:")
        action = input(f"{TEXT_COLOR}{LINE_SYMBOL}").lower()
        match action:
            case "y":
                with open(JSON_PATH, "w") as file:
                    file.write('{"groups_list": [{"name": "Home", "notes_list": []}]}')
                    view.print_status_message("\nJson file was successfully updated! You should reboot the program")
            case "n":
                pass


if __name__ == "__main__":
    input_handler = CustomInput()
    view = View()
    app_buffer = PyperclipClipboard()
    App()

    # Launching errors handling
    try:
        database = DataBaseJsonImp()
        database.load_json()
    except JsonLoadingError:
        view.print_error_message(f"\nCan't find .json file in {JSON_PATH}")
        App.create_json_file()
    except EmptyJsonFileError:
        App.fill_empty_json_file()
    except JsonReadingError:
        view.print_error_message("Can't load .json file. Check it's integrity")
    else:
        App.main_loop()
