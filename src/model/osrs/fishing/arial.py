import random
import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from src.model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class OSRSB(OSRSBot):
    def __init__(self):
        self.options_set = True
        bot_title = "Arial fishing"
        description = (
            "FISH FISH FISH"
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

        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # 5% chance to take a break between tree searches
            if rd.random_chance(probability=0.05) and self.take_breaks:
                self.take_break(max_seconds=5, fancy=True)
            if fishing_spot := self.find_fish():
                self.mouse.move_to(fishing_spot.random_point(), mouseSpeed="fastest")
                self.mouse.click()
                api_m.wait_til_gained_xp('Fishing', 3)
                if fishing_spot := self.find_next_fish():
                    self.mouse.move_to(fishing_spot.random_point(), mouseSpeed="fastest")
                    self.mouse.click()
                    if fish := api_m.get_inv_item_indices([ids.BLUEGILL, ids.COMMON_TENCH, ids.GREATER_SIREN, ids.MOTTLED_EEL]):
                        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')
                        self.mouse.click()
                        self.mouse.move_to(self.win.inventory_slots[fish[0]].random_point(), mouseSpeed='fastest')
                        self.mouse.click()
                    api_m.wait_til_gained_xp('Fishing', 3)
                if api_m.get_if_item_in_inv(ids.GOLDEN_TENCH):
                    self.__logout()
                if len(fish := api_m.get_inv_item_indices([ids.BLUEGILL, ids.COMMON_TENCH, ids.GREATER_SIREN, ids.MOTTLED_EEL])) > 1:
                    self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')
                    self.mouse.click()
                    self.mouse.move_to(self.win.inventory_slots[fish[1]].random_point(), mouseSpeed='fastest')
                    self.mouse.click()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def find_fish(self):
        if not (fishing_spots := self.get_all_tagged_in_rect(self.win.game_view, clr.CYAN)):
            return False
        fishing_spots = sorted(fishing_spots, key=RuneLiteObject.distance_from_rect_center)
        try:
            return fishing_spots[0]  # if next_nearest else fishing_spots[1]
        except IndexError:
            self.log_msg("Can't find fishing spot")
            return False

    def find_next_fish(self):
        if not (fishing_spots := self.get_all_tagged_in_rect(self.win.game_view, clr.CYAN)):
            return False
        fishing_spots = sorted(fishing_spots, key=RuneLiteObject.distance_from_rect_center)
        try:
            if len(fishing_spots) > 1:
                return fishing_spots[1]  # if next_nearest else fishing_spots[1]
            else:
                return False
        except IndexError:
            self.log_msg("Can't find fishing spot")
            return False
