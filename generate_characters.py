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
    print("Generating initial character profiles...")
    character_profiles = get_llm_response(system_prompt, user_prompt, temperature=1.0, review=False)
    
    # Validation loop
    max_attempts = 3
    validation_system = """Analyze character profiles for:
1. All required fields present per character
2. Consistent traits/behaviors
3. Logical relationship mappings
4. Story arc alignment with premise

Respond ONLY with:
[APPROVED] if fully compliant
[REVISE] [specific issues] if needing changes"""
    
    attempt = 0
    stop = False
    
    for attempt in range(max_attempts):
        validation_result = get_llm_response(
            validation_system,
            f"Validate these profiles:\n{character_profiles}",
            0.6,
            review=True
        )
        
        if validation_result.find("[APPROVED]") >= 0:
            stop = True
            
        if (not stop):
            print(f"Revision {attempt + 1}/{max_attempts} needed")
            revision_notes = validation_result.replace("[REVISE]", "").strip()
            character_profiles = get_llm_response(
                f"{system_prompt}\nRevision Notes:\n{revision_notes}",
                user_prompt,
                temperature=0.6,
                review=False
            )
    
    # Save final version
    os.makedirs("character_revisions", exist_ok=True)
    with open(f"character_revisions/{attempt + 1}.txt", "w") as f:
        f.write(f"Final version after {attempt + 1} attempts\n{character_profiles}")
        
    with open(character_file, "w", encoding="UTF-8") as f:
        f.write(str(character_profiles))

    return character_profiles