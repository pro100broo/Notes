"""
Class for custom text input.
Includes realization of text editor and commands auto-completion
"""

import prompt_toolkit
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard

# Constants for enabling/disabling text editor features:
from settings.config import AUTO_COMPLETION, TOOLBAR, LINE_SYMBOL


class CustomInput:

    # System clipboard
    clipboard = PyperclipClipboard()

    # List of groups and notes for the autocompletion
    __groups = []
    __notes = []

    @staticmethod
    def __set_groups(groups: list[str]) -> None:
        CustomInput.__groups = groups

    @staticmethod
    def __get_groups() -> dict[str: None]:
        return {group_name[3:]: None for group_name in CustomInput.__groups}

    @staticmethod
    def __set_notes(notes: list[str]) -> None:
        CustomInput.__notes = notes

    @staticmethod
    def __get_notes() -> dict[str: None]:
        return {note_name: None for note_name in CustomInput.__notes}

    @staticmethod
    def command_input(groups: list[str], notes: list[str]) -> str:
        """
        Method for input commands with autocompletion
        :param groups: The list of the groups from the database
        :param notes: The list of the attached group notes
        :return: text of user's command
        """
        CustomInput.__set_groups(groups)
        CustomInput.__set_notes(notes)
        return prompt_toolkit.prompt(LINE_SYMBOL,
                                     completer=NestedCompleter.from_nested_dict(CustomInput.__get_hints_dict()))

    @staticmethod
    def text_editor(buffered_text="", multiline=True) -> str:
        """
        :param buffered_text: title/text of the attached note or title of the attached group of notes, default: ""
        :param multiline: bool (True for the note text input, False for the note/group of notes title input)
        :return: trimmed user's text

        When launching text editor, buffered_text will be automatically inserted the buffer of text editor and
        system clipboard

        """
        CustomInput.clipboard.set_text(buffered_text)
        text = prompt_toolkit.prompt(
            LINE_SYMBOL,
            prompt_continuation=LINE_SYMBOL,
            clipboard=CustomInput.clipboard,
            multiline=multiline,
            bottom_toolbar=CustomInput.__get_toolbar(multiline) if TOOLBAR else False,
            rprompt='100 character per string limit!' if multiline else '30 character limit!',
            default=buffered_text
        )
        return "\n".join([row[:100] for row in text.split("\n")]) if multiline else text[:30]

    @staticmethod
    def __get_toolbar(multiline: bool) -> str:
        """
        :param multiline: bool
        :return: Bottom toolbar text of the text editor. Editor 'exit' hotkey depends on the multiline parameter

        Can be disabled with the 'TOOLBAR' constant
        """
        return f"Text editor supports Emacs hot keys:" \
               f"\n[ctrl + w] -> cut   [alt + w] -> copy   [ctrl + y] -> paste   " \
               f"{'[esc + enter]' if multiline else '[enter]'} -> end input" \
               f"\n[ctrl + c] -> exit without changes (temporary crutch)"

    @staticmethod
    def __get_hints_dict() -> dict:
        """
        :return: Dictionary with autocompletion tips. Notes and group titles change after corresponding database changes

        Can be disabled with the 'AUTO_COMPLETION' constant
        """
        return {
                "help": {
                    "groups": None,
                    "notes": None,
                },
                "cls": None,
                "quit": None,
                "groups": None,
                "notes": None,
                "group": {
                    "create": None,
                    "rename": CustomInput.__get_groups(),
                    "delete": CustomInput.__get_groups(),
                    "select": CustomInput.__get_groups(),
                },
                "note": {
                    "read": None,
                    "info": None,
                    "delete": None,
                    "copy": None,
                    "create": None,
                    "edit": {
                        "text": None,
                        "title": None,
                    },
                    "select": CustomInput.__get_notes(),
                    }
            } if AUTO_COMPLETION else {}
