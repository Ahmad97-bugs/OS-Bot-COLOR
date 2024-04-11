import time
import keyboard
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.imagesearch as imsearch
from src.model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
import pyautogui as pag
from src.utilities import ocr


def wait(api_m, position):
    while api_m.get_player_position() != position:
        time.sleep(0.3)
    return


class OSRSB(OSRSBot):
    def __init__(self):
        self.runes = None
        self.options_set = True
        bot_title = "Battle staff"
        description = (
            "yes staff, air, stuff, craft, something"
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
        self.runes = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            deposit_bank = self.open_bank()
            if not api_m.get_is_inv_empty():
                self.mouse.move_to(deposit_bank.random_point())
                self.mouse.click()
            self.withdraw_from_bank(["Air_orb_bank"], False, False)
            self.withdraw_from_bank(["Battlestaff_bank"], False, True)

            self.mouse.move_to(self.win.inventory_slots[13].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.mouse.move_to(self.win.inventory_slots[14].random_point(), mouseSpeed='fastest')
            self.mouse.click()
            self.sleep(1500, 1800)
            keyboard.press_and_release('space')

            for _ in range(14):
                api_m.wait_til_gained_xp('Crafting', 5)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def refresh_essence(self, api_m):
        if not api_m.get_if_item_in_inv([ids.BLOOD_ESSENCE, ids.BLOOD_ESSENCE_ACTIVE]):
            self.withdraw_from_bank([f'Blood_essence_bank'], True, False)

    def use_pouch(self):
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')
        keyboard.press('shift')
        self.sleep(100, 200)
        self.mouse.click()
        keyboard.release('shift')

    def refresh_energy(self, api_m):
        if api_m.get_run_energy() < 5000:
            self.select_color(clr.LIGHT_BROWN, 'Drink', api_m)
            while api_m.get_run_energy() < 9000:
                time.sleep(0.6)

    def map_search(self, image):
        step_image = imsearch.BOT_IMAGES.joinpath("map", f"{image}.png")
        while not (step_found := imsearch.search_img_in_rect(step_image, self.win.minimap_area)):
            time.sleep(0.2)
        self.mouse.move_to(step_found.random_point(), mouseSpeed='fast')
        self.mouse.click()

    def click_altar(self, api_m: MorgHTTPSocket):
        while not self.get_nearest_tag(clr.GREEN):
            time.sleep(0.2)

        self.select_color(clr.GREEN, 'Craft', api_m)
        api_m.wait_til_gained_xp("Runecraft", 10)
        self.empty_pouches()
        self.select_color(clr.GREEN, 'Craft', api_m)
        api_m.wait_til_gained_xp("Runecraft", 3)
        self.empty_pouches()
        self.select_color(clr.GREEN, 'Craft', api_m)
        api_m.wait_til_gained_xp("Runecraft", 3)

        time.sleep(1.5)  # Gives enough time to let your character become idle
        self.mouse.move_to(self.win.inventory_slots[4].random_point(), mouseSpeed='fastest')
        self.mouse.click()

    def empty_pouches(self):
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')
        self.mouse.click()
        pag.keyUp('shift')

    def repair_pouches(self, api_m: MorgHTTPSocket):
        if api_m.get_if_item_in_inv(ids.COLOSSAL_POUCH_26786):
            spellbook_tab = self.win.cp_tabs[6]
            self.mouse.move_to(spellbook_tab.random_point())
            self.mouse.click()
            npc_contact_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "npc_contact_on.png")
            npc_contact = imsearch.search_img_in_rect(npc_contact_img, self.win.control_panel)
            self.mouse.move_to(npc_contact.random_point())
            self.mouse.right_click()
            if enter_text := ocr.find_text("Dark Mage NPC Contact", self.win.control_panel, ocr.BOLD_12, [clr.WHITE, clr.GREEN]):
                self.mouse.move_to(enter_text[0].random_point(), knotsCount=0)
            self.mouse.click()
            time.sleep(1)
            api_m.wait_til_gained_xp('Magic', 10)
            pag.press('space')
            time.sleep(1)
            pag.press('2')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            self.mouse.move_to(self.win.cp_tabs[3].random_point())
            self.mouse.click()
            time.sleep(1)
