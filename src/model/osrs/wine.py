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


class OSRSWine(OSRSBot):
    def __init__(self):
        self.clay = None
        self.options_set = True
        bot_title = "Wine"
        description = (
            "make wine"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120
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

            if not (deposit_all_btn := self.open_bank()):
                continue
            self.mouse.move_to(deposit_all_btn.random_point(), mouseSpeed='fastest')
            self.mouse.click()

            if not self.withdraw_from_bank(["Jug_of_water_bank", "Grapes_bank"]):
                continue
            while not (JUG_OF_WATER := api_m.get_inv_item_indices(ids.JUG_OF_WATER)):
                time.sleep(0.2)
            self.mouse.move_to(self.win.inventory_slots[JUG_OF_WATER[-1]].random_point(), mouseSpeed='fastest')
            self.mouse.click()

            while not (GRAPES := api_m.get_inv_item_indices(ids.GRAPES)):
                time.sleep(0.2)
            self.mouse.move_to(self.win.inventory_slots[GRAPES[0]].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.sleep(650, 721)
            self.start_skilling('wine_interface')

            if not self.finished_processing(ids.GRAPES, 1.8):
                continue

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()


# total cost 10.5m supplies

