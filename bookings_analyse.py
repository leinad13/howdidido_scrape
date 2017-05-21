## Uses - dominate - https://github.com/Knio/dominate
## Uses - "python-dateutil" - https://pypi.python.org/pypi/python-dateutil
## Uses - "tinydb" - https://pypi.python.org/pypi/tinydb
## Uses - "tinydb-serialization" - https://pypi.python.org/pypi/tinydb-serialization/

### TODO - Add an hour or workout how to read the UTC to local time somehow...

import dominate
from dominate.tags import *

from datetime import datetime
from dateutil.parser import parse
from tinydb import TinyDB, Query
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware

# Custom Serializer to store datetime object in tinydb
class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')

## register the custom serializer
serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDateTime')

### Path to the json databases
db_path = "C:/Users/dan.cook/tmp/howdidido_scrape/hdidido/spiders"
import os
db_list = list()
### Get list of db files
for file in os.listdir(db_path):
    if file.endswith(".json"):
        db_list.append(file)

for db_name in db_list: # Loop through all recorded competitions - by json file
    db = TinyDB(db_path+'/'+db_name, storage=serialization) # Create db object
    tables = db.tables() # Get list of tables
    snapshots = list() # New list to store the datetime objects

    # Read the all tables in the database, each represents a snapshot of the booking sheet
    for atable in tables:
        if atable != "_default":
            snapshot = parse(atable.replace("_","")) # Parse the string date into a datetime object
            snapshots.append(snapshot)

    snapshots.sort() # Sort the tables by date
    snapshot_data = list() # List to store the grouped snapshot data

    for snapshot_date in snapshots:
        snapshot_date_str = snapshot_date.strftime('%Y_%m_%dT%H_%M_%S')
        db_table = db.table(snapshot_date_str)
        allrows = db_table.all()
        group = sorted(set(map(lambda x:x['bookingtime'], allrows)))
        groupedrows = [[y for y in allrows if y['bookingtime']==x] for x in group]
        if len(groupedrows) > 0: # Check for 0 length results
            snapshot_data.append(groupedrows)

    snapshot_count = len(snapshot_data)
    print('Competition '+db_name.replace(".json","")+' has '+str(snapshot_count)+' snapshots')

    if snapshot_count > 1: # No point in comparing if only 1 snapshot
        i = 0
        for teetimes in snapshot_data:
            if i > 0:
                match = set(teetimes).intersection(snapshot_data[i-1])
            i = i+1
