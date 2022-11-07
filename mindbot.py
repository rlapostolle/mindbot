#!/usr/bin/env python3

import cardlib
import random
import os
import discord
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

@client.event
async def on_ready():
	#Sync the commands with all server
	await tree.sync()
	print("Ready!")

with open('token.txt') as f:
	token=f.read()
	
client.run(token)