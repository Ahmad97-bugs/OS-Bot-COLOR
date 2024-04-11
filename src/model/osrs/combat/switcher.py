import utilities.imagesearch as imsearch
import random
import time
import keyboard
import requests
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from src.model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject
import pyautogui as pag

from src.utilities.api.morg_http_client import SocketError
from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES
class OSRSB(OSRSBot):
    def __init__(self):
        self.clay = None
        self.options_set = True
        self.gear = {
            'melee': [ids.FIRE_CAPE, ids.BANDOS_CHESTPLATE, ids.OSMUMTENS_FANG, ids.BANDOS_TASSETS,
                      ids.AMULET_OF_BLOOD_FURY, ids.FEROCIOUS_GLOVES, ids.DRAGON_DEFENDER],
            'dds': [ids.FIRE_CAPE, ids.BANDOS_CHESTPLATE, ids.DRAGON_DAGGERP_5698, ids.BANDOS_TASSETS,
                      ids.AMULET_OF_BLOOD_FURY, ids.FEROCIOUS_GLOVES, ids.DRAGON_DEFENDER],
            'range': [ids.AVAS_ASSEMBLER, ids.CRYSTAL_BODY, ids.CRYSTAL_LEGS, ids.BOW_OF_FAERDHINEN_C,
                      ids.NECKLACE_OF_ANGUISH, ids.BARROWS_GLOVES],
            'mage': [ids.IMBUED_SARADOMIN_CAPE, ids.SANGUINESTI_STAFF, ids.AHRIMS_ROBESKIRT_100,
                     ids.AHRIMS_ROBETOP_100, ids.OCCULT_NECKLACE, ids.TORMENTED_BRACELET, ids.ELIDINIS_WARD]
        }
        self.api = MorgHTTPSocket()

        bot_title = "Blast furnace"
        description = (
            "make wine"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 240
        self.take_breaks = True
        self.running = False
        keyboard.add_hotkey('q', self.melee)
        keyboard.add_hotkey('w', self.range)
        keyboard.add_hotkey('e', self.mage)
        keyboard.add_hotkey('a', self.dds)

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def range(self):
        for slot in self.api.get_first_occurrence(self.gear['range']):
            self.mouse.move_to(self.win.inventory_slots[slot].random_point(), mouseSpeed="super")
            self.mouse.click()

    def melee(self):
        for slot in self.api.get_first_occurrence(self.gear['melee']):
            self.mouse.move_to(self.win.inventory_slots[slot].random_point(), mouseSpeed="super")
            self.mouse.click()

    def dds(self):
        for slot in self.api.get_first_occurrence(self.gear['dds']):
            self.mouse.move_to(self.win.inventory_slots[slot].random_point(), mouseSpeed="super")
            self.mouse.click()
        keyboard.press_and_release('F3')
        self.mouse.move_to(self.win.prayers[26].random_point(), mouseSpeed="fastest")
        self.mouse.click()

    def mage(self):
        for slot in self.api.get_first_occurrence(self.gear['mage']):
            self.mouse.move_to(self.win.inventory_slots[slot].random_point(), mouseSpeed="super")
            self.mouse.click()

    def main_loop(self):
        api = MorgHTTPSocket()

        start_time = time.time()
        end_time = self.running_time * 60


    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

