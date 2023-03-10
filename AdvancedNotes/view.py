"""
Class for printing tables and information.
Supports color syntax of errors, event statuses, plain text and table's text
"""

from prettytable import PrettyTable

from databases.json_impl.json_view import Note
from settings.colors import TEXT_COLOR, STATUS_COLOR, ERROR_COLOR, GROUP_COLOR
from settings.config import HORIZONTAL_TABLE_CHAR, JUNCTION_TABLE_CHER


class View:
    """ Table view settings """
    __table = PrettyTable()
    __table.horizontal_char = HORIZONTAL_TABLE_CHAR
    __table.junction_char = JUNCTION_TABLE_CHER
    __table.padding_width = 1

    @staticmethod
    def _print_and_clear(function):
        """
        Decorator for printing the tables:
        1. Calls function changing the presentation of the :class:`View` table
        2. Prints "Menu" label if needed
        3. Prints table
        4. Clear the :class:`View` table parameters and content
        """
        def wrapper(*args):
            function(*args)

            # print menu label
            print(f"\n{args[0]}" if args[0].endswith(":") else "")

            # print tabel
            View.__table.align = "l"
            print(View.__table, end="\n")

            # clear table
            View.__table.clear()
        return wrapper

    @staticmethod
    def print_status_message(message_text: str) -> None:
        print(STATUS_COLOR + message_text)

    @staticmethod
    def print_error_message(message_text: str) -> None:
        print(ERROR_COLOR + message_text)

    @staticmethod
    def print_text(message_text: str) -> None:
        print(TEXT_COLOR + message_text)

    @staticmethod
    def print_note_info(note: Note) -> None:
        number_of_strings = note.text.count("\n") + 1
        print(
            f"\n{GROUP_COLOR}Note:{TEXT_COLOR} '{note.title}'"
            f"\n{GROUP_COLOR}Creation date:{TEXT_COLOR} {note.creation_date:%d.%m.%Y %H:%M:%S}"
            f"\n{GROUP_COLOR}Last changes date:{TEXT_COLOR} {note.last_change_date:%d.%m.%Y %H:%M:%S}"
            f"\n{GROUP_COLOR}Number of strings:{TEXT_COLOR} {number_of_strings}"
            f"\n{GROUP_COLOR}Number of symbols:{TEXT_COLOR} {len(note.text)}"
        )

    @staticmethod
    def print_attached_group_and_note(attached_group_name: str, attached_note: Note) -> None:
        if attached_group_name and attached_note:
            # if group of notes and note are attached
            print(TEXT_COLOR + f"\nAttached group: {GROUP_COLOR + attached_group_name}" +
                  TEXT_COLOR + f" Attached note: {GROUP_COLOR + attached_note.title}")
        elif attached_group_name:
            # if group of notes is attached
            print(TEXT_COLOR + f"\nAttached group: {GROUP_COLOR + attached_group_name}")
        else:
            # if nothing is attached
            print(GROUP_COLOR + "\nNote's group doesn't selected")

    @staticmethod
    @_print_and_clear
    def print_note(title: str, text: str) -> None:
        """ A simple one-column table includes two rows: note title and text """
        View.__table.add_column(title, [text.rstrip()])

    @staticmethod
    @_print_and_clear
    def print_table(_: str, commands: list[str], descriptions: list[str]) -> None:
        """ The two-column table includes the names and descriptions of the commands """
        View.__table.field_names = [" Command", "Description"]
        for command, description in zip([GROUP_COLOR + row + TEXT_COLOR if row.isupper() else row for row in commands],
                                        descriptions):
            View.__table.add_row((command, description))

    @staticmethod
    @_print_and_clear
    def print_table_with_pointer(title: str, text: list[str], pointer: str) -> None:
        """
        The two-column table includes column with titles and column with an arrow title pointer.
        Pointer arrow appears when it's positions is the same as the attached group/note

        :param title: The name of the table (if exists)
        :param text: The list of the titles
        :param pointer: The name of the attached note or group of notes
        """
        View.__table.add_column(title, text)
        View.__table.add_column(
            "Selected",
            [GROUP_COLOR + "<--".center(8, " ") + TEXT_COLOR if pointer and row[3:] == pointer else " " for row in text]
        )

