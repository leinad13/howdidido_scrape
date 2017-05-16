## This is a file used to do some code testing with tinydb

from tinydb import TinyDB, Query
from datetime import datetime
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware

# CUstom Serializer to store datetime object in tinydb
class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')

## register the custom serializer
serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDateTime')

## Get current working directory for db path
import os
cwd = os.getcwd()

db = TinyDB(cwd+'/test_db.json', storage=serialization)

## Insert
'''
db.insert({
    'time': datetime.now(),
    'player1': 'Trevor Somebody',
    'player2': 'Alan Nobody',
    'player3': 'John Anybody',
    'player4': 'Frank Noname'
    })
'''

## Query
queryObj = Query()
results = db.search((queryObj.player1.matches('Trevor.*')) | queryObj.player2.matches('Trevor.*'))

print(results[1]['player1'])
