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
        self.skip = False
        self.sent_to_bank = time.time() - 10
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
            teaks = api_m.get_inv_item_indices(ids.TEAK_PLANK)
            if len(teaks) < 10 and not abs(time.time() - self.sent_to_bank) < 10:
                self.fetch_planks(api_m)
                continue
            if len(teaks) < 3 and abs(time.time() - self.sent_to_bank) < 10:
                continue
            if len(api_m.get_inv_item_indices(ids.MYTHICAL_CAPE_22114)) == 2 or (api_m.get_is_item_equipped(ids.MYTHICAL_CAPE_22114) and len(api_m.get_inv_item_indices(ids.MYTHICAL_CAPE_22114)) == 1):
                while not self.interact_cons(clr.YELLOW, "Build Guild trophy space"):
                    self.sleep(654, 843)
                attempt = 0
                while not (search_img_in_rect(BOT_IMAGES.joinpath("skilling", 'construction.png'), self.win.game_view)):
                    self.sleep(200, 432)
                    attempt += 1
                    if attempt == 6:
                        break
                keyboard.press_and_release('4')
                attempt = 0
                while api_m.wait_til_gained_xp('Construction', 3) == -1:
                    attempt += 1
                    if attempt == 3:
                        break
                    keyboard.press_and_release('4')
                self.remove_cape(api_m)

            self.sleep(400, 632)
            if len(api_m.get_inv_item_indices(ids.MYTHICAL_CAPE_22114)) == 1 or (api_m.get_is_item_equipped(ids.MYTHICAL_CAPE_22114) and not len(api_m.get_inv_item_indices(ids.MYTHICAL_CAPE_22114))):
                if api_m.get_is_inv_full():
                    self.handle_cape(api_m)
                while not self.interact_cons(clr.RED, "Remove Mythical cape"):
                    self.sleep(654, 843)
                attempt = 0
                while not self.chatbox_text_QUEST('No'):
                    attempt += 1
                    if attempt == 6:
                        break
                    self.sleep(200, 432)
                keyboard.press_and_release('1')
                self.sleep(654, 843)
            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def interact_cons(self, color, text):
        speed = "fastestest"
        while not (space := self.get_nearest_tag(color)):
            time.sleep(0.2)
            print('no color')
        random_speed = random.randint(1, 10)
        if random_speed < 3:
            speed = "fastest"
        self.mouse.move_to(space.random_point(), mouseSpeed=speed)
        self.mouse.right_click()

        if enter_text := ocr.find_text(text, self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.CYAN]):
            self.mouse.move_to(enter_text[0].random_point(), knotsCount=0, mouseSpeed='fastestest')
            if not self.mouse.click(check_red_click=True):
                return False
        else:
            space = self.get_nearest_tag(clr.GREEN)
            self.mouse.move_to(space.random_point())
            return False
        return True

    def fetch_planks(self, api_m):
        if len(api_m.get_inv_item_indices(ids.TEAK_PLANK)) < 3 and not self.get_nearest_tagged_NPC():
            while abs(time.time() - self.sent_to_bank) < 10:
                time.sleep(0.5)
        if npc := self.get_nearest_tagged_NPC():
            self.mouse.move_to(npc.random_point())
            self.mouse.click()
            self.sleep(650, 853)
            if self.chatbox_text_QUEST('Un-note'):
                keyboard.press_and_release('1')
                self.sent_to_bank = time.time()
            elif self.chatbox_text_QUEST('I have returned'):
                return
        elif time.time() - self.sent_to_bank < 10:
            return
        else:
            keyboard.press_and_release('F11')
            menu_selection = imsearch.BOT_IMAGES.joinpath("skilling", "house_options.png")
            while not (options := imsearch.search_img_in_rect(menu_selection, self.win.control_panel)):
                self.sleep(150, 200)
            self.mouse.move_to(options.random_point())
            self.mouse.click()
            self.sleep(350, 553)
            self.mouse.click()
            self.sleep(350, 553)
            if self.chatbox_text_QUEST('Un-note'):
                keyboard.press_and_release('1')
                self.sent_to_bank = time.time()
            keyboard.press_and_release('F1')

    def handle_cape(self, api_m):
        self.mouse.move_to(self.win.inventory_slots[api_m.get_inv_item_indices(ids.MYTHICAL_CAPE_22114)[0]].random_point(), mouseSpeed='fastest')
        self.mouse.click()
        while api_m.get_inv_item_indices(ids.MYTHICAL_CAPE_22114):
            self.sleep(200, 300)

    def remove_cape(self, api_m):
        if api_m.get_is_item_equipped(ids.MYTHICAL_CAPE_22114):
            self.sleep(600, 841)
            keyboard.press_and_release('F2')
            self.sleep(200, 341)
            menu_selection = imsearch.BOT_IMAGES.joinpath("combat", "Mythical_cape.png")
            cape = imsearch.search_img_in_rect(menu_selection, self.win.control_panel)
            self.mouse.move_to(cape.random_point(), mouseSpeed='fastest')
            self.mouse.click()
            keyboard.press_and_release('F1')
            return True
        return False
