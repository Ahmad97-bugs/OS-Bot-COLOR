import random
import time
import keyboard
import src.utilities.api.item_ids as ids
import src.utilities.color as clr
import src.utilities.random_util as rd
from src.model.osrs.osrs_bot import OSRSBot
from src.model.runelite_bot import BotStatus
from src.utilities.api.morg_http_client import MorgHTTPSocket
from src.utilities.api.status_socket import StatusSocket
from src.utilities.geometry import RuneLiteObject
import pyautogui as pag

from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES


class OSRSClay(OSRSBot):
    def __init__(self):
        self.options_set = True
        bot_title = "Glass"
        description = (
            "This bot power-fish. Position your character near some trees, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 175
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

        self.clay = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if nearest := self.get_nearest_tagged_NPC():
                self.mouse.move_to(nearest.random_point())
                time.sleep(random.randint(231, 435)/1000)
                self.mouse.click()
            while not search_img_in_rect(BOT_IMAGES.joinpath("bank", "bank_opened.png"), self.win.game_view):
                time.sleep(0.1)

            if api_m.get_inv_item_indices(ids.MOLTEN_GLASS):
                while not (deposit_all_btn := search_img_in_rect(BOT_IMAGES.joinpath("bank", "deposit.png"), self.win.game_view)):
                    time.sleep(0.1)

                if deposit_all_btn:
                    self.mouse.move_to(deposit_all_btn.random_point())
                    self.mouse.click()
                    # time.sleep(random.randint(700, 1200) / 1000)

            while not (seaweed := search_img_in_rect(BOT_IMAGES.joinpath("bank", "Giant_seaweed_bank.png"), self.win.game_view)):
                time.sleep(0.3)
            if seaweed:
                self.mouse.move_to(seaweed.random_point())
                # time.sleep(random.randint(62, 89) / 1000)
                self.mouse.click()
                # time.sleep(random.randint(61, 72) / 1000)
                self.mouse.click()
                # time.sleep(random.randint(65, 81) / 1000)

            while not (bucket := search_img_in_rect(BOT_IMAGES.joinpath("bank", "Bucket_of_sand_bank.png"), self.win.game_view)):
                time.sleep(0.3)
            if bucket:
                self.mouse.move_to(bucket.random_point())
                time.sleep(random.randint(62, 88) / 1000)
                pag.keyDown("shift")
                time.sleep(random.randint(64, 71) / 1000)
                self.mouse.click()
                time.sleep(random.randint(72, 81) / 1000)
                pag.keyUp("shift")
                time.sleep(random.randint(81, 95) / 1000)
                keyboard.press_and_release('esc')

            time.sleep(random.randint(751, 891) / 1000)

            if not (spell := search_img_in_rect(BOT_IMAGES.joinpath("spellbooks", "lunar", "Superglass_make.png"), self.win.control_panel)):
                self.mouse.move_to(self.win.cp_tabs[6].random_point())
                self.mouse.click()
                time.sleep(random.randint(751, 891) / 1000)
            if spell:
                self.mouse.move_to(spell.random_point())
                time.sleep(random.randint(81, 95) / 1000)
                if self.mouseover_text(contains="Cast", color=clr.OFF_WHITE):
                    self.mouse.click()
                    time.sleep(random.randint(1851, 2002) / 1000)

            attempt = 0
            while not api_m.get_inv_item_indices(ids.MOLTEN_GLASS):
                time.sleep(random.randint(251, 302) / 1000)
                attempt += 1
                if attempt == 10:
                    break
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")


    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()


# total cost 10.5m supplies

