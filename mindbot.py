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

CARD_GENERATOR_APP_NAME="Card Generator 0.0.3"
BUG_TRACKING_URL="https://github.com/rlapostolle/mindbot/issues"

#region DB STUFF
mongodb = MongoClient(host = os.getenv('DB_HOST'), port = int(os.getenv('DB_PORT')))

def saveCardinDB(myInteraction: discord.Interaction, myCardToSave: Card, existing_obj:dict=None):
	print(myCardToSave.filename)
	db = mongodb["cardcreator"]
	obj = myCardToSave.toDdObj()
	obj['user_id'] = myInteraction.user.id
	obj['user_name'] = myInteraction.user.name
	if existing_obj != None:
		db["customcreatures"].replace_one(filter={ "_id" : existing_obj["_id"] }, replacement=obj, upsert=True)
	else:
		db["customcreatures"].insert_one(obj)
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

#region CONF
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

image_whiteList = ['png', 'PNG', 'jpg', 'JPG']
embed_description = "Name: \nUnique name between 1-16 characters \n\nPower: \nPossible characters are numbers 1-9 and X \n\nCapabilities: \nPossible values are Frenzy, Tough, Poisonous, Hunter, Sneaky and the respective translations into other languages. You are welcome to invent new Capabilites if you need an explanation in the chat. \nNote: If there is more than one capabilite, there MUST be a space after the comma. \n\nEffect: \nEverything can be here, but if you want to use triggers you must have a '#' as prefix and a colon with a space ': ' as suffix. Example: '#Play: ' This is needed so that the triggers can be written in bold. Allowed values are currently:   '#Attack: ', '#Block: ', '#Defeat: ', '#Draw: ', '#Play: ', '#Unblocked: ', '#Attack: ', '#Play: ', '#Defeated: ', '#Block: ', '#Unblocked: ', '#Draw: ' \nNote: if you want to add more triggers, contact us or post a request on Github. \n\nQuote: \nAnything funny can be put here. \n\nCardnumber in Set: \nIf you have created your own card set give each card a unique number like '1/12'. \n\nLanguage: \nPossible values are all ISO code country abbreviations. \n\nOverride: \nIs a temporary solution to override (edit) a card and can only be set when calling the command."
#endregion

#region HELPER FUNCS
def str2bool(v) -> bool:
    return v.lower() in ("yes", "true", "t", "1")

class embeddata:
	def __init__(self, myInteraction: discord.Interaction):
		embedFields = myInteraction.message.embeds[0].to_dict()

		self.name = embedFields["fields"][0]["value"]
		self.power = embedFields["fields"][1]["value"]
		self.capabilities = embedFields["fields"][2]["value"]
		self.effect = embedFields["fields"][3]["value"]
		self.quote = embedFields["fields"][4]["value"]
		self.cardnumber = embedFields["fields"][5]["value"]
		self.setname = embedFields["fields"][6]["value"]
		self.language = embedFields["fields"][7]["value"]
		self.filename = embedFields["fields"][8]["value"]
		self.override = embedFields["fields"][9]["value"]
		self.threeDEffect = embedFields["fields"][10]["value"]

#endregion

#region UI STUFF
class EditCardData(ui.Modal, title='Edit Card Name'):

	def __init__(self, interaction: discord.Interaction):
		super().__init__()
		data = embeddata(interaction)
		self.nameInput = ui.TextInput(label='Name', default=data.name if data.name != "?" else "", placeholder="Sirus Snape", required=True, min_length=1, max_length=24)
		self.add_item(self.nameInput)
		self.powerInput = ui.TextInput(label='Power', default=data.power if data.power != "?" else "", placeholder="9", required=True, min_length=1, max_length=2)
		self.add_item(self.powerInput)
		self.capabilitiesInput = ui.TextInput(label='Keywords', default=data.capabilities if data.capabilities != "?" else "", placeholder="Frenzy, Tough", required=False)
		self.add_item(self.capabilitiesInput)
		self.effectInput = ui.TextInput(label='Effect', default=data.effect if data.effect != "?" else "", placeholder="#Play: Draw a card. #Defeat: Gain 1 life point.", required=False)
		self.add_item(self.effectInput)
		self.quoteInput = ui.TextInput(label='Quote', default=data.quote if data.quote != "?" else "", placeholder="Nothing special", required=False)
		self.add_item(self.quoteInput)
	
	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		data = embeddata(interaction)

		myEmbed = discord.Embed(title=CARD_GENERATOR_APP_NAME, url=BUG_TRACKING_URL,color = discord.Color.random(), description=embed_description)
		myEmbed.add_field(name="Name", value=self.nameInput.value.strip(), inline=True) # Index 0
		myEmbed.add_field(name="Power", value=self.powerInput.value.strip(), inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=self.capabilitiesInput.value.strip() if (len(self.capabilitiesInput.value)  != 0 ) else "?", inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=self.effectInput.value.strip() if (len(self.effectInput.value)  != 0 ) else "?"  , inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=self.quoteInput.value.strip() if (len(self.quoteInput.value) != 0 ) else "?" , inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=data.cardnumber, inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=data.setname, inline=False) # Index 6
		myEmbed.add_field(name="Language", value=data.language, inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=str(data.filename), inline=False) # Index 8
		myEmbed.add_field(name="Override", value=str(data.override), inline=False) # Index 9
		myEmbed.add_field(name="3D-Effect", value=str(data.threeDEffect), inline=False) # Index 10
		myEmbed.set_footer(text="mindbug.me")
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)

class EditCardMetaData(ui.Modal, title='Edit Card Name'):
	
	def __init__(self, interaction: discord.Interaction):
		super().__init__()
		data = embeddata(interaction)
		self.languageInput = ui.TextInput(label='Language', default=data.language, placeholder="en", required=True, min_length=2, max_length=2)
		self.add_item(self.languageInput)
		self.setnameInput = ui.TextInput(label='Card Set', default=data.setname, placeholder="Second Wave", required=True)
		self.add_item(self.setnameInput)
		self.uid_from_setInput = ui.TextInput(label='Cardnumber', default=data.cardnumber, placeholder="1/24", required=True)
		self.add_item(self.uid_from_setInput)
	
	async def on_submit(self, interaction: discord.Interaction):

		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		data = embeddata(interaction)

		myEmbed = discord.Embed(title=CARD_GENERATOR_APP_NAME, url=BUG_TRACKING_URL, color = discord.Color.random(), description=embed_description)
		myEmbed.add_field(name="Name", value=data.name, inline=True) # Index 0
		myEmbed.add_field(name="Power", value=data.power, inline=False) # Index 1
		myEmbed.add_field(name="Capabilities", value=data.capabilities, inline=False) # Index 2
		myEmbed.add_field(name="Effect", value=data.effect, inline=False) # Index 3
		myEmbed.add_field(name="Quote", value=data.quote, inline=False) # Index 4
		myEmbed.add_field(name="Cardnumber in Set", value=self.uid_from_setInput.value.strip(), inline=False) # Index 5
		myEmbed.add_field(name="Name from Set", value=self.setnameInput.value.strip(), inline=False) # Index 6
		myEmbed.add_field(name="Language", value=self.languageInput.value.strip(), inline=False) # Index 7
		myEmbed.add_field(name="Filename", value=str(data.filename), inline=False) # Index 8
		myEmbed.add_field(name="Override", value=str(data.override), inline=False) # Index 9	
		myEmbed.add_field(name="3D-Effect", value=str(data.threeDEffect), inline=False) # Index 10
		myEmbed.set_footer(text="http://mindbug.me")	
	
		await interaction.followup.send(embed = myEmbed, view = EditMenu(), ephemeral=True)

class EditMenu(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
	
	async def GeneratePreview(self, interaction, wich3DMode = 0):
		await interaction.response.defer(ephemeral=True, thinking=True)
		# Update the Mindbug-Card
		with BytesIO() as image_binary:
			data = embeddata(interaction)

			if (wich3DMode == 0):
				data.threeDEffect = "0"
			elif (wich3DMode == 1):
				data.threeDEffect = "1"
			elif (wich3DMode == 2):
				data.threeDEffect = "2"

			finalCardAsImage, finalCardObj = cardgenerator.CreateACreatureCard(
													artwork_filename = data.filename,
													uid_from_set=data.cardnumber,
													lang = data.language,
													name = data.name,
													power = data.power,
													keywords = data.capabilities if (data.capabilities  != "?" ) else "",
													effect = data.effect if (data.effect  != "?" ) else "",
													quote = data.quote if (data.quote  != "?" ) else "",
													cardset=data.setname,
													use_3D_effect = data.threeDEffect
													)
			finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300), optimize= True)
			image_binary.seek(0)

			myEmbed = discord.Embed(title=CARD_GENERATOR_APP_NAME, url=BUG_TRACKING_URL,color = discord.Color.random(), description=embed_description)
			myEmbed.set_image(url=f"attachment://{data.filename}")
			myEmbed.add_field(name="Name", value=data.name, inline=True) # Index 0
			myEmbed.add_field(name="Power", value=data.power, inline=False) # Index 1
			myEmbed.add_field(name="Capabilities", value=data.capabilities, inline=False) # Index 2
			myEmbed.add_field(name="Effect", value=data.effect, inline=False) # Index 3
			myEmbed.add_field(name="Quote", value=data.quote, inline=False) # Index 4
			myEmbed.add_field(name="Cardnumber in Set", value=data.cardnumber, inline=False) # Index 5
			myEmbed.add_field(name="Setname", value=data.setname, inline=False) # Index 6
			myEmbed.add_field(name="Language", value=data.language, inline=False) # Index 7
			myEmbed.add_field(name="Filename", value=str(data.filename), inline=False) # Index 8
			myEmbed.add_field(name="Override", value=str(data.override), inline=False) # Index 9
			myEmbed.add_field(name="3D-Effect", value=str(data.threeDEffect), inline=False) # Index 10
			myEmbed.set_footer(text="mindbug.me")
			
			await interaction.followup.send(embed = myEmbed, view = EditMenu(), file=discord.File(fp=image_binary, filename=data.filename), ephemeral=True)

	@discord.ui.button(custom_id = "EditCardDataButton",label="Data" ,emoji="✏️", style=discord.ButtonStyle.gray, row=0)
	async def editCardData(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardData(interaction=interaction))

	@discord.ui.button(custom_id = "EditCardMetaDataButton",label="Meta" ,emoji="✏️", style=discord.ButtonStyle.gray, row=0)
	async def editCardMeta(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(EditCardMetaData(interaction=interaction))

	@discord.ui.button(custom_id = "EditCard3DEffectButton_UpperHalf",label="3D Effect - 1/2" ,emoji="🚧", style=discord.ButtonStyle.gray, row=0)
	async def editCard3DEffectUpperHalf(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.GeneratePreview(interaction, 1)

	@discord.ui.button(custom_id = "EditCard3DEffectButton_UpperRigthQuater",label="3D Effect - 1/4" ,emoji="🚧", style=discord.ButtonStyle.gray, row=0)
	async def editCard3DEffectUpperRigthQuater(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.GeneratePreview(interaction, 2)

	@discord.ui.button(custom_id = "PreviewButton",label="Preview",emoji="🖼️", style=discord.ButtonStyle.red,row=2)
	async def previewCard(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.GeneratePreview(interaction, 0)
 
	@discord.ui.button(custom_id = "ReleaseButton",label="", emoji="✔️",style=discord.ButtonStyle.green ,row=2)
	async def releaseCard(self, interaction: discord.Interaction, button: discord.ui.Button):
		
		await interaction.response.defer(ephemeral=False, thinking=True)

		data = embeddata(interaction)

		#Check if the card does not exist yet
		db = mongodb["cardcreator"]
		dbcard = db["customcreatures"].find_one({ 'cardset': data.setname, 'lang': data.language, 'name': data.name })
		if dbcard != None:
			if dbcard['user_id'] != interaction.user.id:
				await interaction.followup.send(f"A card name already exists in this set and you cannot modify it.", ephemeral=True)
				return
			elif not data.override:
				if dbcard['user_id'] == interaction.user.id:
					await interaction.followup.send(f"This card name already exists in this set, please chose a different one or use override option to replace it.", ephemeral=True)
					return

		# Update the Mindbug-Card
		with BytesIO() as image_binary:
	
			finalCardAsImage, finalCardObj = cardgenerator.CreateACreatureCard(
												artwork_filename = data.filename,
												uid_from_set = data.cardnumber,
												lang = data.language,
												name = data.name,
												power = data.power,
												keywords = data.capabilities if (data.capabilities  != "?" ) else "",
												effect = data.effect if (data.effect  != "?" ) else "",
												quote = data.quote if (data.quote  != "?" ) else "",
												cardset = data.setname,
												use_3D_effect=data.threeDEffect
												)
			finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300), optimize= True)
			image_binary.seek(0)
			
			saveCardinDB(interaction, finalCardObj, dbcard)
		
			# await interaction.followup.send(embed = myEmbed, view = EditMenu(), file=discord.File(fp=image_binary, filename=filename), ephemeral=False)
			message = await interaction.followup.send(content="Release #1 from <@" + str(interaction.user.id) + ">", file=discord.File(fp=image_binary, filename=data.filename), ephemeral=False)
			await message.add_reaction('\N{THUMBS UP SIGN}')

#endregion

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

@tree.command(name = "createamindbug", description = "Create a Mindbug Card with a given Artwork.")
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
				finalCardAsImage, finalCardObj = cardgenerator.CreateAMindbugCard(artwork_filename=artwork_filename, lang=lang, cardset=cardset, uid_from_set=uid_from_set )
				finalCardAsImage.save(image_binary, 'PNG', dpi = (300,300))
				image_binary.seek(0)
				saveCardinDB(interaction, finalCardObj)

				message = await interaction.followup.send(content="Release #1 from <@" + str(interaction.user.id) + ">", file=discord.File(fp=image_binary, filename=artwork_filename), ephemeral=False)
				await message.add_reaction('\N{THUMBS UP SIGN}')
		else:
			await interaction.response.send_message(f'No File')
	except Exception as e:
		print("Error on Create Mindbug Card: " + str(e))
		await interaction.followup.send(f"I choked and had to abort.")

# First only an embed, the we can edit the data, add a preview Button and a release button
@tree.command(name = "createacreature", description = "Create a Creature Card with a given Artwork.")
async def createcreaturecard(interaction: discord.Interaction, artwork : discord.Attachment):
	try:
		if (artwork):
			# The first answer must be given within 3sec.
			await interaction.response.defer(ephemeral=True, thinking=True)
			# From now on we have 15 minutes
			
			# Check if the Image is a PNG
			ext = artwork.filename.split(".")[-1]
			if ext not in image_whiteList:
				await interaction.followup.send("The artwork is not a PNG or JPG file.", ephemeral=True)
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
			myEmbed = discord.Embed(title=CARD_GENERATOR_APP_NAME, url=BUG_TRACKING_URL,color = discord.Color.random(), description=embed_description)
			myEmbed.add_field(name="Name", value="?", inline=True) # Index 0
			myEmbed.add_field(name="Power", value="?", inline=False) # Index 1
			myEmbed.add_field(name="Capabilities", value="?", inline=False) # Index 2
			myEmbed.add_field(name="Effect", value= "?"  , inline=False) # Index 3
			myEmbed.add_field(name="Quote", value= "?" , inline=False) # Index 4
			myEmbed.add_field(name="Cardnumber in Set", value="1", inline=False) # Index 5
			myEmbed.add_field(name="Name from Set", value="default", inline=False) # Index 6
			myEmbed.add_field(name="Language", value="en", inline=False) # Index 7
			myEmbed.add_field(name="Filename", value=f"{artwork_filename}", inline=False) # Index 8
			myEmbed.add_field(name="Override", value=f"{False}", inline=False) # Index 9
			myEmbed.add_field(name="3D-Effect", value="0", inline=False) # Index 10
			myEmbed.set_footer(text="http://mindbug.me")
			await interaction.followup.send(embed=myEmbed, view=EditMenu())
		else:
			await interaction.response.send_message(f'No File')
	except Exception as e:
		print("Error on Create Crature Card:" + str(e))
		await interaction.followup.send(f"I choked and had to abort.")

@tree.command(name = "editcreature", description = "Edit a Creature Card.")
async def editcreaturecard(interaction: discord.Interaction, name: str, cardset:str ):
	try:
		if (name):
			userid = interaction.user.id

			# The first answer must be given within 3sec.
			await interaction.response.defer(ephemeral=True, thinking=True)
			# From now on we have 15 minutes
			
			#Get all cards from user
			db = mongodb["cardcreator"]
			card = db["customcreatures"].find_one(filter={ "user_id": userid, "name": name ,"cardset": cardset})

			# Create the Mindbug-Card
			myEmbed = discord.Embed(title=CARD_GENERATOR_APP_NAME, url=BUG_TRACKING_URL,color = discord.Color.random(), description=embed_description)
			myEmbed.add_field(name="Name", value="{}".format(card["name"]), inline=True) # Index 0
			myEmbed.add_field(name="Power", value="{}".format(card["power"]), inline=False) # Index 1
			myEmbed.add_field(name="Capabilities", value="{}".format(card["keywords"] if (card["keywords"] != "") else "?"), inline=False) # Index 2
			myEmbed.add_field(name="Effect", value= "{}".format(card["effect"] if (card["effect"] != "") else "?"), inline=False) # Index 3
			myEmbed.add_field(name="Quote", value= "{}".format(card["quote"] if (card["quote"] != "") else "?"), inline=False) # Index 4
			myEmbed.add_field(name="Cardnumber in Set", value="{}".format(card["uid_from_set"]), inline=False) # Index 5
			myEmbed.add_field(name="Name from Set", value="{}".format(card["cardset"]), inline=False) # Index 6
			myEmbed.add_field(name="Language", value="{}".format(card["lang"]), inline=False) # Index 7
			myEmbed.add_field(name="Filename", value="{}".format(card["filename"]), inline=False) # Index 8
			myEmbed.add_field(name="Override", value=f"{True}", inline=False) # Index 9

			# This is necessary, because this field is missing by old cards in the db
			if "use_3d_effect" in card:
				myEmbed.add_field(name="3D-Effect", value="{}".format(card["use_3d_effect"] if (card["use_3d_effect"] != "") else "0"), inline=False) # Index 10
			else:
				myEmbed.add_field(name="3D-Effect", value="0", inline=False) # Index 10

			myEmbed.set_footer(text="http://mindbug.me")
			await interaction.followup.send(embed=myEmbed, view=EditMenu())
		else:
			await interaction.response.send_message(f'No Card found')
	except Exception as e:
		print("Error on Edit Creature Card:" + str(e))
		await interaction.followup.send(f"I choked and had to abort.")


@client.event
async def on_ready():

	print("Loading assets...")
	# Load the Cardframes from the assets-Folder
	cardgenerator.card_frame_normal, cardgenerator.card_frame_mindbug = cardgenerator.LoadingCardFrames()

	# Load the Fonts from the assets-Folder
	cardgenerator.name_font_52, cardgenerator.name_font_42, cardgenerator.name_font_20, cardgenerator.trigger_and_capabilites_font, cardgenerator.description_font, cardgenerator.quote_font, cardgenerator.card_key_font_18, cardgenerator.power_font = cardgenerator.LoadingFonts()

	# Download Model for 3D-Effect
	cardgenerator.LoadingModelforRembg()

	print("Sync commands on all discord server...")
	#Sync the commands with all server
	await tree.sync()
	print("Ready!")

with open('token.txt') as f:
	token=f.read()

client.run(token)
