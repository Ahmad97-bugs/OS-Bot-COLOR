import random
import time
import keyboard
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from src.model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject
import pyautogui as pag

from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES


class OSRSBlast(OSRSBot):
    def __init__(self):
        self.clay = None
        self.options_set = True
        bot_title = "Blast furnace"
        description = (
            "make wine"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 240
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
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if 'Your cannon is out' in api_m.get_latest_chat_message():
                self.select_color(clr.LIGHT_PURPLE, ['Fire'], api_m)
                while 'You load' not in api_m.get_latest_chat_message():
                    time.sleep(0.1)
                self.select_color(clr.LIGHT_PURPLE, ['Fire'], api_m)
            while not api_m.get_is_in_combat():
                # Find a target
                target = self.get_nearest_tagged_NPC()
                if target is None:
                    failed_searches += 1
                    if failed_searches % 10 == 0:
                        self.log_msg("Searching for targets...")
                    if failed_searches > 60:
                        # If we've been searching for a whole minute...
                        self.__logout("No tagged targets found. Logging out.")
                        return
                    time.sleep(1)
                    continue
                failed_searches = 0

                # Click target if mouse is actually hovering over it, else recalculate
                self.mouse.move_to(target.random_point())
                if not self.mouseover_text(contains="Attack", color=clr.OFF_WHITE):
                    continue
                self.mouse.click()
                time.sleep(0.5)

            # self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

