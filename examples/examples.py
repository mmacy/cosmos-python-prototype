from azure.cosmos import HTTPFailure, CosmosClient, Container, Database

# All interaction with Cosmos DB starts with an instance of the CosmosClient
import os
url = os.environ['ACCOUNT_HOST']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, key)

test_database_name = 'testDatabase'
test_container_name = 'testContainer'

# Create a database
db = client.create_database(id=test_database_name, fail_if_exists=False)
try:
    db.create_container(id=test_container_name)
except HTTPFailure as e:
    if e.status_code != 409:
        raise
    db.get_container(test_container_name)

# Retrieve a container by using known database and container names, then
# insert an item:
container = Container(client.client_context, database=test_database_name, id=test_container_name)
container.upsert_item({
    'id': 'something',
    'value': 'else'
})

# Retrieve a container by walking down resource hierarchy (client->databases->containers), then
# insert an item.
database = client.get_database(test_database_name)
container = database.get_container(test_container_name)
container.upsert_item({
    'id': 'something',
    'value': 'new'
})

# Once you have a container, you can query items within it:
items = list(container.query_items(query='SELECT * FROM root r WHERE r.id="something"'))

# Enumerate the items you've retrieved with your query:
import json
for item in items:
    print(json.dumps(item, indent=True))

# It should be (almost) free to ask the length of a query
# if len(items) > 4711: # TODO: NYI (should use header to get this info to make it O(1))
#    print('Big number')

# Insert new items by defining a dict and calling Container.upsert_item
for i in range(1, 10):
    container.upsert_item(dict(
        id=f'item{i}',
        firstName='David',
        lastName='Smith'
        )
    )

# Modify an existing item in the container
item = items[0]
item['firstName'] = 'Some Other Name'
updated_item = container.upsert_item(item) # ISSUE: do we update the item "in place" for system properties and  headers?

# Retrieve the properties of a database
properties = database.properties
print(json.dumps(properties))

# Modify the properties of an existing container
# This example sets the default time to live (TTL) for items in the container to 10 seconds
# An item in container are deleted when the TTL expires since it was last edited
database.set_container_properties(container, default_ttl=10)
container = database.get_container(container)
print(container)
