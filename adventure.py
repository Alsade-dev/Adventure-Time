"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
import json
from typing import Optional

from game_entities import Location, Item, Player
from event_logger import Event, EventList

MENU = ["look", "inventory", "score", "log", "quit"]  # Regular MENU options available at each location
ITEM_INTERACTIONS = ["pick up", "drop", "use"]  # Actions available for interacting with objects
MAX_MOVES = 35  # Max number of moves avaible in a game
INVENTORY_LIMIT = 5  # Max number of items allowed in inventory
PUZZLE_LOCATIONS = [4, 5, 6, 8, 9, 10]  # Game locations where a puzzle unfolds
DORM_ITEMS = ["laptop charger", "usb drive", "lucky mug"]  # Items that must be returned to dorm


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - player: an instance of the Player class which stores data for the current player
        - initial_location_id: the ID of the starting location for the game
        - ongoing: a boolean value that indicates whether the game is still running (player can still make moves)

    Representation Invariants:
        - len(self._locations) > 0
        - len(self._items) > 0
        - self.player.current_location_id in self._locations
        - self.current_location_id in self._locations
    """

    # Private Instance Attributes:
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    player: Player
    ongoing: bool

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        self._locations, self._items = self._load_game_data(game_data_file)

        self.player = Player(current_location_id=initial_location_id, inventory=[], score=0, moves=0)
        self.ongoing = True  # whether the game is ongoing

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        and (2) a list of all Item objects."""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []

        for item_data in data['items']:
            new_item = Item(item_data['name'], item_data['description'], item_data['start_position'],
                            item_data['target_position'], item_data['target_points'])
            items.append(new_item)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """
        Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """
        if loc_id is None:
            return self._locations[self.player.current_location_id]
        else:
            return self._locations[loc_id]

    def get_item_points(self, item_name: str) -> int:
        """Return the number of points assoicated with using an item in its target location"""
        for item in self._items:
            if item.name == item_name:
                return item.target_points
        return 0

# ---------------- Helper Functions ---------------- #


def extract_item_name(command: str) -> str:
    """
    This function extracts and returns the name of an item from a given item interaction command.

    Preconditions:
    - choice.startswith("pick up") or choice.startswith("drop") or choice.startswith("use")

    """
    if command.startswith("pick up"):
        item_name = command[len("pick up "):].strip()  # This line is an excerpt from ChatGPT
    elif command.startswith("drop"):
        item_name = command[len("drop "):].strip()
    else:
        # choice.startswith("use"):
        item_name = command[len("use "):].strip()
    return item_name


def use_item(current_game: AdventureGame, command: str) -> bool:
    """
    Use an item in inventory.

    Checks that the item is in inventory. If the item is in inventory, it is removed and True is returned.
    Otherwise, False is returned
    """
    item_to_use = extract_item_name(command)
    if current_game.player.has_item(item_to_use):
        current_game.player.inventory.remove(item_to_use)
        return True
    return False


def validate_command(current_location: Location, menu: list[str], item_interactions: list[str]) -> str | None:
    """
    Prompts the user to enter a valid command.
    """
    while True:
        command = input("Enter action: ").lower().strip()
        if command in current_location.available_commands or command in menu or \
                any(command.startswith(x) for x in item_interactions) or command == "exit":
            return command
        else:
            print("That was an invalid option; try again.")
    return None


def call_quit(current_game: AdventureGame) -> None:
    """
    Quits this game
    """
    current_game.ongoing = False


def print_location_description(current_location: Location) -> None:
    """
    Prints a long or short description of a location, depending on if it was visited before
    """
    if current_location.visited:
        print(current_location.brief_description)
    else:
        print(current_location.long_description)
        current_location.visited = True


def handle_menu_command(current_game: AdventureGame, current_game_log: EventList, command: str,
                        current_location: Location) -> None:
    """
    Performs an action for a MENU command that is called
    """

    if command == 'look':
        print(current_location.long_description)
    elif command == 'inventory':
        print(current_game.player.inventory)
    elif command == 'score':
        print(current_game.player.score)
    elif command == 'log':
        if current_game_log.is_empty():
            print("Nothing yet")
        else:
            current_game_log.display_events()
    else:
        current_game.ongoing = False


def handle_movement(current_game: AdventureGame, command: str, current_location: Location) -> None:
    """
    Performs an action for a 'go' command
    """
    new_loc_id = current_location.available_commands.get(command)
    if new_loc_id is not None:
        current_game.player.current_location_id = new_loc_id
        current_location.visited = True
        print("You moved\n")
    else:
        print("You can't go that way.")


def handle_item_command(current_game: AdventureGame, command: str, current_location: Location, is_unlocked: bool)\
        -> None:
    """
    Performs an action for a desired iem interaction
    """
    item_name = extract_item_name(command)

    if command.startswith("pick up"):
        if len(current_game.player.inventory) >= INVENTORY_LIMIT:
            print(f"Inventory full. You already have {INVENTORY_LIMIT} items")
        elif item_name in current_location.items and (is_unlocked or current_location.id_num not in PUZZLE_LOCATIONS):
            current_game.player.pick_up(item_name)
            current_location.items.remove(item_name)
            print(f"{item_name} was added to inventory")

    elif command.startswith("drop"):
        if item_name in current_game.player.inventory:
            current_game.player.drop_item(item_name)
            current_location.items.append(item_name)
            print(f"{item_name} was successfully dropped and is now in its original location")

    elif command.startswith("use") and use_item(current_game, command):

        current_game.player.score += current_game.get_item_points(item_name)

        print(f"You used {item_name} and earned {current_game.get_item_points(item_name)} points")


def handle_command(current_game_log: EventList, current_game: AdventureGame, command: str, current_location: Location,
                   is_unlocked: bool) -> None:
    """
    Dispatch command to the appropriate handler and log event.
    Commands are dispatched based on wehter they are from menu, item iteractions, or movement commands
    """
    if command in MENU:
        handle_menu_command(current_game, current_game_log, command, current_location)
    elif command.startswith("go"):
        handle_movement(current_game, command, current_location)
    else:
        handle_item_command(current_game, command, current_location, is_unlocked)

    # Log event
    event = Event(id_num=current_location.id_num, description=current_location.long_description)
    current_game_log.add_event(event, command)


def give_mug(current_game: AdventureGame, item: str) -> bool:
    """Helper for interact_6: handle item offer for the lucky mug."""
    if use_item(current_game, f"use {item}"):
        if item == "jam":
            print("I accept your jam! Take your mug.")
        else:
            print("I prefer jam, but oh well. Take your mug.")
        current_game.player.score += current_game.get_item_points(item)
        current_game.player.pick_up("lucky mug")
        return True
    else:
        print("You don't have that item.")
        return False

# ---------------- Interaction Functions ---------------- #


def interact_4(current_game: AdventureGame) -> bool:
    """
    Location 4 interaction: give the beggar the toonie if in inventory.
    """
    if "toonie" in current_game.player.inventory and use_item(current_game, "use toonie"):
        current_game.player.score += current_game.get_item_points("toonie")
        print("\nYou returned the toonie! Points earned.")
        print("The beggar hints that something important lies in the West")
        return True
    return False


def interact_5(current_game_log: EventList, current_game: AdventureGame) -> bool:
    """
    Location 5 interaction: solve riddle for key fob.
    """
    print("Who goes there?! You must answer my riddle to access this box.")
    print("What library on campus is open 24/7? One word.")
    print("Type 'exit' to leave or 'quit' to end the game.")

    while True:
        response = input("\nEnter response: ").lower().strip()
        if response == "robarts":
            print("You got it! Your key fob is inside. Be more responsible next time.")
            return True
        elif response == "exit":
            print("You left the interaction.")
            current_game_log.add_event(Event(5, "Exited the riddle interaction."), response)
            return False
        elif response == "quit":
            call_quit(current_game)
            return False
        else:
            print("Incorrect. Try again.")
    return False


def interact_6(current_game: AdventureGame) -> bool:
    """Location 6 interaction: trade items with Sarah for the lucky mug."""
    print("So what's it gonna be? I'm craving a sweet treat.")
    print("Offer something using 'use <item>' or type 'exit'.")

    while True:
        command = validate_command(current_game.get_location(), MENU, ITEM_INTERACTIONS)
        if command == "exit":
            return False
        if not command.startswith("use "):
            print("You must offer something using 'use <item>'.")
            continue

        item = extract_item_name(command)
        if item in ["jam", "box of cookies"]:
            if give_mug(current_game, item):
                return True
        else:
            print("No thank you.")

    return False


def interact_8(current_game: AdventureGame) -> bool:
    """
    Location 8 interaction: join the line at Sidney Smith Commons.
    """
    print("Do you want to join the line? Enter 'yes' or 'no'.")

    while True:
        response = input("\nEnter response (yes/no): ").lower().strip()
        if response == "yes":
            print("You were in line for an hour! Nothing notable happened but you lost a lot of time")
            current_game.player.moves += 5
            print("You can still take your cookies.")
            return True
        elif response == "no":
            print("You chose not to join the line.")
            return False
        else:
            print("Invalid input. Enter 'yes' or 'no'.")
    return False


def interact_9(current_game: AdventureGame) -> bool:
    """
    Location 9 interaction: offer item to receptionist.
    """
    print("Offer the receptionist an item with 'use <item>' or type 'exit'.")

    while True:
        command = validate_command(current_game.get_location(), MENU, ITEM_INTERACTIONS)
        if command == "exit":
            print("You got your charger eventually, but lost some time.")
            return True
        if not command.startswith("use "):
            print("You must use 'use <item>'.")
            continue

        item = extract_item_name(command)
        if item == "pencil":
            if use_item(current_game, command):
                print("Receptionist hands you your charger. You saved time!")
                current_game.player.score += current_game.get_item_points(item)
                return True
            else:
                print("You don't have that item.")
        else:
            print("Receptionist rejects your item.")
    return False


def interact_11(current_game: AdventureGame) -> bool:
    """
    Location 11 interaction: unlock dorm door with key fob.
    """
    print("Use your key fob or type 'exit'.")

    while True:
        command = validate_command(current_game.get_location(), MENU, ITEM_INTERACTIONS)
        if command == "exit":
            return False
        if not command.startswith("use "):
            print("Must use 'use <item>'.")
            continue

        item = extract_item_name(command)
        if item == "key fob":
            if use_item(current_game, command):
                print("You unlocked the door!")
                current_game.player.score += current_game.get_item_points(item)
                return True
            else:
                print("You don't have that item.")
        else:
            print("That item doesn't work here.")
    return False


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    choice = None

    INTERACTIONS = {
        4: interact_4,
        5: lambda g: interact_5(game_log, g),  # lambda wraps interact_5 since it takes 2 args. ChatGPT suggestion
        6: interact_6,
        8: interact_8,
        9: interact_9,
        11: interact_11
    }

    print("\n" + "=" * 60)
    print("🎓  WELCOME TO CAMPUS QUEST: THE 1PM DEADLINE  🎓")
    print("=" * 60)
    print("\nYou've spent all day finishing your first-year CS project.")
    print("After a short nap, you wake up in a panic —")
    print("your USB drive, laptop charger, and lucky U of T mug are missing!\n")
    print("Find them and return to your dorm before 1PM.\n")

    print("RULES:")
    print("  1. Maximum 5 items in inventory.")
    print("  2. Maximum 35 moves.")
    print("  3. Every action counts as a move.")
    print("  4. Using items correctly earns points.\n")

    print("Let the adventure begin!\n")

    starting_location = game.get_location()
    print(starting_location.long_description)

    while game.ongoing:

        location = game.get_location()
        previous_location_id = game.player.current_location_id

        # show moves made out of max moves
        print(f"{game.player.moves}/{MAX_MOVES} moves made")

        # Display possible actions
        print("\nActions available:", MENU)
        print("Item interactions: [pick up <item>, drop <item>, use <item>]")
        print("Available location commands:")
        for action in location.available_commands:
            print("-", action)

        # ---------------- Handle interactions ---------------- #
        unlocked = False
        if location.id_num in INTERACTIONS and not location.unlocked:
            unlocked = INTERACTIONS[location.id_num](game)
            location.unlocked = unlocked

        # ---------------- Check winning condition ---------------- #
        dorm = game.get_location()

        if (
                dorm.id_num == 11 and dorm.unlocked is True
                and all(item in game.player.inventory for item in DORM_ITEMS)
        ):
            print("\nCongratulations! You have returned all items to your dorm before the deadline. You win!")
            print(f"you score is {game.player.score}")
            game.ongoing = False
            break

        # ---------------- User command ---------------- #
        choice = validate_command(location, MENU, ITEM_INTERACTIONS)
        handle_command(game_log, game, choice, location, unlocked)
        game.player.moves += 1

        new_location = game.get_location(game.player.current_location_id)

        if new_location.id_num != previous_location_id:
            print_location_description(new_location)

        # ---------------- Check losing condition ---------------- #
        if game.player.moves >= MAX_MOVES:
            print("\nYou have run out of allowed moves! It is now 1pm. Game over.")
            game.ongoing = False
            break
