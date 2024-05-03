"""
A Bot is a base class for bot script models. It is abstract and cannot be instantiated. Many of the methods in this base class are
pre-implemented and can be used by subclasses, or called by the controller. Code in this class should not be modified.
"""
import ctypes
import platform
import re
import threading
import warnings
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union

import customtkinter
import numpy as np
import pyautogui as pag
import pytweening
from deprecated import deprecated

import src.utilities.color as clr
import src.utilities.debug as debug
import src.utilities.imagesearch as imsearch
import src.utilities.ocr as ocr
import src.utilities.random_util as rd
from src.utilities.geometry import Point, Rectangle
from src.utilities.mouse import Mouse
from src.utilities.options_builder import OptionsBuilder
from src.utilities.window import Window, WindowInitializationError
import random
import time
import keyboard
import pyautogui

import src.utilities.color as clr
import src.utilities.random_util as rd

from src.utilities.api.morg_http_client import MorgHTTPSocket
from src.utilities.imagesearch import search_img_in_rect, BOT_IMAGES

warnings.filterwarnings("ignore", category=UserWarning)


class BotThread(threading.Thread):
    def __init__(self, target: callable):
        threading.Thread.__init__(self)
        self.target = target

    def run(self):
        try:
            print("Thread started.")
            self.target()
        finally:
            print("Thread stopped successfully.")

    def __get_id(self):
        """Returns id of the respective thread"""
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop(self):
        """Raises SystemExit exception in the thread. This can be called from the main thread followed by join()."""
        thread_id = self.__get_id()
        if platform.system() == "Windows":
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                print("Exception raise failure")
        elif platform.system() == "Linux":
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(SystemExit))
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)
                print("Exception raise failure")


class BotStatus(Enum):
    """
    BotStatus enum.
    """

    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    CONFIGURING = 4
    CONFIGURED = 5


class Bot(ABC):
    mouse = Mouse()
    options_set: bool = False
    progress: float = 0
    status = BotStatus.STOPPED
    thread: BotThread = None

    @abstractmethod
    def __init__(self, game_title, bot_title, description, window: Window):
        """
        Instantiates a Bot object. This must be called by subclasses.
        Args:
            game_title: title of the game the bot will interact with
            bot_title: title of the bot to display in the UI
            description: description of the bot to display in the UI
            window: window object the bot will use to interact with the game client
            launchable: whether the game client can be launched with custom arguments from the bot's UI
        """
        self.game_title = game_title
        self.bot_title = bot_title
        self.description = description
        self.options_builder = OptionsBuilder(bot_title)
        self.win = window

    @abstractmethod
    def main_loop(self):
        """
        Main logic of the bot. This function is called in a separate thread.
        """
        pass

    @abstractmethod
    def create_options(self):
        """
        Defines the options for the bot using the OptionsBuilder.
        """
        pass

    @abstractmethod
    def save_options(self, options: dict):
        """
        Saves a dictionary of options as properties of the bot.
        Args:
            options: dict - dictionary of options to save
        """
        pass

    def get_options_view(self, parent) -> customtkinter.CTkFrame:
        """
        Builds the options view for the bot based on the options defined in the OptionsBuilder.
        """
        self.clear_log()
        self.log_msg("Options panel opened.")
        self.create_options()
        view = self.options_builder.build_ui(parent, self.controller)
        self.options_builder.options = {}
        return view

    def play(self):
        """
        Fired when the user starts the bot manually. This function performs necessary set up on the UI
        and locates/initializes the game client window. Then, it launches the bot's main loop in a separate thread.
        """
        if self.status in [BotStatus.STOPPED, BotStatus.CONFIGURED]:
            self.clear_log()
            self.log_msg("Starting bot...")
            if not self.options_set:
                self.log_msg("Options not set. Please set options before starting.")
                return
            try:
                self.__initialize_window()
            except WindowInitializationError as e:
                self.log_msg(str(e))
                return
            self.reset_progress()
            self.set_status(BotStatus.RUNNING)
            self.thread = BotThread(target=self.main_loop)
            self.thread.setDaemon(True)
            self.thread.start()
        elif self.status == BotStatus.RUNNING:
            self.log_msg("Bot is already running.")
        elif self.status == BotStatus.CONFIGURING:
            self.log_msg("Please finish configuring the bot before starting.")

    def __initialize_window(self):
        """
        Attempts to focus and initialize the game window by identifying core UI elements.
        """
        self.win.focus()
        time.sleep(0.5)
        self.win.initialize()

    def stop(self):
        """
        Fired when the user stops the bot manually.
        """
        self.log_msg("Stopping script.")
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
            self.thread.stop()
            self.thread.join()
        else:
            self.log_msg("Bot is already stopped.")

    # ---- Controller Setter ----
    def set_controller(self, controller):
        self.controller = controller

    # ---- Functions that notify the controller of changes ----
    def reset_progress(self):
        """
        Resets the current progress property to 0 and notifies the controller to update UI.
        """
        self.progress = 0
        self.controller.update_progress()

    def update_progress(self, progress: float):
        """
        Updates the progress property and notifies the controller to update UI.
        Args:
            progress: float - number between 0 and 1 indicating percentage of progress.
        """
        if progress < 0:
            progress = 0
        elif progress > 1:
            progress = 1
        self.progress = progress
        self.controller.update_progress()

    def set_status(self, status: BotStatus):
        """
        Sets the status property of the bot and notifies the controller to update UI accordingly.
        Args:
            status: BotStatus - status to set the bot to
        """
        self.status = status
        self.controller.update_status()

    def walk_to(self, destination, api_m):
        current_location = api_m.get_player_position()
        while abs(current_location[0] - destination[0]) > 5 or abs(current_location[1] - destination[1]) > 5:
            x_move = -60
            # ok
            y_move = 50

            # ok
            if (destination[0] - current_location[0]) > 17:
                x_move = 60
            elif 17 > (x_destination := (destination[0] - current_location[0])) > 0:
                x_move = -1 * (x_destination / 17 * 60)
            # ok
            elif 0 > (x_destination := (destination[0] - current_location[0])) > -17:
                x_move = x_destination / 17 * 60

            if (destination[1] - current_location[1]) > 14:
                y_move = -50
            # ok
            elif 14 > (y_destination := (destination[1] - current_location[1])) > 0:
                y_move = y_destination / 17 * 50
            elif 0 > (y_destination := (destination[1] - current_location[1])) > -14:
                y_move = -1 * (y_destination / 14 * 50)

            x = int(self.win.minimap.get_center().x + x_move)
            y = int(self.win.minimap.get_center().y + y_move)
            self.mouse.move_to((x, y))
            # self.mouse.click()

            while not (api_m.get_is_player_idle(0.2)):
                time.sleep(0.2)


    def log_msg(self, msg: str, overwrite=False):
        '''
        Sends a message to the controller to be displayed in the log for the user.
        Args:
            msg: str - message to log
            overwrite: bool - if True, overwrites the current log message. If False, appends to the log.
        '''
        self.controller.update_log(msg, overwrite)

    def clear_log(self):
        '''
        Requests the controller to tell the UI to clear the log.
        '''
        self.controller.clear_log()

    # --- Misc Utility Functions
    def drop_all(self, skip_rows: int = 0, skip_slots: List[int] = None) -> None:
        """
        Shift-clicks all items in the inventory to drop them.
        Args:
            skip_rows: The number of rows to skip before dropping.
            skip_slots: The indices of slots to avoid dropping.
        """
        self.log_msg("Dropping inventory...")
        # Determine slots to skip
        if skip_slots is None:
            skip_slots = []
        if skip_rows > 0:
            row_skip = list(range(skip_rows * 4))
            skip_slots = np.unique(row_skip + skip_slots)
        # Start dropping
        pag.keyDown("shift")
        for i, slot in enumerate(self.win.inventory_slots):
            if i in skip_slots:
                continue
            p = slot.random_point()
            self.mouse.move_to(
                (p[0], p[1]),
                mouseSpeed="fastest",
                knotsCount=1,
                offsetBoundaryY=40,
                offsetBoundaryX=40,
                tween=pytweening.easeInOutQuad,
            )
            self.mouse.click()
        pag.keyUp("shift")

    def chatbox_text_QUEST(self, contains: str = None) -> Union[bool, str]:
        """
        Examines the chatbox for text. Currently only captures player chat text.
        Args:
            contains: The text to search for (single word or phrase). Case sensitive. If left blank,
                      returns all text in the chatbox.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the chatbox.
        """
        if contains is None:
            return ocr.extract_text(self.win.chat, ocr.QUILL_8, clr.BLACK)
        if ocr.find_text(contains, self.win.chat, ocr.QUILL_8, clr.BLACK):
            return True

    def chatbox_text_BLACK(self, contains: str = None) -> Union[bool, str]:
        """
        Examines the chatbox for text. Currently only captures player chat text.
        Args:
            contains: The text to search for (single word or phrase). Case sensitive. If left blank,
                      returns all text in the chatbox.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the chatbox.
        """
        if contains is None:
            return ocr.extract_text(self.win.chat, ocr.PLAIN_12, clr.BLACK)
        if ocr.find_text(contains, self.win.chat, ocr.PLAIN_12, clr.BLACK):
            return True

    def chatbox_text_BLACK_first_line(self, contains: str = None) -> Union[bool, str]:
        """
        Examines the chatbox for text. Currently only captures player chat text.
        Args:
            contains: The text to search for (single word or phrase). Case sensitive. If left blank,
                      returns all text in the chatbox.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the chatbox.
        """
        if contains is None:
            return ocr.extract_text(self.win.chat_first_line, ocr.PLAIN_12, clr.BLACK)
        if ocr.find_text(contains, self.win.chat_first_line, ocr.PLAIN_12, clr.BLACK):
            return True

    def chatbox_text_RED(self, contains: str = None) -> Union[bool, str]:
        """
        Examines the chatbox for text. Currently only captures player chat text.
        Args:
            contains: The text to search for (single word or phrase). Case sensitive. If left blank,
                      returns all text in the chatbox.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the chatbox.
        """
        if contains is None:
            return ocr.extract_text(self.win.chat, ocr.PLAIN_12, clr.TEXT_RED)
        if ocr.find_text(contains, self.win.chat, ocr.PLAIN_12, clr.TEXT_RED):
            return True

    def chatbox_text_GREEN(self, contains: str = None) -> Union[bool, str]:
        """
        Examines the chatbox for text. Currently only captures player chat text.
        Args:
            contains: The text to search for (single word or phrase). Case sensitive. If left blank,
                      returns all text in the chatbox.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the chatbox.
        """
        if contains is None:
            return ocr.extract_text(self.win.chat, ocr.PLAIN_12, clr.TEXT_GREEN)
        if ocr.find_text(contains, self.win.chat, ocr.PLAIN_12, clr.TEXT_GREEN):
            return True

    def drop(self, slots: List[int]) -> None:
        """
        Shift-clicks inventory slots to drop items.
        Args:
            slots: The indices of slots to drop.
        """
        self.log_msg("Dropping items...")
        pag.keyDown("shift")
        drop_order = generate_matrix_path()
        for spot in drop_order:
            if spot not in slots:
                continue
            p = self.win.inventory_slots[spot].random_point()
            self.mouse.move_to(
                (p[0], p[1]),
                mouseSpeed="fastestest",
                offsetBoundaryY=40,
                offsetBoundaryX=40,
                tween=pytweening.easeInOutQuad,
            )
            self.mouse.click()
        pag.keyUp("shift")

    def friends_nearby(self) -> bool:
        """
        Checks the minimap for green dots to indicate friends nearby.
        Returns:
            True if friends are nearby, False otherwise.
        """
        minimap = self.win.minimap.screenshot()
        # debug.save_image("minimap.png", minimap)
        only_friends = clr.isolate_colors(minimap, [clr.GREEN])
        # debug.save_image("minimap_friends.png", only_friends)
        mean = only_friends.mean(axis=(0, 1))
        return mean != 0.0

    def logout(self):  # sourcery skip: class-extract-method
        """
        Logs player out.
        """
        self.log_msg("Logging out...")
        self.mouse.move_to(self.win.cp_tabs[10].random_point())
        self.mouse.click()
        time.sleep(1)
        self.mouse.move_rel(0, -53, 5, 5)
        self.mouse.click()

    def take_break(self, min_seconds: int = 1, max_seconds: int = 30, fancy: bool = False):
        """
        Takes a break for a random amount of time.
        Args:
            min_seconds: minimum amount of time the bot could rest
            max_seconds: maximum amount of time the bot could rest
            fancy: if True, the randomly generated value will be from a truncated normal distribution
                   with randomly selected means. This may produce more human results.
        """
        self.log_msg("Taking a break...")
        if fancy:
            length = rd.fancy_normal_sample(min_seconds, max_seconds)
        else:
            length = rd.truncated_normal_sample(min_seconds, max_seconds)
        length = round(length)
        for i in range(length):
            self.log_msg(f"Taking a break... {int(length) - i} seconds left.", overwrite=True)
            time.sleep(1)
        self.log_msg(f"Done taking {length} second break.", overwrite=True)

    # --- Player Status Functions ---
    def has_hp_bar(self) -> bool:
        """
        Returns whether the player has an HP bar above their head. Useful alternative to using OCR to check if the
        player is in combat. This function only works when the game camera is all the way up.
        """
        # Position of character relative to the screen
        char_pos = self.win.game_view.get_center()

        # Make a rectangle around the character
        offset = 30
        char_rect = Rectangle.from_points(
            Point(char_pos.x - offset, char_pos.y - offset),
            Point(char_pos.x + offset, char_pos.y + offset),
        )
        # Take a screenshot of rect
        char_screenshot = char_rect.screenshot()
        # Isolate HP bars in that rectangle
        hp_bars = clr.isolate_colors(char_screenshot, [clr.RED, clr.GREEN])
        # If there are any HP bars, return True
        return hp_bars.mean(axis=(0, 1)) != 0.0

    def get_hp(self) -> int:
        """
        Gets the HP value of the player. Returns -1 if the value couldn't be read.
        """
        if res := ocr.extract_text(self.win.hp_orb_text, ocr.PLAIN_11, [clr.ORB_GREEN, clr.ORB_RED]):
            return int("".join(re.findall(r"\d", res)))
        return -1

    def get_prayer(self) -> int:
        """
        Gets the Prayer points of the player. Returns -1 if the value couldn't be read.
        """
        if res := ocr.extract_text(self.win.prayer_orb_text, ocr.PLAIN_11, [clr.ORB_GREEN, clr.ORB_RED]):
            return int("".join(re.findall(r"\d", res)))
        return -1

    def get_run_energy(self) -> int:
        """
        Gets the run energy of the player. Returns -1 if the value couldn't be read.
        """
        if res := ocr.extract_text(self.win.run_orb_text, ocr.PLAIN_11, [clr.ORB_GREEN, clr.ORB_RED]):
            return int("".join(re.findall(r"\d", res)))
        return -1

    def get_special_energy(self) -> int:
        """
        Gets the special attack energy of the player. Returns -1 if the value couldn't be read.
        """
        if res := ocr.extract_text(self.win.spec_orb_text, ocr.PLAIN_11, [clr.ORB_GREEN, clr.ORB_RED]):
            return int("".join(re.findall(r"\d", res)))
        return -1

    def get_total_xp(self) -> int:
        """
        Gets the total XP of the player using OCR. Returns -1 if the value couldn't be read.
        """
        fonts = [ocr.PLAIN_11, ocr.PLAIN_12, ocr.BOLD_12]
        for font in fonts:
            if res := ocr.extract_text(self.win.total_xp, font, [clr.WHITE]):
                return int("".join(re.findall(r"\d", res)))
        return -1

    def mouseover_text(
        self,
        contains: Union[str, List[str]] = None,
        color: Union[clr.Color, List[clr.Color]] = None,
    ) -> Union[bool, str]:
        """
        Examines the mouseover text area.
        Args:
            contains: The text to search for (single word, phrase, or list of words). Case sensitive. If left blank,
                      returns all text in the mouseover area.
            color: The color(s) to isolate. If left blank, isolates all expected colors. Consider using
                   clr.OFF_* colors for best results.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the mouseover area.
        """
        if color is None:
            color = [
                clr.OFF_CYAN,
                clr.OFF_GREEN,
                clr.OFF_ORANGE,
                clr.OFF_WHITE,
                clr.OFF_YELLOW,
            ]
        if contains is None:
            return ocr.extract_text(self.win.mouseover, ocr.BOLD_12, color)
        return bool(ocr.find_text(contains, self.win.mouseover, ocr.BOLD_12, color))

    def chatbox_text(self, contains: str = None) -> Union[bool, str]:
        """
        Examines the chatbox for text. Currently only captures player chat text.
        Args:
            contains: The text to search for (single word or phrase). Case sensitive. If left blank,
                      returns all text in the chatbox.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the chatbox.
        """
        if contains is None:
            return ocr.extract_text(self.win.chat, ocr.PLAIN_12, clr.BLUE)
        if ocr.find_text(contains, self.win.chat, ocr.PLAIN_12, clr.BLUE):
            return True

    # --- Client Settings ---
    def set_compass_north(self):
        self.log_msg("Setting compass North...")
        self.mouse.move_to(self.win.compass_orb.random_point())
        self.mouse.click()

    def set_compass_west(self):
        self.__compass_right_click("Setting compass West...", 72)

    def set_compass_east(self):
        self.__compass_right_click("Setting compass East...", 43)

    def set_compass_south(self):
        self.__compass_right_click("Setting compass South...", 57)

    def __compass_right_click(self, msg, rel_y):
        self.log_msg(msg)
        self.mouse.move_to(self.win.compass_orb.random_point())
        self.mouse.right_click()
        self.mouse.move_rel(0, rel_y, 5, 2)
        self.mouse.click()

    def move_camera(self, horizontal: int = 0, vertical: int = 0):
        """
        Rotates the camera by specified degrees in any direction.
        Agrs:
            horizontal: The degree to rotate the camera (-360 to 360).
            vertical: The degree to rotate the camera up (-90 to 90).
        Note:
            A negative degree will rotate the camera left or down.
        """
        if horizontal == 0 and vertical == 0:
            raise ValueError("Must specify at least one argument.")
        if horizontal < -360 or horizontal > 360:
            raise ValueError("Horizontal degree must be between -360 and 360.")
        if vertical < -90 or vertical > 90:
            raise ValueError("Vertical degree must be between -90 and 90.")

        rotation_time_h = 3.549  # seconds to do a full 360 degree rotation horizontally
        rotation_time_v = 1.75  # seconds to do a full 90 degree rotation vertically
        sleep_h = rotation_time_h / 360 * abs(horizontal)  # time to hold arrow key
        sleep_v = rotation_time_v / 90 * abs(vertical)  # time to hold arrow key

        direction_h = "right" if horizontal < 0 else "left"
        direction_v = "down" if vertical < 0 else "up"

        def keypress(direction, duration):
            pag.keyDown(direction)
            time.sleep(duration)
            pag.keyUp(direction)

        thread_h = threading.Thread(target=keypress, args=(direction_h, sleep_h), daemon=True)
        thread_v = threading.Thread(target=keypress, args=(direction_v, sleep_v), daemon=True)
        delay = rd.fancy_normal_sample(0, max(sleep_h, sleep_v))
        if sleep_h > sleep_v:
            thread_h.start()
            time.sleep(delay)
            thread_v.start()
        else:
            thread_v.start()
            time.sleep(delay)
            thread_h.start()
        thread_h.join()
        thread_v.join()

    def toggle_auto_retaliate(self, toggle_on: bool):
        """
        Toggles auto retaliate. Assumes client window is configured.
        Args:
            toggle_on: Whether to turn on or off.
        """
        state = "on" if toggle_on else "off"
        self.log_msg(f"Toggling auto retaliate {state}...")
        # click the combat tab
        self.mouse.move_to(self.win.cp_tabs[0].random_point())
        self.mouse.click()
        time.sleep(0.5)

        if toggle_on:
            if auto_retal_btn := imsearch.search_img_in_rect(
                imsearch.BOT_IMAGES.joinpath("combat", "autoretal_off.png"),
                self.win.control_panel,
            ):
                self.mouse.move_to(auto_retal_btn.random_point(), mouseSpeed="medium")
                self.mouse.click()
            else:
                self.log_msg("Auto retaliate is already on.")
        elif auto_retal_btn := imsearch.search_img_in_rect(
            imsearch.BOT_IMAGES.joinpath("combat", "autoretal_on.png"),
            self.win.control_panel,
        ):
            self.mouse.move_to(auto_retal_btn.random_point(), mouseSpeed="medium")
            self.mouse.click()
        else:
            self.log_msg("Auto retaliate is already off.")

    def select_combat_style(self, combat_style: str):
        """
        Selects a combat style from the combat tab.
        Args:
            combat_style: the attack type ("accurate", "aggressive", "defensive", "controlled", "rapid", "longrange").
        """
        # Ensuring that args are valid
        if combat_style not in ["accurate", "aggressive", "defensive", "controlled", "rapid", "longrange"]:
            raise ValueError(f"Invalid combat style: {combat_style}. See function docstring for valid options.")

        # Click the combat tab
        self.mouse.move_to(self.win.cp_tabs[0].random_point(), mouseSpeed="fastest")
        self.mouse.click()

        # It is important to keep ambiguous words at the end of the list so that they are matched as a last resort
        styles = {
            "accurate": ["Accurate", "Short fuse", "Punch", "Chop", "Jab", "Stab", "Spike", "Reap", "Bash", "Flick", "Pound", "Pummel"],
            "aggressive": ["Kick", "Smash", "Hack", "Swipe", "Slash", "Impale", "Lunge", "Pummel", "Chop", "Pound"],
            "defensive": ["Block", "Fend", "Focus", "Deflect"],
            "controlled": ["Spike", "Lash", "Lunge", "Jab"],
            "rapid": [
                "Rapid",
                "Medium fuse",
            ],
            "longrange": [
                "Longrange",
                "Long fuse",
            ],
        }

        for style in styles[combat_style]:
            # Try and find the center of the word with OCR
            if result := ocr.find_text(style, self.win.control_panel, ocr.PLAIN_11, clr.OFF_ORANGE):
                # If the word is found, draw a rectangle around it and click a random point in that rectangle
                center = result[0].get_center()
                rect = Rectangle.from_points(Point(center[0] - 32, center[1] - 34), Point(center[0] + 32, center[1] + 10))
                self.mouse.move_to(rect.random_point(), mouseSpeed="fastest")
                self.mouse.click()
                self.log_msg(f"Combat style {combat_style} selected.")
                return
        self.log_msg(f"{combat_style.capitalize()} style not found.")

    def toggle_run(self, toggle_on: bool):
        """
        Toggles run. Assumes client window is configured. Images not included.
        Args:
            toggle_on: True to turn on, False to turn off.
        """
        state = "on" if toggle_on else "off"
        self.log_msg(f"Toggling run {state}...")

        if toggle_on:
            if run_status := imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("run_off.png"), self.win.run_orb, 0.323):
                self.mouse.move_to(run_status.random_point())
                self.mouse.click()
            else:
                self.log_msg("Run is already on.")
        elif run_status := imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("run_on.png"), self.win.run_orb, 0.323):
            self.mouse.move_to(run_status.random_point())
            self.mouse.click()
        else:
            self.log_msg("Run is already off.")

    def withdraw_from_bank(self, item_pic, single=False, close=True):
        for item in item_pic:
            timer = 0
            while not (item_in_bank := search_img_in_rect(BOT_IMAGES.joinpath("bank", f'{item}.png'), self.win.game_view)):
                timer += 1
                time.sleep(1)
                if timer == 50:
                    return False
            if item_in_bank:
                self.mouse.move_to(item_in_bank.random_point(), mouseSpeed='fastest')
                while not self.mouseover_text(contains=["Withdraw"], color=clr.OFF_WHITE) and not self.mouse.move_to(item_in_bank.random_point(), mouseSpeed='fastest'):
                    timer += 1
                    time.sleep(0.2)
                    if timer == 50:
                        return False
                if single:
                    keyboard.press('shift')
                    self.mouse.click()
                    keyboard.release('shift')
                else:
                    self.mouse.click()
        if close:
            keyboard.press_and_release('esc')
            time.sleep(random.randint(751, 891) / 1000)
        return True

    def start_skilling(self, interface):
        time.sleep(random.randint(780, 850) / 1000)
        timer = 0
        while not (start_skilling := search_img_in_rect(BOT_IMAGES.joinpath("skilling", f'{interface}.png'), self.win.chat)):
            time.sleep(1)
            timer += 1
            if timer == 10:
                return False
        if start_skilling:
            self.mouse.move_to(start_skilling.random_point(), mouseSpeed='fastest')
            self.mouse.click()
        return True

    def finished_processing(self, item_name, tick: float):
        api_m = MorgHTTPSocket()
        timer = 0
        while len(api_m.get_inv_item_indices(item_name)) != 0:
            timer += 1
            time.sleep(tick)
            if timer == 27:
                return False
        if rd.random_chance(probability=0.05) and self.take_breaks:
            self.take_break(max_seconds=10, fancy=True)
        time.sleep(random.randint(251, 302) / 1000)
        return True

    def hop(self):
        pyautogui.press('num9')

    def select_item(self, text, location):
        timer = 0
        while not self.mouseover_text(contains=text, color=[clr.OFF_WHITE, clr.OFF_ORANGE]):
            self.mouse.move_to(location.random_point(), mouseSpeed='fastest')
            time.sleep(1)
            timer += 1
            if timer == 50:
                return False
        return True

    def select_color(self, color, mouse_text, api_m, mouse_speed='fastest'):
        while not (object_found := self.get_nearest_tag(color)):
            time.sleep(0.1)
        if object_found:
            while api_m.get_animation_id() not in [808, 813]:
                continue
            while not self.mouseover_text(contains=mouse_text, color=[clr.OFF_WHITE, clr.OFF_CYAN]):
                if object_found := self.get_nearest_tag(color):
                    self.mouse.move_to(object_found.random_point(), mouseSpeed=mouse_speed)
                time.sleep(0.2)
            if not self.mouse.click(check_red_click=True):
                return self.select_color(color, mouse_text, api_m)


    def sleep(self, min_time, max_time):
        time.sleep(random.randint(min_time, max_time) / 1000)

    def open_bank(self):
        timer = 0
        if bank_npc := self.get_nearest_tagged_NPC():
            self.mouse.move_to(bank_npc.random_point(), mouseSpeed='fastest')
        while not self.mouseover_text(contains=['Bank', 'Use'], color=[clr.OFF_WHITE, clr.OFF_CYAN, clr.OFF_YELLOW]):
            if bank_npc := self.get_nearest_tagged_NPC():
                self.mouse.move_to(bank_npc.random_point(), mouseSpeed='fastest')
            time.sleep(0.2)
            timer += 1
            if timer == 50:
                return None
        self.mouse.click()
        timer = 0
        while not (deposit_all_btn := imsearch.search_img_in_rect(BOT_IMAGES.joinpath("bank", "deposit.png"), self.win.game_view)):
            time.sleep(1)
            timer += 1
            if timer == 50:
                return None
        return deposit_all_btn

    def map_search(self, image):
        timer = 0
        step_image = imsearch.BOT_IMAGES.joinpath("map", f"{image}.png")
        while not (step_found := imsearch.search_img_in_rect(step_image, self.win.minimap_area)):
            timer += 1
            time.sleep(0.2)
            if timer == 30:
                return False
        self.mouse.move_to(step_found.random_point(), mouseSpeed='fast')
        self.mouse.click()
        return True

    def wait_location(self, api_m, position):
        while api_m.get_player_position() != position:
            time.sleep(0.3)
        return


def is_valid_move(curr_x, curr_y, new_x, new_y):
    return (abs(curr_x - new_x) == 1 and abs(curr_y - new_y) == 0) or (abs(curr_x - new_x) == 0 and abs(curr_y - new_y) == 1)


def generate_path(matrix, visited, x, y, target_len):
    if len(visited) == target_len:
        return visited

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    random.shuffle(moves)

    for dx, dy in moves:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < len(matrix) and 0 <= new_y < len(matrix[0]) and is_valid_move(x, y, new_x, new_y) and matrix[new_x][new_y] not in visited:

            visited.append(matrix[new_x][new_y])
            result = generate_path(matrix, visited, new_x, new_y, target_len)
            if result:
                return result
            visited.pop()
    return None


def generate_matrix_path():
    matrix = [[i + j * 4 for i in range(4)] for j in range(7)]
    start_candidates = [2, 4] * 3 + [random.choice([2, 4])]

    for start in start_candidates:
        path = generate_path(matrix, [start], start // 4, start % 4, 28)
        if path:
            return path
    return None
