from pymongo import MongoClient
from datetime import datetime, timezone
import random

MAX_PORTAL_USE_PER_DAY=5

gr1 = ["Ri", "Ta", "Mi", "Tsu", "Ko", "E", "Ma", "Nu", "El", "Ma", "Cron", "Ur"]
gr2 = ["jo", "se", "gar", "cia", "cy", "ril", "le", "de", "lon", "mi"]
gr3 = ["re", "ne", "cha", "to", "na", "dia", "bou", "y", "ne"]
gr4 = ["bri", "gi", "te", "bar", "do"]

def generate_name():
    name = random.choice(gr1)
    if random.randint(0, 10) > 0:
        name += random.choice(gr2)
    if random.randint(0, 4) > 0:
        name += random.choice(gr3)
    if random.randint(0, 2) > 0:
        name += random.choice(gr4)
    return name

creatures = {
    "Axolotl Healer" : {
        "dna1": ["Axolotl"],
        "dna2": [],
        "item": ["Healing Purse"]
    },
    "Bee Bear" : {
        "dna1": ["Bee"],
        "dna2": ["Bear"],
        "item": []
    },
    "Brain Fly" : {
        "dna1": ["Bug"],
        "dna2": [],
        "item": ["Brain"]
    },
    "Chameleon Sniper" : {
        "dna1": ["Chameleon"],
        "dna2": [],
        "item": ["Weapon"]
    },
    "Compost Dragon" : {
        "dna1": ["Dragon"],
        "dna2": [],
        "item": ["Soil"]
    },
    "Deathweaver" : {
        "dna1": ["Spider"],
        "dna2": ["Goblin"],
        "item": []
    },
    "Elephantopus" : {
        "dna1": ["Elephant"],
        "dna2": ["Octopus"],
        "item": []
    },
    "Explosive Toad" : {
        "dna1": ["Frog"],
        "dna2": [],
        "item": ["Explosive"]
    },
    "Ferret Bomber" : {
        "dna1": ["Ferret"],
        "dna2": [],
        "item": ["Explosive"]
    },
    "Giraffodile" : {
        "dna1": ["Giraffe"],
        "dna2": ["Crocodile"],
        "item": []
    },
    "Goblin Werewolf" : {
        "dna1": ["Goblin"],
        "dna2": ["Wolf"],
        "item": []
    },
    "Gorillion" : {
        "dna1": ["Gorilla"],
        "dna2": ["Lion"],
        "item": []
    },
    "Grave Robber" : {
        "dna1": ["Bird"],
        "dna2": [],
        "item": ["Soil"]
    },
    "Harpy Mother" : {
        "dna1": ["Bird"],
        "dna2": ["Human"],
        "item": []
    },
    "Kangasaurus Rex" : {
        "dna1": ["Kangaroo"],
        "dna2": ["Dinosaur"],
        "item": []
    },
    "Killer Bee" : {
        "dna1": ["Bee"],
        "dna2": [],
        "item": ["Weapon"]
    },
    "Lone Yeti" : {
        "dna1": ["Human"],
        "dna2": [],
        "item": ["Snow"]
    },
    "Luchataur" : {
        "dna1": ["Bull"],
        "dna2": [],
        "item": ["Mask"]
    },
    "Mysterious Mermaid" : {
        "dna1": ["Fish"],
        "dna2": ["Human"],
        "item": []
    },
    "Plated Scorpion" : {
        "dna1": ["Scorpion"],
        "dna2": [],
        "item": ["Ore"]
    },
    "Rhino Turtle" : {
        "dna1": ["Rhinoceros"],
        "dna2": ["Turtle"],
        "item": []
    },
    "Shark Dog" : {
        "dna1": ["Shark"],
        "dna2": ["Dog"],
        "item": []
    },
    "Sharky Crab-Dog-Mummypus" : {
        "dna1": ["Monster"],
        "dna2": ["Shark", "Crustacean", "Dog", "Octopus"],
        "item": []
    },
    "Shield Bugs" : {
        "dna1": ["Bug"],
        "dna2": [],
        "item": ["Ore"]
    },
    "Snail Hydra" : {
        "dna1": ["Snail"],
        "dna2": ["Snake", "Snail"],
        "item": []
    },
    "Snail Thrower" : {
        "dna1": ["Goblin"],
        "dna2": ["Snail"],
        "item": []
    },
    "Spider Owl" : {
        "dna1": ["Spider"],
        "dna2": ["Bird"],
        "item": []
    },
    "Strange Barrel" : {
        "dna1": ["Monster"],
        "dna2": [],
        "item": ["Ore"]
    },
    "Tiger Squirrel" : {
        "dna1": ["Tiger"],
        "dna2": ["Squirrel"],
        "item": []
    },
    "Turbo Bug" : {
        "dna1": ["Bug"],
        "dna2": [],
        "item": ["Boosters"]
    },
    "Tusked Extorter" : {
        "dna1": ["Elephant"],
        "dna2": ["Human"],
        "item": []
    },
    "Urchin Hurler" : {
        "dna1": ["Urchin"],
        "dna2": [],
        "item": ["Weapon"]
    },
    "Bugserker" : {
        "dna1": ["Bug"],
        "dna2": [],
        "item": ["Weapon"]
    },
    "Count Draculeech" : {
        "dna1": ["Leech"],
        "dna2": ["Human"],
        "item": []
    },
    "Creep from the Deep" : {
        "dna1": ["Ghost", "Monster"],
        "dna2": ["Jellyfish"],
        "item": []
    },
    "Ferret Pacifier" : {
        "dna1": ["Ferret"],
        "dna2": ["Human"],
        "item": []
    },
    "Froblin Instigator" : {
        "dna1": ["Goblin"],
        "dna2": ["Frog"],
        "item": []
    },
    "Goreagle Alpha" : {
        "dna1": ["Gorilla"],
        "dna2": ["Bird"],
        "item": []
    },
    "Hamster Lion" : {
        "dna1": ["Hamster"],
        "dna2": ["Lion"],
        "item": []
    },
    "Hungry Hungry Hamster" : {
        "dna1": ["Hamster"],
        "dna2": [],
        "item": ["Food"]
    },
    "Hyenix" : {
        "dna1": ["Hyena"],
        "dna2": ["Pheonix"],
        "item": []
    },
    "Majestic Manticore" : {
        "dna1": ["Scorpion"],
        "dna2": ["Lion"],
        "item": []
    },
    "The Lurker" : {
        "dna1": ["Turtle"],
        "dna2": ["Crocodile"],
        "item": []
    },
    "Turf the Surfer" : {
        "dna1": ["Bull"],
        "dna2": ["Crustacean"],
        "item": []
    },
    "Slugapult" : {
        "dna1": ["Snail"],
        "dna2": [],
        "item": ["Explosive", "Ore"]
    },
    "Mindbug Bug" : {
        "dna1": ["Octopus"],
        "dna2": ["Bug"],
        "item": ["Brain"]
    },
    "Ratomancer" : {
        "dna1": ["Mouse"],
        "dna2": ["Ghost"],
        "item": []
    },
    "Ram Hopper" : {
        "dna1": ["Sheep"],
        "dna2": ["Bug"],
        "item": []
    },
    "Boar-Zooka" : {
        "dna1": ["Pig"],
        "dna2": [],
        "item": ["Boosters", "Explosive"]
    },
    "Sluggernaut" : {
        "dna1": ["Snail"],
        "dna2": [],
        "item": ["Ore"]
    }
}

def pick_dna():
    creature_name = random.choice(list(creatures.keys()))
    creature = creatures[creature_name]
    dnas = list(creature['dna1'])
    if creature['dna2'] != None:
        dnas.extend(creature['dna2'])
    if len(dnas) > 0:
        return random.choice(dnas)
    else:
        return None

def pick_item():
    creature_name = random.choice(list(creatures.keys()))
    creature = creatures[creature_name]
    if creature['item'] != None and len(creature['item']) > 0:
        return random.choice(creature['item'])
    else:
        None

def explore(id: str, mongodb: MongoClient):
    db = mongodb["exploration"]
    collection = db["players"]
    player = collection.find_one({ 'player_id': id })
    if player == None:
        player = {
            'player_id': id,
            'dna': [],
            'items': [],
            'creatures': {}
        }
        collection.insert_one(player)
    if 'portal_usage_left' not in player:
        player['portal_usage_left'] = MAX_PORTAL_USE_PER_DAY
    if 'date' not in player:
        player['date'] = datetime.now(tz=timezone.utc)
    
    if player['date'].date() != datetime.now(tz=timezone.utc).date():
        player['date'] = datetime.now(tz=timezone.utc)
        player['portal_usage_left'] = MAX_PORTAL_USE_PER_DAY
    if player['portal_usage_left'] == 0:
        return {
            "message" : "You cannot use the portal anymore today"
        }
    player['portal_usage_left'] -= 1
    new_dna = []
    new_item = []
    if random.randint(0, 100) < 80:
        dna = pick_dna()
        if dna != None:
            new_dna.append(dna)
            player['dna'].append(dna)
    if random.randint(0, 100) < 50:
        dna = pick_dna()
        if dna != None:
            new_dna.append(dna)
            player['dna'].append(dna)
    if random.randint(0, 100) < 25:
        item = pick_item()
        if item != None:
            new_item.append(item)
            player['items'].append(item)

    collection.update_one({ 'player_id': id }, { '$set': player })
    return {
        "message": f"You use the portal and arrive on planet {generate_name()}...",
        'portal_usage_left': player['portal_usage_left'],
        'items': new_item,
        'dna': new_dna
    }

def get_inventory(id: str, mongodb: MongoClient):
    db = mongodb["exploration"]
    collection = db["players"]
    player = collection.find_one({ 'player_id': id })
    if player == None:
        return {
            "message": "You have no inventory"
        }
    return {
        "message": "Here is your inventory",
        "items": player['items'],
        "dna": player['dna'],
        "creatures": player['creatures']
    }

def try_merge(id: str, mongodb: MongoClient, item1: str, item2: str):
    db = mongodb["exploration"]
    collection = db["players"]
    player = collection.find_one({ 'player_id': id })
    
    if player == None:
        return {
            "message": "You don't have required items or DNA available"
        }
    try:
        player['dna'].remove(item1)
    except:
        try:
            player['items'].remove(item1)
        except:
            return {
                "message": f"You don't have {item1} available"
            }
    try:
        player['dna'].remove(item2)
    except:
        try:
            player['items'].remove(item2)
        except:
            return {
                "message": f"You don't have {item2} available"
            }

    for name, creature in creatures.items():
        if (item1 in creature['dna1'] and (item2 in creature['dna2'] or item2 in creature['item'])) \
            or ((item1 in creature['dna2'] or item1 in creature['item']) and item2 in creature['dna1']):
            if name not in player['creatures']:
                player['creatures'][name] = 1
            else:
                player['creatures'][name] += 1
            collection.update_one({ 'player_id': id }, { '$set': player })
            return {
                "message": f"You use {item1}'s DNA and {item2}'s DNA and... Wow ! You have created a {name}"
            }
    
    # Not found, consume items
    collection.update_one({ 'player_id': id }, { '$set': player })
    return {
        "message": f"You use {item1}'s DNA and {item2}'s DNA and... Oops ! Nothing happened"
    }
