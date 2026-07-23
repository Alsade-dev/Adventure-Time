"""CSC111 Project 1: Text Adventure Game - Game Entities

Instructions (READ THIS FIRST!)
===============================

This Python module contains the entity classes for Project 1, to be imported and used by
 the `adventure` module.
 Please consult the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from dataclasses import dataclass


@dataclass
class Player:
    """ A player of our text adventure game world.

    Instance Attributes:
    - self.current_location_id: the ID of the location the player is currently at
    - self.inventory: a list of items currently in the player's inventory
    - self.score: an integer value representing the player's current score (points collected)
    - self.moves: the number of moves the player makes

    Representation Invariants:
    - self.current_location_id > 0
    - 0 <= len(self.inventory) <= 5
    - self.score >= 0
    - self.moves >= 0

    """
    current_location_id: int
    inventory: list[str]
    score: int
    moves: int

    def pick_up(self, item_name: str) -> bool:
        """Add an item to the player's inventory if it is not yet in inventory, and inventory has < 4 items.\
        Return true if successful and False otherwise.

        Preconditions:
        - item_name != ''
        - item_name is present at the player's location
        """

        if item_name not in self.inventory and len(self.inventory) < 4:
            self.inventory.append(item_name)
            return True
        return False

    def drop_item(self, item_name: str) -> bool:
        """Remove an item from the player's inventory. Return True if successful and False otherwise.

        Preconditions:
        - item_name != ''
        """
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            return True
        return False

    def has_item(self, item_name: str) -> bool:
        """Return True if the player has a specified item in inventory. Return False otherwise.

        Preconditions:
        - item_name != ''
        """
        return item_name in self.inventory


@dataclass
class Location:
    """A location in our text adventure game world.

    Instance Attributes:
        - id_num: integer id for this location
        - brief_description: short description of this location
        - long_description: long description of this location
        - available_commands: a mapping of available commands at this location to the location executing that
                                command would lead
        - items: a list of items at the current location
        - visited: a boolean value representing if the player has visited this location
        - unlocked: tracks whether the puzzle/interaction at this location has been completed.

    Representation Invariants:
        - self.id_num >= 0
        - self.brief_description != ''
        - self.long_description != ''
    """

    id_num: int
    brief_description: str
    long_description: str
    available_commands: dict[str, int]
    items: list[str]
    visited: bool = False
    unlocked: bool = False


@dataclass
class Item:
    """An item in our text adventure game world.

    Instance Attributes:
        - name: the name of this item
        - description : a description of this item
        - start_position: an integer representing the location where the item was found
        - target_position: an integer representing the location where the item must be deposited to score points
        - target_points: number of points gained for depositing the item in the correct location

    Representation Invariants:
        - name != ''
        - description != ''
        - start_position >= 0
        - target position >= 0
        - target_points >= 0
    """

    name: str
    description: str
    start_position: int
    target_position: int
    target_points: int


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })
