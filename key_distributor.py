from pymongo import MongoClient
from datetime import datetime, timezone

def get_key(id: str, mongodb: MongoClient):
    db = mongodb["steamkeys"]
    collection = db["users"]
    user = collection.find_one({ 'id': id })
    if user != None:
        return user["key"]
    
    
    keyinfoCol = db["info"]
    info = keyinfoCol.find_one({})
    if info == None:
        info = { 'key': 0 }
        keyinfoCol.insert_one(info)

    key_index = info['key']
    #read key from file
    with open("/data/steamkeys/keys.txt", "r") as f:
        content = f.read()
        keys = content.splitlines()
        if key_index >= len(keys):
            return "No more keys available"
        key = keys[key_index]
        if key == "":
            return "No more keys available"
        key_index += 1
        info['key'] = key_index
        keyinfoCol.update_one({}, { '$set': info })


    user = {
        'id': id,
        'key': key,
        'timestamp': datetime.now(timezone.utc)
    }
    collection.insert_one(user)

    return key