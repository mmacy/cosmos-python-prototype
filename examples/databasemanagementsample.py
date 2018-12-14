import os

from azure.cosmos import CosmosClient, HTTPFailure

AUTH_URI = os.environ["ACCOUNT_URI"]
AUTH_KEY = os.environ["ACCOUNT_KEY"]
TEST_DB_NAME = "testdatabasemanagementdb"


class DatabaseManagement:
    @staticmethod
    def find_database(client, id):
        print("1. Query for database")
        try:
            database = client.get_database(id)
            print(f"Database with id {database.id} was found")
        except HTTPFailure:
            print(f"Database with id {id} was not found")

    @staticmethod
    def create_database(client, id):
        print("2. Create database")
        try:
            database = client.create_database(id, fail_if_exists=True)
            print(f"A database with id {database.id} created")
        except HTTPFailure as e:
            if e.status_code == 409:
                print(f"A database with id {id} already exists")
            else:
                raise

    @staticmethod
    def read_database(client, id):
        print("3. Get a database by id")
        database = client.get_database(id)

    @staticmethod
    def list_databases(client):
        print("4. Listing all databases on an account")
        databases = client.list_databases()
        for database in databases:
            print(database.id)

    @staticmethod
    def delete_database(client, id):
        print("5. Delete database")
        try:
            client.delete_database(id)
        except HTTPFailure as e:
            if e.status_code == 404:
                print(f"A database with id {id} does not exist")
            else:
                raise


client = CosmosClient(AUTH_URI, AUTH_KEY)
DatabaseManagement.find_database(client, TEST_DB_NAME)
DatabaseManagement.create_database(client, TEST_DB_NAME)
DatabaseManagement.read_database(client, TEST_DB_NAME)
DatabaseManagement.list_databases(client)
DatabaseManagement.delete_database(client, TEST_DB_NAME)

