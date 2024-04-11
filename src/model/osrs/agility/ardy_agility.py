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

from src.utilities import ocr
from src.utilities.geometry import Rectangle
from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES


def count_marks(inventory):
    for item in inventory:
        if item.get('id', 0) == 11849:
            return item.get('quantity', 0)


class OSRSAgility(OSRSBot):
    def __init__(self):
        self.amount_of_marks = 0
        self.laps = None
        self.options_set = True
        bot_title = "Ardy Agility"
        description = (
            "Agility + marks"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.laps_run = random.randint(235, 250)
        self.total_laps = 0
        self.total_marks = 0
        self.fails = 0
        self.take_breaks = True

    def create_options(self):
        self.options_builder.add_slider_option("laps_run", "How long to run (laps)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "laps_run":
                self.laps_run = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running laps: {self.laps_run}.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup API
        api_m = MorgHTTPSocket()

        self.laps = 0
        self.amount_of_marks = count_marks(api_m.get_inv())

        obstacles = {
            (2668, 3297, 0): {
                'text': ["Climb", "up", "Wooden", "Beams"],
                'yellow_step': False,
                'mark': False,
                'color': clr.GREEN
            },
            (2671, 3299, 3): {
                'text': ["Jump", "Gap"],
                'yellow_step': True,
                'mark': False,
                'color': clr.ORANGE
            },
            (2671, 3309, 3): {
                'text': ["Jump", "Gap"],
                'yellow_step': False,
                'mark': False,
                'color': clr.ORANGE
            },
            (2665, 3318, 3): {
                'text': ["Walk-on", "Plank"],
                'yellow_step': False,
                'mark': False,
                'color': clr.DARK_BLUE
            },
            (2662, 3318, 3): {
                'text': ["Walk-on", "Plank"],
                'yellow_step': False,
                'mark': False,
                'color': clr.DARK_BLUE
            },
            (2656, 3318, 3): {
                'text': ["Jump", "Gap"],
                'yellow_step': False,
                'mark': True,
                'color': clr.LIGHT_RED
            },
            (2653, 3314, 3): {
                'text': ["Jump", "Gap"],
                'yellow_step': False,
                'mark': False,
                'color': clr.GROUND_PURPLE
            },
            (2651, 3309, 3): {
                'text': ["Balance", "across", "Steep", "roof"],
                'yellow_step': True,
                'mark': False,
                'color': clr.LIGHT_CYAN
            },
            (2653, 3300, 3): {
                'text': ["Balance", "across", "Steep", "roof"],
                'yellow_step': False,
                'mark': False,
                'color': clr.LIGHT_CYAN
            },
            (2656, 3297, 3): {
                'text': ["Jump", "Gap"],
                'yellow_step': False,
                'mark': False,
                'color': clr.DARK_GREEN
            },
        }
        # Main loop
        last_message = api_m.get_latest_chat_message()
        while self.total_laps < self.laps_run:
            if rd.random_chance(probability=0.02) and self.take_breaks:
                self.take_break(max_seconds=10, fancy=True)

            new_message = api_m.get_latest_chat_message()
            if 'Your Ardougne' in new_message and new_message != last_message:
                last_message = new_message
                self.total_laps += 1
                self.log_msg(f"Laps: {self.total_laps}, Marks: {self.total_marks}, Fails: {self.fails}")
                self.update_progress(self.total_laps)
            try:
                if not self.obstacle(obstacles[api_m.get_player_position()], api_m):
                    self.obstacle(obstacles[(2668, 3297, 0)], api_m)
            except KeyError:
                continue

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def pick_up_mark(self):
        if ocr.find_text("Mark of grace", self.win.game_view, ocr.PLAIN_11, [clr.GROUND_PURPLE]):
            while not self.mouseover_text(contains=['Take'], color=[clr.OFF_WHITE]):
                enter_text = ocr.find_text("of", self.win.game_view, ocr.PLAIN_11, [clr.GROUND_PURPLE])
                self.mouse.move_to(enter_text[0].random_point(), mouseSpeed='fastest')
                time.sleep(0.2)
            self.mouse.click()
            return True
        return False

    def obstacle(self, step, api_m):
        if step['yellow_step'] and not self.get_all_tagged_in_rect(self.win.game_view, step['color']):
            if yellow_step := self.get_nearest_tag(clr.YELLOW):
                self.mouse.move_to(yellow_step.random_point(), mouseSpeed='fastest')
                self.mouse.click()
                time.sleep(random.randint(2100, 2400) / 1000)

        if step['mark']:
            if self.pick_up_mark():
                self.total_marks += 1
                self.log_msg(f"Marks collected: ~{self.total_marks}")
                attempt = 0
                while self.amount_of_marks == count_marks(api_m.get_inv()):
                    attempt += 1
                    time.sleep(1)
                    if attempt == 20:
                        break
                self.amount_of_marks = count_marks(api_m.get_inv())

        time.sleep(0.7)
        while not self.mouseover_text(contains=step['text'], color=[clr.OFF_WHITE, clr.OFF_CYAN]):
            if nearest := self.get_all_tagged_in_rect(self.win.game_view, step['color']):
                self.mouse.move_to(nearest[0].random_point(), mouseSpeed='fastest')
        self.mouse.click()
        api_m.wait_til_gained_xp('Agility', 10)
        # while not api_m.get_is_player_idle(1):
        #     time.sleep(0.1)
        if api_m.get_player_position()[2] == 0 and api_m.get_player_position() != (2668, 3297, 0):
            while not self.get_nearest_tag(clr.GREEN):
                if enter_text := self.get_all_tagged_in_rect(self.win.game_view, clr.RED):
                    self.fails += 1
                    self.mouse.move_to(enter_text[0].random_point(), mouseSpeed='fastest')
                    time.sleep(0.2)
                    self.mouse.click()
                    # time.sleep(random.randint(3500, 4500) / 1000)
            return False
        # time.sleep(random.randint(850, 933) / 1000)
        return True
