#!/usr/bin/env python3

import re
import uuid
import cardlib
import random
import os
import discord
import cardgenerator
from models import Card
from io import BytesIO
from discord import app_commands
from pymongo import MongoClient

#region DB STUFF
mongodb = MongoClient(host = os.getenv('DB_HOST'), port = int(os.getenv('DB_PORT')))

def saveCardinDB(myInteraction: discord.Interaction, myCardToSave: Card, existing_obj:dict=None):
	print(myCardToSave.filename)
	db = mongodb["cardcreator"]
	obj = myCardToSave.toDdObj()
	obj['user_id'] = myInteraction.user.id
	obj['user_name'] = myInteraction.user.name
	db["customcreatures"].replace_one(filter={ "_id" : (existing_obj["_id"] if existing_obj != None else None) }, replacement=obj, upsert=True)
#endregion

async def checkUserId(interaction: discord.Interaction, usertag: str):
	try:
		if usertag != None:
			userid = int(re.search(r"<@!?(\d+)>", usertag).group(1))
		else:
			userid = None
	except:
		await interaction.response.send_message("Invalid user", ephemeral=True)
		return
	return userid

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

image_whiteList = ['png', 'PNG']

@tree.command(name = "card", description = "Display a card by name")
async def card(interaction: discord.Interaction, card: str):
	name = cardlib.SearchSimilar(card)
	if name != None:
		name = name.replace(' ', '_')
		await interaction.response.send_message(f'https://mindbug.fandom.com/wiki/{name}')
	else:
		await interaction.response.send_message(f'No matching card')

@tree.command(name = "randomcard", description = "Display a random card")
async def randomcard(interaction: discord.Interaction):
	card = random.choice(cardlib.AllCards)
	name = card.replace(' ', '_')
	await interaction.response.send_message(f'https://mindbug.fandom.com/wiki/{name}')

@tree.command(name = "randomcustom", description = "Display a random custom card created by the community")
async def randomcustom(interaction: discord.Interaction, user:str = None):
	userid = await checkUserId(interaction, user)
	
	await interaction.response.defer(ephemeral=False, thinking=True)

	#Get a random card
	db = mongodb["cardcreator"]
	card = list(db["customcreatures"].aggregate([
		{"$match": { "$and" : [
			{ "filename": { "$exists": True } },
			{ "filename": { '$ne': None} },
			] + ([{"user_id": userid }] if userid != None else [])
		} },
		{"$sample": { "size": 1}}]))

	if(len(card) > 0 and 'filename' in card[0]):
		c = Card(**card[0])
		img_path = os.path.join(os.getenv('CARD_OUTPUT_FOLDER'), c.relativePath())
		if(os.path.exists(img_path)):
			await interaction.followup.send(file=discord.File(fp=img_path))
		else:
			print(f"Creature image unavailable: {img_path}")
			await interaction.followup.send("Sorry, there was an error while reading card...")
	else:
		await interaction.followup.send("No record available.")

@tree.command(name = "customcards", description = "Display the list of cards from a user")
async def customcards(interaction: discord.Interaction, user:str = None):
	
	userid = await checkUserId(interaction, user)
	if userid == None:
		userid = interaction.user.id

	await interaction.response.defer(ephemeral=False, thinking=True)

	#Get all cards from user
	db = mongodb["cardcreator"]
	cards = db["customcreatures"].find(filter={ "user_id": userid })

	text = ""
	for card in cards:
		text += card["name"] + " [" + card["lang"] + "] from cardset '" + card["cardset"] + "'\n"
	if text == "":
		await interaction.followup.send("No record available.")
	else:
		await interaction.followup.send(text)

@tree.command(name = "createamindbug", description = "Create a Mindbug Card with a given Artwork. The Artwork must be a PNG-File.")
async def createmindbugcard(interaction: discord.InteractionMessage, artwork : discord.Attachment, lang: str, cardset: str, uid_from_set: str):
	try:
		if (artwork):
			# The first answer must be given within 3sec.
			await interaction.response.defer(ephemeral=False, thinking=True)
			# From now on we have 15 minutes
			
			# Check if the Artwork is a PNG
			ext = artwork.filename.split(".")[-1]
			if ext not in image_whiteList:
				await interaction.followup.send("The artwork is not a PNG file.")
				return

			#rename asset with random name to avoid collision
			artwork_filename = uuid.uuid4().hex + "." + ext

			# Save the Upload-Artwork
			await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"{artwork_filename}"))

			# Check if the Set Icon is a PNG
			# TODO: See CreateCreatureCard
			# if (Icon != None):
			# 	if Icon.filename.split(".")[-1] not in image_whiteList:
			# 		await interaction.followup.send("The Set Icon is not a PNG file.")
			# 		return
			# 	await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"cardset_{cardset}.png"))

			# Create the Mindbug-Card
			with BytesIO() as image_binary:
				finalCardAsImage, finalCardObj = cardgenerator.CreateAMindbugCard(artwork_filename=artwork_filename,image_width= artwork.width,image_height= artwork.height, lang=lang, cardset=cardset, uid_from_set=uid_from_set )
				finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300))
				image_binary.seek(0)
				saveCardinDB(interaction, finalCardObj)

				await interaction.followup.send(file=discord.File(fp=image_binary, filename=f'image.png'))
		else:
			await interaction.response.send_message(f'No File')
	except Exception as e:
		print("Error on Create Mindbug Card: " + str(e))
		await interaction.followup.send(f"I choked and had to abort.")

@tree.command(name = "createacreature", description = "Create a Creature Card with a given Artwork. The Artwork must be a PNG-File.")
async def createcreaturecard(interaction: discord.InteractionMessage, artwork : discord.Attachment, lang: str, cardset: str, uid_from_set: str, name:str, power:str, effect:str = None, keywords:str = None, quote:str = None, override:bool = False):
	try:
		if (artwork):
			# The first answer must be given within 3sec.
			await interaction.response.defer(ephemeral=False, thinking=True)
			# From now on we have 15 minutes
			
			#Check if the card does not exist yet
			db = mongodb["cardcreator"]
			dbcard = db["customcreatures"].find_one({ 'cardset': cardset, 'lang': lang, 'name': name })
			if dbcard != None:
				if dbcard['user_id'] != interaction.user.id:
					await interaction.followup.send(f"A card name already exists in this set and you cannot modify it.")
					return
				elif not override:
					if dbcard['user_id'] == interaction.user.id:
						await interaction.followup.send(f"This card name already exists in this set, please chose a different one or use override option to replace it.")
						return


			# Check if the Image is a PNG
			ext = artwork.filename.split(".")[-1]
			if ext not in image_whiteList:
				await interaction.followup.send("The artwork is not a PNG file.")
				return

			#rename asset with random name to avoid collision
			artwork_filename = uuid.uuid4().hex + "." + ext

			# Save the Uploaded Artwork
			await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"{artwork_filename}"))

			# Check if the Set Icon is a PNG
			# I think we need an other command to Upload a Set Icon, wich can use here.
			# if (Icon != None):
			# 	if Icon.filename.split(".")[-1] not in image_whiteList:
			# 		await interaction.followup.send("The Set Icon is not a PNG file.")
			# 		return
			# 	await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"cardset_{cardset}.png"))

			# Create the Mindbug-Card
			with BytesIO() as image_binary:
				finalCardAsImage, finalCardObj = cardgenerator.CreateACreatureCard(artwork_filename=artwork_filename,
													image_width=artwork.width,
													image_height= artwork.height, 
													lang=lang,
													cardset=cardset, 
													uid_from_set=uid_from_set, 
													name=name, 
													power=power, 
													keywords=keywords, 
													effect=effect, 
													quote=quote)
				finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300))
				image_binary.seek(0)
				
				saveCardinDB(interaction, finalCardObj, dbcard)
				
				await interaction.followup.send(file=discord.File(fp=image_binary, filename=artwork.filename))
		else:
			await interaction.response.send_message(f'No File')
	except Exception as e:
		print("Error on Create Crature Card:" + str(e))
		await interaction.followup.send(f"I choked and had to abort.")




@client.event
async def on_ready():

	print("Loading assets...")
	# Load the Cardframes from the assets-Folder
	cardgenerator.card_frame_normal, cardgenerator.card_frame_mindbug = cardgenerator.LoadingCardFrames()

	# Load the Fonts from the assets-Folder
	cardgenerator.name_font_52, cardgenerator.name_font_20, cardgenerator.trigger_and_capabilites_font, cardgenerator.description_font, cardgenerator.quote_font, cardgenerator.card_key_font_18, cardgenerator.power_font = cardgenerator.LoadingFonts()

	print("Sync commands on all discord server...")
	#Sync the commands with all server
	await tree.sync()
	print("Ready!")

with open('token.txt') as f:
	token=f.read()

client.run(token)