import random
import time
import keyboard
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.imagesearch as imsearch
from src.model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
import pyautogui as pag
from src.utilities import ocr
from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES


def wait(api_m, position):
    while api_m.get_player_position() != position:
        time.sleep(0.3)
    return


class OSRSB(OSRSBot):
    def __init__(self):
        self.runes = None
        self.options_set = True
        bot_title = "Blood rune"
        description = (
            "rc blood rune true altar"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120 + random.randint(-5, 41)
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
        self.runes = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # self.cast_and_kill(api_m)
            self.open_bank()
            self.withdraw_from_bank(["Ensouled_bloodveld_head_bank"])

            self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.sleep(2700, 3000)

            self.refresh_energy(api_m)

            self.select_color(clr.RED, ['Last', '-', 'destination', '(cis)'], api_m)
            self.sleep(2000, 2500)
            self.map_search('dark_altar_step_1')
            self.map_search('dark_altar_step_2')
            self.map_search('dark_altar_step_3')
            # while api_m.get_animation_id() not in [808, 813]:
            #     self.sleep(700, 831)
            # while api_m.get_player_position() != (1677, 3881, 0):
            #     time.sleep(0.3)
            while not (spot := self.get_nearest_tag(clr.YELLOW)):
                self.sleep(200, 300)
            self.mouse.move_to(spot.random_point())
            self.mouse.click()
            self.sleep(700, 921)
            keyboard.press_and_release('F3')
            self.mouse.move_to(self.win.prayers[18].random_point(), mouseSpeed="fastest")
            self.mouse.click()
            while api_m.get_if_item_in_inv(ids.ENSOULED_BLOODVELD_HEAD_13496):
                if api_m.get_skill_level('Hitpoints', boost=True) < 20:
                    break
                self.cast_and_kill(api_m)
            keyboard.press_and_release('F1')
            self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def refresh_energy(self, api_m):
        self.select_color(clr.YELLOW, 'Drink', api_m)
        while api_m.get_skill_level('Prayer', boost=True) < 82:
            self.sleep(200, 300)

    def cast_and_kill(self, api_m):
        self.log_msg('another kill')
        if not search_img_in_rect(BOT_IMAGES.joinpath("spellbooks", "arceuus", "Arceuus_home_teleport.png"), self.win.control_panel):
            keyboard.press_and_release('F4')
        attempt = 0
        while not (reanimate := search_img_in_rect(BOT_IMAGES.joinpath("spellbooks", "arceuus", "Expert_reanimation.png"), self.win.control_panel)):
            self.sleep(200, 300)
            attempt += 1
            if attempt == 6:
                self.mouse.move_to(search_img_in_rect(BOT_IMAGES.joinpath("spellbooks", "arceuus", "Arceuus_home_teleport.png"), self.win.control_panel).random_point())
                self.log_msg('can not find spell')

        self.mouse.move_to(reanimate.random_point())
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[api_m.get_inv_item_indices(ids.ENSOULED_BLOODVELD_HEAD_13496)[0]].random_point())
        self.mouse.click()
        while not (object_found := self.get_nearest_tag(clr.CYAN)):
            time.sleep(0.1)
            if api_m.get_is_in_combat():
                break
        if object_found:
            self.mouse.move_to(object_found.random_point(), mouseSpeed='fastest')
            self.mouse.click()
        api_m.wait_til_gained_xp('Prayer', 15)
        self.sleep(200, 300)







