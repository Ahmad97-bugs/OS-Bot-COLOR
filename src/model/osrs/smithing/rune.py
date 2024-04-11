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


class OSRSB(OSRSBot):
    def __init__(self):
        self.clay = None
        self.options_set = True
        self.collect = False
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
            self.cycle(api_m, 'Coal')
            if self.collect:
                self.get_bars(api_m)
            self.cycle(api_m, 'Coal')
            self.cycle(api_m, 'Runite_ore')
            self.collect = True
            self.cycle(api_m, 'Coal')
            self.get_bars(api_m)
            self.cycle(api_m, 'Runite_ore')
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def cycle(self, api_m, ore):
        self.open_bank()
        self.deposit_bar('Runite_bar')
        self.refresh_energy(api_m)
        self.use_coal_bag(api_m, True)
        if not self.withdraw_from_bank([f'{ore}_bank']):
            self.__logout('out of item')
        self.select_color(clr.GREEN, ['Put', 'ore', 'on'], api_m)
        if self.chatbox_text_QUEST(contains='You don'):
            pag.press('space')
        timer = 0
        while api_m.get_is_inv_full():
            timer += 1
            time.sleep(0.2)
            if timer == 75:
                self.select_color(clr.GREEN, ['Put', 'ore', 'on'], api_m)
        self.use_coal_bag(api_m, False)
        self.select_color(clr.GREEN, ['Put'], api_m)
        if self.chatbox_text_QUEST(contains='You don'):
            pag.press('space')
        timer = 0
        while api_m.get_is_inv_full():
            time.sleep(0.2)
            timer += 1
            time.sleep(0.2)
            if timer == 10:
                self.select_color(clr.GREEN, ['Put', 'ore', 'on'], api_m)

    def use_coal_bag(self, api_m, bank_open):
        found_bag = search_img_in_rect(BOT_IMAGES.joinpath("items", 'Open_coal_bag.png'), self.win.control_panel)
        self.mouse.move_to(found_bag.random_point(), mouseSpeed='fastest')
        if bank_open:
            keyboard.press('shift')
            time.sleep(random.randint(100, 200) / 1000)
            self.mouse.click()
            keyboard.release('shift')
        if not bank_open:
            self.mouse.click()
            self.log_msg('returning')
            return
        timer = 0
        while 'The coal bag contains 27' not in api_m.get_latest_chat_message():
            # if 'The coal bag contains' in api_m.get_latest_chat_message():
            #     keyboard.press_and_release('esc')
            #     self.__logout('Out of coal')
            time.sleep(0.6)
            timer += 1
            if timer > 4:
                self.use_coal_bag(api_m, bank_open)

    def get_bars(self, api_m):
        self.select_color(clr.RED, ['Take'], api_m)
        self.start_skilling('rune_bar')
        while not api_m.get_is_inv_full():
            time.sleep(0.2)

    def refresh_energy(self, api_m):
        if api_m.get_run_energy() < 7000:
            self.withdraw_from_bank([f'Stamina_potion_bank'], single=True, close=False)
            while not (stamina := search_img_in_rect(BOT_IMAGES.joinpath("items", 'Stamina_potion.png'), self.win.control_panel)):
                time.sleep(0.1)
            self.mouse.move_to(stamina.random_point(), mouseSpeed='fastest')
            keyboard.press('shift')
            self.mouse.click()
            keyboard.release('shift')

    def deposit_bar(self, bar):
        if found_bar := search_img_in_rect(BOT_IMAGES.joinpath("items", f'{bar}.png'), self.win.control_panel):
            self.mouse.move_to(found_bar.random_point(), mouseSpeed='fastest')
            self.mouse.click()
