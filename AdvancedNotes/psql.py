from datetime import datetime

from view import View
from databases.idatabase import DataBase
from databases.note import Note
from settings.colors import GROUP_COLOR, TEXT_COLOR, ERROR_COLOR

class DataBasePSQLImp(DataBase):
    connection = None

    @staticmethod
    def _update_foreign_keys(function):
        def wrapper(*args):
            with DataBasePSQLImp.connection.cursor() as cursor:
                try:
                    cursor.execute("ALTER TABLE groups_notes DROP CONSTRAINT groups_notes_group_id_fkey")
                    cursor.execute("ALTER TABLE groups_notes DROP CONSTRAINT groups_notes_note_id_fkey")

                    function(*args)

                    cursor.execute(
                        "ALTER TABLE groups_notes ADD CONSTRAINT groups_notes_group_id_fkey FOREIGN KEY (group_id) "
                        "REFERENCES groups(id)"
                    )

                    cursor.execute(
                        "ALTER TABLE groups_notes ADD CONSTRAINT groups_notes_note_id_fkey FOREIGN KEY (note_id) "
                        "REFERENCES notes(id)"
                    )

                except Exception as error:
                    DataBasePSQLImp.connection.rollback()
                    view.print_error_message(str(error))

        return wrapper

    @staticmethod
    def _make_transaction(function):
        def wrapper(*args):
            with DataBasePSQLImp.connection.cursor() as cursor:
                try:
                    result = function(*args, cursor)
                except Exception as error:
                    DataBasePSQLImp.connection.rollback()
                    view.print_error_message(str(error))
                else:
                    DataBasePSQLImp.connection.commit()
                    return result
        return wrapper

    @staticmethod
    def get_grouped_notes() -> list[str]:
        column = []
        for group_title in DataBasePSQLImp.get_all_groups():
            # Painting group name
            column.append(f"{GROUP_COLOR}Group: {group_title}{TEXT_COLOR}")
            # if group is empty
            if note_titles := DataBasePSQLImp.get_attached_group_notes(group_title):
                for index, title in enumerate(note_titles, start=1):
                    column.append(f"{index}. {title}")
            else:
                column.append(ERROR_COLOR + "empty group" + TEXT_COLOR)
            column.append("")
        return column[:-1]

    @staticmethod
    def set_connection(connection) -> None:
        DataBasePSQLImp.connection = connection

    @staticmethod
    @_make_transaction
    def get_attached_group_notes(group_title: str, cursor) -> list[str]:
        cursor.execute(
            f"SELECT title FROM notes WHERE id IN (SELECT note_id FROM groups_notes WHERE group_id='{group_title}')"
        )

        if note_titles := cursor.fetchall():
            return [title[0] for title in note_titles]

    @staticmethod
    @_make_transaction
    def get_all_groups(cursor) -> list[str]:
        cursor.execute("select title FROM groups")
        return [title[0] for title in cursor.fetchall()]

    @staticmethod
    @_make_transaction
    def get_all_notes(cursor) -> list[str]:
        cursor.execute("select title FROM notes")
        return [title[0] for title in cursor.fetchall()]

    @staticmethod
    @_make_transaction
    def check_group(group_title: str, cursor) -> int | None:
        cursor.execute(f"select COUNT(*) from groups WHERE id='{group_title}'")
        if cursor.fetchall()[0][0]:
            return 1

    @staticmethod
    @_make_transaction
    def check_note(note_title: str, cursor) -> Note | None:
        cursor.execute(f"select id, text, creation_date, last_change_date from notes WHERE title='{note_title}'")
        if note_data := cursor.fetchall():
            return Note(
                note_id=note_data[0][0],
                title=note_title,
                text=note_data[0][1],
                creation_date=note_data[0][2],
                last_change_date=note_data[0][3]
            )

    @staticmethod
    @_make_transaction
    def create_group(group_title: str, cursor) -> None:
        cursor.execute(f"INSERT INTO groups(id, title) values(%s, %s)", (group_title, group_title))

    @staticmethod
    @_make_transaction
    @_update_foreign_keys
    def update_group(group_title: str, new_group_title: str, cursor) -> None:
        cursor.execute(
            f"UPDATE groups_notes SET group_id=%s WHERE group_id=%s", (new_group_title, group_title)
        )
        cursor.execute(
            f"UPDATE groups SET id=%s, title=%s WHERE id=%s", (new_group_title, new_group_title, group_title)
        )

    @staticmethod
    @_make_transaction
    @_update_foreign_keys
    def delete_group(group_title: str, cursor) -> None:
        cursor.execute(
            f"DELETE FROM notes WHERE id IN (SELECT note_id FROM groups_notes WHERE group_id='{group_title}')"
        )
        cursor.execute(f"DELETE FROM groups_notes WHERE group_id='{group_title}'")
        cursor.execute(f"DELETE FROM groups WHERE id='{group_title}'")

    @staticmethod
    @_make_transaction
    def create_note(group_title: str, note_title: str, note_text: str, cursor) -> None:
        cursor.execute(
            "INSERT INTO notes (id, title, text, creation_date, last_change_date) values(%s, %s, %s, %s, %s)",
            (note_title, note_title, note_text, datetime.now(), datetime.now())
        )

        cursor.execute("INSERT INTO groups_notes (group_id, note_id) values(%s, %s)", (group_title, note_title))

    @staticmethod
    @_make_transaction
    @_update_foreign_keys
    def update_note(note_title: int, text: str, option: str, cursor) -> None:
        if option == "title":
            cursor.execute(f"UPDATE notes SET id=%s, title=%s WHERE title=%s", (text, text, note_title))
            cursor.execute(f"UPDATE groups_notes SET note_id=%s WHERE note_id=%s", (text, note_title))
            DataBasePSQLImp.connection.commit()
        else:
            cursor.execute(f"UPDATE notes SET text=%s WHERE title=%s", (text, note_title))


    @staticmethod
    @_make_transaction
    def delete_note(note_title: int, cursor) -> None:
        cursor.execute(f"DELETE FROM notes WHERE title={note_title}")
        cursor.execute(f"DELETE FROM groups_notes WHERE note_id={note_title}")


view = View()
