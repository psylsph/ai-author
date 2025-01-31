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
    description: List[str]
    character_development: Dict[str, str]
    setting: str
    tone: str
    conflicts: List[str]

chapter_outlines = {}

def generate_chapter_outlines(premise, characters, num_chapters):

    # Check if the chapter_outlines file already exists
    outline_data = read_chapter_outlines_from_files()
    if outline_data:
        return outline_data

    # Use string formatting to safely insert premise
    prompt = f"""Based on the following story premise: {premise} and {characters}
        Create detailed chapter outlines each of {num_chapters} chapters.
        Each chapter should have the following fields,
        and the response should be a JSON array where each chapter is an object with these fields:
        - chapter_number: int (1-indexed)
        - title: string (a brief, engaging title)
        - key_events: array of strings (brief descriptions of key events)
        - description: array of strings (a long summary of the chapter)
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
                "description": ["They go to Scotland to find the monster."],
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
Take the description of the story and the number of chapters and generate a detailed outline for each chapter.
Ensures each chapter advances the plot and develops characters.
Include:
1. A unique and descriptive chapter title
2. Key plot points
3. Character appearances and interactions
4. Setting descriptions
5. Major events or revelations
6. All your responses should provide your output in a JSON format for ALL chapters.""",
            llm_config=llm_config
        )

    outline_reviewer = autogen.AssistantAgent("outline_reviewer",
            system_message="""You are a skilled book outline reviewer who:
1. Reviews chapter outlines for clarity, flow, and provides constructive feedback
2. Ensures plot consistency and character development
3. Suggests improvements for pacing and tension
4. Please be constructive and specific in your feedback.
5. Ensure all character appearances and actions align with their established profiles.
6. Provide your feedback in a JSON format.""",
            llm_config=llm_config )

    chat_manager = autogen.GroupChat(
            agents=[get_user_proxy(), outline_writer, outline_reviewer],
            messages=[],
            max_round=3,
            speaker_selection_method="auto",allow_repeat_speaker=True
        )

    manager = autogen.GroupChatManager(groupchat=chat_manager)

    get_user_proxy().initiate_chat(
            manager,
            message=prompt,
            max_turns=2
        )

    response = ""

    # Extract the response from the outline_writer
    for message in chat_manager.messages:
        if "outline_writer" in message["name"]:
            response += message["content"]
    
    with open("chapter_outline.txt", "w") as f:
        f.write(response)
        f.flush()
        exit(1)

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
                    chapter_outlines[chapter_data['chapter_number']] = chapter
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


    # Save individual chapters to separate text files
    for chapter_number, chapter in chapter_outlines.items():
        chapter_file = f"story_output/chapter_outline_{chapter_number}.txt"
        with open(chapter_file, "w", encoding="UTF-8") as f:
            f.write(f"Chapter {chapter_number}:\n{chapter.title}\n")
            f.write("Key Events:\n")
            for event in chapter.key_events:
                f.write(f"{event}\n")
            f.write("Description:\n")
            for line in chapter.description:
                f.write(f"{line}\n")
            f.write("Character Development:\n")
            for character, development in chapter.character_development.items():
                f.write(f"{character}: {development}\n")
            f.write(f"Setting:\n{chapter.setting}\n")
            f.write(f"Tone:\n{chapter.tone}\n")
            f.write("Conflicts:\n")
            for conflict in chapter.conflicts:
                f.write(f"{conflict}\n")

    print ("Outlines Generated and Saved, now run again to generate the story")
    exit(0)

def read_chapter_outlines_from_files():
    chapter_outlines = {}
    for filename in os.listdir("story_output"):
        if filename.startswith("chapter_outline_") and filename.endswith(".txt"):
            with open(os.path.join("story_output", filename), "r", encoding="UTF-8") as f:
                content = f.read()
                chapter_data = {}
                lines = content.split("\n")
                chapter_data["chapter_number"] = int(lines[0].split(":")[0].split(" ")[1])
                chapter_data["title"] = lines[1].strip()
                key_events_start = lines.index("Key Events:")+1
                key_events_end = lines.index("Description:")
                chapter_data["key_events"] = [line.strip() for line in lines[key_events_start:key_events_end]]
                description_start = key_events_end + 1
                description_end = lines.index("Character Development:")
                chapter_data["description"] = [line.strip() for line in lines[description_start:description_end]]

                character_development = {}
                characters_start = lines.index("Character Development:")+1
                characters_end: int = lines.index("Setting:")
                for line in lines[characters_start:characters_end]:
                    char, dev = line.strip("- ").split(": ")
                    character_development[char] = dev
                chapter_data["character_development"] = character_development
                chapter_data["setting"] = lines[lines.index("Setting:")+1].strip()
                chapter_data["tone"] = lines[lines.index("Tone:")+1].strip()
                chapter_data["conflicts"] = [line.strip("- ").strip() for line in lines[lines.index("Conflicts:")+1:]]
                chapter_outlines[chapter_data["chapter_number"]] = chapter_data
    return chapter_outlines
