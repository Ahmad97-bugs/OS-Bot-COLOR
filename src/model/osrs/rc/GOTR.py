import random
import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSGOTR(OSRSBot):
    def __init__(self):
        bot_title = "GOTR"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
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
            self.first_sequence(api_m)
            self.normal_sequence(api_m)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    # Full sequences

    def first_sequence(self, api_m: MorgHTTPSocket):
        self.log_msg("\t\t\t\t\t\t\t\tFirst sequence")
        self.guardian_remains(api_m)
        self.activate_spec()
        time.sleep(random.randint(125, 130))
        top_rubble = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(top_rubble.random_point())
        while not self.mouseover_text(contains="Climb", color=clr.OFF_WHITE):
            if top_rubble := self.get_nearest_tag(clr.RED):
                self.mouse.move_to(top_rubble.random_point(), mouseSpeed='fast')
            time.sleep(0.2)
        self.mouse.click()
        time.sleep(6)
        self.return_to_start(api_m)
        time.sleep(1)
        self.portal_sequence(api_m)

    def normal_sequence(self, api_m: MorgHTTPSocket):
        self.log_msg("\t\t\t\t\t\t\t\tGather sequence")
        self.get_essence_workbench(api_m)

        self.power_up_guardian(api_m)
        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.is_portal_active(api_m)
        self.deposit_runes(api_m)
        return self.normal_sequence(api_m)

    def portal_sequence(self, api_m: MorgHTTPSocket):
        self.log_msg("                                Portal sequence")
        self.blue_portal_sequence(api_m)
        # time.sleep(1)
        self.power_up_guardian(api_m)

        self.choose_guardian(api_m)
        self.click_altar(api_m)
        self.deposit_runes(api_m)
        self.log_msg("                          Returning to normal sequence")
        return self.normal_sequence(api_m)

    def power_up_guardian(self, api_m: MorgHTTPSocket):
        if api_m.get_if_item_in_inv([ids.CATALYTIC_GUARDIAN_STONE, ids.ELEMENTAL_GUARDIAN_STONE]):
            power_up = self.get_nearest_tag(clr.DARKER_YELLOW)
            while not power_up:
                self.log_msg('looking for guardian')
                power_up = self.get_nearest_tag(clr.DARKER_YELLOW)
                self.is_guardian_defeated(api_m)
                time.sleep(1)
            try:
                self.log_msg("Powering up the guardian..")
                self.mouse.move_to(power_up.random_point())
                self.mouse.click()
                api_m.wait_til_gained_xp("Runecraft", 7)
                pag.press('space')  # In case the game ends before we get to deposit the last batch
                self.is_guardian_defeated(api_m)
            except:
                AttributeError

    def deposit_runes(self, api_m: MorgHTTPSocket):
        self.is_guardian_defeated(api_m)
        if api_m.get_if_item_in_inv([ids.AIR_RUNE, ids.WATER_RUNE, ids.EARTH_RUNE, ids.FIRE_RUNE, ids.MIND_RUNE, ids.BODY_RUNE, ids.CHAOS_RUNE, ids.COSMIC_RUNE, ids.DEATH_RUNE, ids.NATURE_RUNE, ids.BLOOD_RUNE, ids.LAW_RUNE, ids.BLOOD_RUNE]):
            self.log_msg("Heading to deposit runes")
            self.find_deposit()
            counter = 0
            while not self.chatbox_text_BLACK_first_line(contains=f"You deposit all of your runes into the pool"):
                if self.chatbox_text_BLACK(contains="You have no runes to deposit into the pool"):
                    self.log_msg("You had no runes to deposit")
                    break
                self.log_msg("Looking for successful deposit message")
                self.is_guardian_defeated(api_m)
                counter += 1
                time.sleep(1)
                if counter == 8:
                    self.log_msg("Counter reached 15, returning to get_essence_workbench function")
                    return self.normal_sequence(api_m)
            time.sleep(0.5)
        self.is_portal_active(api_m)

    def huge_guardian_remains(self, api_m: MorgHTTPSocket):
        self.is_guardian_defeated(api_m)
        self.log_msg("Running to huge guardian remains")
        while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself in another part of the temple"):
            self.is_guardian_defeated(api_m)
            time.sleep(1)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated(api_m)
            time.sleep(1)
        self.fill_pouches(api_m)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated(api_m)
            time.sleep(1)
        self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest')  # small pouch
        self.mouse.click()
        time.sleep(1)
        self.repair_pouches(api_m)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated(api_m)
            time.sleep(1)

    def click_altar(self, api_m: MorgHTTPSocket):
        time.sleep(random.randint(820, 850) / 1000)

        if red_path := self.get_nearest_tag(clr.RED):
            self.mouse.move_to(red_path.random_point(), mouseSpeed='fast')
            self.mouse.click()
            time.sleep(random.randint(2000, 2300) / 1000)
        while not (altar := self.get_nearest_tag(clr.GREEN)):
            time.sleep(1)

        if altar:
            self.log_msg("Crafting first set of essence..")
            while not self.mouseover_text(contains="Craft", color=clr.OFF_WHITE):
                altar = self.get_nearest_tag(clr.GREEN)
                self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
                time.sleep(0.2)
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 10)
        self.empty_pouches()
        if altar := self.get_nearest_tag(clr.GREEN):
            self.log_msg("Crafting second set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 3)
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest')  # small pouch
        self.mouse.click()
        pag.keyUp('shift')
        if altar := self.get_nearest_tag(clr.GREEN):
            self.log_msg("Crafting third set of essence..")
            self.mouse.move_to(altar.random_point(), mouseSpeed='fast')
            self.mouse.click()
        api_m.wait_til_gained_xp("Runecraft", 3)
        time.sleep(1.5)  # Gives enough time to let your character become idle
        if red_path := self.get_nearest_tag(clr.RED):
            self.mouse.move_to(red_path.random_point(), mouseSpeed='fast')
            self.mouse.click()
            time.sleep(random.randint(2000, 2300) / 1000)
        while not self.mouseover_text(contains="Use", color=clr.OFF_WHITE):
            if portal := self.get_nearest_tag(clr.ORANGE):
                self.mouse.move_to(portal.random_point(), mouseSpeed='fast')
            time.sleep(0.2)
        self.mouse.click()
        self.log_msg("Heading back to main area..")
        # while not self.chatbox_text_BLACK(contains=f"You step through the portal and find yourself back in the temple"):
        #     self.is_guardian_defeated()
        #     time.sleep(1)

    def special_portal(self, api_m: MorgHTTPSocket):
        counter = 0
        self.is_guardian_defeated(api_m)
        portal = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Waiting for portal to appear.")
        while not portal:
            portal = self.get_nearest_tag(clr.CYAN)
            self.activate_spec()
            self.is_guardian_defeated(api_m)
            time.sleep(1)
        self.mouse.move_to(portal.random_point())
        if self.chatbox_text_RED(contains='A portal to the huge guardian fragment mine has opened to the east!') or self.mouseover_text(contains=["Guardian"]):
            self.mouse.right_click()
            if enter_text := ocr.find_text("Enter Portal", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.CYAN]):
                self.mouse.move_to(enter_text[0].random_point(), knotsCount=0)
        self.mouse.click()
        while not self.chatbox_text_BLACK('You step through the portal and find yourself in another part of the temple'):
            counter += 1
            time.sleep(1)
            if counter == 15:
                return self.normal_sequence(api_m)

    def blue_portal_sequence(self, api_m: MorgHTTPSocket):
        self.log_msg("                                 Blue portal sequence")
        # Loop to locate blue portal
        self.is_guardian_defeated(api_m)
        portal = self.get_nearest_tag(clr.CYAN)
        self.log_msg("Waiting for portal to appear.")
        # Constantly check for blue portal to spawn
        counter = 0
        while not portal:
            portal = self.get_nearest_tag(clr.CYAN)
            self.activate_spec()
            self.is_guardian_defeated(api_m)
            counter += 1
            time.sleep(1)
            if counter == 30:
                return self.normal_sequence(api_m)
        while not self.mouseover_text(contains="Enter", color=[clr.OFF_WHITE, clr.OFF_CYAN]):
            if portal := self.get_nearest_tag(clr.CYAN):
                self.mouse.move_to(portal.random_point())
        # This sequence is for the blue portal that spawns on the east side
        if self.chatbox_text_RED(contains='A portal to the huge guardian fragment mine has opened to the east!'):
            self.mouse.right_click()
            if enter_text := ocr.find_text("Enter Portal", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.CYAN]):
                self.mouse.move_to(enter_text[0].random_point(), knotsCount=0)
        self.mouse.click()
        self.log_msg("Heading to huge guardian remains")
        # Counter sequence to break us out of this if we get stuck
        self.check_chatbox_blue_portal(api_m)
        # Mine huge guardian essence
        while not (remains := self.get_nearest_tag(clr.RED)):
            time.sleep(0.6)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        # Check if inventory is full
        self.huge_guardian_remains_is_inv_full(api_m)
        self.fill_pouches(api_m)
        remains = self.get_nearest_tag(clr.RED)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        # Check if inventory is full
        self.huge_guardian_remains_is_inv_full(api_m)
        self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest')
        self.mouse.click()
        time.sleep(1)
        # self.repair_pouches(api_m)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        # Check if inventory is full
        self.huge_guardian_remains_is_inv_full(api_m)
        # Return to the main area via blue portal

        while not self.mouseover_text(contains="Enter", color=clr.OFF_WHITE):
            if portal := self.get_nearest_tag(clr.CYAN):
                self.mouse.move_to(portal.random_point(), mouseSpeed='fastest')
                time.sleep(0.2)
        self.mouse.click()
        self.log_msg("Returning to main area...")
        time.sleep(1)
        self.check_chatbox_blue_portal(api_m)

    def choose_guardian(self, api_m: MorgHTTPSocket):
        self.is_guardian_defeated(api_m)
        self.log_msg("Picking a guardian..")

        chaos_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_chaos.png")
        cosmic_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_cosmic.png")
        earth_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_earth.png")
        fire_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_fire.png")
        nature_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_nature.png")
        water_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_water.png")
        air_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_air.png")
        law_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_law.png")
        body_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_body.png")
        mind_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_mind.png")
        death_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_death.png")
        blood_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_blood.png")

        chaos_pillar = imsearch.search_img_in_rect(chaos_img, self.win.game_view)
        cosmic_pillar = imsearch.search_img_in_rect(cosmic_img, self.win.game_view)
        earth_pillar = imsearch.search_img_in_rect(earth_img, self.win.game_view)
        fire_pillar = imsearch.search_img_in_rect(fire_img, self.win.game_view)
        nature_pillar = imsearch.search_img_in_rect(nature_img, self.win.game_view)
        water_pillar = imsearch.search_img_in_rect(water_img, self.win.game_view)
        air_pillar = imsearch.search_img_in_rect(air_img, self.win.game_view)
        law_pillar = imsearch.search_img_in_rect(law_img, self.win.game_view)
        body_pillar = imsearch.search_img_in_rect(body_img, self.win.game_view)
        mind_pillar = imsearch.search_img_in_rect(mind_img, self.win.game_view)
        death_pillar = imsearch.search_img_in_rect(death_img, self.win.game_view)
        blood_pillar = imsearch.search_img_in_rect(blood_img, self.win.game_view)

        chosen_altar = None
        altar = None

        if blood_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_GREEN)
            chosen_altar = 'Blood'
        # el
        elif fire_pillar:
            altar = self.get_nearest_tag(clr.PINK)
            chosen_altar = 'Fire'
        elif earth_pillar:
            altar = self.get_nearest_tag(clr.PURPLE)
            chosen_altar = 'Earth'
        elif death_pillar:
            altar = self.get_nearest_tag(clr.HIGH_PINK)
            chosen_altar = 'Death'
        elif law_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_PURPLE)
            chosen_altar = 'Law'
        elif nature_pillar:
            altar = self.get_nearest_tag(clr.DARKER_GREEN_50)
            chosen_altar = 'Nature'
        elif cosmic_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_RED)
            chosen_altar = 'Cosmic'
        elif chaos_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_BROWN)
            chosen_altar = 'Chaos'
        elif body_pillar:
            altar = self.get_nearest_tag(clr.LIGHT_CYAN)
            chosen_altar = 'Body'
        elif water_pillar:
            altar = self.get_nearest_tag(clr.BLUE)
            chosen_altar = 'Water'
        elif air_pillar:
            altar = self.get_nearest_tag(clr.DARK_YELLOW)
            chosen_altar = 'Air'
        elif mind_pillar:
            altar = self.get_nearest_tag(clr.DARK_ORANGE)
            chosen_altar = 'Mind'

        colors = {
            'Law': clr.LIGHT_PURPLE,
            'Fire': clr.PINK,
            'Chaos': clr.LIGHT_BROWN,
            'Nature': clr.DARKER_GREEN_50,
            'Mind': clr.DARK_ORANGE,
            'Earth': clr.PURPLE,
            'Cosmic': clr.LIGHT_RED,
            'Body': clr.LIGHT_CYAN,
            'Water': clr.BLUE,
            'Air': clr.DARK_YELLOW,
            'Death': clr.HIGH_PINK,
            'Blood': clr.LIGHT_GREEN
        }

        try:
            if self.chatbox_text_BLACK_first_line(contains=f"You step through the rift and find yourself at the"):
                chosen_altar = None
                return self.choose_guardian(api_m)
        except UnboundLocalError:
            self.log_msg("Idk why this happens lol")

        self.is_guardian_defeated(api_m)
        self.log_msg(f"Going to {chosen_altar} altar")
        try:
            altar = self.get_nearest_tag(colors[chosen_altar])
            self.mouse.move_to(altar.random_point(), mouseSpeed='fastest')
            time.sleep(0.2)
            while not self.mouseover_text(contains="Enter", color=clr.OFF_WHITE):
                altar = self.get_nearest_tag(colors[chosen_altar])
                self.mouse.move_to(altar.random_point(), mouseSpeed='fastest')
                time.sleep(0.2)
            self.mouse.click()
        except (AttributeError, KeyError):
            self.log_msg(f"Could not locate {chosen_altar} pillar")
            return self.choose_guardian(api_m)
        self.is_guardian_defeated(api_m)
        while not self.chatbox_text_BLACK_first_line(contains=f"You step through the rift and find yourself at the"):
            self.is_guardian_defeated(api_m)
            time.sleep(1)
            if self.chatbox_text_QUEST(contains="The Guardian is dormant. Its energy might return soon."):
                pag.press('space')
                self.log_msg("Altar was dormant. Trying again")
                self.choose_guardian(api_m)
                break
        self.log_msg(f"Successfully entered the {chosen_altar} altar room!!")

    # Mini-sequences
    def get_essence_workbench(self, api_m: MorgHTTPSocket):
        self.check_chatbox_guardian_fragment()
        self.is_guardian_defeated(api_m)
        self.log_msg("Waiting until inventory is full..")
        self.work_at_bench()
        api_m.wait_til_gained_xp("Crafting", 5)
        self.workbench_is_inv_full(api_m)
        pag.press('space')
        self.fill_pouches(api_m)
        self.log_msg("Waiting until inventory is full #2..")
        self.work_at_bench()
        self.workbench_is_inv_full(api_m)
        pag.press('space')
        self.mouse.move_to(self.win.inventory_slots[3].random_point(), mouseSpeed='fastest')  # fill giant pouch
        self.mouse.click()
        time.sleep(1)
        self.repair_pouches(api_m)
        self.log_msg("Waiting until inventory is full #3..")
        self.work_at_bench()
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more essence"):
            self.is_guardian_defeated(api_m)
            if self.chatbox_text_BLACK_first_line(contains="You have no more guardian fragments to combine"):
                break
            time.sleep(1)
        pag.press('space')

    # Check functions
    def is_portal_active(self, api_m: MorgHTTPSocket):
        portal = self.get_nearest_tag(clr.CYAN)
        if portal:
            portal = self.get_nearest_tag(clr.CYAN)
            return self.portal_sequence(api_m)

    def workbench_is_inv_full(self, api_m: MorgHTTPSocket):
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more essence"):
            self.is_portal_active(api_m)
            if self.chatbox_text_GREEN(contains="The Great Guardian"):
                self.power_up_guardian(api_m)
                break
            self.is_guardian_defeated(api_m)
            if self.chatbox_text_BLACK_first_line(contains="You have no more guardian fragments to combine"):
                break
            time.sleep(1)

    def huge_guardian_remains_is_inv_full(self, api_m):
        while not self.chatbox_text_QUEST(contains="Your inventory is too full to hold any more guardian essence"):
            self.is_guardian_defeated(api_m)
            time.sleep(1)

    def is_guardian_active(self):
        while not self.chatbox_text_RED(contains="The rift becomes active!"):
            self.log_msg("Waiting for new game to start..")
            if orange_portal := self.get_nearest_tag(clr.ORANGE):
                self.mouse.move_to(orange_portal.random_point())
                self.mouse.click()
            time.sleep(1)

    def is_guardian_defeated(self, api_m):
        game_ended_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "game_ended.png")
        if self.chatbox_text_GREEN(contains="The Great Guardian") or self.chatbox_text_RED(contains="defeated") or imsearch.search_img_in_rect(game_ended_img, self.win.game_view):
            self.log_msg("Game has ended.")
            time.sleep(1)
            orange_portal = self.get_nearest_tag(clr.ORANGE)
            blue_portal = self.get_nearest_tag(clr.CYAN)
            if blue_portal:
                if api_m.get_player_position()[0] <= 3591:
                    self.blue_portal()
                    time.sleep(5)
                return_to_start = self.get_nearest_tag(clr.DARKER_GREEN)
                if return_to_start:
                    self.return_to_start(api_m)
                    time.sleep(1)
            elif self.get_nearest_tag(clr.DARKER_GREEN):
                self.return_to_start(api_m)
                time.sleep(1)
            elif orange_portal:
                self.orange_portal(api_m)
                time.sleep(5)
                return_to_start = self.get_nearest_tag(clr.DARKER_GREEN)
                if return_to_start:
                    self.return_to_start(api_m)
            time.sleep(3)
            self.top_rubble(api_m)
            time.sleep(1)
            self.is_guardian_active()
            return self.main_loop()

    def check_chatbox_guardian_fragment(self):
        while self.chatbox_text_QUEST("You'll need at least one guardian fragment to craft guardian essence."):
            time.sleep(1)
            pag.press('space')

    def check_chatbox_blue_portal(self, api_m: MorgHTTPSocket):
        counter = 0
        # portal_active = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_portal.png")
        self.log_msg("Checking chat for 'another part of the temple' after clicking blue portal")
        while not self.chatbox_text_BLACK_first_line('You step through the portal and find yourself in another part of the temple'):
            self.is_guardian_defeated(api_m)
            counter += 1
            time.sleep(1)
            if counter == 15:
                self.log_msg("Returning to normal sequence")
                return self.normal_sequence(api_m)

    # Smaller functions
    def activate_spec(self):
        spec_energy = self.get_special_energy()
        if spec_energy >= 100:
            self.mouse.move_to(self.win.spec_orb.random_point())
            self.mouse.click()

    def fill_pouches(self, api_m: MorgHTTPSocket):
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')  # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest')  # medium pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[2].random_point(), mouseSpeed='fastest')  # large pouch
        self.mouse.click()
        # time.sleep(1)
        # self.repair_pouches(api_m)

    def empty_pouches(self):
        pag.keyDown('shift')
        self.mouse.move_to(self.win.inventory_slots[0].random_point(), mouseSpeed='fastest')  # small pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[1].random_point(), mouseSpeed='fastest')  # medium pouch
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[2].random_point(), mouseSpeed='fastest')  # large pouch
        self.mouse.click()
        pag.keyUp('shift')

    def repair_pouches(self, api_m: MorgHTTPSocket):
        # giant_rune_pouch_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "giant_pouch.png")
        giant_rune_pouch_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "Large_pouch.png")
        giant_rune_pouch = imsearch.search_img_in_rect(giant_rune_pouch_img, self.win.inventory_slots[2])
        if not giant_rune_pouch:
            spellbook_tab = self.win.cp_tabs[6]
            self.mouse.move_to(spellbook_tab.random_point())
            self.mouse.click()
            npc_contact_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "npc_contact_on.png")
            npc_contact = imsearch.search_img_in_rect(npc_contact_img, self.win.control_panel)
            self.mouse.move_to(npc_contact.random_point())
            self.mouse.click()
            time.sleep(1)
            dark_mage_img = imsearch.BOT_IMAGES.joinpath("gotr_image", "npc_contact_darkmage.png")
            dark_mage = imsearch.search_img_in_rect(dark_mage_img, self.win.game_view)
            self.mouse.move_to(dark_mage.random_point())
            self.mouse.click()
            api_m.wait_til_gained_xp('Magic', 10)
            pag.press('space')
            time.sleep(1)
            pag.press('2')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            pag.press('2')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            pag.press('2')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            pag.press('space')
            time.sleep(1)
            self.mouse.move_to(self.win.cp_tabs[3].random_point())
            self.mouse.click()
            time.sleep(1)

    def find_deposit(self):
        while not self.mouseover_text(contains="Deposit", color=clr.OFF_WHITE):
            if deposit := self.get_nearest_tag(clr.DARK_BLUE):
                self.mouse.move_to(deposit.random_point())
            time.sleep(0.2)
        self.mouse.click()

    def work_at_bench(self):
        self.log_msg("Converting fragments to essence..")
        while not self.mouseover_text(contains="Work", color=clr.OFF_WHITE):
            if workbench := self.get_nearest_tag(clr.DARK_PURPLE):
                self.mouse.move_to(workbench.random_point(), mouseSpeed='fast')
            time.sleep(0.2)
        self.mouse.click()

    def guardian_remains(self, api_m: MorgHTTPSocket):
        self.is_guardian_defeated(api_m)
        self.log_msg("Mining guardian fragments")
        remains = self.get_nearest_tag(clr.YELLOW)
        self.mouse.move_to(remains.random_point(), mouseSpeed='fast')
        self.mouse.click()
        api_m.wait_til_gained_xp('Mining', 10)
        self.is_guardian_defeated(api_m)

    def return_to_start(self, api_m):
        if api_m.get_player_position()[0] <= 3591:
            self.blue_portal()
            time.sleep(5)
        self.power_up_guardian(api_m)
        if return_to_start := self.get_nearest_tag(clr.DARKER_GREEN):
            self.mouse.move_to(return_to_start.random_point())
            self.mouse.click()
        time.sleep(3)

    def orange_portal(self, api_m):
        if red_path := self.get_nearest_tag(clr.RED):
            self.mouse.move_to(red_path.random_point(), mouseSpeed='fast')
            self.mouse.click()
            time.sleep(random.randint(2000, 2300) / 1000)
        while not self.mouseover_text(contains="Use", color=clr.OFF_WHITE):
            if api_m.get_player_region_data()(2) == 14484:
                return
            if portal := self.get_nearest_tag(clr.ORANGE):
                self.mouse.move_to(portal.random_point(), mouseSpeed='fast')
            time.sleep(0.2)
        self.mouse.click()
        self.log_msg("Heading back to main area..")
        while not self.chatbox_text_BLACK(contains="You step through the portal and find yourself back in the temple"):
            time.sleep(1)

    def blue_portal(self):
        if self.get_nearest_tag(clr.CYAN):
            while not self.mouseover_text(contains="Enter", color=clr.OFF_WHITE):
                blue_portal = self.get_nearest_tag(clr.CYAN)
                self.mouse.move_to(blue_portal.random_point())
            self.mouse.click()
            while not self.chatbox_text_BLACK('You step through the portal and find yourself in another part of the temple'):
                time.sleep(1)

    def top_rubble(self, api_m):
        portal_active = imsearch.BOT_IMAGES.joinpath("gotr_image", "gotr_portal.png")

        while imsearch.search_img_in_rect(portal_active, self.win.game_view) or self.get_nearest_tag(clr.CYAN):
            time.sleep(1)
        walk = imsearch.BOT_IMAGES.joinpath("gotr_image", "walk.png")
        while not (next_rubble := imsearch.search_img_in_rect(walk, self.win.game_view)):
            time.sleep(1)
        self.mouse.move_to(next_rubble.random_point(), mouseSpeed='fast')
        self.mouse.click()
        time.sleep(random.randint(5000, 6000) / 1000)
        self.pink_rock()
        time.sleep(random.randint(2000, 3000) / 1000)
        if 'I can' in api_m.get_latest_chat_message():
            self.pink_rock()

    def pink_rock(self):
        pink_rock_image = imsearch.BOT_IMAGES.joinpath("gotr_image", "pink_rock.png")
        while not self.mouseover_text(contains="Climb", color=clr.OFF_WHITE):
            if rock_found := imsearch.search_img_in_rect(pink_rock_image, self.win.game_view):
                self.mouse.move_to(rock_found.random_point(), mouseSpeed='fast')
            time.sleep(0.5)
        self.mouse.click()
