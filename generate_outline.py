import autogen
from dataclasses import asdict, dataclass
from typing import List, Dict
from json_repair import json_repair
import json
import re
import os

from config import get_config, get_user_proxy

llm_config = get_config()

@dataclass
class Chapter:
    chapter_number: int
    title: str
    key_events: List[str]
    description: str
    character_development: Dict[str, str]
    setting: str
    tone: str
    conflicts: List[str]

chapter_outlines = {}

def generate_chapter_outlines(premise, characters, num_chapters):

    outlines_file = "story_output/chapter_outlines.json"

    # Check if the chapter_outlines file already exists
    if os.path.exists(outlines_file):
        with open(outlines_file, "r", encoding="UTF-8") as f:
            outlines_data = json.load(f)
            print("Outlines loaded from existing file.\n")
            return outlines_data

    # Use string formatting to safely insert premise
    prompt = f"""Based on the following story premise: {premise} and {characters}
        Create detailed chapter outlines each of {num_chapters} chapters.
        Each chapter should have the following fields,
        and the response should be a JSON array where each chapter is an object with these fields:
        - chapter_number: int (1-indexed)
        - title: string (a brief, engaging title)
        - key_events: array of strings (brief descriptions of key events)
        - description: string (a brief summary of the chapter)
        - character_development: object mapping character names to their development in this chapter (e.g., "John Doe": "Grows from reckless youth to responsible leader")
        - setting: string (description of the setting)
        - tone: string (description of the tone)
        - conflicts: array of strings (brief descriptions of conflicts)

                Example format:
        ```json
        [
            {{
                "chapter_number": 1,
                "title": "It's 1984",
                "key_events": ["Boarding the Train", "Meeting the Monster"],
                "description": "They go to Scotland to  find the monster.",
                "character_development": {{
                    "Stuart Little": "Spots the Monster",
                    "The Monster": "Gets to know Stuart"
                }},
                "setting": "Scotland",
                "tone": "Adventure",
                "conflicts": "The Monster is hiding from the world"
            }}
        ]
        ```
        """
    
    outline_writer = autogen.AssistantAgent("outline_writer",
            system_message="""You are a chapter outline writer who:
Creates detailed chapter outlines based on the story premise and plot structure.
Ensures each chapter advances the plot and develops characters.
Include:
1. A unique and descriptive chapter title
2. Key plot points
3. Character appearances and interactions
4. Setting descriptions
5. Major events or revelations
6. Ensure each chapter is self-contained and does not repeat anything from the previous chapter.
Ensure all character appearances and actions align with their established profiles.
Be thorough and specific in your outlines.""",
            llm_config=llm_config
        )

    chat_manager = autogen.GroupChat(
            agents=[get_user_proxy(), outline_writer],
            messages=[],
            max_round=2,
            speaker_selection_method="auto",allow_repeat_speaker=False
        )
    
    manager = autogen.GroupChatManager(groupchat=chat_manager)

    get_user_proxy().initiate_chat(
            manager,
            message=prompt
        )

    # Extract the response from the story_outline_writer

    for message in reversed(chat_manager.messages):
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
        chapters = json_repair.loads(striped_json)
        for chapter_data in chapters:
            print(f"Chapter {chapter_data['chapter_number']}: {chapter_data['title']}")            # Create and add the character
            if chapter_data['title']:  # Only add if we have at least a name
                try:
                    chapter = Chapter(**chapter_data)
                    chapter_outlines[chapter_data['title']] = chapter
                    print(f"Added Chapter: {chapter_data['title']}")
                except Exception as e:
                    print(f"Error creating Chapter {chapter_data['title']}: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON Chapter data: {e}")
        print("Response was:", response)
        exit (1) # treat as fatal error

    except Exception as e:
        print(f"Error parsing Chapter data: {e}")
        print("Response was:", response)
        exit (1) # treat as fatal error

    with open(outlines_file, "w", encoding="UTF-8") as f:

        chapter_outlines_dict = {name: asdict(char) for name, char in chapter_outlines.items()}
        json.dump(chapter_outlines_dict, f, indent=2, separators=(',', ': '))
        f.flush()
        
    return chapter_outlines