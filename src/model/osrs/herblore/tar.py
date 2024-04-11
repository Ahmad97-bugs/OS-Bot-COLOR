import random
import time
import pyautogui as pag
import src.utilities.api.item_ids as ids
import src.utilities.color as clr
import src.utilities.random_util as rd
from src.model.osrs.osrs_bot import OSRSBot
from src.model.runelite_bot import BotStatus
from src.utilities.api.morg_http_client import MorgHTTPSocket
from src.utilities.geometry import RuneLiteObject

from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES


class OSRSTar(OSRSBot):
    def __init__(self):
        self.options_set = True
        bot_title = "Create tar"
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
        # self.mouse.click()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            while not (TARROMIN_NOTED := api_m.get_inv_item_indices(ids.TARROMIN_NOTED)):
                time.sleep(0.2)
            self.mouse.move_to(self.win.inventory_slots[TARROMIN_NOTED[0]].random_point())
            self.mouse.click()
            banker = self.get_nearest_tag(clr.CYAN)
            self.mouse.move_to(banker.random_point())
            self.mouse.click()
            timer = 0
            while not search_img_in_rect(BOT_IMAGES.joinpath("skilling", "unnote_bank.png"), self.win.chat):
                time.sleep(1)
                timer += 1
                if timer == 50:
                    continue
            time.sleep(random.randint(800, 950) / 1000)
            pag.press('1')
            while not api_m.get_inv_item_indices(ids.TARROMIN):
                time.sleep(1)
                timer += 1
                if timer == 50:
                    continue
            self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.mouse.move_to(self.win.inventory_slots[4].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.start_skilling('herb_interface')
            self.finished_processing(ids.TARROMIN, 1.8)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def first_sequence(self, api_m: MorgHTTPSocket):
        if red_path := self.get_nearest_tag(clr.RED):
            self.mouse.move_to(red_path.random_point(), mouseSpeed='fast')
            self.mouse.click()
            time.sleep(random.randint(2000, 2300) / 1000)

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

