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

from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES


class OSRSB(OSRSBot):
    def __init__(self):
        self.clay = None
        self.options_set = True
        bot_title = "Wine"
        description = (
            "make wine"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120 + random.randint(-9, 65)
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

            self.log_msg("open bank")
            if not self.open_bank():
                continue
            self.log_msg("deposit")
            self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest')
            self.mouse.click()

            self.log_msg("withdraw")
            if not self.withdraw_from_bank(["Yew_logs_bank"]):
                continue
            while not (YEW_LOGS := api_m.get_inv_item_indices(ids.YEW_LOGS)):
                time.sleep(0.2)
            self.log_msg("clicking knife")
            self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.log_msg("clicking log")
            self.mouse.move_to(self.win.inventory_slots[YEW_LOGS[0]].random_point(), mouseSpeed='fastest')
            self.mouse.click()

            self.sleep(650, 721)
            time.sleep(random.randint(780, 850) / 1000)
            timer = 0
            while not search_img_in_rect(BOT_IMAGES.joinpath("skilling", f'fletching.png'), self.win.chat):
                time.sleep(1)
                timer += 1
                if timer == 10:
                    continue
            keyboard.press_and_release('3')
            self.log_msg("started skilling")
            if not self.finished_processing(ids.YEW_LOGS, 1.8):
                continue
            self.log_msg("finished")

            if rd.random_chance(probability=0.82) and self.take_breaks:
                self.take_break(max_seconds=21, fancy=True)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()


# total cost 10.5m supplies

