#!/usr/bin/env python3

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

def saveCardinDB(myInteraction: discord.Interaction, myCardToSave: Card):
	db = mongodb["cardcreator"]
	db["customcreatures"].insert_one({
		'cardset': myCardToSave.cardset,
		'uid_from_set': myCardToSave.uid_from_set,
		'lang': myCardToSave.lang,
		'name': myCardToSave.name,
		'power': myCardToSave.power, 
		'keywords': myCardToSave.keywords,
		'effect': myCardToSave.effect, 
		'quote': myCardToSave.quote,
		'filename':myCardToSave.filename,
		'artworkAsBase64': myCardToSave.artwork_base64,
		'final_card_filename':myCardToSave.final_card_name,
		'final_card_as_base64': myCardToSave.final_card_base_64,
		'final_card_cropped_filename':myCardToSave.final_cropped_card_name,
		'final_cropped_card_as_base64': myCardToSave.cropped_final_card_base64,
		'user_id': myInteraction.user.id,
		'user_name': myInteraction.user.name
		})
#endregion

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

@tree.command(name = "createamindbug", description = "Create a Mindbug Card with a given Artwork. The Artwork must be a PNG-File.")
async def createmindbugcard(interaction: discord.InteractionMessage, artwork : discord.Attachment, lang: str, cardset: str, uid_from_set: str):
	try:
		if (artwork):
			# The first answer must be given within 3sec.
			await interaction.response.defer(ephemeral=False, thinking=True)
			# From now on we have 15 minutes
			
			# Check if the Artwork is a PNG
			if artwork.filename.split(".")[-1] not in image_whiteList:
				await interaction.followup.send("The artwork is not a PNG file.")
				return

			# Save the Upload-Artwork
			await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"{artwork.filename}"))

			# Check if the Set Icon is a PNG
			# TODO: See CreateCreatureCard
			# if (Icon != None):
			# 	if Icon.filename.split(".")[-1] not in image_whiteList:
			# 		await interaction.followup.send("The Set Icon is not a PNG file.")
			# 		return
			# 	await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"cardset_{cardset}.png"))

			# Create the Mindbug-Card
			with BytesIO() as image_binary:
				finalCardAsImage, finalCardObj = cardgenerator.CreateAMindbugCard(artwork_filename=artwork.filename,image_width= artwork.width,image_height= artwork.height, lang=lang, cardset=cardset, uid_from_set=uid_from_set )
				finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300))
				image_binary.seek(0)
				saveCardinDB(interaction, finalCardObj)

				await interaction.followup.send(file=discord.File(fp=image_binary, filename=f'image.png'))
		else:
			await interaction.response.send_message(f'No File')
	except:
		print("Error on Create Mindbug Card.")
		await interaction.followup.send(f"I choked and had to abort.")

@tree.command(name = "createacreature", description = "Create a Creature Card with a given Artwork. The Artwork must be a PNG-File.")
async def createcreaturecard(interaction: discord.InteractionMessage, artwork : discord.Attachment, lang: str, cardset: str, uid_from_set: str, name:str, power:str, effect:str = None, keywords:str = None, quote:str = None):
	try:	
		if (artwork):
			# The first answer must be given within 3sec.
			await interaction.response.defer(ephemeral=False, thinking=True)
			# From now on we have 15 minutes
			# 			
			# Check if the Image is a PNG
			if artwork.filename.split(".")[-1] not in image_whiteList:
				await interaction.followup.send("The artwork is not a PNG file.")
				return

			# Save the Upload-Artwor
			await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"{artwork.filename}"))

			# Check if the Set Icon is a PNG
			# I think we need an other command to Upload a Set Icon, wich can use here.
			# if (Icon != None):
			# 	if Icon.filename.split(".")[-1] not in image_whiteList:
			# 		await interaction.followup.send("The Set Icon is not a PNG file.")
			# 		return
			# 	await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"cardset_{cardset}.png"))

			# Create the Mindbug-Card
			with BytesIO() as image_binary:
				finalCardAsImage, finalCardObj = cardgenerator.CreateACreatureCard(artwork_filename=artwork.filename,
													image_width=artwork.width,
													image_height= artwork.height, 
													lang=lang,
													cardset=cardset, 
													uid_from_set=uid_from_set, 
													name=name, 
													power=power, 
													keywords=keywords, 
													effect=effect, 
													quote=quote )
				finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300))
				image_binary.seek(0)
				
				saveCardinDB(interaction, finalCardObj)
				
				await interaction.followup.send(file=discord.File(fp=image_binary, filename=artwork.filename))
		else:
			await interaction.response.send_message(f'No File')
	except:
		print("Error on Create Crature Card.")
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