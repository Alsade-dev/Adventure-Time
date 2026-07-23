"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This module allows simulating a playthrough of AdventureGame using a list
of predetermined commands.

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
from event_logger import Event, EventList
from adventure import AdventureGame, ITEM_INTERACTIONS, handle_command, MENU
from game_entities import Location


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """
        Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from the location at initial_location_id
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        initial_location = self._game.get_location()
        first_event = Event(id_num=initial_location.id_num, description=initial_location.long_description)
        self._events.add_event(first_event)

        # Generate the remaining events based on the commands and initial location
        self.generate_events(commands, initial_location)

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """
        Generate events in this simulation, based on current_location and commands, a valid list of commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from current_location
        """
        for command in commands:
            # Movement commands
            if command.startswith("go") and command in current_location.available_commands:
                next_loc_id = current_location.available_commands[command]
                self._game.player.current_location_id = next_loc_id
                next_loc = self._game.get_location(next_loc_id)
                new_event = Event(
                    id_num=next_loc_id,
                    description=next_loc.long_description
                )
                self._events.add_event(new_event, command)
                current_location = next_loc

            # Item interactions or menu commands
            elif command in MENU or any(command.startswith(x) for x in ITEM_INTERACTIONS):
                # Execute the command on the game state so the simulation is accurate
                handle_command(self._events, self._game, command, current_location, is_unlocked=True)

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.

        >>> sim = AdventureGameSimulation('sample_locations.json', 1, ["go east"])
        >>> sim.get_id_log()
        [1, 2]

        >>> sim = AdventureGameSimulation('sample_locations.json', 1, ["go east", "go east", "buy coffee"])
        >>> sim.get_id_log()
        [1, 2, 3, 3]
        """

        return self._events.get_id_log()

    def get_inventory(self) -> list[str]:
        """
        Return the current inventory of the player in the simulation.

        >>> sim = AdventureGameSimulation('game_data.json', 1, ["pick up toonie", "pick up pencil"])
        >>> sim.get_inventory()
        ['toonie', 'pencil']
        """
        return self._game.player.inventory

    def run(self) -> None:
        """
        Run the game simulation and print location descriptions.
        """

        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":
    # ---------------- WIN WALKTHROUGH ---------------- #
    win_walkthrough = [
        "pick up toonie",
        "pick up pencil",
        "go east",
        "pick up usb drive",
        "go west",
        "go south",
        "pick up jam",
        "go south",
        "go west",
        # enter robarts for riddle
        "pick up key fob",
        "go east",
        "go south",
        "use jam",
        "pick up lucky mug",
        "go north",
        "go east",
        "go east",
        "use pencil",
        "pick up laptop charger",
        "go east",
        "go south"
        "use key fob"
    ]

    expected_log_win = [
        1, 1, 1, 2, 2, 1, 3, 3, 4, 5, 5, 4, 6, 6, 6, 4, 7, 9, 9, 9, 10
    ]

    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    assert expected_log_win == sim.get_id_log()

    # ---------------- LOSE DEMO ---------------- #
    lose_demo = ["go south", "go north"] * 17 + ["go south"]
    expected_log_lose = [1, 3] * 18

    sim = AdventureGameSimulation('game_data.json', 1, lose_demo)
    assert expected_log_lose == sim.get_id_log()

    # ---------------- INVENTORY DEMO ---------------- #
    inventory_demo = [
        "pick up toonie",
        "pick up pencil",
        "inventory",
        "go east",
        "pick up USB drive",
        "inventory"
    ]
    expected_log_inventory = [1, 1, 1, 1, 2, 2, 2]

    sim = AdventureGameSimulation('game_data.json', 1, inventory_demo)
    assert expected_log_inventory == sim.get_id_log()

    # ---------------- SCORES DEMO ---------------- #
    scores_demo = [
        "pick up toonie",
        "go south",
        "score"
    ]
    expected_log_scores = [1, 1, 3, 3]

    sim = AdventureGameSimulation('game_data.json', 1, scores_demo)
    assert expected_log_scores == sim.get_id_log()

    # ---------------- ENHANCEMENT DEMO ---------------- #
    enhancement_demo = [
        "pick up toonie",
        "go south",
        "go south",
        "go west",
        "pick up key fob"
    ]
    expected_log_enhancement = [1, 1, 3, 4, 5, 5]

    sim = AdventureGameSimulation('game_data.json', 1, enhancement_demo)
    assert expected_log_enhancement == sim.get_id_log()


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })
