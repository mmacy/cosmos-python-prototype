import os
import datetime

from azure.cosmos import CosmosClient, HTTPFailure, PartitionKey

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos DB account -
#    https://docs.microsoft.com/azure/cosmos-db/how-to-manage-database-account#create-a-database-account
#
# 2. Microsoft Azure Cosmos DB PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Database resource for Azure Cosmos DB
#
# 1. Query for Database (QueryDatabases)
#
# 2. Create Database (CreateDatabase)
#
# 3. Get a Database by its Id property (ReadDatabase)
#
# 4. List all Database resources on an account (ReadDatabases)
#
# 5. Delete a Database given its Id property (DeleteDatabase)
# ----------------------------------------------------------------------------------------------------------


class DocumentManagement:
    @staticmethod
    def create_documents(container):
        print("Creating Documents")

        # Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
        # This can be saved as JSON as-is, without converting into rows/columns.
        sales_order = DocumentManagement.GetSalesOrder("SalesOrder1")
        try:
            container.create_item(sales_order)
        except HTTPFailure as e:
            if e.status_code == 409:
                print('Document with id "{}" already exists'.format(sales_order["id"]))
        # As your app evolves, let's say your object has a new schema. You can insert SalesOrderV2 objects without any
        # changes to the database tier.
        sales_order2 = DocumentManagement.GetSalesOrderV2("SalesOrder2")
        try:
            container.create_item(sales_order2)
        except HTTPFailure as e:
            if e.status_code == 409:
                print("Document with id {} already exists".format(sales_order["id"]))

    @staticmethod
    def read_document(container, id):
        print("\n1.2 Reading Document by Id\n")

        # Note that Reads require a partition key to be specified. This can be skipped if your collection is not
        # partitioned i.e. does not have a partition key definition during creation.
        response = container.get_item(id, partition_key="PO18009186470")

        print("Document read by Id {0}".format(id))
        print("Account Number: {0}".format(response.get("account_number")))

    @staticmethod
    def read_documents(container):
        print("\n1.3 - Reading all documents in a container\n")

        # NOTE: Use MaxItemCount on Options to control how many documents come back per trip from the server.
        #       It's important to handle throttling whenever you are doing operations such as this that might
        #       result in a 429 (throttled request).
        documentlist = list(container.list_items(max_item_count=1))

        print("Found {0} documents".format(len(documentlist)))

        for doc in documentlist:
            print("Document Id: {0}".format(doc.get("id")))

    @staticmethod
    def GetSalesOrder(document_id):
        order1 = {
            "id": document_id,
            "account_number": "Account1",
            "purchase_order_number": "PO18009186470",
            "order_date": datetime.date(2005, 1, 10).strftime("%c"),
            "subtotal": 419.4589,
            "tax_amount": 12.5838,
            "freight": 472.3108,
            "total_due": 985.018,
            "items": [
                {
                    "order_qty": 1,
                    "product_id": 100,
                    "unit_price": 418.4589,
                    "line_price": 418.4589,
                }
            ],
            "ttl": 60 * 60 * 24 * 30,
        }

        return order1

    @staticmethod
    def GetSalesOrderV2(document_id):
        # Notice new fields have been added to the sales order
        order2 = {
            "id": document_id,
            "account_number": "Account2",
            "purchase_order_number": "PO15428132599",
            "order_date": datetime.date(2005, 7, 11).strftime("%c"),
            "due_date": datetime.date(2005, 7, 21).strftime("%c"),
            "shipped_date": datetime.date(2005, 7, 15).strftime("%c"),
            "subtotal": 6107.0820,
            "tax_amount": 586.1203,
            "freight": 183.1626,
            "discount_amt": 1982.872,
            "total_due": 4893.3929,
            "items": [
                {
                    "order_qty": 3,
                    "product_code": "A-123",  # Notice how in item details we no longer reference a ProductId.
                    "product_name": "Product 1",  # Instead, we've decided to de-normalize our schema and include
                    "currency_symbol": "$",  # the Product details relevant to the Order on the Order directly.
                    "currency_code": "USD",  # This is a typical refactor that happens in the course of an application
                    "unit_price": 17.1,  # that would have previously required schema changes, data migrations, etc.
                    "line_price": 5.7,
                }
            ],
            "ttl": 60 * 60 * 24 * 30,
        }

        return order2


def run_sample():
    AUTH_URI = os.environ.get("ACCOUNT_URI")
    AUTH_KEY = os.environ.get("ACCOUNT_KEY")
    DATABASE_ID = "testdocumentmanagementdb"
    CONTAINER_ID = "testdocumentmanagementcollection"

    client = CosmosClient(AUTH_URI, AUTH_KEY)
    database = client.create_database(id=DATABASE_ID)
    partition_key = PartitionKey(path="/purchase_order_number")
    try:
        container = database.create_container(
            id=CONTAINER_ID, partition_key=partition_key
        )
        print(f'Container with id "{CONTAINER_ID}"" created')
    except HTTPFailure as e:
        if e.status_code == 409:
            print(f"Container with id {CONTAINER_ID} already exists")
            container = database.get_container(container=CONTAINER_ID)
        else:
            raise

    DocumentManagement.create_documents(container)
    DocumentManagement.read_document(container, "SalesOrder1")
    DocumentManagement.read_documents(container)

    client.delete_database(database=DATABASE_ID)
    print("\nrun_sample done")


if __name__ == "__main__":
    run_sample()
