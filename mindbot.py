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

@client.event
async def on_ready():
	#use a specific guild as Mindbug France: 1010510391878619146, sync is faster in that case.
    await tree.sync(guild=discord.Object(id= 1010510391878619146))
    print("Ready!")

with open('myfile.txt') as f:
	token=f.read()
	
client.run(token)