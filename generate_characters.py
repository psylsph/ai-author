from config import get_llm_response
import os

character_file = "story_output/characters.txt"

def get_character_profiles(premise):

    # Check if the character file already exists
    if os.path.exists(character_file):
        with open(character_file, "r", encoding="UTF-8") as f:
            return f.read()

    # Use string formatting to safely insert premise
    system_prompt = f"""Based on the following story premise: '{premise}'
Create detailed character profiles for each character.
The response should contain the following information for each character:
- name: string
- description: string
- personality: string
- relationships: object mapping character names to relationship descriptions
- story_arc: string

Ensure that the characters are well-rounded and their roles are clearly defined.
Provide the charter profiles for all characters in the story.
"""
    
    user_prompt="""You are a character consistency manager who:
1. Tracks all characters and their attributes
2. Ensures character names, traits, and behaviors remain consistent
3. Flags any inconsistencies in character portrayal
4. Maintains character relationships and development arcs
5. Provides character information to other agents
6. Your only job is to describe the characters and their attributes
7. Do not write any story
8. Do not write any dialogue or narrative text
9. Do not write any descriptions of scenes or events
"""
    print("Generating character profiles...")  
    character_profiles = get_llm_response(system_prompt, user_prompt)

    with open (character_file, "w", encoding="UTF-8") as f:
        f.write(str(character_profiles))

    return character_profiles