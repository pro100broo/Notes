import os

from view import View
from settings.colors import *
from settings.config import LINE_SYMBOL
from dotenv import load_dotenv


def create_json_file() -> None:
    """
    Method calls before the first launching of the app.
    Automatically generates an empty .json file with basic content
    """
    view.print_text("\nProgram keeps data in the json format."
                    "\nCould I create .json file in the chosen path [Y/N]?"
                    "\nAttention! Existing .json file will be overwritten:")
    match input(LINE_SYMBOL).lower():
        case "y":
            try:
                with open(os.environ.get("JSON_PATH"), "w") as file:
                    # Initialisation of the database view
                    file.write('{"groups_list": [{"title": "Home", "notes_list": []}]}')
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


def fill_empty_json_file() -> None:
    """
    Method calls if json file is empty.
    Automatically fills an empty .json file with basic content
    """
    view.print_error_message("\nIt looks like your .json file is empty!"
                             "\nCould I initialize database in it to start work [Y/N]?"
                             "\nAttention! Existing .json file will be overwritten:")
    match input(f"{TEXT_COLOR}{LINE_SYMBOL}").lower():
        case "y":
            with open(os.environ.get("JSON_PATH"), "w") as file:
                file.write('{"groups_list": [{"title": "Home", "notes_list": []}]}')
                view.print_status_message("\nJson file was successfully updated! You should reboot the program")


view = View()
load_dotenv()
