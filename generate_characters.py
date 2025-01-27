import autogen
from dataclasses import asdict, dataclass
from typing import List, Dict
from json_repair import json_repair
from character_manager import CharacterManager, CharacterProfile
import json
import re
import os

from config import get_config, get_user_proxy

llm_config = get_config()

character_profile_dict = {}

def generate_character_profiles(premise):

    character_manager = CharacterManager()

    character_file = "story_output/characters.json"

    # Check if the character file already exists
    if os.path.exists(character_file):
        with open(character_file, "r", encoding="UTF-8") as f:
            characters_data = json.load(f)
            character_manager.from_dict(characters_data)
            print("Characters loaded from existing file.\n")
            return character_manager

    # Use string formatting to safely insert premise
    prompt = f"""Based on the following story premise: '{premise}'
            Create detailed character profiles for each character.
        The response should be a JSON array where each character is an object with these fields:
        - name: string
        - role: string
        - description: string
        - personality: string
        - relationships: object mapping character names to relationship descriptions
        - key_traits: array of strings
        - first_appearance: string (chapter number)
        - story_arc: string

        Example format:
        ```json
        [
            {{
                "name": "John Doe",
                "role": "Protagonist",
                "description": "A tall man with brown hair...",
                "personality": "Brave but reckless...",
                "relationships": {{
                    "Jane Smith": "Love interest",
                    "Bob Johnson": "Best friend"
                }},
                "key_traits": ["courageous", "stubborn", "loyal"],
                "first_appearance": "1",
                "story_arc": "Grows from reckless youth to responsible leader"
            }}
        ]
        ```
        """
    
    character_agent = autogen.AssistantAgent("character_agent",
            system_message="""You are a character consistency manager who:
1. Tracks all characters and their attributes
2. Ensures character names, traits, and behaviors remain consistent
3. Flags any inconsistencies in character portrayal
4. Maintains character relationships and development arcs
5. Provides character information to other agents
Be thorough and specific in maintaining character consistency.""",
            llm_config=llm_config
        )

    chat_manager = autogen.GroupChat(
            agents=[get_user_proxy(), character_agent],
            messages=[],
            max_round=2,
            speaker_selection_method="auto",allow_repeat_speaker=False
        )
    
    manager = autogen.GroupChatManager(groupchat=chat_manager)

    get_user_proxy().initiate_chat(
            manager,
            message=prompt
        )

    for message in reversed(chat_manager.messages):
        if message["name"] == "character_agent":
            response = message["content"]
            break

    # Extract JSON from code blocks
    json_match = re.search(r'```json(.*?)```', response, re.DOTALL)
    if json_match:
        striped_json = json_match.group(1).strip()
    else:
        striped_json = response

    striped_json = striped_json.replace("\n", "")
    striped_json = striped_json.replace("<0x0A>", "") # erm binary new line returned from some models
    striped_json = striped_json.replace("TERMINATE", "")
    try:
        characters = json_repair.loads(striped_json)
        for char_data in characters:
            # Add last_appearance field (will be updated as the story progresses)
            char_data['last_appearance'] = char_data['first_appearance']
            # erm some models can't spell
            if 'descripton' in char_data:
                char_data['description'] = char_data['descripton']

            # Create and add the character
            if char_data['name']:  # Only add if we have at least a name
                try:
                    character = CharacterProfile(**char_data)
                    character_manager.add_character(character)
                    print(f"Added character: {char_data['name']}")
                except Exception as e:
                    print(f"Error creating character {char_data['name']}: {e}")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON character data: {e}")
        print("Response was:", response)
        exit (1) # treat as fatal error

    except Exception as e:
        print(f"Error parsing character data: {e}")
        print("Response was:", response)
        exit (1) # treat as fatal error

    with open(character_file, "w", encoding="UTF-8") as f:
        json.dump(character_manager.to_dict(), f, indent=2, separators=(',', ': '))
        f.flush()
        
    return character_manager