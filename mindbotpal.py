import os
import tkinter as tk
from tkinter import filedialog, PhotoImage, Canvas
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import discord
from discord import SyncWebhook
from PIL import Image, ImageTk

import cardgenerator
from models import Card, ThreeDEffectKind

__location__:str = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class Creator(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=BOTH, expand=YES)

        app.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.active_frame:str="cards"

        self.webhook = SyncWebhook.from_url(os.getenv('DISCORD_WEBHOOK'))

        self.edit_card_index:int = None
        self.customcards = []
        
        self.read_customcards_local_db()
        
        print(f"Count custom cards: {len(self.customcards)}")

        self.card_name:tk.StringVar = tk.StringVar().set("Sirus Snape")
        self.card_power = tk.StringVar().set("9")
        self.card_capabilities = tk.StringVar()
        self.card_effect = tk.StringVar()
        self.card_quote = tk.StringVar()
        self.card_lang = tk.StringVar().set("en")
        self.card_cardset = tk.StringVar().set("default")
        self.card_cardnumber = tk.StringVar().set("1")
        self.card_author = tk.StringVar()
        self.card_artwork_filename:str = None


        for i in range(2):
            self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".\\assets")
        self.logo_image = PhotoImage(os.path.join(image_path, "CustomTkinter_logo_single.png"), width=26, height=26)
        self.image_icon_image = PhotoImage(os.path.join(image_path, "image_icon_light.png"), width=20, height=20)
        self.home_image = PhotoImage(os.path.join(image_path, "home_dark.png"), width=20, height=20)

        # create navigation frame - col 1
        self.navigation_frame = ttk.Frame(self, padding=10)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        # self.navigation_frame.grid_rowconfigure(0, weight=1)

        self.navigation_frame_label = ttk.Label(self.navigation_frame, text="  Image Example")
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        self.cards_button = ttk.Button(self.navigation_frame, text="Cards", width=20, command=self.card_frame_button_event)
        self.cards_button.grid(row=1, column=0, padx=4, pady=4)

        self.home_button = ttk.Button(self.navigation_frame, text="Add", width=20,command=self.home_button_event)
        self.home_button.grid(row=2, column=0, padx=4, pady=4)

        self.sheetcreator_button = ttk.Button(self.navigation_frame, width=20,text="Sheet Creator",command=self.card_frame_button_event)
        self.sheetcreator_button.grid(row=3, column=0, padx=4, pady=4)

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
        self.update_card_image(Image.open(os.path.join(image_path, "cardback.png")))

        # Second Column
        self.card_data_label_frame = ttk.Frame(self.home_frame, padding=4)
        self.card_data_label_frame.pack(side="left", fill=BOTH, expand=True)

        self.card_name_label = ttk.Label(self.card_data_label_frame, text="Name:")
        self.card_name_label.pack(fill=X,padx= 4, pady=4)
        self.card_name_entry = ttk.Entry(self.card_data_label_frame,textvariable=self.card_name)
        self.card_name_entry.pack(fill=X, padx= 4, pady=(0,8))

        self.card_power_label = ttk.Label(self.card_data_label_frame, text="Power:",)
        self.card_power_label.pack(fill=X, padx= 4, pady=4)
        self.card_power_entry = ttk.Entry(self.card_data_label_frame,textvariable=self.card_power, width=80)
        self.card_power_entry.pack(fill=X, padx= 4, pady=(0,8))

        
        self.card_capabilities_label = ttk.Label(self.card_data_label_frame, text="Capabilities:")
        self.card_capabilities_label.pack(fill=X, padx= 4, pady=4)        
        self.card_capabilities_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_capabilities,  width=80)
        self.card_capabilities_entry.pack(fill=X, padx= 4, pady=(0,8))


        self.card_effect_label = ttk.Label(self.card_data_label_frame, text="Effect:")
        self.card_effect_label.pack(fill=X, padx= 4, pady=4)        
        self.card_effect_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_effect, width=80)
        self.card_effect_entry.pack(fill=X, padx= 4, pady=(0,8))


        self.card_quote_label = ttk.Label(self.card_data_label_frame, text="Quote:")
        self.card_quote_label.pack(fill=X, padx= 4, pady=4)
        self.card_quote_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_quote, width=80)
        self.card_quote_entry.pack(fill=X, padx= 4, pady=(0,8))

        self.card_artwork_label = ttk.Label(self.card_data_label_frame, text="Artwork")
        self.card_artwork_label.pack(fill=X, padx= 4, pady=4)
        self.card_artwork_button = ttk.Button(self.card_data_label_frame, text="SELECT",compound="left", command=self.card_artwork_button_event, width=80)
        self.card_artwork_button.pack(fill=X, padx= 4, pady=(0,8))

        self.card_metadata_label = ttk.Label(self.card_data_label_frame, text="Metadata", underline=10)
        self.card_metadata_label.pack(fill=X, padx= 4, pady=(10, 8))

        self.card_language_label = ttk.Label(self.card_data_label_frame, text="Language:")
        self.card_language_label.pack(fill=X, padx= 4, pady=4)        
        self.card_language_entry = ttk.Entry(self.card_data_label_frame,textvariable=self.card_lang, width=80)
        self.card_language_entry.pack(fill=X, padx= 4, pady=(0,8))


        self.card_cardset_label = ttk.Label(self.card_data_label_frame, text="Card Set:")
        self.card_cardset_label.pack(fill=X, padx= 4, pady=4) 
        self.card_cardset_entry = ttk.Entry(self.card_data_label_frame,textvariable=self.card_cardset,  width=80)
        self.card_cardset_entry.pack(fill=X, padx= 4, pady=(0,8))

        self.card_cardnumber_label = ttk.Label(self.card_data_label_frame, text="Cardnumber:")
        self.card_cardnumber_label.pack(fill=X, padx= 4, pady=4) 
        self.card_cardnumber_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_cardnumber, width=80)
        self.card_cardnumber_entry.pack(fill=X, padx= 4, pady=(0,8))   
                
        self.card_atuthor_label = ttk.Label(self.card_data_label_frame, text="Author:")
        self.card_atuthor_label.pack(fill=X, padx= 4, pady=4)     
        self.card_author_entry = ttk.Entry(self.card_data_label_frame, textvariable=self.card_author,width=80)
        self.card_author_entry.pack(fill=X, padx= 4, pady=(0,8))

        # TODO: Vorschaubutton

        self.home_frame_button_1 = ttk.Button(self.card_data_label_frame, text="SUBMIT",compound="left", command=self.home_frame_submit_button_event, width=80)
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


        self.cards_frame_export_card_button = ttk.Button(self.cards_frame_Button_Frame, text="Send to Discord",compound="left", command=self.cards_frame_export_button_event)
        self.cards_frame_export_card_button.pack(side="right",padx=4, pady=4)

        self.listbox = tk.Listbox(self.cards_frame, selectmode=tk.SINGLE)
        self.listbox.pack(expand=True,side="left", fill=tk.BOTH, padx=4, pady=4)

        self.update_card_frame_listbox()
        
        scrollbar = ttk.Scrollbar(self.listbox, command=self.listbox.yview)
        scrollbar.pack(side="right", fill=tk.Y, padx=4, pady=4)
        
        # select default frame
        self.select_frame_by_name("add")

    def select_frame_by_name(self, name):
        
        # show selected frame
        if name == "add":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
            self.active_frame = "add"
        else:
            self.home_frame.grid_forget()

        if name == "cards":
            self.cards_frame.grid(row=0, column=1, sticky="nsew")
            self.active_frame = "cards"
        else:
            self.cards_frame.grid_forget()

        # if name == "sheetcreator":
        #     self.third_frame.grid(row=0, column=1, sticky="nsew")
        #     self.active_frame = "sheetcreator"
        # else:
        #     self.third_frame.grid_forget()

    def home_button_event(self):

        if( self.active_frame == "add"):
            self.clear_card_data()

        self.select_frame_by_name("add")
        self.cards_frame.update()
        self.card_name_entry.focus()

    def card_frame_button_event(self):
        self.select_frame_by_name("cards")

    # def frame_3_button_event(self):
    #     self.select_frame_by_name("frame_3")

    def home_frame_submit_button_event(self):
        card_backup_background, myCard = cardgenerator.CreateACreatureCard(
            artwork_filename=self.card_artwork_filename,
            lang=self.card_language_entry.get(),
            cardset=self.card_cardset_entry.get(),
            uid_from_set=self.card_cardnumber_entry.get(),
            name=self.card_name_entry.get(),
            power=self.card_power_entry.get(),
            keywords=self.card_capabilities_entry.get(),
            effect=self.card_effect_entry.get(),
            quote=self.card_quote_entry.get(),
            use_3D_effect=ThreeDEffectKind.NONE
        )

        if (self.edit_card_index != None):
            self.customcards[self.edit_card_index] = myCard
        else:
            self.customcards.append(myCard)

        self.update_card_frame_listbox()

        if (self.edit_card_index != None):
            self.select_frame_by_name("cards")
            self.listbox.select_set(self.edit_card_index)
            self.edit_card_index = None

        self.clear_card_data()

    def update_card_frame_listbox(self):
        self.listbox.delete(0, tk.END)
        for card in self.customcards:
            self.listbox.insert(tk.END, card.toStrForList())

    def clear_card_data(self):
        self.card_name_entry.delete(0, tk.END)
        self.card_power_entry.delete(0,tk.END)
        self.card_capabilities_entry.delete(0,tk.END)
        self.card_effect_entry.delete(0,tk.END)
        self.card_quote_entry.delete(0,tk.END)
        # self.card_language_entry.delete(0,tk.END)
        # self.card_cardset_entry.delete(0,tk.END)
        self.card_cardnumber_entry.delete(0,tk.END)
        # self.card_author_entry.delete(0,tk.END)
        self.update_card_image(Image.open(os.path.join(__location__, "assets\\cardback.png")))
      

    def cards_frame_edit_button_event(self):
        self.select_frame_by_name("add")
        for i in self.listbox.curselection():
            myCard = self.customcards[i]
            # self.card_name.set(myCard.name)
            # self.card_power.set(myCard.name)

            self.update_card_image(cardgenerator.decode_base64(myCard.cropped_final_card_base64))

            self.edit_card_index = i

    def cards_frame_export_button_event(self):
        print("Send Webhook")
        for i in self.listbox.curselection():
            myCard = self.customcards[i]
            image_binary = cardgenerator.card_as_binary(myCard.cropped_final_card_base64)
            self.webhook.send(content="Release #1 from", file=discord.File(fp=image_binary, filename=str(myCard.image_path)))
            print("Send Webhook: FINISHED")

    def card_artwork_button_event(self):
        f_types =[("Image Files", "*.png")]
        tmp_path = filedialog.askopenfilename(parent=app, initialdir=os.getenv('ASSETS_UPLOAD_FOLDER'), title="Please select a Artwork:", filetypes=f_types )
        image = Image.open(tmp_path)
        pathname, extension = os.path.splitext(tmp_path)	
        name = pathname.split('/')
        self.card_artwork_filename = f"{name[-1]}{extension}"
        tmp_path = os.path.join(f"{os.getenv('ASSETS_UPLOAD_FOLDER')}\\{self.card_artwork_filename}")
        
        if (os.path.exists(tmp_path) == False):
            image.save(tmp_path)

        self.update_card_image(image)

    
    def update_card_image(self, myImage:Image):
        self.card_image = ImageTk.PhotoImage(myImage.resize((816//2, 1110//2),resample= Image.Resampling.LANCZOS))#, width=816//3, height=1110//3)
        self.card_image_canvas.create_image(0,0, anchor=NW, image = self.card_image)
        self.card_image_frame.update()

    def cards_frame_delete_button_event(self):
        for i in self.listbox.curselection():
            del self.customcards[i]

        self.update_card_frame_listbox()
        self.listbox.select_set(0)
            

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
        app.destroy()

if __name__ == "__main__":
    
    # Set environment variables
    os.environ['ASSETS_UPLOAD_FOLDER'] = f'{__location__}/uploaded_assets'
    os.environ['CARD_OUTPUT_FOLDER'] = f'{__location__}/card_outputs'
    os.environ['DISCORD_WEBHOOK'] = "https://discord.com/api/webhooks/1058301650491678750/kqsJTCIDe--Ib6GHcNfQqrj7yLAvROiivW9DJu2aAaQsfzds36U6htIGv3ZRZsCOgsMZ"
    
    print("Loading assets...")
	# Load the Cardframes from the assets-Folder
    cardgenerator.card_frame_normal, cardgenerator.card_frame_mindbug = cardgenerator.LoadingCardFrames()

	# Load the Fonts from the assets-Folder
    cardgenerator.name_font_52, cardgenerator.name_font_42, cardgenerator.name_font_20, cardgenerator.trigger_and_capabilites_font, cardgenerator.description_font, cardgenerator.quote_font, cardgenerator.card_key_font_18, cardgenerator.power_font = cardgenerator.LoadingFonts()

	# Download Model for 3D-Effect
    cardgenerator.LoadingModelforRembg()

    app = ttk.Window(
        title = "MindbotPal",
        size = (850,750),
        minsize = (850,750),
        themename= "darkly"
    )
    Creator(app)

    app.mainloop()
