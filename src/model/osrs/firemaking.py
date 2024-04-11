import random
import time
import pyautogui as pag
import src.utilities.api.item_ids as ids
import src.utilities.color as clr

from src.utilities import ocr
import src.utilities.random_util as rd
from src.model.osrs.osrs_bot import OSRSBot
from src.model.runelite_bot import BotStatus
from src.utilities.api.morg_http_client import MorgHTTPSocket
from src.utilities.geometry import RuneLiteObject

from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES


def check_position(api_m):
    timer = 0
    if api_m.get_player_position() not in [(3213, 3428, 0), (3213, 3429, 0), (3212, 3428, 0), (3215, 3429, 0)]:
        timer += 1
        time.sleep(1)
        if timer == 50:
            return False
    return True


class OSRSFiremaking(OSRSBot):
    def __init__(self):
        self.inventory_selected = True
        self.options_set = True
        self.sleep = False
        bot_title = "Light logs"
        description = (
            "Light logs YUPYUP."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 180
        self.take_breaks = True

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

    def main_loop(self):
        # Setup API
        api_m = MorgHTTPSocket()

        # self.log_msg("Selecting inventory...")
        # self.mouse.move_to(self.win.cp_tabs[3].random_point())
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if self.fm_sequence(api_m, clr.LIGHT_RED, self.sleep):
                self.sleep = True
            if self.fm_sequence(api_m, clr.GREEN, self.sleep):
                self.sleep = True
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def fm_sequence(self, api_m: MorgHTTPSocket, color, sleep):
        self.select_tele('Varrock', color)
        self.mouse.click()
        if sleep:
            time.sleep(random.randint(2600, 3400) / 1000)
            self.sleep = False
        while not (start_tile := self.get_nearest_tag(color)):
            time.sleep(0.3)
        self.mouse.move_to(start_tile.random_point())
        self.mouse.click()
        if not self.inventory_selected:
            self.mouse.move_to(self.win.cp_tabs[3].random_point())
            self.mouse.click()
            self.inventory_selected = True

        while not api_m.get_is_player_idle():
            time.sleep(0.5)
        if not check_position(api_m):
            return False
        if not api_m.get_inv_item_indices(ids.logs):
            self.select_tele('Camelot')
            self.mouse.click()
            api_m.wait_til_gained_xp('Magic', 10)

        while logs_in_inv := api_m.get_inv_item_indices(ids.logs):
            if 'You can' in api_m.get_latest_chat_message():
                self.inventory_selected = False
                cf.hop(self)
                time.sleep(random.randint(10, 15))
                return True
            if tinderbox := search_img_in_rect(BOT_IMAGES.joinpath("items", "Tinderbox.png"), self.win.control_panel):
                self.mouse.move_to(tinderbox.random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.mouse.move_to(self.win.inventory_slots[logs_in_inv[0]].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            api_m.wait_til_gained_xp('Firemaking', 10)

        # while not (start_tile := self.get_nearest_tag(clr.GREEN)):
        #     time.sleep(0.3)
        # self.mouse.move_to(start_tile.random_point())
        # self.mouse.click()
        # while not api_m.get_is_player_idle():
        #     time.sleep(0.2)
        time.sleep(random.randint(200, 456) / 1000)
        if not cf.open_bank(self):
            return False

        if not cf.withdraw_from_bank(self, "Maple_logs_bank"):
            return False

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def select_tele(self, location, color):
        if self.get_nearest_tag(color):
            return
        if self.inventory_selected:
            self.inventory_selected = False
            self.mouse.move_to(self.win.cp_tabs[6].random_point())
            self.mouse.click()
            time.sleep(random.randint(751, 891) / 1000)

        # while not self.mouseover_text(contains="Cast", color=clr.OFF_WHITE) or self.mouseover_text(contains="Seers'", color=clr.OFF_WHITE):
        if spell := search_img_in_rect(BOT_IMAGES.joinpath("spellbooks", "normal", f"{location}_teleport.png"), self.win.control_panel):
            self.mouse.move_to(spell.random_point())
