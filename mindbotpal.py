import os
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import Canvas, PhotoImage, filedialog

import discord
import ttkbootstrap as ttk
from discord import SyncWebhook
from PIL import Image, ImageTk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Querybox

import cardgenerator
from models import Card, ThreeDEffectKind

__location__:str = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__title__:str = "MindbotPal"
__appsize__= (850,750)

# HELPER FUNCS
def on_focus_in(entry):
    # if entry.cget('state') == 'disabled':
    entry.delete(0, 'end')


def on_focus_out(entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)
        # entry.configure(state='disabled')

def validate_name(x) -> bool:
    """Validates that the input from name"""
    if len(x) > 24:
        return False
    elif x == "":
        return True
    else:
        return True

#

class Splashscreen(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.my_size = (600,350)
    
        self.overrideredirect(True) #Hide the Titlebar
        self.geometry(f"+{self.winfo_screenwidth()//2-self.my_size[0]//2}+{self.winfo_screenheight()//2-self.my_size[1]//2}")
        self.size = self.my_size
        self.splash_frame = ttk.Frame(self, padding=10)
        self.splash_frame.pack(fill=BOTH, expand=True)
        self.splash_canvas = ttk.Canvas(self.splash_frame, width=self.my_size[0], height=self.my_size[1]-50)
        self.splash_canvas.pack()

        self.splash_image = ImageTk.PhotoImage(Image.open(os.path.join(__location__+"\\assets\\splashscreen.png")).resize((self.my_size[0], self.my_size[1]-50),resample= Image.Resampling.LANCZOS).convert("RGBA"))
        self.splash_canvas.create_image(0,0, anchor=NW, image = self.splash_image)

        self.splash_floodgauge = ttk.Floodgauge(self.splash_frame, length=600, text="Loading ...",bootstyle="success")
        #self.splash_floodgauge = ttk.Progressbar(self.splash_frame, length=600,bootstyle="danger-striped")
        self.splash_floodgauge.pack(side="bottom")
        ## required to make window show before the program gets to the mainloop
        self.update()

class Creator(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        app.withdraw()
        splash = Splashscreen(self)
        splash.title(__title__)
        splash.splash_floodgauge.start()

        # Load the Cardframes from the assets-Folder
        cardgenerator.card_frame_normal, cardgenerator.card_frame_mindbug = cardgenerator.LoadingCardFrames()

        # Load the Fonts from the assets-Folder
        cardgenerator.name_font_52, cardgenerator.name_font_42, cardgenerator.name_font_20, cardgenerator.trigger_and_capabilites_font, cardgenerator.description_font, cardgenerator.quote_font, cardgenerator.card_key_font_18, cardgenerator.power_font = cardgenerator.LoadingFonts()

        # Download Model for 3D-Effect
        cardgenerator.LoadingModelforRembg()

        self.pack(fill=BOTH, expand=YES)

        app.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.active_frame:str="cards"

        self.webhook = SyncWebhook.from_url(os.getenv('DISCORD_WEBHOOK'))

        self.edit_card_index:int = None
        self.customcards = []
        
        self.read_customcards_local_db()
        
        print(f"Count custom cards: {len(self.customcards)}")

        ## finished loading so destroy splash
        splash.splash_floodgauge.stop()
        splash.destroy()

        ## show window again
        app.deiconify()

        if( os.getenv("DISCORD_USER_NAME") is None):
            res =  Querybox.get_string(prompt='If you want to Share your Cards with Discord.\n Please tell us your Discord-Username?', title='Username', initialvalue=None, parent=master) 
            if res != None:
                os.environ['DISCORD_USER_NAME'] = res


        self.card_name:tk.StringVar = tk.StringVar(self, name="card_name")
        self.card_power:tk.StringVar = tk.StringVar(self,name="card_power")
        self.card_capabilities:tk.StringVar = tk.StringVar(self,name="card_capabilities")
        self.card_effect:tk.StringVar = tk.StringVar(self,name="card_effect")
        self.card_quote:tk.StringVar = tk.StringVar(self,name="card_quote")
        self.card_lang:tk.StringVar = tk.StringVar(self,name="card_lang")
        self.card_cardset:tk.StringVar = tk.StringVar(self,name="card_set")
        self.card_cardnumber:tk.StringVar = tk.StringVar(self,name="card_cardnumber")
        self.card_author:tk.StringVar = tk.StringVar(self,name="card_author")
        self.card_artwork_filename:str = None
        self.discord_user_name:tk.StringVar = tk.StringVar(self, name="discord_user_name")

        # register the validation callback
        self.name_validation = app.register(validate_name)


        for i in range(2):
            self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        

        # load icons
        # TODO: Doesnt work at the Moment
        self.icons = [
            PhotoImage(
                name='home', 
                file= __location__+"\\assets\\home_light.png", 
                width=20, height=20)
        ]

        # create navigation frame - col 1
        self.navigation_frame = ttk.Frame(self, padding=10)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        # self.navigation_frame.grid_rowconfigure(0, weight=1)

        self.cards_button = ttk.Button(self.navigation_frame, bootstyle="primary-outline", text="Cards", width=20,  compound = LEFT , command=self.card_frame_button_event)
        self.cards_button.grid(row=1, column=0, padx=4, pady=4)

        self.home_button = ttk.Button(self.navigation_frame, bootstyle="primary-outline", text="Add", width=20,command=self.home_button_event)
        self.home_button.grid(row=2, column=0, padx=4, pady=4)

        self.sheetcreator_button = ttk.Button(self.navigation_frame, bootstyle="primary-outline", width=20, text="Sheet Creator",command=self.cardsheetcreator_frame_button_event)
        self.sheetcreator_button.grid(row=3, column=0, padx=4, pady=4)

        self.settings_button = ttk.Button(self.navigation_frame, bootstyle="primary-outline", width=20, text="Settings",command=self.settings_frame_button_event)
        self.settings_button.grid(row=4, column=0, padx=4, pady=4)

        # create home frame
        self.home_frame = ttk.Frame(self, padding=10) 
        self.home_frame.grid(row=0, column=1, sticky="nsew")
        self.home_frame.columnconfigure(0, weight=1)
        self.home_frame.columnconfigure(1, weight=1)

        # First Column
        self.card_image_frame = ttk.Frame(self.home_frame, padding=4)
        self.card_image_frame.pack(side="left", fill=Y)
        
        width = self.card_image_frame.winfo_width()
        height = self.card_image_frame.winfo_height()

        self.card_image_canvas = Canvas(self.card_image_frame, width=816//2, height=1110//2)
        self.card_image_canvas.pack()
        self.update_card_image(Image.open(__location__+"\\assets\\cardback.png"))

        # Second Column
        self.card_data_label_frame = ttk.Frame(self.home_frame, padding=4)
        self.card_data_label_frame.pack(side="left", fill=BOTH, expand=True)

        self.card_name_label = ttk.Label(self.card_data_label_frame, text="Name:")
        self.card_name_label.pack(fill=X,padx= 4, pady=4)
        self.card_name_entry = ttk.Entry(self.card_data_label_frame,textvariable=self.card_name, validate="key", validatecommand=(self.name_validation, '%P'))
        self.card_name_entry.pack(fill=X, padx= 4, pady=(0,8))
        self.card_name_entry.insert(0, "Sirus Snape")
        # self.card_name_entry.configure(state='disabled')
        self.card_name_entry_focus_in = self.card_name_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_name_entry))
        self.card_name_entry_focus_out = self.card_name_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_name_entry, 'Sirus Snape'))
        ToolTip(self.card_name_entry, text="Unique name between 1-24 characters.", bootstyle=(INFO, INVERSE))


        self.card_power_label = ttk.Label(self.card_data_label_frame, text="Power:",)
        self.card_power_label.pack(fill=X, padx= 4, pady=4)
        self.card_power_entry = ttk.Entry(self.card_data_label_frame,textvariable=self.card_power, width=80)
        self.card_power_entry.insert(0, "9")
        self.card_power_entry_focus_in = self.card_power_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_power_entry))
        self.card_power_entry_focus_out = self.card_power_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_power_entry, '9'))
        self.card_power_entry.pack(fill=X, padx= 4, pady=(0,8))
        ToolTip(self.card_power_entry, text="Possible characters are numbers 1-9 and X", bootstyle=(INFO, INVERSE))

        
        self.card_capabilities_label = ttk.Label(self.card_data_label_frame, text="Capabilities:")
        self.card_capabilities_label.pack(fill=X, padx= 4, pady=4)        
        self.card_capabilities_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_capabilities,  width=80)
        self.card_capabilities_entry.insert(0, "Frenzy, Tough...")
        self.card_capabilities_entry_focus_in = self.card_capabilities_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_capabilities_entry))
        self.card_capabilities_entry_focus_out = self.card_capabilities_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_capabilities_entry, 'Frenzy, Tough...'))
        self.card_capabilities_entry.pack(fill=X, padx= 4, pady=(0,8))
        ToolTip(self.card_capabilities_entry, text="Possible values are Frenzy, Tough, Poisonous, Hunter, Sneaky and the respective translations into other languages. You are welcome to invent new Capabilites if you need an explanation in the chat. Note: If there is more than one capabilite, there MUST be a space after the comma.", bootstyle=(INFO, INVERSE))


        self.card_effect_label = ttk.Label(self.card_data_label_frame, text="Effect:")
        self.card_effect_label.pack(fill=X, padx= 4, pady=4)        
        self.card_effect_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_effect, width=80)
        self.card_effect_entry.insert(0, "#Play: Draw a card. #Defeat: Gain 1 life point.")
        self.card_effect_entry_focus_in = self.card_effect_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_effect_entry))
        self.card_effect_entry_focus_out = self.card_effect_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_effect_entry, '#Play: Draw a card. #Defeat: Gain 1 life point.'))
        self.card_effect_entry.pack(fill=X, padx= 4, pady=(0,8))
        ToolTip(self.card_effect_entry, text="Everything can be here, but if you want to use triggers you must have a '#' as prefix and a colon with a space ': ' as suffix. Example: '#Play: ' This is needed so that the triggers can be written in bold.", bootstyle=(INFO, INVERSE))


        self.card_quote_label = ttk.Label(self.card_data_label_frame, text="Quote:")
        self.card_quote_label.pack(fill=X, padx= 4, pady=4)
        self.card_quote_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_quote, width=80)
        self.card_quote_entry.pack(fill=X, padx= 4, pady=(0,8))
        self.card_quote_entry.insert(0, "Nothing special")
        self.card_quote_entry_focus_in = self.card_quote_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_quote_entry))
        self.card_quote_entry_focus_out = self.card_quote_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_quote_entry, 'Nothing special'))
        ToolTip(self.card_quote_entry, text="Anything funny can be put here.", bootstyle=(INFO, INVERSE))

        self.card_artwork_label = ttk.Label(self.card_data_label_frame, text="Artwork")
        self.card_artwork_label.pack(fill=X, padx= 4, pady=4)
        self.card_artwork_button = ttk.Button(self.card_data_label_frame, text="SELECT",compound="left", command=self.card_artwork_button_event, width=80)
        self.card_artwork_button.pack(fill=X, padx= 4, pady=(0,8))
        ToolTip(self.card_artwork_button, text="Select a funny and crazy Artwork.", bootstyle=(INFO, INVERSE))

        self.card_metadata_label = ttk.Label(self.card_data_label_frame, text="Metadata", underline=10)
        self.card_metadata_label.pack(fill=X, padx= 4, pady=(10, 8))

        self.card_language_label = ttk.Label(self.card_data_label_frame, text="Language:")
        self.card_language_label.pack(fill=X, padx= 4, pady=4)        
        self.card_language_entry = ttk.Entry(self.card_data_label_frame,textvariable=self.card_lang, width=80)
        self.card_language_entry.insert(0, "en")
        self.card_language_entry_focus_in = self.card_language_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_language_entry))
        self.card_language_entry_focus_out = self.card_language_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_language_entry, 'en'))
        self.card_language_entry.pack(fill=X, padx= 4, pady=(0,8))
        ToolTip(self.card_language_entry, text="Possible values are all ISO code country abbreviations.", bootstyle=(INFO, INVERSE))


        self.card_cardset_label = ttk.Label(self.card_data_label_frame, text="Card Set:")
        self.card_cardset_label.pack(fill=X, padx= 4, pady=4) 
        self.card_cardset_entry = ttk.Entry(self.card_data_label_frame,textvariable=self.card_cardset,  width=80)
        self.card_cardset_entry.insert(0, "default")
        self.card_cardset_entry_focus_in = self.card_cardset_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_cardset_entry))
        self.card_cardset_entry_focus_out = self.card_cardset_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_cardset_entry, 'default'))
        self.card_cardset_entry.pack(fill=X, padx= 4, pady=(0,8))
        ToolTip(self.card_cardset_entry, text="How we call your Set of Cards?", bootstyle=(INFO, INVERSE))

        self.card_cardnumber_label = ttk.Label(self.card_data_label_frame, text="Cardnumber:")
        self.card_cardnumber_label.pack(fill=X, padx= 4, pady=4) 
        self.card_cardnumber_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_cardnumber, width=80)
        self.card_cardnumber_entry.insert(0, "1")
        self.card_cardnumber_entry_focus_in = self.card_cardnumber_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_cardnumber_entry))
        self.card_cardnumber_entry_focus_out = self.card_cardnumber_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_cardnumber_entry, '1'))
        self.card_cardnumber_entry.pack(fill=X, padx= 4, pady=(0,8)) 
        ToolTip(self.card_cardnumber_entry, text="If you have created your own card set give each card a unique number like '1/12'.", bootstyle=(INFO, INVERSE))  
                
        self.card_author_label = ttk.Label(self.card_data_label_frame, text="Author:")
        self.card_author_label.pack(fill=X, padx= 4, pady=4)     
        self.card_author_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_author,width=80)
        self.card_author_entry.insert(0, "Gandalf")
        self.card_author_entry_focus_in = self.card_author_entry.bind('<FocusIn>', lambda x: on_focus_in(self.card_author_entry))
        self.card_author_entry_focus_out = self.card_author_entry.bind('<FocusOut>', lambda x: on_focus_out(self.card_author_entry, 'Gandalf'))
        self.card_author_entry.pack(fill=X, padx= 4, pady=(0,8))
        ToolTip(self.card_author_entry, text="The Author from this Card, will be printed on this.", bootstyle=(INFO, INVERSE))  

        # TODO: Vorschaubutton

        self.home_frame_button_1 = ttk.Button(self.card_data_label_frame, text="SUBMIT",compound="left", command=self.home_frame_submit_button_event, width=80, bootstyle="success")
        self.home_frame_button_1.pack(fill=X, padx= 4, pady=4)

        # created cards frame
        self.cards_frame = ttk.Frame(self)
        self.cards_frame.grid(row=0, column=1, sticky="nsew")
        self.cards_frame.grid_columnconfigure(0, weight=1)

        self.cards_frame_Button_Frame = ttk.Frame(self.cards_frame)
        self.cards_frame_Button_Frame.pack(side="top",padx=4, pady=4)

        self.cards_frame_edit_card_button = ttk.Button(self.cards_frame_Button_Frame, text="Edit",compound="left", command=self.cards_frame_edit_button_event)
        self.cards_frame_edit_card_button.pack(side="left",padx=4, pady=4)

        self.cards_frame_delete_card_button = ttk.Button(self.cards_frame_Button_Frame, text="Delete",compound="left", command=self.cards_frame_delete_button_event)
        self.cards_frame_delete_card_button.pack(side="left",padx=4, pady=4)


        self.cards_frame_export_card_button = ttk.Button(self.cards_frame_Button_Frame, text="Share with Discord",compound="left", command=self.cards_frame_export_button_event)

        if os.getenv("DISCORD_USER_NAME") is None:
            self.cards_frame_export_card_button.configure(state='disabled')

        self.cards_frame_export_card_button.pack(side="right",padx=4, pady=4)

        self.listbox = tk.Listbox(self.cards_frame, selectmode=tk.SINGLE)
        self.listbox.pack(expand=True,side="left", fill=tk.BOTH, padx=4, pady=4)

        self.update_card_frame_listbox()
        
        scrollbar = ttk.Scrollbar(self.listbox, command=self.listbox.yview)
        scrollbar.pack(side="right", fill=tk.Y, padx=4, pady=4)
        
        self.cardsheetcreator_frame = ttk.Frame(self)
        self.cardsheetcreator_frame.grid(row=0, column=1, sticky="nsew")
        self.cardsheetcreator_frame.grid_columnconfigure(0, weight=1)
        self.cardsheetcreator_frame_label = ttk.Label(self.cardsheetcreator_frame, text="Coming soon.")
        self.cardsheetcreator_frame_label.pack(fill=BOTH, expand=True)


        self.settings_frame = ttk.Frame(self)
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.discord_user_name_label = ttk.Label(self.settings_frame, text="Discord Username:")
        self.discord_user_name_label.pack(fill=X, padx= 4, pady=4)     
        self.discord_user_name_entry = ttk.Entry(self.settings_frame, textvariable=self.discord_user_name,width=80)
        
        if ( os.getenv("DISCORD_USER_NAME") is None or len(str(os.getenv("DISCORD_USER_NAME"))) == 0):
            self.discord_user_name_entry.insert(0, "Frodo")
        else:
            self.discord_user_name_entry.insert(0, os.getenv("DISCORD_USER_NAME"))

        self.discord_user_name_focus_in = self.card_author_entry.bind('<FocusIn>', lambda x: on_focus_in(self.discord_user_name_entry))
        self.discord_user_name_focus_out = self.card_author_entry.bind('<FocusOut>', lambda x: on_focus_out(self.discord_user_name_entry, 'Frodo'))
        self.discord_user_name_entry.pack(fill=X, padx= 4, pady=(0,8))
        ToolTip(self.discord_user_name_entry, text="Your Discord Username to share your Card with the Community.", bootstyle=(INFO, INVERSE))  

        self.settings_frame_submit_button = ttk.Button(self.settings_frame, text="SUBMIT",compound="left", command=self.settings_frame_submit_button_event)
        self.settings_frame_submit_button.pack(side=BOTTOM,padx=4, pady=4)

        # select default frame
        self.select_frame_by_name("add")

    def select_frame_by_name(self, name):
        
        # show selected frame
        if name == "add":
            self.cards_button.configure(bootstyle="primary-outline")
            self.home_button.configure(bootstyle="primary")
            self.sheetcreator_button.configure(bootstyle="primary-outline")
            self.settings_button.configure(bootstyle="primary-outline")

            self.home_frame.grid(row=0, column=1, sticky="nsew")
            self.active_frame = "add"
        else:
            self.home_frame.grid_forget()

        if name == "cards":
            self.cards_button.configure(bootstyle="primary")
            self.home_button.configure(bootstyle="primary-outline")
            self.sheetcreator_button.configure(bootstyle="primary-outline")
            self.settings_button.configure(bootstyle="primary-outline")

            self.cards_frame.grid(row=0, column=1, sticky="nsew")
            self.active_frame = "cards"
        else:
            self.cards_frame.grid_forget()

        if name == "sheetcreator":
            self.cards_button.configure(bootstyle="primary-outline")
            self.home_button.configure(bootstyle="primary-outline")
            self.sheetcreator_button.configure(bootstyle="primary")
            self.settings_button.configure(bootstyle="primary-outline")

            self.cardsheetcreator_frame.grid(row=0, column=1, sticky="nsew")
            self.active_frame = "sheetcreator"
        else:
            self.cardsheetcreator_frame.grid_forget()

        if name == "settings":
            self.cards_button.configure(bootstyle="primary-outline")
            self.home_button.configure(bootstyle="primary-outline")
            self.sheetcreator_button.configure(bootstyle="primary-outline")
            self.settings_button.configure(bootstyle="primary")

            self.settings_frame.grid(row=0, column=1, sticky="nsew")
            self.active_frame = "settings"
        else:
            self.settings_frame.grid_forget()

    def home_button_event(self):

        if( self.active_frame == "add"):
            self.clear_card_data()

        self.select_frame_by_name("add")
        self.cards_frame.update()
        self.card_name_entry.focus()

    def card_frame_button_event(self):
        self.select_frame_by_name("cards")

    def cardsheetcreator_frame_button_event(self):
        self.select_frame_by_name("sheetcreator")

    def settings_frame_button_event(self):
        self.select_frame_by_name("settings")

    def home_frame_submit_button_event(self):
        # try:
            sys.stdout.writelines("Submit Event")
            createCard, myCard = cardgenerator.CreateACreatureCard(
                artwork_filename=self.card_artwork_filename,
                lang=self.card_language_entry.get(),
                cardset=self.card_cardset_entry.get(),
                uid_from_set=self.card_cardnumber_entry.get(),
                name=self.card_name_entry.get(),
                power=self.card_power_entry.get(),
                keywords= self.card_capabilities_entry.get() if self.card_capabilities_entry.get() != "Frenzy, Tough..." else "",
                effect=self.card_effect_entry.get() if self.card_effect_entry.get() != "#Play: Draw a card. #Defeat: Gain 1 life point." else "",
                quote=self.card_quote_entry.get() if self.card_quote_entry.get() != "Nothing special" else "",
                use_3D_effect=ThreeDEffectKind.NONE
            )
            print(createCard.text)
            if (self.edit_card_index != None):
                # Update version
                old_card = self.customcards[self.edit_card_index]
                myCard.version = old_card.version + 1
                self.customcards[self.edit_card_index] = myCard
            else:
                self.customcards.append(myCard)

            self.update_card_frame_listbox()

            if (self.edit_card_index != None):
                self.select_frame_by_name("cards")
                self.listbox.select_set(self.edit_card_index)
                self.edit_card_index = None

            self.clear_card_data()
        # except Exception as e:
        #     print("Error on Create Crature Card:" + str(e))

    def update_card_frame_listbox(self):
        self.listbox.delete(0, tk.END)
        for card in self.customcards:
            self.listbox.insert(tk.END, card.toStrForList())

    def clear_card_data(self, all:bool = False):
        
        self.edit_card_index = None

        self.card_name_entry.delete(0, tk.END)
        self.card_power_entry.delete(0,tk.END)
        self.card_capabilities_entry.delete(0,tk.END)
        self.card_effect_entry.delete(0,tk.END)
        self.card_quote_entry.delete(0,tk.END)
        self.card_cardnumber_entry.delete(0,tk.END)
        self.update_card_image(Image.open(os.path.join(__location__, "assets\\cardback.png")))

        if all:
            self.card_language_entry.delete(0,tk.END)
            self.card_cardset_entry.delete(0,tk.END)  
            self.card_author_entry.delete(0,tk.END)

      

    def cards_frame_edit_button_event(self):
        self.select_frame_by_name("add")
        self.clear_card_data(all=True)
        for i in self.listbox.curselection():
            myCard:Card = self.customcards[i]
            self.card_name_entry.insert(0,myCard.name)
            self.card_power_entry.insert(0,myCard.power)
            self.card_capabilities_entry.insert(0,myCard.keywords)
            self.card_effect_entry.insert(0,myCard.effect)
            self.card_quote_entry.insert(0,myCard.quote)
            self.card_language_entry.insert(0,myCard.lang)
            self.card_cardset_entry.insert(0,myCard.cardset)
            self.card_cardnumber_entry.insert(0,myCard.uid_from_set)
            self.card_artwork_filename = myCard.image_path
            # self.card_author_entry.insert(0,myCard.author) # TODO

            self.update_card_image(cardgenerator.decode_base64(myCard.cropped_final_card_base64))

            self.edit_card_index = i

    def cards_frame_export_button_event(self):
        print("Send Webhook")
        for i in self.listbox.curselection():
            myCard = self.customcards[i]
            print(myCard)
            metaData = cardgenerator.create_extra_pnginfos(myCard=myCard, forDiscord=True)
            print("Metadata created")

            tmp_path = cardgenerator.save_pnginfos_in_tmpCard(myCard = myCard, myMetaData=metaData)
            print(tmp_path)
            with open(file=tmp_path, mode='rb') as f:
                my_file = discord.File(f)
 
                
            response = self.webhook.send(content=f">MindbotPal: New Card is beamed", username=os.getenv("DISCORD_USER_NAME"),file=my_file, wait=True)
            my_file.close()
            f.close()
            if f.closed:
                os.remove(tmp_path)

            print("Send Webhook: FINISHED")
            response.delete()
            print("Message: DELETED")

    def card_artwork_button_event(self):
        f_types =[("Image Files", "*.png")]
        tmp_path = filedialog.askopenfilename(parent=app, initialdir=os.getenv('ASSETS_UPLOAD_FOLDER'), title="Please select a Artwork:", filetypes=f_types )
        image = Image.open(tmp_path)
        pathname, extension = os.path.splitext(tmp_path)	
        name = pathname.split('/')
        self.card_artwork_filename = f"{name[-1]}{extension}"
        tmp_path = os.path.join(f"{os.getenv('ASSETS_UPLOAD_FOLDER')}\\{self.card_artwork_filename}")
        
        if (os.path.exists(tmp_path) == False):
            # TODO: Maybe correct Card Size?
            # image = cardgenerator.cropandresizecard(image)
            image.save(tmp_path,'PNG', dpi = (300,300), optimize=True)

        self.update_card_image(image)

    
    def update_card_image(self, myImage:Image):
        self.card_image = ImageTk.PhotoImage(myImage.resize((816//2, 1110//2),resample= Image.Resampling.LANCZOS))#, width=816//3, height=1110//3)
        self.card_image_canvas.create_image(0,0, anchor=NW, image = self.card_image)
        # self.card_image_frame.update()

    def cards_frame_delete_button_event(self):
        for i in self.listbox.curselection():
            del self.customcards[i]

        self.update_card_frame_listbox()
        self.listbox.select_set(0)

    def settings_frame_submit_button_event(self):

        os.environ["DISCORD_USER_NAME"] =  self.discord_user_name_entry.get()

        print(os.getenv("DISCORD_USER_NAME"))
        if(os.getenv("DISCORD_USER_NAME") is None or len(str(os.getenv("DISCORD_USER_NAME"))) == 0):
            print("Disable Export Button")
            self.cards_frame_export_card_button.configure(state="disabled")
        else:
            print("Enable Export Button")
            self.cards_frame_export_card_button.configure(state="enabled")
        
        self.cards_frame.update()
            

    def read_customcards_local_db(self):
        print("Reading CSV for baking new Creatures:")
        path = os.path.join(__location__, "customcardslocal.db")

        if (os.path.exists(path) == False):
            return

        with open(path, encoding='utf-8') as csv_file:
            lines = csv_file.readlines()
            for line in lines:
                
                if(line.startswith("#")):
                    continue

                row = line.split(",")

                if(len(row) <= 0):
                    continue

                myCard = Card(
                    uid_from_set                = row[0].strip(),
                    lang                        = row[1].strip(),
                    name                        = row[2].strip(),
                    power                       = row[3].strip(),
                    keywords                    = row[4].strip(),
                    effect                      = row[5].strip(),
                    quote                       = row[6].strip(),
                    image_path                  = row[7].strip(),
                    filename                    = row[8].strip(),
                    cardset                     = row[9].strip(),
                    use_3d_effect               = row[10].strip(),
                    cropped_final_card_base64   = row[11].strip(),
                    final_card_base_64          = row[12].strip(),
                    artwork_base64              = row[13].strip()
                    )

                self.customcards.append(myCard)

    def on_closing(self):
        with open(os.path.join(__location__, "customcardslocal.db"), "w+") as db:
            for card in self.customcards:
                db.write(card.toCSVLine())

        print("SAVE SUCESSFUL")
        
        if (os.path.exists(os.path.join(os.getenv("CARD_OUTPUT_FOLDER"), "tmp"))):
            shutil.rmtree(os.path.join(os.getenv("CARD_OUTPUT_FOLDER"), "tmp"))
            print("PURGE TMP-FOLDER SUCESSFUL")

        app.destroy()

if __name__ == "__main__":
    
    # Set environment variables
    os.environ['ASSETS_UPLOAD_FOLDER'] = f'{__location__}/uploaded_assets'
    os.environ['CARD_OUTPUT_FOLDER'] = f'{__location__}/card_outputs'
    os.environ['DISCORD_WEBHOOK'] = "https://discord.com/api/webhooks/1058301650491678750/kqsJTCIDe--Ib6GHcNfQqrj7yLAvROiivW9DJu2aAaQsfzds36U6htIGv3ZRZsCOgsMZ"
    
    Path(os.getenv('ASSETS_UPLOAD_FOLDER')).mkdir(parents=True, exist_ok=True)
    Path(os.getenv('CARD_OUTPUT_FOLDER')).mkdir(parents=True, exist_ok=True)

    app = ttk.Window(
        title = __title__,
        size = __appsize__,
        minsize = __appsize__,
        themename= "darkly",
    )
    icon = PhotoImage(name="icon", file=os.path.join(__location__+"\\assets\\icon.png"))
    app.iconphoto(True, icon)
    Creator(app)

    app.mainloop()
