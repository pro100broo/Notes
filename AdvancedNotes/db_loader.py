"""
You can choose database before launching program.
choose_db() function checks existence of the chosen database
"""

import os

from view import View
from psql import DataBasePSQLImp

from databases.idatabase import DataBase

from databases.psql_impl.config import PSQL_USER, PSQL_DATA_BASE_NAME

from databases.psql_impl.connection import PSQLConnection
from databases.mongodb_impl.connection import MongoDBConnection

from mongo import DataBaseMongoImp


def choose_db() -> DataBase:
    print("How can I load your notes [mongo/psql]?")
    match input(">>> ").lower():
        case "mongo":
            test_connection = MongoDBConnection()
            if test_connection.check_connection() is not None:
                database = DataBaseMongoImp()
                database.set_connection(test_connection.check_connection())
                os.system('cls' if os.name == 'nt' else 'clear')
                View.print_status_message(f"Successfully connected to MongoDB 'mynotes'")

                return database

        case "psql":
            test_connection = PSQLConnection()
            if connection := test_connection.check_connection():
                database = DataBasePSQLImp()
                database.set_connection(connection)
                os.system('cls' if os.name == 'nt' else 'clear')
                View.print_status_message(
                    f"Successfully connected to database '{PSQL_DATA_BASE_NAME}' as user: {PSQL_USER}"
                )

                return database
        case _:
            View.print_error_message("Invalid input!")


View()
