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

from src.utilities import ocr
from src.utilities.geometry import Rectangle
from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES


def count_marks(inventory):
    for item in inventory:
        if item.get('id', 0) == 11849:
            return item.get('quantity', 0)


class OSRSAgility(OSRSBot):
    def __init__(self):
        self.laps = None
        self.options_set = True
        bot_title = "Seers Agility"
        description = (
            "Agility + marks"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.laps_run = 240
        self.total_laps = 0
        self.total_marks = 0
        self.take_breaks = True

    def create_options(self):
        self.options_builder.add_slider_option("laps_run", "How long to run (laps)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "laps_run":
                self.laps_run = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running laps: {self.laps_run}.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup API
        api_m = MorgHTTPSocket()

        self.laps = 0
        amount_of_marks = count_marks(api_m.get_inv())

        # Main loop
        last_message = api_m.get_latest_chat_message()

        while self.total_laps < self.laps_run:
            if rd.random_chance(probability=0.02) and self.take_breaks:
                self.take_break(max_seconds=10, fancy=True)

            new_message = api_m.get_latest_chat_message()
            if 'Your Seers' in new_message and new_message != last_message:
                self.total_laps += 1
                self.log_msg(f"Laps completed: ~{self.total_laps}")
                self.update_progress(self.total_laps)
                self.teleport_to_start()

            if self.pick_up_mark():
                self.total_marks += 1
                self.log_msg(f"Marks collected: ~{self.total_marks}")
                attempt = 0
                while amount_of_marks == count_marks(api_m.get_inv()):
                    attempt += 1
                    time.sleep(1)
                    if attempt == 20:
                        break
                amount_of_marks = count_marks(api_m.get_inv())

            attempt = 0
            while not self.mouseover_text(contains=["Climb", "up", "Wall", "Cross", "Jump", "Gap", "Edge"], color=[clr.OFF_WHITE, clr.OFF_CYAN]):
                attempt += 1
                if attempt == 15:
                    self.teleport_to_start()
                    break
                if nearest := self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN):
                    self.mouse.move_to(nearest[0].random_point(), mouseSpeed='fastest')
                time.sleep(1)

            self.mouse.click()
            api_m.wait_til_gained_xp('Agility', 10)
            while not api_m.get_is_player_idle(0.1):
                time.sleep(0.1)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def pick_up_mark(self):
        if ocr.find_text("Mark of grace", self.win.game_view, ocr.PLAIN_11, [clr.GROUND_PURPLE]):
            while not self.mouseover_text(contains=['Take'], color=[clr.OFF_WHITE]):
                enter_text = ocr.find_text("of", self.win.game_view, ocr.PLAIN_11, [clr.GROUND_PURPLE])
                self.mouse.move_to(enter_text[0].random_point(), mouseSpeed='fastest')
                time.sleep(0.2)
            self.mouse.click()
            return True
        return False

    def teleport_to_start(self):
        if not search_img_in_rect(BOT_IMAGES.joinpath("spellbooks", "normal", "Camelot_teleport.png"), self.win.control_panel):
            self.mouse.move_to(self.win.cp_tabs[6].random_point(), mouseSpeed='fastest')
            self.mouse.click()
        while not (spell := search_img_in_rect(BOT_IMAGES.joinpath("spellbooks", "normal", "Camelot_teleport.png"), self.win.control_panel)):
            time.sleep(random.randint(231, 435) / 1000)

        if spell:
            self.mouse.move_to(spell.random_point(), mouseSpeed='fastest')
            time.sleep(random.randint(751, 891) / 1000)
        if self.mouseover_text(contains="Seer", color=clr.OFF_WHITE):
            self.mouse.click()
            time.sleep(random.randint(1151, 1791) / 1000)

