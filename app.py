import tkinter as tk
from tkinter import filedialog

import customtkinter
import os
from PIL import Image
import cardgenerator
from models import Card


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mindbot1")
        self.geometry("1024x450")
        
        self.edit_card_index:int = None
        self.customcards = []
        self.customcards.append(Card(
        uid_from_set="1",
        lang="en",
        cardset="default",
        name="MINDBUG",
        power = "",
        keywords = "",
        effect = "",
        quote = "",
    ))

        self.card_name = tk.StringVar()
        self.card_power = tk.StringVar()
        self.card_capabilities = tk.StringVar()
        self.card_effect = tk.StringVar()
        self.card_quote = tk.StringVar()
        self.card_lang = tk.StringVar()
        self.card_cardset = tk.StringVar()
        self.card_cardnumber = tk.StringVar()

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".\\assets")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(0, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Image Example", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        self.cards_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Cards",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.card_frame_button_event)
        self.cards_button.grid(row=1, column=0)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Add",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=2, column=0)

        self.sheetcreator_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Sheet Creator",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.card_frame_button_event)
        self.sheetcreator_button.grid(row=3, column=0)


        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=4, pady=4, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.home_frame.grid(row=0, column=1, sticky="nsew")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_columnconfigure(1, weight=1)
        self.home_frame.grid_columnconfigure(2, weight=2)

        # First Column
        self.card_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(816//3,1110//3))
        self.home_frame_card_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.card_image, compound="left", corner_radius=40)
        self.home_frame_card_image_label.grid(row=0, rowspan=10, column=0, padx=4, pady=4 , sticky='nsew')

        # Second Column

        self.card_name_label = customtkinter.CTkLabel(self.home_frame, text="Name:")
        self.card_name_label.grid(row=0, column=1, padx= 4, pady=4)
        self.card_name_entry = customtkinter.CTkEntry(self.home_frame,textvariable=self.card_name, placeholder_text="Sirius Snape", width=250)
        self.card_name_entry.grid(row=0, column=2, padx= 4, pady=4)

        self.card_power_label = customtkinter.CTkLabel(self.home_frame, text="Power:")
        self.card_power_label.grid(row=1, column=1, padx= 4, pady=4)
        self.card_power_entry = customtkinter.CTkEntry(self.home_frame,textvariable=self.card_power, placeholder_text="9", width=250)
        self.card_power_entry.grid(row=1, column=2, padx= 4, pady=4)

        self.card_capabilities_label = customtkinter.CTkLabel(self.home_frame, text="Capabilities:")
        self.card_capabilities_label.grid(row=2, column=1, padx= 4, pady=4)
        self.card_capabilities_entry = customtkinter.CTkEntry(self.home_frame, textvariable=self.card_capabilities, placeholder_text="Frenzy, Tough", width=250)
        self.card_capabilities_entry.grid(row=2, column=2, padx= 4, pady=4)

        self.card_effect_label = customtkinter.CTkLabel(self.home_frame, text="Effect:")
        self.card_effect_label.grid(row=3, column=1, padx= 4, pady=4)
        self.card_effect_entry = customtkinter.CTkEntry(self.home_frame, textvariable=self.card_effect,placeholder_text="#Play: Draw a card. #Defeated: Gain 1 life point.", width=250)
        self.card_effect_entry.grid(row=3, column=2, padx= 4, pady=4)

        self.card_quote_label = customtkinter.CTkLabel(self.home_frame, text="Quote:")
        self.card_quote_label.grid(row=4, column=1, padx= 4, pady=4)
        self.card_quote_entry = customtkinter.CTkEntry(self.home_frame, textvariable=self.card_quote,placeholder_text="Nothing Special", width=250)
        self.card_quote_entry.grid(row=4, column=2, padx= 4, pady=4)

        self.card_artwork_label = customtkinter.CTkLabel(self.home_frame, text="Artwork")
        self.card_artwork_label.grid(row=5, column=1, padx= 4, pady=4)
        self.card_artwork_button = customtkinter.CTkButton(self.home_frame, text="SELECT",compound="left", command=self.card_artwork_button_event, width=250)
        self.card_artwork_button.grid(row=5, column=2, padx= 4, pady=4)

        self.card_metadata_label = customtkinter.CTkLabel(self.home_frame, text="Metadata")
        self.card_metadata_label.grid(row=7, column=2, padx= 4, pady=4)
        self.card_language_label = customtkinter.CTkLabel(self.home_frame, text="Language:", width=250)
        self.card_language_label.grid(row=8, column=1, padx= 4, pady=4)
        self.card_language_entry = customtkinter.CTkEntry(self.home_frame,textvariable=self.card_lang, placeholder_text="en", width=250)
        self.card_language_entry.grid(row=8, column=2, padx= 4, pady=4)

        self.card_cardset_label = customtkinter.CTkLabel(self.home_frame, text="Card Set:")
        self.card_cardset_label.grid(row=9, column=1, padx= 4, pady=4)
        self.card_cardset_entry = customtkinter.CTkEntry(self.home_frame,textvariable=self.card_cardset, placeholder_text="default", width=250)
        self.card_cardset_entry.grid(row=9, column=2, padx= 4, pady=4)

        self.card_cardnumber_label = customtkinter.CTkLabel(self.home_frame, text="Cardnumber:")
        self.card_cardnumber_label.grid(row=10, column=1, padx= 4, pady=4)
        self.card_cardnumber_entry = customtkinter.CTkEntry(self.home_frame, textvariable=self.card_cardnumber,placeholder_text="1", width=250)
        self.card_cardnumber_entry.grid(row=10, column=2, padx= 4, pady=4)

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="SUBMIT",compound="left", command=self.home_frame_submit_button_event, width=250)
        self.home_frame_button_1.grid(row=11, column=2, padx=4, pady=4)


        # create cards frame
        self.cards_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.cards_frame.grid(row=0, column=1, sticky="nsew")
        self.cards_frame.grid_columnconfigure(0, weight=1)

        self.cards_frame_edit_card_button = customtkinter.CTkButton(self.cards_frame, text="Edit",compound="left", command=self.cards_frame_edit_button_event)
        self.cards_frame_edit_card_button.pack(side="top", padx=4, pady=4)

        # self.list_items = tk.Variable(value=self.items)
        self.listbox = tk.Listbox(self.cards_frame, background="gray17", foreground="white", selectmode=tk.SINGLE)
        self.listbox.pack(expand=True,side="left", fill=tk.BOTH, padx=4, pady=4)

        for card in self.customcards:
            self.listbox.insert(tk.END, card.toStrForList())
        
        scrollbar = customtkinter.CTkScrollbar(self.listbox, command=self.listbox.yview)
        scrollbar.pack(side="right", fill=tk.Y, padx=4, pady=4)
        
        # select default frame
        self.select_frame_by_name("add")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")

        # show selected frame
        if name == "add":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()

        if name == "cards":
            self.cards_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.cards_frame.grid_forget()
        # if name == "sheet creator":
        #     self.third_frame.grid(row=0, column=1, sticky="nsew")
        # else:
        #     self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("add")

    def card_frame_button_event(self):
        self.select_frame_by_name("cards")

    # def frame_3_button_event(self):
    #     self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

        if(new_appearance_mode == "Light" or "System"):
            self.listbox.config(background="white", foreground="black")
        else:
            self.listbox.config(background="gray17", foreground="white")

    def home_frame_submit_button_event(self):

        if (self.edit_card_index != None):
            self.customcards[self.edit_card_index] = self.card_name.get()
        else:
            self.customcards.append(self.card_name.get())

        self.listbox.delete(0, tk.END)
        for card in self.customcards:
            self.listbox.insert(tk.END, card)

        if (self.edit_card_index != None):
            self.select_frame_by_name("cards")
            self.listbox.select_set(self.edit_card_index)
            self.edit_card_index = None

    def cards_frame_edit_button_event(self):
        self.select_frame_by_name("home")

        for i in self.listbox.curselection():
            self.card_name.set(self.listbox.get(i))
            self.edit_card_index = i

    def card_artwork_button_event(self):
        f_types =[("Image Files", "*.png")]
        answer = filedialog.askopenfilename(parent=app, initialdir=os.getcwd(), title="Please select a Artwork:", filetypes=f_types )
        self.card_image =  customtkinter.CTkImage(Image.open(answer), size=(816//3,1110//3))
        self.home_frame_card_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.card_image, compound="left", corner_radius=40)
        self.home_frame_card_image_label.grid(row=0, rowspan=10, column=0, padx=4, pady=4 , sticky='nsew')


    def cards_frame_delete_button_event(self):
        pass

    def cards_frame_export_button_event(self):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
