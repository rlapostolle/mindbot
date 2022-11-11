import os

# This needs to be redesigned, it is only for the first test
class Card():
    def __init__(self, uid_from_set, lang, name, power, keywords, effect, quote, image_path, filename, cardset = ""): 
        self.uid_from_set = uid_from_set # 0
        self.lang = lang # 1
        self.name = name # 3
        self.power = power
        self.keywords = keywords
        self.effect = effect
        self.quote = quote
        self.image_path = image_path # 6
        self.filename = filename # 7
        self.cardset = cardset #8
        #Image data
        self.cropped_final_card_base64 = ""
        self.final_card_base_64 = ""
        self.artwork_base64 = ""
        self.set_icon_base64 = ""

    #Used to init from a db record
    def __init__(self, **args):
        self.__dict__.update(args)

    def toDdObj(self):
        return {
            'cardset': self.cardset,
            'uid_from_set': self.uid_from_set,
            'lang': self.lang,
            'name': self.name,
            'power': self.power, 
            'keywords': self.keywords,
            'effect': self.effect, 
            'quote': self.quote,
            'image_path': self.image_path,
            'filename':self.filename
        }

    def relativePath(self):
        return os.path.join(f"{self.cardset}", f"{self.lang}", "cropped", f"{self.filename}.png")