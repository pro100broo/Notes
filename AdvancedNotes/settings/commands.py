"""
User's commands management
"""


MAIN_COMMANDS = {
    "commands": [
        " help",
        " cls",
        " help groups",
        " help notes",
        " settings (temporary disabled)",
        " quit"
    ],
    "descriptions": [
        "Open main commands",
        "Clear terminal screen",
        "Open groups navigation commands",
        "Open notes navigation commands",
        "Open program settings",
        "Exit the program"
    ]
}


GROUPS_COMMANDS = {
    "commands": [
        " NAVIGATION COMMANDS:",
        " groups",
        " group select 'group_name'",
        "",
        " EDITING COMMANDS:",
        " group create 'new_group_name'",
        " group delete 'group_name'",
        " group edit title 'group_name'"
    ],
    "descriptions": [
        "",
        "Show list of groups",
        "Select a group",
        "",
        "",
        "Create a new group",
        "Rename selected group",
        "Delete existing group"

    ]
}


NOTES_COMMANDS = {
    "commands": [
        " NAVIGATION COMMANDS:",
        " note select 'note_title'",
        " notes",
        " note read",
        " note info",
        "",
        " EDITING COMMANDS:",
        " note create 'new_note_title'",
        " note edit title",
        " note edit text",
        " note delete",
        " note copy"
    ],
    "descriptions": [
        "",
        "Select a note",
        "Show a list of notes",
        "Show text",
        "Show info",
        "",
        "",
        "Create a note",
        "Edit note title",
        "Edit note text",
        "Delete a note",
        "Copy selected note in the clipboard",
        "Move note to the other group"
    ]
}

