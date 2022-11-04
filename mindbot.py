#!/usr/bin/env python3

import discord
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "card", description = "Display a card by name")
async def card(interaction: discord.Interaction, card: str):
	name=card.replace(' ', '_')
	await interaction.response.send_message(f'https://mindbug.fandom.com/wiki/{name}')
	
@tree.command(name = "randomcard", description = "Display a random card")
async def randomcard(interaction: discord.Interaction):
	await interaction.response.send_message(f'https://mindbug.fandom.com/wiki/Shark_Dog')

@client.event
async def on_ready():
	#Sync the commands with all server
	await tree.sync()
	print("Ready!")

with open('token.txt') as f:
	token=f.read()
	
client.run(token)