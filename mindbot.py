#!/usr/bin/env python3

import re
import uuid
import cardlib
import random
import os
import datetime
import discord
import cardgenerator
from models import Card
from io import BytesIO
from discord import app_commands, ui
from pymongo import MongoClient, ASCENDING

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
#region HELPER FUNCS

def getCardDataFromEmbed(myInteraction: discord.Interaction)
	embedFields = myInteraction.message.embeds[0].to_dict()
	NameField = 0
	PowerField = 1
	CapabilitiesField = 2
	EffectField = 3
	QuoteField = 4
	CardnumberField = 5
	SetnameField = 6
	LanguageField = 7
	FilenameField = 8

	nameFieldAsDict = embedFields["fields"][NameField]
	powerFiledAsDict = embedFields["fields"][PowerField]
	CapabilitiesFieldAsDict = embedFields["fields"][CapabilitiesField]
	EffectFieldAsDict = embedFields["fields"][EffectField]
	QuoteFieldAsDict = embedFields["fields"][QuoteField]
	CardnumberFielddAsDict = embedFields["fields"][CardnumberField]
	SetnameFieldAsDict = embedFields["fields"][SetnameField]
	LanguageFieldAsDict = embedFields["fields"][LanguageField]
	filenameFiledAsDict = embedFields["fields"][FilenameField]
		
	name = nameFieldAsDict["value"]
	power = powerFiledAsDict["value"]
	capabilities = CapabilitiesFieldAsDict["value"]
	effect = EffectFieldAsDict["value"]
	quote = QuoteFieldAsDict["value"]
	cardnumber = CardnumberFielddAsDict["value"]
	setname = SetnameFieldAsDict["value"]
	language = LanguageFieldAsDict["value"]
	filename = filenameFiledAsDict["value"]
			
	return name, power, capabilities, effect, quote, cardnumber, setname, language, filename
#endregion

#region UI STUFF
class EditCardData(ui.Modal, title='Edit Card Name'):
	name = ui.TextInput(label='Name', placeholder="Sirus Snape", required=True)
	
	power = ui.TextInput(label='Power', placeholder="9", required=True)
	
	capabilities = ui.TextInput(label='Keywords', placeholder="Frenzy, Tough", required=False)
	
	effect = ui.TextInput(label='Effect', placeholder="#Play: Draw a card. #Defeat: Gain +1 HP.", required=False)
	
	quote = ui.TextInput(label='Quote', placeholder="Nothing special", required=False)
	# lang = ui.TextInput(label='Language', placeholder="en", required=True)
	# cardset = ui.TextInput(label='Card Set', placeholder="Second Wave", required=True)
	# uid_from_set = ui.TextInput(label='Cardnumber', placeholder="1/24", required=True)
	
	async def on_submit(self, interaction: discord.Interaction):

		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)

		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=self.name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=self.power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=self.capabilities if (self.capabilities  != "" ) else "?", inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=self.effect if (self.effect  != "" ) else "?"  , inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=self.quote if (self.quote != "" ) else "?" , inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=language, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)
		
class EditCardName(ui.Modal, title='Edit Card Name'):
	name = ui.TextInput(label='Name', placeholder="Sirus Snape", required=True)
	async def on_submit(self, interaction: discord.Interaction):

		
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)

		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=self.name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=language, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)

class EditCardPower(ui.Modal, title='Edit Card Power'):
	power = ui.TextInput(label='Power', placeholder="9", required=True)
	async def on_submit(self, interaction: discord.Interaction):

		
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)
		
		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=self.power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=language, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)

class EditCardCapabilites(ui.Modal, title='Edit Card Capabilites'):
	capabilities = ui.TextInput(label='Keywords', placeholder="Frenzy, Tough", required=False)
	# effect = ui.TextInput(label='Effect', placeholder="#Play: Draw a card. #Defeat: Gain +1 HP.", required=False)
	# quote = ui.TextInput(label='Quote', placeholder="Nothing special", required=False)
	# lang = ui.TextInput(label='Language', placeholder="en", required=True)
	# cardset = ui.TextInput(label='Card Set', placeholder="Second Wave", required=True)
	# uid_from_set = ui.TextInput(label='Cardnumber', placeholder="1/24", required=True)

	async def on_submit(self, interaction: discord.Interaction):

		
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)
		
		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=self.capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=language, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)


class EditCardEffect(ui.Modal, title='Edit Card Effect'):
	effect = ui.TextInput(label='Effect', placeholder="#Play: Draw a card. #Defeat: Gain +1 HP.", required=False)
	async def on_submit(self, interaction: discord.Interaction):

		
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)
		
		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=self.effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=language, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)

class EditCardQuote(ui.Modal, title='Edit Card Quote'):
	quote = ui.TextInput(label='Quote', placeholder="Nothing special", required=False)

	async def on_submit(self, interaction: discord.Interaction):

			
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)
		
		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=self.quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=language, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)

class EditCardLanguage(ui.Modal, title='Edit Card Language'):
	lang = ui.TextInput(label='Language', placeholder="en", required=True)
	async def on_submit(self, interaction: discord.Interaction):

		
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)
		
		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=self.language, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)

class EditCardSet(ui.Modal, title='Edit Card Setname'):
	cardset = ui.TextInput(label='Name from Set', placeholder="Second Wave", required=True)

	async def on_submit(self, interaction: discord.Interaction):

		
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)
		
		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=self.setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=lang, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)

class EditCardNumber(ui.Modal, title='Edit Card Number'):
	cardnumber = ui.TextInput(label='Cardnumber', placeholder="1/24", required=True)

	async def on_submit(self, interaction: discord.Interaction):

		
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)
		
		myEmbed = discord.Embed(color = discord.Color.random())
		myEmbed.add_field(name="Name", value=name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=self.cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=lang, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)
#endregion

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

image_whiteList = ['png', 'PNG', 'jpg', 'JPG']

class EditMenu(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(custom_id = "EditCardDataButton",label="Data" ,emoji="✏️", style=discord.ButtonStyle.gray, row=0)
	async def editCardName(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardData())

"""
	@discord.ui.button(custom_id = "NameButton",label="Name" ,emoji="✏️", style=discord.ButtonStyle.gray, row=0)
	async def editCardName(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardName())
			
	@discord.ui.button(custom_id = "PowerButton",label="Power",emoji="✏️", style=discord.ButtonStyle.gray, row=0)
	async def editCardPower(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardPower())

	@discord.ui.button(custom_id = "CapabilitesButton",label="Capabilites",emoji="✏️", style=discord.ButtonStyle.gray, row=0)
	async def editCardCapabilites(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardCapabilites()())

	@discord.ui.button(custom_id = "EffectButton",label="Effect",emoji="✏️", style=discord.ButtonStyle.gray, row=0)
	async def editCardEffect(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardEffect())

	@discord.ui.button(custom_id = "QuoteButton",label="Quote",emoji="✏️", style=discord.ButtonStyle.gray, row=0)
	async def editCardQuote(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardQuote())
"""
	@discord.ui.button(custom_id = "cardNumberButton",label="Card Nr",emoji="✏️", style=discord.ButtonStyle.gray, row=1)
	async def editCardNumber(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardNumber())

	@discord.ui.button(custom_id = "SetNameButton",label="Setname",emoji="✏️", style=discord.ButtonStyle.gray,row=1)
	async def editCardSet(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardSet()())

	@discord.ui.button(custom_id = "LangugageButton",label="Lang",emoji="✏️", style=discord.ButtonStyle.gray,row=1)
	async def editCardLanguage(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardLanguage())

	@discord.ui.button(custom_id = "PreviewButton",label="Preview",emoji="🖼️", style=discord.ButtonStyle.red,row=2)
	async def previewCard(self, interaction: discord.Interaction, button: discord.ui.Button):
		
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		with BytesIO() as image_binary:
			name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)

			finalCardAsImage, finalCardObj = cardgenerator.CreateACreatureCard(artwork_filename=filename,
												uid_from_set=cardnumber,
												lang=language,
												name=name,
												power = power,
												keywords = capabilities if (capabilities  != "?" ) else "",
												effect = effect if (effect  != "?" ) else "",
												quote = quote if (quote  != "?" ) else "",
												cardset=setname
												)
			finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300))
			image_binary.seek(0)

			myEmbed = discord.Embed(color = discord.Color.random())
			myEmbed.set_image(url=f"attachment://{filename}")
			myEmbed.add_field(name="Name", value=name, inline=True) # Index 0
			myEmbed.add_field(name="Power", value=power, inline=False) # Index 1
			myEmbed.add_field(name="Capabilities", value=capabilities, inline=False) # Index 2
			myEmbed.add_field(name="Effect", value=effect, inline=False) # Index 3
			myEmbed.add_field(name="Quote", value=quote, inline=False) # Index 4
			myEmbed.add_field(name="Cardnumber in Set", value=cardnumber, inline=False) # Index 5
			myEmbed.add_field(name="Setname", value=setname, inline=False) # Index 6
			myEmbed.add_field(name="Language", value=language, inline=False) # Index 7
			myEmbed.add_field(name="Filename", value=f"{filename}", inline=True) # Index 8
		
			await interaction.followup.send(embed = myEmbed, view = EditMenu(), file=discord.File(fp=image_binary, filename=filename), ephemeral=True)

	@discord.ui.button(custom_id = "ReleaseButton",label="", emoji="✔️",style=discord.ButtonStyle.green ,row=2)
	async def releaseCard(self, interaction: discord.Interaction, button: discord.ui.Button):
		
		
		await interaction.response.defer(ephemeral=False, thinking=True)
		# Update the Mindbug-Card
		with BytesIO() as image_binary:
			name, power, capabilities, effect, quote, cardnumber, setname, language, filename = getCardDataFromEmbed(interaction)
	
			finalCardAsImage, finalCardObj = cardgenerator.CreateACreatureCard(artwork_filename=filename,
												uid_from_set=cardnumber,
												lang=language,
												name=name,
												power = power,
												keywords = capabilities if (capabilities  != "?" ) else "",
												effect = effect if (effect  != "?" ) else "",
												quote = quote if (quote  != "?" ) else "",
												cardset=setname
												)
			finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300))
			image_binary.seek(0)
			
			saveCardinDB(interaction, finalCardObj)
		
			# await interaction.followup.send(embed = myEmbed, view = EditMenu(), file=discord.File(fp=image_binary, filename=filename), ephemeral=False)
			await interaction.followup.send(content="Release #1", file=discord.File(fp=image_binary, filename=filename), ephemeral=False)



# First only an embed, the we can edit the data, add a preview Button and a release button
@tree.command(name = "upload", description = "Test")
async def upload(interaction: discord.Interaction, artwork : discord.Attachment):
	try:
		if (artwork):
			# The first answer must be given within 3sec.
			await interaction.response.defer(ephemeral=True, thinking=True)
			# From now on we have 15 minutes
			
			# Check if the Artwork is a PNG
			if artwork.filename.split(".")[-1] not in image_whiteList:
				await interaction.followup.send("The artwork is not a supported file.", ephemeral=True)
				return

			# Save the Upload-Artwork
			await artwork.save(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"{artwork.filename}"))
						
			# Create the Mindbug-Card
			myEmbed = discord.Embed(color = discord.Color.random())
			# myEmbed.set_image(url=f"attachment://{artwork.filename}")
			myEmbed.add_field(name="Name", value="Sirus Snape", inline=False) # Index 0
			myEmbed.add_field(name="Power", value="X", inline=False) # Index 1
			myEmbed.add_field(name="Capabilities", value="?", inline=False) # Index 2
			myEmbed.add_field(name="Effect", value="?", inline=False) # Index 3
			myEmbed.add_field(name="Quote", value="?", inline=False) # Index 4
			myEmbed.add_field(name="Cardnumber in Set", value="1/1", inline=False) # Index 5
			myEmbed.add_field(name="Setname", value="Second Wave", inline=False) # Index 6
			myEmbed.add_field(name="Language", value="en", inline=False) # Index 7
			myEmbed.add_field(name="Filename", value=f"{artwork.filename}", inline=False) # Index 8
		
			await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)
		else:
			await interaction.response.send_message(f'No File', ephemeral=True)
	except Exception as e:
		print("Error on Create Mindbug Card.")
		print (str(e))
		await interaction.followup.send(f"I choked and had to abort.", ephemeral=True)


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
				finalCardAsImage, finalCardObj = cardgenerator.CreateAMindbugCard(artwork_filename=artwork.filename, lang=lang, cardset=cardset, uid_from_set=uid_from_set )
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
				finalCardAsImage, finalCardObj = cardgenerator.CreateACreatureCard(artwork_filename=artwork.filename,
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
