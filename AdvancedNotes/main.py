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

from view import View
from custom_input import CustomInput
from databases.note import Note
from db_loader import choose_db

from settings.commands import MAIN_COMMANDS, GROUPS_COMMANDS, NOTES_COMMANDS
from settings.colors import TEXT_COLOR, STATUS_COLOR
from settings.config import LINE_SYMBOL


class App:
    __attached_group = None
    __attached_note = None

    @staticmethod
    def _screen_cleaner(function):
        """ Cosmetic decorator. Cleans app screen before and after using a text editor """
        def wrapper(*args):
            os.system('cls' if os.name == 'nt' else 'clear')
            if status_message := function(*args):
                os.system('cls' if os.name == 'nt' else 'clear')
                View.print_status_message(status_message)
        return wrapper

    @staticmethod
    def _delete_confirmation(function):
        def wrapper(title):
            View.print_error_message(f"\nAre you sure to delete this [Y/N]?{TEXT_COLOR}")
            match input(LINE_SYMBOL).lower():
                case "y":
                    function(title)
                case "n":
                    View.print_status_message("\nThe deletion was rejected")
                case _:
                    View.print_error_message("\nInvalid input")
        return wrapper

    @staticmethod
    def _empty_title(function):
        def wrapper(title):
            if title:
                function(title)
            else:
                View.print_error_message("Title shouldn't be empty")

        return wrapper

    @staticmethod
    def _wrong_group_title(function):
        def wrapper(*args):
            """
            :param args: args[0] -> The name of the group
            """
            if database.check_group(args[0]):
                function(*args)
            else:
                View.print_error_message(f"Group title: '{args[0]}' doesn't exists")

        return wrapper

    @staticmethod
    def _wrong_note_title(function):
        def wrapper(note_title):
            if not database.get_attached_group_notes(group_title := App.get_attached_group()):
                View.print_error_message(f"Group: '{group_title}' is empty")
            elif not (database.check_note(note_title)):
                View.print_error_message(f"Note title: '{note_title}' doesn't exists")
            else:
                function(note_title)
        return wrapper

    @staticmethod
    def _group_title_duplication(function):
        def wrapper(group_title):
            if database.check_group(group_title):
                View.print_error_message(f"Group title: '{group_title}' already exists")
            else:
                function(group_title)
        return wrapper

    @staticmethod
    def _note_title_duplication(function):
        def wrapper(note_title):
            if database.check_note(note_title):
                View.print_error_message(f"Note title: '{note_title}' already exists")
            else:
                function(note_title)
        return wrapper

    @staticmethod
    def _title_input(function):
        def wrapper():
            os.system('cls' if os.name == 'nt' else 'clear')
            if new_title := input_handler.text_editor(multiline=False):
                function(new_title)
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                View.print_error_message("title shouldn't be empty")

        return wrapper

    @staticmethod
    def _group_not_selected(function):
        def wrapper(title):
            if App.get_attached_group():
                function(title)
            else:
                View.print_error_message(f"Group doesn't selected")
        return wrapper

    @staticmethod
    def _note_not_selected(function):
        def wrapper():
            if App.get_attached_note():
                function()
            else:
                View.print_error_message(f"Note doesn't selected")
        return wrapper

    @staticmethod
    def _get_note(function):
        def wrapper(*args):
            return function(*args, App.get_attached_note())

        return wrapper

    @staticmethod
    def mainloop() -> int:
        View.print_text("\nWelcome to MyNotes!\nEnter 'help' option to show context menu")
        while True:
            try:
                View.print_attached_group_and_note(App.get_attached_group(), App.get_attached_note())
                command = input_handler.command_input(database.get_all_groups(),
                                                      database.get_attached_group_notes(App.get_attached_group()))
                match command.split():

                    # Main menu commands
                    case "help", :
                        View.print_table("Main commands:", MAIN_COMMANDS["commands"], MAIN_COMMANDS["descriptions"])
                    case "cls", :
                        os.system('cls' if os.name == 'nt' else 'clear')
                    case "help", "groups":
                        View.print_table("Groups commands:", GROUPS_COMMANDS["commands"],
                                         GROUPS_COMMANDS["descriptions"])
                    case "help", "notes":
                        View.print_table("Notes commands:", NOTES_COMMANDS["commands"], NOTES_COMMANDS["descriptions"])
                    case "quit", :
                        return 0

                    # Groups navigation commands
                    case "groups", :
                        View.print_table_with_pointer("Groups", database.get_all_groups(), App.get_attached_group())
                    case "group", "select", *group_title:
                        App.group_select(" ".join(group_title))

                    # Groups editing commands
                    case "group", "create", *group_title:
                        App.group_create(" ".join(group_title))

                    case "group", "edit", "title":
                        App.group_edit_title()

                    case "group", "delete", *group_title:
                        App.group_delete(" ".join(group_title))

                    # Notes navigation commands
                    case "notes", :
                        View.print_table_with_pointer("Notes", database.get_grouped_notes(),
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
                        View.print_error_message("Wrong command, try again")

            except KeyboardInterrupt:
                View.print_error_message("Ctrl+C hotkey was intercepted. Use 'quit' option to close the program!")

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
        View.print_status_message(f"\nNew group: {group_title} was successfully created")

    @staticmethod
    @_title_input
    @_group_not_selected
    @_group_title_duplication
    @_screen_cleaner
    def group_edit_title(new_group_title: str) -> str:
        database.update_group(App.get_attached_group(), new_group_title)
        App.__set_attached_group(new_group_title)
        return f"\nGroup title was successfully changed to '{new_group_title}'"

    @staticmethod
    @_empty_title
    @_wrong_group_title
    @_delete_confirmation
    def group_delete(group_title: str) -> None:
        database.delete_group(group_title)
        App.__set_attached_group(None)
        View.print_status_message(f"\nGroup: '{group_title}' was successfully deleted")

    @staticmethod
    @_empty_title
    @_group_not_selected
    @_wrong_note_title
    def note_select(note_title: str) -> None:
        App.__set_attached_note(database.check_note(note_title))

    @staticmethod
    @_note_not_selected
    @_get_note
    def note_read(note: Note) -> None:
        View.print_note(note.title, note.text)

    @staticmethod
    @_note_not_selected
    @_get_note
    def note_info(note: Note) -> None:
        View.print_note_info(note)

    @staticmethod
    @_note_not_selected
    @_get_note
    def note_copy(note: Note) -> None:
        """ Copies text of the attached note in the system clipboard """
        View.print_text(f"\n{STATUS_COLOR}Note's text was copied in the global clipboard!!!")
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
    @_get_note
    @_screen_cleaner
    def note_edit_text(note: Note) -> str:
        new_text = input_handler.text_editor(buffered_text=note.text)
        database.update_note(note.note_id, new_text, "text")
        return "Note text was successfully changed!"

    @staticmethod
    @_note_not_selected
    @_title_input
    @_note_title_duplication
    @_get_note
    @_screen_cleaner
    def note_edit_title(new_note_title: str, note: Note) -> str:
        database.update_note(note.note_id, new_note_title, "title")
        App.__set_attached_note(database.check_note(new_note_title))
        return "Note title was successfully changed!"

    @staticmethod
    @_note_not_selected
    @_delete_confirmation
    def note_delete(note: Note) -> None:
        database.delete_note(note.note_id)
        App.__set_attached_note(None)
        View.print_status_message(f"Note: '{note.title}' was successfully deleted!")


if __name__ == "__main__":
    if database := choose_db():
        App()
        View()
        input_handler = CustomInput()
        App.mainloop()
