from datetime import datetime
from pymongo.collection import Collection

from databases.idatabase import DataBase
from databases.note import Note

from settings.colors import GROUP_COLOR, TEXT_COLOR, ERROR_COLOR


class DataBaseMongoImp(DataBase):
    connection: Collection = None

    @staticmethod
    def _get_groups_collection(function):
        def wrapper(*args):
            collection = DataBaseMongoImp.connection["groups"]
            return function(*args, collection)

        return wrapper

    @staticmethod
    def _get_notes_collection(function):
        def wrapper(*args):
            collection = DataBaseMongoImp.connection["notes"]
            return function(*args, collection)

        return wrapper

    @staticmethod
    def set_connection(connection) -> None:
        DataBaseMongoImp.connection = connection

    @staticmethod
    def get_grouped_notes() -> list[str]:
        column = []
        for group_title in DataBaseMongoImp.get_all_groups():
            # Painting group name
            column.append(f"{GROUP_COLOR}Group: {group_title}{TEXT_COLOR}")
            # if group is empty
            if note_titles := DataBaseMongoImp.get_attached_group_notes(group_title):
                for index, title in enumerate(note_titles, start=1):
                    column.append(f"{index}. {title}")
            else:
                column.append(ERROR_COLOR + "empty group" + TEXT_COLOR)
            column.append("")
        return column[:-1]

    @staticmethod
    @_get_notes_collection
    def get_attached_group_notes(group_title: str, collection: Collection | None) -> list[str]:
        return collection.distinct("title", {"group_id": group_title})

    @staticmethod
    @_get_groups_collection
    def get_all_groups(collection: Collection) -> list[str]:
        return collection.distinct("title")

    @staticmethod
    @_get_notes_collection
    def get_all_notes(collection: Collection) -> list[str]:
        return collection.distinct("title")

    @staticmethod
    @_get_groups_collection
    def check_group(group_title: str, collection: Collection) -> int | None:
        if collection.find_one({"id": group_title}):
            return 1

    @staticmethod
    @_get_notes_collection
    def check_note(note_title: str, collection: Collection) -> Note | None:
        if note_data := collection.find_one({"id": note_title}):
            return Note(
                note_id=note_title,
                title=note_title,
                text=note_data["text"],
                creation_date=note_data["creation_date"],
                last_change_date=note_data["last_change_date"]
            )

    @staticmethod
    @_get_groups_collection
    def create_group(group_title: str, collection: Collection | None) -> None:
        collection.insert_one({"id": group_title, "title": group_title})

    @staticmethod
    @_get_groups_collection
    @_get_notes_collection
    def update_group(group_title: str, new_group_title: str, groups: Collection, notes: Collection) -> None:
        groups.update_one({"id": group_title}, {"$set": {"title": new_group_title, "id": new_group_title}})
        notes.update_many({"group_id": group_title}, {"$set": {"group_id": new_group_title}})

    @staticmethod
    @_get_groups_collection
    @_get_notes_collection
    def delete_group(group_title: str, groups: Collection, notes: Collection) -> None:
        groups.delete_one({"id": group_title})
        notes.delete_many({"group_id": group_title})

    @staticmethod
    @_get_notes_collection
    def create_note(group_title: str, note_title: str, note_text: str, collection: Collection) -> None:
        collection.insert_one(
            {
                "id": note_title,
                "group_id": group_title,
                "title": note_title,
                "text": note_text,
                "creation_date": datetime.now(),
                "last_change_date": datetime.now()
            }
        )

    @staticmethod
    @_get_notes_collection
    def update_note(note_title: str, text: str, option: str, collection: Collection) -> None:
        if option == "title":
            collection.update_one({"id": note_title}, {"$set": {"title": text, "id": text}})
        else:
            collection.update_one({"id": note_title}, {"$set": {"text": text}})

    @staticmethod
    @_get_notes_collection
    def delete_note(note_title: str, collection: Collection) -> None:
        collection.delete_one({"id": note_title})
