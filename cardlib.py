from Levenshtein import ratio

FirstContact=[
   "Axolotl Healer",
   "Bee Bear",
   "Brain Fly",
   "Chameleon Sniper",
   "Compost Dragon",
   "Deathweaver",
   "Elephantopus",
   "Explosive Toad",
   "Ferret Bomber",
   "Giraffodile",
   "Goblin Werewolf",
   "Gorillion",
   "Grave Robber",
   "Harpy Mother",
   "Kangasaurus Rex",
   "Killer Bee",
   "Lone Yeti",
   "Luchataur",
   "Mysterious Mermaid",
   "Plated Scorpion",
   "Rhino Turtle",
   "Shark Dog",
   "Shield Bugs",
   "Snail Hydra",
   "Snail Thrower",
   "Spider Owl",
   "Strange Barrel",
   "Tiger Squirrel",
   "Turbo Bug",
   "Tusked Extorter",
   "Urchin Hurler",
]

NewCreatures=[
   "Bugserker",
   "Count Draculeech",
   "Creep From The Deep",
   "Ferret Pacifier",
   "Froblin Instigator",
   "Goreagle Alpha",
   "Hamster Lion",
   "Hungry Hungry Hamster",
   "Hyenix",
   "Majestic Manticore",
   "The Lurker",
   "Turf The Surfer"
]

Promos=[
   "Slugapult",
   "Mindbug Bug",
   "Ratomancer",
   "Ram Hopper",
   "Boar-zooka",
   "Sluggernaut",
]

AllCards = FirstContact + NewCreatures + Promos

def SearchSimilar(name: str):
	highest=0.0
	found=None
	searchedVal=name.lower()
	for card in AllCards:
		val = ratio(searchedVal, card.lower(), score_cutoff=0.65)
		if val > 0 and val > highest:
			highest = val
			found = card
	return found