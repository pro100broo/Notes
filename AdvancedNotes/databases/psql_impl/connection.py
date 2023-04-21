import psycopg2

from psycopg2.errors import UndefinedTable, OperationalError
from colorama import Fore, Style

from .psql_exceptions import TablesDoesNotExists
from .config import PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASSWORD, PSQL_DATA_BASE_NAME


class PSQLConnection:
    def check_connection(self):
        try:
            connection = psycopg2.connect(
                host=PSQL_HOST,
                port=PSQL_PORT,
                user=PSQL_USER,
                password=PSQL_PASSWORD,
                database=PSQL_DATA_BASE_NAME
            )
            self.tables_checker(connection)
        except OperationalError:
            print(f"\n{Fore.LIGHTYELLOW_EX}Invalid connection parameters or database doesn't exists")
        except TablesDoesNotExists:

            print(f"\n{Fore.LIGHTYELLOW_EX}DataBase tables do not exists or damaged"
                  f"\nCould I initialize new tables in it to start work [Y/N]?"
                  f"\nAttention! Existing tables will be overwritten:{Style.RESET_ALL}")

            match input("\n>>> ").lower():
                case "y":
                    self.create_tables(connection)
                    print("\nTables was successfully created! You should reboot the program")
                case "n":
                    pass
        else:
            return connection

    @staticmethod
    def tables_checker(connection) -> None:
        """
        Makes multiple queries against tables in the database to check their existence
        """
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM notes")
                cursor.execute("SELECT * FROM groups")
                cursor.execute("SELECT * FROM groups_notes")
            except UndefinedTable:
                connection.rollback()
                raise TablesDoesNotExists

    @staticmethod
    def create_tables(connection) -> None:
        """
        Creates tables via following patterns. Also fill 'groups' table with a default group 'Home'
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE groups("
                "id varchar(30) primary key, "
                "title varchar(30)"
                ")"
            )
            cursor.execute(
                "CREATE TABLE notes("
                "id varchar(30) primary key,"
                "title varchar(30),"
                "text text,"
                "creation_date timestamp,"
                "last_change_date timestamp"
                ")"
            )
            cursor.execute(
                "CREATE TABLE groups_notes("
                "group_id varchar(30) references groups(id),"
                "note_id varchar(30) references notes(id)"
                ")"
            )

            cursor.execute("INSERT INTO groups(id, title) VALUES('Home', 'Home')")

            connection.commit()


