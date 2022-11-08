#!/usr/bin/env python3

import discord
import cardlib
import random
import os
import discord
import cardgenerator
from discord import app_commands
from pymongo import MongoClient

mongodb = MongoClient(host = os.getenv('DB_HOST'), port = int(os.getenv('DB_PORT')))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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
	if (artwork):
		# The first answer must be given within 3sec.
		await interaction.response.defer(ephemeral=False, thinking=True)
		
		# From now on we have 15 minutes
		# Save the Upload-Image
		# TODO Accept only PNGs
		# TODO Maybe use Buffers
		await artwork.save(os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))),f"input/{artwork.filename}" ))

		# Create the Mindbug-Card
		with BytesIO() as image_binary:
			cardgenerator.CreateAMindbugCard(artwork_filename=artwork.filename,image_width= artwork.width,image_height= artwork.height, lang=lang, cardset=cardset, uid_from_set=uid_from_set ).save(image_binary, 'PNG', dpi = (300,300))
			image_binary.seek(0)
			await interaction.followup.send(file=discord.File(fp=image_binary, filename=f'image.png'))
	else:
		await interaction.response.send_message(f'No File')

@tree.command(name = "createacreature", description = "Create a Creature Card with a given Artwork. The Artwork must be a PNG-File.")
async def createcreaturecard(interaction: discord.InteractionMessage, artwork : discord.Attachment, lang: str, cardset: str, uid_from_set: str, name:str, power:str, keywords:str, effect:str, quote:str):
	if (artwork):
		# The first answer must be given within 3sec.
		await interaction.response.defer(ephemeral=False, thinking=True)
		
		# From now on we have 15 minutes
		# Save the Upload-Image
		# TODO Accept only PNGs
		# TODO Maybe use Buffers
		await artwork.save(os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))),f"input/{artwork.filename}" ))

		# Create the Mindbug-Card
		with BytesIO() as image_binary:
			cardgenerator.CreateACreatureCard(artwork_filename=artwork.filename,
												image_width=artwork.width,
												image_height= artwork.height, 
												lang=lang,
												cardset=cardset, 
												uid_from_set=uid_from_set, 
												name=name, 
												power=power, 
												keywords=keywords, 
												effect=effect, 
												quote=quote ).save(image_binary, 'PNG', dpi = (300,300))

			image_binary.seek(0)
			#TODO: generate Filename with e.g: Name_en_cropped.png
			await interaction.followup.send(file=discord.File(fp=image_binary, filename=artwork.filename))
	else:
		await interaction.response.send_message(f'No File')



@client.event
async def on_ready():

	# Load the Cardframes from the assets-Folder
	cardgenerator.card_frame_normal, cardgenerator.card_frame_mindbug = cardgenerator.LoadingCardFrames()

	# Load the Fonts from the assets-Folder
	cardgenerator.name_font_52, cardgenerator.name_font_20, cardgenerator.trigger_and_capabilites_font, cardgenerator.description_font, cardgenerator.quote_font, cardgenerator.card_key_font_18, cardgenerator.power_font = cardgenerator.LoadingFonts()

	#Sync the commands with all server
	await tree.sync()
	print("Ready!")

with open('token.txt') as f:
	token=f.read()

client.run(token)