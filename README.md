# Azure Cosmos DB SDK for Python

The Azure Cosmos DB SDK for Python provides support for working with Cosmos DB resources like databases, containers, and items. Use the Python SDK to create, read, update, and delete data using the API of your choice: SQL, MongoDB, Gremlin, Cassandra, and Azure Table.

## Prerequisites

### Required

* Azure subscription - [Create a free account][azure_sub]
* Azure [Cosmos DB account][cosmos_account]
* [Python 3.7+][python]

## Installation

The installation of the Azure Cosmos DB Python SDK involves installing packages via [pip][pip], optionally within a virtual environment via [venv][venv].

### Configure a virtual environment (optional)

Although not required, we recommend that you install the SDK within a Python virtual environment. By using a virtual environment, you can keep your your base system and Azure SDK environments isolated.

Execute the following commands to configure and then enter a virtual environment with [venv][venv]:

```Bash
python3 -m venv azure-cosmosdb-sdk-environment
source azure-cosmosdb-sdk-environment/bin/activate
```

### Install the SDK

Install the Azure Cosmos DB SDK for Python with [pip][pip]:

```Bash
pip install git+https://github.com/johanste/azure-cosmos-python.git@ux git+https://github.com/johanste/azure-cosmos-python-prototype.git@master
```

## Authentication

Interaction with Cosmos DB starts with an instance of the **CosmosClient** class. To create the **CosmosClient** object, supply your Cosmos DB account's URI and one of its account keys to the **CosmosClient** constructor.

You can get your account URI and account key in several ways, including with the [Azure CLI][azure_cli] and [Azure portal][azure_portal]. The Bash snippet below retrieves the account URI and its primary master key with the Azure CLI, and exports those values as environment variables.

```Bash
RES_GROUP=<resource-group-name>
ACCT_NAME=<cosmos-db-account-name>

export ACCOUNT_HOST=$(az cosmosdb show --resource-group $RES_GROUP --name $ACCT_NAME --query documentEndpoint --output tsv)
export ACCOUNT_KEY=$(az cosmosdb list-keys --resource-group $RES_GROUP --name $ACCT_NAME --query primaryMasterKey --output tsv)
```

Once you've populated the `ACCOUNT_HOST` and `ACCOUNT_HOST` environment variables, you can create the **CosmosClient**.

```Python
from azure.cosmos import HTTPFailure, CosmosClient, Container, Database

import os
url = os.environ['ACCOUNT_HOST']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, key)
```

## Usage

Once you have an initialized **CosmosClient**, you can interact with the primary resource types in Cosmos DB.

* [Database][cosmos_database]: Each Cosmos DB account contains one or more databases. When you create the database, you specify the API you'd like to use when interacting with it: SQL, MongoDB, Gremlin, Cassandra, or Azure Table.
* [Container][cosmos_container]: Each database contains one or more containers. The container type is determined by the database API (see table below).
* [Item][cosmos_item]: Containers hold one or more items. Items represent different entities depending on the database API (see table below).

**TODO: Link the container and item types to Python classes in API reference. Or remove it if this is too much info.**

| Database API | Container type | Item type |
| ------------ | -------------- | --------- |
| SQL          | Container      | Item |
| Cassandra    | Table          | Row |
| MongoDB      | Collection     | Document |
| Gremlin      | Graph          | Node or Edge |
| Azure Table  | Table          | Item |

For more information on these resources, see [Working with Azure Cosmos databases, containers and items][cosmos_resources].

## Examples

The following sections provide several example code snippets covering some of the most common Comsos DB tasks, including:

* [Create a database and container](#create-a-database-and-container)
* [Get an existing container](#get-an-existing-container)
* [Query the database](#query-the-database)
* [Insert and update data](#insert-and-update-data)
* [Get database properties](#get-database-properties)
* [Modify database properties](#modify-database-properties)

### Create a database and container

After authenticating your **CosmosClient**, you can work with any resource in the account. The code snippet below creates a SQL API database, which is the default when no API is specified when `create_database` is invoked. It also creates a container in the database, into which you can insert items.

```Python
test_database_name = 'testDatabase'
test_container_name = 'testContainer'

database = client.create_database(id=test_database_name, fail_if_exists=False)
try:
    database.create_container(id=test_container_name)
except HTTPFailure as e:
    if e.status_code != 409:
        raise
    database.get_container(test_container_name)
```

The preceding snippet also handles the `HTTPFailure` exception if the container creation failed. For more information on error handling and troubleshooting, see the [Troublshooting](#troubleshooting) section.

### Get an existing container

Get an existing container using a known database and container name, then insert an item:

```Python
client = CosmosClient(url, key)
container = Container(client.client_context, database=test_database_name, id=test_container_name)
container.upsert_item({
    'id': 'something',
    'value': 'else'
})
```

You can also get a container from the database object:

```Python
database = client.get_database(test_database_name)
container = database.get_container(test_container_name)
container.upsert_item({
    'id': 'something',
    'value': 'new'
})
```

### Query the database

Query a container for a list of items:

```Python
database = client.get_database(test_database_name)
container = database.get_container(test_container_name)

# Get a list of items from the container
items = list(container.query_items(query='SELECT * FROM root r WHERE r.id="something"'))

# Enumerate the returned items
import json
for item in items:
    print(json.dumps(item, indent=True))
```

### Insert and update data

Insert items into the container:

```Python
database = client.get_database(test_database_name)
container = database.get_container(test_container_name)

for i in range(1, 10):
    container.upsert_item(dict(
        id=f'item{i}',
        firstName='David',
        lastName='Smith'
        )
    )
```

Update an existing item:

```Python
item = items[0]
item['firstName'] = 'Some Other Name'
updated_item = container.upsert_item(item)
```

### Get database properties

Get and display the properties of a database:

```Python
database = client.get_database(test_database_name)
properties = database.properties
print(json.dumps(properties))
```

### Modify container properties

Certain properties of an existing container can be modified. This example sets the default time to live (TTL) for items in the container to 10 seconds.

```Python
database = client.get_database(test_database_name)
container = database.get_container(test_container_name)
database.set_container_properties(container, default_ttl=10)
```

For more information on TTL, see [Time to Live for Azure Cosmos DB data][cosmos_ttl].

## Troubleshooting

**TODO: Information on errors, exception handling, and anything that SDK users might commonly encounter as they learn and use the SDK.**

```Python
# Snippets for unpacking/handling common errors/exceptions
```

## Next steps

**TODO: Links to other content or SDKs that might be useful, including closely related SDKs for which they might have initially been searching for.**

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview
[cosmos_account]: https://docs.microsoft.com/azure/cosmos-db/account-overview
[cosmos_container]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-containers
[cosmos_database]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-databases
[cosmos_item]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-items
[cosmos_resources]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-containers
[cosmos_ttl]: https://docs.microsoft.com/azure/cosmos-db/time-to-live
[pip]: https://pypi.org/project/pip/
[python]: https://www.python.org/downloads/
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io
