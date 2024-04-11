import time

import keyboard
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSTemplate(OSRSBot):
    def __init__(self):
        bot_title = "Divine potions"
        description = "<Script description here>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 120

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):

        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            elif option == "multi_select_example":
                self.log_msg(f"Multi-select example: {options[option]}")
            elif option == "menu_example":
                self.log_msg(f"Menu example: {options[option]}")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):

        # Setup APIs
        api_m = MorgHTTPSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.open_bank()
            if api_m.get_if_item_in_inv(ids.DIVINE_SUPER_COMBAT_POTION4):
                self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fast')
                self.mouse.click()
            if not api_m.get_if_item_in_inv([ids.HALF_A_BOTANICAL_PIE, ids.BOTANICAL_PIE]):
                self.withdraw_from_bank(['Botanical_pie_bank'], True, False)
            self.withdraw_from_bank(['Super_combat'], False)
            if api_m.get_skill_level('Herblore', True) < 97:
                self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fast')
                self.mouse.click()
                self.sleep(700, 900)
                if api_m.get_if_item_in_inv([ids.PIE_DISH]):
                    keyboard.press('shift')
                    time.sleep(0.3)
                    self.mouse.click()
                    keyboard.release('shift')
            self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fast')
            self.mouse.click()
            self.mouse.move_to(self.win.inventory_slots[5].random_point(), mouseSpeed='fast')
            self.mouse.click()
            self.sleep(1300, 1500)

            keyboard.press_and_release('space')

            self.sleep(33000, 35000)




            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
