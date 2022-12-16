import os, cv2, base64
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageOps
from pathlib import Path
from models import Card

optimize_pngs:bool = True
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
card_frame_normal = None
card_frame_mindbug = None
name_font_52 = None
name_font_42 = None
name_font_20 = None
trigger_and_capabilites_font = None
description_font = None
quote_font = None
card_key_font_18 = None
power_font = None
trigger_words_from_mindbug = (  "Play:", "Ausspielen:",
                                "Attack:", "Angreifen:",
                                "Defeat:","Besiegt:",
                                "Block:", "Blocken:",
                                "Unblocked:", "Ungeblockt:"
                                "Draw:", "Ziehen:"
                                )

#region HELPER FUNC
def LoadingCardFrames():
    print("Loading card frames:")
    # Open frame for normal card and Convert image to RGBA
    card_frame_normal = Image.open(os.path.join(__location__, "assets/NormalCardTemplate.png"))
    card_frame_normal = card_frame_normal.resize((816, 1110),resample= Image.Resampling.LANCZOS)
    card_frame_normal = card_frame_normal.convert("RGBA")
    # Open frame for mindbug card and Convert image to RGBA
    card_frame_mindbug = Image.open(os.path.join(__location__, "assets/MindbugCardTemplate.png"))
    card_frame_mindbug = card_frame_mindbug.resize((816, 1110),resample= Image.Resampling.LANCZOS)
    card_frame_mindbug = card_frame_mindbug.convert("RGBA")
    print("Loading card frames: SUCESSFULL.")
    return card_frame_normal, card_frame_mindbug

def LoadingFonts():
    print("Loading card fonts:")
    fontPath = __location__ +"/assets/ZalamanderCaps-Extrabold.otf"
    name_font_52 = ImageFont.truetype(fontPath,52)
    name_font_42 = ImageFont.truetype(fontPath,42)
    name_font_20 = ImageFont.truetype(fontPath,20)

    trigger_and_capabilites_font = ImageFont.truetype(__location__ + "/assets/Brandon_blk.otf",32)

    description_font = ImageFont.truetype( __location__ + "/assets/Brandon_med.otf",32)

    quote_font = ImageFont.truetype( __location__ + "/assets/Graphit-ThinItalic.otf", 32) # TODO: Brandon Italic Fonts

    card_key_font_18 = ImageFont.truetype( __location__ + "/assets/Brandon_blk.otf",16) # TODO: maybe in Bold? check Prints

    power_font = ImageFont.truetype( __location__ + "/assets/Graphit-Black.otf" ,76)
    print("Loading card fonts: SUCESSFULL.")
    return name_font_52, name_font_42, name_font_20, trigger_and_capabilites_font, description_font, quote_font, card_key_font_18, power_font

def text_wrap(text, font, max_width):
        """Wrap text base on specified width. 
        This is to enable text of width more than the image width to be display
        nicely.
        @params:
            text: str
                text to wrap
            font: obj
                font of the text
            max_width: int
                width to split the text with
        @return
            lines: list[str]
                list of sub-strings
        """
        lines = []
        
        # If the text width is smaller than the image width, then no need to split
        # just add it to the line list and return
        if font.getlength(text)  <= max_width:
            lines.append(text)
        else:
            #split the line by spaces to get words
            words = text.split(' ')
            
            i = 0
            # append every word to a line while its width is shorter than the image width
            while i < len(words):
                line = ''

                while i < len(words) and font.getlength(line + words[i]) <= max_width:
                    line = line + words[i]+ " "
                    i += 1
                if not line:
                    line = words[i]
                    i += 1
                lines.append(line)

            # A try to put Triggerwords in a new line
            # inserts = {}
            # for index_from_line in range(len(lines)):
            #     tmp = lines[index_from_line].split(":")
            #     inserts.update(index_from_line, tmp)
            
            # for key in inserts:
            #     lines.insert(key, insert[key])

        return lines

def cleanup_triggers(myTriggers):    
    """Remove unneccassary stuff from List[str]
    @params:
        text: List[str]
            List to clean
    @return
        lines: list[str]
            Cleaned list
    """
    # Remove unneccasary elements
    myTriggers = list(filter(None, myTriggers))
    myTriggers = list(filter(bool, myTriggers))
    myTriggers = list(filter(len, myTriggers))
    myTriggers = list(filter(lambda item: item, myTriggers))

    # Remove whitestpaces
    myTriggers = [item.strip() for item in myTriggers]
        
    return myTriggers
#endregion

# TODO: Safe all Input Images (Artwork, Set-Icon) as Base64 and use it in this Function
def CreateAMindbugCard(artwork_filename: str, lang: str, cardset: str, uid_from_set: str):
    print("Beam a Mindbug to the World.")
    
    pathname, extension = os.path.splitext(artwork_filename)	
    myCard = Card(
        uid_from_set=uid_from_set,
        lang=lang,
        cardset=cardset,
        name="MINDBUG",
        power = "",
        keywords = "",
        effect = "",
        quote = "",
        image_path=artwork_filename,
        filename=pathname.split('/')[-1]
    )

    # Empty Card
    newCardBackground = Image.new("RGBA", (816,1110), (0,0,0,0))
    
    # CREATURE
    creature_image = Image.open(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"{artwork_filename}"))
    creature_image = creature_image.resize((744, 1038),resample= Image.Resampling.LANCZOS)
    creature_image = creature_image.convert("RGBA")

    # Create a Blurred Background so that we have a safe cutting area.
    creature_image_blurred = creature_image.resize((816, 1110),resample= Image.Resampling.LANCZOS)
    creature_image_blurred = creature_image_blurred.convert("RGBA")
    creature_image_blurred = creature_image_blurred.filter(ImageFilter.BoxBlur(48))
    
    # Calculate width to be at the center
    x_pos = (newCardBackground.width - creature_image_blurred.width) // 2
    
    # Calculate height to be at the center
    y_pos = (newCardBackground.height - creature_image_blurred.height) // 2
    
    # Paste the Blurred Background at center
    newCardBackground.paste(creature_image_blurred, (x_pos, y_pos), creature_image_blurred)

    # Calculate width to be at the center
    x_pos = (newCardBackground.width - creature_image.width) // 2

    # Calculate height to be at the center
    y_pos = (newCardBackground.height - creature_image.height) // 2
    
    # Paste the CardFrame at center
    newCardBackground.paste(creature_image, (x_pos, y_pos), creature_image)


    # FRAME
    # Calculate width to be at the center
    x_pos = (newCardBackground.width - card_frame_mindbug.width) // 2

    # Calculate height to be at the center
    y_pos = (newCardBackground.height - card_frame_mindbug.height) // 2
    
    # Paste the CardFrame at center
    newCardBackground.paste(card_frame_mindbug, (x_pos, y_pos), card_frame_mindbug)

    # Create a Editable Image
    card_editable = ImageDraw.Draw(newCardBackground)
    
    # Create the Name
    card_editable.text((newCardBackground.size[0]/2,138), "MINDBUG", fill="white", font=name_font_52, anchor="mm" )

    #region CARDNUMBER AND SET LOGO
    # The Logo must be an black Icon with transparent Background and name like the Cardset Name with prefix: cardset_<CardsetName>.png
    
    # If a Set-Logo exists, then load it
    logo_path = os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"cardset_{myCard.cardset}.png")
    set_logo_exist = os.path.exists(logo_path)

    if (set_logo_exist):
        set_logo = Image.open(logo_path)
        # Resize Set Logo
        set_logo = set_logo.resize((24, 24),resample= Image.Resampling.LANCZOS)
        set_logo = set_logo.convert("RGBA")
        
        # Save Set Icon as Base64 String
        with BytesIO() as image_binary:
            set_logo.save(image_binary,format="png", dpi = (300,300))
            image_binary.seek(0)
            image_as_base64 =  base64.b64encode(image_binary.getvalue()).decode()
            myCard.set_icon_base64 = image_as_base64


    # Calculate the Position for the Logo
    x_pos = newCardBackground.width*2//3 + 40
    y_pos = newCardBackground.height-60
    
    # Should the uid_from_set printed in white or black according the actual given color on pixel
    pixel_information =  newCardBackground.getpixel((x_pos + 15,y_pos))
    if ( pixel_information[0]< 120 and pixel_information[1]< 120 and pixel_information[2]< 120 ):
        
        # Add the Card-uid_from_set
        card_editable.text((x_pos + 15,y_pos), myCard.uid_from_set, fill="white", font=card_key_font_18,anchor="lm" , align="right")
        
        if(set_logo_exist):
            # Convert the black into white
            triggers,g,b,a = set_logo.split()
            rgb_image = Image.merge('RGB', (triggers,g,b))
            inverted_image = ImageOps.invert(rgb_image)
            r2,g2,b2 = inverted_image.split()
            inverted_set_logo = Image.merge('RGBA', (r2,g2,b2,a))
            
            # Add the Logo
            newCardBackground.paste(inverted_set_logo, (int(x_pos - 15),int(y_pos - 12 )), inverted_set_logo)

    else:
        # Add the Card-uid_from_set
        card_editable.text((x_pos + 15,y_pos), myCard.uid_from_set, fill="black", font=card_key_font_18,anchor="lm" , align="right")
        
        if(set_logo_exist):
            # Add the Logo
            newCardBackground.paste(set_logo, (int(x_pos - 15),int(y_pos - 12 )), set_logo)

    # Save the final card
    card_folder = os.path.join(os.getenv('CARD_OUTPUT_FOLDER'), f"{myCard.cardset}", f"{myCard.lang}")
    Path(card_folder).mkdir(parents=True, exist_ok=True)
    newCardBackground.save(os.path.join(card_folder, f"{myCard.filename}.png"), format="png", dpi = (300,300), optimize= optimize_pngs)
    
    # Save final Card as Base64 String
    with BytesIO() as image_binary:
        newCardBackground.save(image_binary,format="png", dpi = (300,300))
        image_binary.seek(0)
        image_as_base64 =  base64.b64encode(image_binary.getvalue()).decode()
        myCard.cropped_final_card_base64 = image_as_base64

    #endregion

    #region SAVE CROPPED CARD

    # Open a Black Safe Area as Mask to crop the image and transform black to transparent
    mask = Image.open(__location__ + "/assets/SafeAreaMask.png")
    mask = mask.resize((816, 1110),resample= Image.Resampling.LANCZOS)
    mask = mask.convert("RGBA")

    # Calculate width to be at the center
    x_pos = (newCardBackground.width - mask.width) // 2

    # Calculate height to be at the center
    y_pos = (newCardBackground.height - mask.height) // 2

    # Add the Safe Area
    newCardBackground.paste(mask, (x_pos, y_pos), mask)

    left = (newCardBackground.size[0] - 744)/2
    top  = (newCardBackground.size[1] - 1038)/2
    right = 744 + left
    bottom = 1038 + top
    final_card_without_sage_area = newCardBackground.crop((left, top, right, bottom))
    
    newCardBackground.close()

    tmp_path = os.path.join(os.getenv('CARD_OUTPUT_FOLDER'), str(myCard.cardset), str(myCard.lang), "cropped", str(myCard.image_path))
    Path(os.path.join(os.getenv('CARD_OUTPUT_FOLDER'), str(myCard.cardset), str(myCard.lang), "cropped")).mkdir(parents=True, exist_ok=True)
    final_card_without_sage_area.save(tmp_path, format="png", dpi = (300,300))
    final_card_without_sage_area.close()

    # Read the tmp Image with cv2 form Transformint black to transparent
    src = cv2.imread(tmp_path, 1)
    # Convert image to image gray
    tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    
    # Applying thresholding technique
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    
    # Using cv2.split() to split channels 
    # of coloured image
    b, g, pixel_information = cv2.split(src)
    
    # Making list of Red, Green, Blue
    # Channels and alpha
    rgba = [b, g, pixel_information, alpha]
    
    # Using cv2.merge() to merge rgba
    # into a coloured/multi-channeled image
    dst = cv2.merge(rgba, 4)
    
    # Writing and saving to a new image
    cv2.imwrite(tmp_path, dst)

    # Restore missing black Pixel on the regular Card
    card_backup_background = Image.open(os.path.join(__location__, "assets/BackupCardBackground.png"))
    card_backup_background = card_backup_background.resize((744, 1038),resample= Image.Resampling.LANCZOS)
    card_backup_background = card_backup_background.convert("RGBA")
    
    clean_card = Image.open(tmp_path)
    clean_card = clean_card.convert("RGBA")
    # Calculate width to be at the center
    x_pos = (card_backup_background.width - clean_card.width) // 2

    # Calculate height to be at the center
    y_pos = (card_backup_background.height - clean_card.height) // 2

    # Paste the frontImage at (width, height)
    card_backup_background.paste(clean_card, (x_pos, y_pos), clean_card)
    card_backup_background.save(tmp_path,format="png", dpi = (300,300), optimize= optimize_pngs)

    # Save cropped final Card as Base64 String
    with BytesIO() as image_binary:
        card_backup_background.save(image_binary,format="png", dpi = (300,300))
        image_binary.seek(0)
        image_as_base64 =  base64.b64encode(image_binary.getvalue()).decode()
        myCard.cropped_final_card_base64 = image_as_base64

    clean_card.close()
    #endregion

    return card_backup_background, myCard

# This Function Create a Card from a given File
# TODO: Create a Edit Function wich use a Base64 String
def CreateACreatureCard(artwork_filename: str, lang: str, cardset: str, uid_from_set: str, name: str, power: str, keywords:str = None, effect:str = None, quote:str= None):
   
    pathname, extension = os.path.splitext(artwork_filename)	

    if (keywords is None):
        keywords = ""

    if (effect is None):
        effect = ""

    if (quote is None):
        quote = ""

    myCard = Card(
        uid_from_set=uid_from_set,
        lang=lang,
        name=name,
        power = power,
        keywords=keywords,
        effect = effect,
        quote = quote,
        image_path=artwork_filename,
        filename=name,
        cardset=cardset
    )

    print(f"Cooking Creature '{myCard.name}'")
    
    # Empty Card
    newCardBackground = Image.new("RGBA",(816,1110), (0,0,0,0))
    
    # CREATURE AND BLURRED BACKGROUND
    creature_image = Image.open(os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"{artwork_filename}"))
    creature_image = creature_image.resize((744, 1038),resample= Image.Resampling.LANCZOS)
    creature_image = creature_image.convert("RGBA")

    # Save Artwork as Base64 String
    with BytesIO() as image_binary:
        creature_image.save(image_binary,format="png", dpi = (300,300))
        image_binary.seek(0)
        image_as_base64 =  base64.b64encode(image_binary.getvalue()).decode()
        myCard.artwork_base64 = image_as_base64

    # Create a Blurred Background so that we have a safe cutting area.
    creature_image_blurred = creature_image.resize((816, 1110),resample= Image.Resampling.LANCZOS)
    creature_image_blurred = creature_image_blurred.convert("RGBA")
    creature_image_blurred = creature_image_blurred.filter(ImageFilter.BoxBlur(48))
    
    # Calculate width to be at the center
    x_pos = (newCardBackground.width - creature_image_blurred.width) // 2
    
    # Calculate height to be at the center
    y_pos = (newCardBackground.height - creature_image_blurred.height) // 2
    
    # Paste the Blurred Background at center
    newCardBackground.paste(creature_image_blurred, (x_pos, y_pos), creature_image_blurred)
    
        # Calculate width to be at the center
    x_pos = (newCardBackground.width - creature_image.width) // 2
    
    # Calculate height to be at the center
    y_pos = (newCardBackground.height - creature_image.height) // 2
    # Paste the Artwork at center
    newCardBackground.paste(creature_image, (x_pos, y_pos), creature_image)

    # For the Future, requires "from rembg import remove"
    # creature_image_clean = None
    # if(myCard.use_3d_effect != ""):
    #     creature_image_clean = remove(creature_image.copy()) # With this copy, we can build a depth-effect  

    # FRAME
    # Calculate width to be at the center
    x_pos = (newCardBackground.width - card_frame_normal.width) // 2

    # Calculate height to be at the center
    y_pos = (newCardBackground.height - card_frame_normal.height) // 2
    
    # Paste the CardFrame at center
    newCardBackground.paste(card_frame_normal, (x_pos, y_pos), card_frame_normal)

    # Create a Editable Image
    card_editable = ImageDraw.Draw(newCardBackground)
    
    # Create the Name
    # If normal Name Font Size greater then Namefield use a smaller Font Size.
    name_length = name_font_52.getlength(myCard.name.upper())
    if (name_length <= card_frame_normal.width - 350):
        card_editable.text((240,138), myCard.name.upper(), fill="white", font=name_font_52, anchor="lm" )
    else:
        card_editable.text((240,138), myCard.name.upper(), fill="white", font=name_font_42, anchor="lm" )

    # Power
    card_editable.text((145,125), myCard.power, fill="white", font=power_font,anchor="mm" )

    #region TEST FOR 3D DEPTH-EFFECT, HIDDEN PARTS OF THE NAME FIELD WITH CREATURE BY GIVEN BOOL
    # For the Future, when we can Edit a card
    # if(myCard.use_3d_effect != ""):
    #     # 1. CROP THE MONSTER 1/4 or 1/2
    #     if(myCard.use_3d_effect == "1"):    
    #         left = 0
    #         top = 0
    #         right = creature_image_clean.size[0]
    #         bottom = creature_image_clean.size[1]//2
    #         creature_image_clean = creature_image_clean.crop((left, top, right, bottom)).resize((744, 1038//2),resample= Image.Resampling.BICUBIC)

    #         # 2. PASTE THE new IMAGE
    #         x = (816-744)//2 #newCardBackground.size[0]//2 
    #         y = y_pos + (1110-1038)//2

    #     elif (myCard.use_3d_effect == "2"):    
    #         left = creature_image_clean.size[0]//2
    #         top = 0
    #         right = creature_image_clean.size[0]
    #         bottom = creature_image_clean.size[1]//2
    #         creature_image_clean = creature_image_clean.crop((left, top, right, bottom)).resize((744//2, 1038//2),resample= Image.Resampling.BICUBIC)

    #         # 2. PASTE THE new IMAGE
    #         x = newCardBackground.size[0]//2 
    #         y = y_pos + (1110-1038)//2
        
    #     if( not playtestMode):
    #         newCardBackground.paste(creature_image_clean,(x,y), creature_image_clean)
    #endregion


    # Calculate max Width from Textarea
    max_text_area_width_on_card = card_frame_normal.width - 220

    # Keywords
    position_of_text_end_in_y = newCardBackground.height/2+255
    capabilities = text_wrap(myCard.keywords.upper(), trigger_and_capabilites_font,max_text_area_width_on_card )
    i = 0
    for line in capabilities:
        # Calculate the new Text position
        if (i != 0):
            position_of_text_end_in_y += 40

        card_editable.text((newCardBackground.width/2,position_of_text_end_in_y), line, fill="white", font=trigger_and_capabilites_font, anchor="mm" )
        i  += 1

    #region DESCRIPTION    
    if (capabilities[0] != ""):
        # Add Offset between Keywords and Description
        position_of_text_end_in_y += 50
    else:
        # Offset between Textboxborder and Descripton
        position_of_text_end_in_y += 40

    # Split the description to # to detect the triggers
    triggers = cleanup_triggers(myCard.effect.split("#"))

    more_than_one_trigger = False
    for triggersentence in triggers:

        if more_than_one_trigger:
            position_of_text_end_in_y += 40

        descriptionlines = text_wrap(triggersentence,description_font, max_text_area_width_on_card)
        # IDEA:
        # Calculate the Text height, then check if its fit on the card
        # Maybe use a smaller font.
        # max_height = description_font.getbbox(lines[0]) * lines.count
        i = 0
        for line in descriptionlines:
            # Calculate the new Text position
            if (i != 0):
                position_of_text_end_in_y += 40

            trigger_word = line.split(" ")[0]

            if trigger_word in trigger_words_from_mindbug:
                line_length = description_font.getlength(line)
                trigger_word_length = trigger_and_capabilites_font.getlength(trigger_word)
                x_pos_trigger = newCardBackground.width//2 - line_length//2 + trigger_word_length//2

                x_pos_rest = newCardBackground.width//2 + trigger_word_length//2 + 4 #offset 4px

                # Remove Triggerword from line for seperate printing
                line = line.replace(trigger_word, "").strip()
                # Printing
                card_editable.text((x_pos_trigger,position_of_text_end_in_y), trigger_word, fille="white", font=trigger_and_capabilites_font,anchor="mm" )
                card_editable.text((x_pos_rest,position_of_text_end_in_y), line, fille="white", font=description_font,anchor="mm" )
            else:
                card_editable.text((newCardBackground.width//2,position_of_text_end_in_y), line, fille="white", font=description_font,anchor="mm" )

            i += 1
        more_than_one_trigger = True
    #endregion

    #region QUOATES
    if (myCard.keywords != "" and myCard.effect != ""):
        position_of_text_end_in_y += 50
    else:
        position_of_text_end_in_y += 45

    quotes = text_wrap(myCard.quote, quote_font, max_text_area_width_on_card)

    i = 0
    for line in quotes:
        # Calculate the new Text position
        if (i != 0):
            position_of_text_end_in_y += 40

        card_editable.text((newCardBackground.width/2,position_of_text_end_in_y), line, fille="white", font=quote_font,anchor="mm" )
        i += 1
    #endregion


    #region CARDNUMBER AND SET LOGO
    # The Logo must be an black Icon with transparent Background and name like the Cardset Name with prefix: cardset_<CardsetName>.png
    
    # If a Set-Logo exists, then load it    
    logo_path = os.path.join(os.getenv('ASSETS_UPLOAD_FOLDER'), f"cardset_{myCard.cardset}.png")
    set_logo_exist = os.path.exists(logo_path)

    if (set_logo_exist):
        set_logo = Image.open(logo_path)
        # Resize Set Logo
        set_logo = set_logo.resize((24, 24),resample= Image.Resampling.LANCZOS)
        set_logo = set_logo.convert("RGBA")
        
        # Save Set Icon as Base64 String
        with BytesIO() as image_binary:
            set_logo.save(image_binary,format="png", dpi = (300,300))
            image_binary.seek(0)
            image_as_base64 =  base64.b64encode(image_binary.getvalue()).decode()
            myCard.set_icon_base64 = image_as_base64


    # Calculate the Position for the Logo
    x_pos = newCardBackground.width*2//3 + 40
    y_pos = newCardBackground.height-60
    
    # Should the uid_from_set printed in white or black according the actual given color on pixel
    pixel_information =  newCardBackground.getpixel((x_pos + 15,y_pos))
    if ( pixel_information[0]< 120 and pixel_information[1]< 120 and pixel_information[2]< 120 ):
        
        # Add the Card-uid_from_set
        card_editable.text((x_pos + 15,y_pos), myCard.uid_from_set, fill="white", font=card_key_font_18,anchor="lm" , align="right")
        
        if(set_logo_exist):
            # Convert the black into white
            triggers,g,b,a = set_logo.split()
            rgb_image = Image.merge('RGB', (triggers,g,b))
            inverted_image = ImageOps.invert(rgb_image)
            r2,g2,b2 = inverted_image.split()
            inverted_set_logo = Image.merge('RGBA', (r2,g2,b2,a))
            
            # Add the Logo
            newCardBackground.paste(inverted_set_logo, (int(x_pos - 15),int(y_pos - 12 )), inverted_set_logo)

    else:
        # Add the Card-uid_from_set
        card_editable.text((x_pos + 15,y_pos), myCard.uid_from_set, fill="black", font=card_key_font_18,anchor="lm" , align="right")
        
        if(set_logo_exist):
            # Add the Logo
            newCardBackground.paste(set_logo, (int(x_pos - 15),int(y_pos - 12 )), set_logo)

    # Save the final card
    card_folder = os.path.join(os.getenv('CARD_OUTPUT_FOLDER'), f"{myCard.cardset}", f"{myCard.lang}")
    Path(card_folder).mkdir(parents=True, exist_ok=True)
    newCardBackground.save(os.path.join(card_folder, f"{myCard.filename}.png"), format="png", dpi = (300,300), optimize= optimize_pngs)

    # Save final Card as Base64 String
    with BytesIO() as image_binary:
        newCardBackground.save(image_binary,format="png", dpi = (300,300))
        image_binary.seek(0)
        image_as_base64 =  base64.b64encode(image_binary.getvalue()).decode()
        myCard.final_card_base_64 = image_as_base64
    #endregion

    #region SAVE CROPPED CARD

    # Open a Black Safe Area as Mask to crop the image and transform black to transparent
    mask = Image.open(__location__ + "/assets/SafeAreaMask.png")
    mask = mask.resize((816, 1110),resample= Image.Resampling.LANCZOS)
    mask = mask.convert("RGBA")

    # Calculate width to be at the center
    x_pos = (newCardBackground.width - mask.width) // 2

    # Calculate height to be at the center
    y_pos = (newCardBackground.height - mask.height) // 2

    # Add the Safe Area
    newCardBackground.paste(mask, (x_pos, y_pos), mask)

    left = (newCardBackground.size[0] - 744)/2
    top  = (newCardBackground.size[1] - 1038)/2
    right = 744 + left
    bottom = 1038 + top
    final_card_without_sage_area = newCardBackground.crop((left, top, right, bottom))
    
    newCardBackground.close()
    
    tmp_path = os.path.join(os.getenv('CARD_OUTPUT_FOLDER'), str(myCard.cardset), str(myCard.lang), "cropped", str(myCard.image_path))
    Path(os.path.join(os.getenv('CARD_OUTPUT_FOLDER'), str(myCard.cardset), str(myCard.lang))).mkdir(parents=True, exist_ok=True)
    final_card_without_sage_area.save(tmp_path, format="png", dpi = (300,300))
    final_card_without_sage_area.close()

    # Read the tmp Image with cv2 form Transformint black to transparent
    src = cv2.imread(tmp_path, 1)
    # Convert image to image gray
    tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    
    # Applying thresholding technique
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    
    # Using cv2.split() to split channels 
    # of coloured image
    b, g, pixel_information = cv2.split(src)
    
    # Making list of Red, Green, Blue
    # Channels and alpha
    rgba = [b, g, pixel_information, alpha]
    
    # Using cv2.merge() to merge rgba
    # into a coloured/multi-channeled image
    dst = cv2.merge(rgba, 4)
    
    # Writing and saving to a new image
    cv2.imwrite(tmp_path, dst)

    # Restore missing black Pixel on the regular Card
    card_backup_background = Image.open(os.path.join(__location__, "assets/BackupCardBackground.png"))
    card_backup_background = card_backup_background.resize((744, 1038),resample= Image.Resampling.LANCZOS)
    card_backup_background = card_backup_background.convert("RGBA")
    
    clean_card = Image.open(tmp_path)
    clean_card = clean_card.convert("RGBA")
    # Calculate width to be at the center
    x_pos = (card_backup_background.width - clean_card.width) // 2

    # Calculate height to be at the center
    y_pos = (card_backup_background.height - clean_card.height) // 2

    # Paste the frontImage at (width, height)
    card_backup_background.paste(clean_card, (x_pos, y_pos), clean_card)
    card_backup_background.save(tmp_path,format="png", dpi = (300,300), optimize= optimize_pngs)

    # Save cropped final Card as Base64 String
    with BytesIO() as image_binary:
        card_backup_background.save(image_binary,format="png", dpi = (300,300))
        image_binary.seek(0)
        image_as_base64 =  base64.b64encode(image_binary.getvalue()).decode()
        myCard.final_card_base_64 = image_as_base64

    #endregion

    clean_card.close()

    return card_backup_background, myCard
