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
        self.filename = filename # from image_path
        self.cardset = cardset #8
        self.cropped_final_card_base64 = ""
        self.final_cropped_card_name = ""
        self.final_card_base_64 = ""
        self.final_card_name = ""
        self.artwork_base64 = ""
        self.set_icon_base64 = ""