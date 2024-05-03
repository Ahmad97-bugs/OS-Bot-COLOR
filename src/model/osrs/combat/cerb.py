import src.utilities.imagesearch as imsearch
import random
import time
import keyboard
import requests
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from src.model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject
import pyautogui as pag

from src.utilities.api.morg_http_client import SocketError
from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES
class OSRSBlast(OSRSBot):
    def __init__(self):
        self.clay = None
        self.options_set = True
        self.last_attack = {'attack': None, 'time': 0.0}
        self.two_before = {'attack': None, 'time': 0.0}
        bot_title = "Blast furnace"
        description = (
            "make wine"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 240
        self.take_breaks = True
        self.running = False
        self.last_location = (40, 17, 11603)
        keyboard.add_hotkey('1', self.toggle_script)

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

    def toggle_script(self):
        self.running = not self.running
        if self.running:
            print("Script started")
        else:
            print("Script paused")

    def main_loop(self):
        # Setup API
        api_m = Cerb()
        # Main loop
        api = MorgHTTPSocket()

        start_time = time.time()
        end_time = self.running_time * 60
        prayers = {
            'Magic': self.win.prayers[16],
            'Range': self.win.prayers[17],
            'Melee': self.win.prayers[18]
        }

        while time.time() - start_time < end_time:
            if (attacks := api_m.get_cerb_attack()) and self.running:
                print(attacks)
                # if self.last_attack['attack'] == 'Range' and self.two_before['attack'] == 'Magic' and (abs(self.two_before['time'] - self.last_attack['time']) < 1.5):
                #     self.update_dict('Melee')
                #     self.sleep(600, 623)
                #     self.mouse.move_to(prayers['Melee'].random_point(), mouseSpeed="fastest")
                #     self.mouse.click()
                #     self.sleep(1200, 1423)
                #     continue
                #
                # if attacks == 'Lava':
                #     time.sleep(4)
                #
                # if attacks in ['Magic', 'Range'] and attacks != self.last_attack['attack']:
                #     self.log_msg(attacks)
                #     self.update_dict(attacks)
                #     self.mouse.move_to(prayers[attacks].random_point(), mouseSpeed="fastest")
                #     self.mouse.click()
                #     continue

                # if attacks == self.last_attack['attack'] and attacks != 'Melee' and (abs(time.time() - self.last_attack['time']) > 3.0):
                #     self.update_dict('Melee')
                #     self.mouse.move_to(prayers['Melee'].random_point(), mouseSpeed="fastest")
                #     self.mouse.click()
                #     continue

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def update_dict(self, style):
        self.two_before['attack'] = self.last_attack['attack']
        self.two_before['time'] = self.last_attack['time']
        self.last_attack['attack'] = style
        self.last_attack['time'] = time.time()

class Cerb:
    def __init__(self):
        self.base_endpoint = "http://localhost:8083/"
        self.cerb_endpoint = "cerb"
        self.timeout = 500

    def __do_get(self, endpoint: str) -> dict:
        """
        Args:
                endpoint: One of either "inv", "stats", "equip", "events"
        Returns:
                All JSON data from the endpoint as a dict.
        Raises:
                SocketError: If the endpoint is not valid or the server is not running.
        """
        try:
            response = requests.get(f"{self.base_endpoint}{endpoint}", timeout=self.timeout)
        except ConnectionError as e:
            raise SocketError("Unable to reach socket", endpoint) from e

        if response.status_code != 200:
            if response.status_code == 204:
                return {}
            else:
                raise SocketError(
                    f"Unable to reach socket. Status code: {response.status_code}",
                    endpoint,
                )

        return response.json()

    def test_endpoints(self) -> bool:
        """
        Ensures all endpoints are working correctly to avoid errors happening when any method is called.
        Returns:
                True if successful, False otherwise.
        """
        for i in list(self.__dict__.values())[1:-1]:  # Look away
            try:
                self.__do_get(endpoint=i)
            except SocketError as e:
                print(e)
                print(f"Endpoint {i} is not working.")
                return False
        return True

    def get_cerb_attack(self):
        data = self.__do_get(endpoint=self.cerb_endpoint)
        if attack := data[0].get('attack', ''):
            return attack