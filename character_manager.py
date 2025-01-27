from dataclasses import asdict, dataclass
from typing import List, Dict


@dataclass
class CharacterProfile:
    name: str
    role: str
    description: str
    personality: str
    relationships: Dict[str, str]
    key_traits: List[str]
    first_appearance: str  # Chapter number
    last_appearance: str   # Chapter number
    story_arc: str

class CharacterManager:
    def __init__(self):
        self.characters = {}
        self.mentions = {}  # Track character mentions by chapter

    def add_character(self, character: CharacterProfile):
        try:
            int(character.first_appearance)
        except ValueError:
            character.first_appearance = 0
            character.last_appearance = 0
        self.characters[character.name.lower()] = character

    def get_character(self, name: str) -> CharacterProfile:
        return self.characters.get(name.lower())

    def update_appearance(self, name: str, chapter: str):
        char = self.get_character(name.lower())
        if char:
            if not char.first_appearance:
                char.first_appearance = chapter
            char.last_appearance = chapter

    def track_mention(self, chapter: str, name: str):
        if chapter not in self.mentions:
            self.mentions[chapter] = {}
        name_lower = name.lower()
        self.mentions[chapter][name_lower] = self.mentions[chapter].get(name_lower, 0) + 1

    def to_dict(self):
        return {
            "characters": {name: asdict(char) for name, char in self.characters.items()},
            "mentions": self.mentions
        }

    def from_dict(self, data: Dict):
        self.characters = {
            name: CharacterProfile(**char_data)
            for name, char_data in data["characters"].items()
        }
        self.mentions = data["mentions"]
