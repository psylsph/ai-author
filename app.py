from generate_characters import generate_character_profiles
from generate_outline import generate_chapter_outlines
from generate_chapter import write_chapter_with_revisions
import json
from datetime import datetime


def main():
    # Create the story_output directory if it doesn't exist
    import os
    os.makedirs("story_output", exist_ok=True)

    premise = open("ideas/foursome.md", "r", encoding="UTF-8").read()

    # Generate the story using the characters  from the generate_characters module
    character_manager = generate_character_profiles(premise)

    # Generate the chapter 
    outlines = generate_chapter_outlines(premise, character_manager.characters, num_chapters)

    story = {
        "metadata": {
            "premise": premise,
            "created_date": datetime.now().isoformat(),
            "num_chapters": num_chapters
        },
        "characters": character_manager.to_dict(),
        "chapters": {}
    }

    for title in outlines:
        # Write the chapter with revisions
        chapter = outlines[title]
        chapter_number = int(chapter["chapter_number"])
        chapter_versions = write_chapter_with_revisions(outline=chapter, chapter_num=chapter_number, num_chapters=num_chapters, character_manager=character_manager)

        # Store chapter and its metadata
        story[f"Chapter_{chapter_number}"] = {
            "outline": chapter,
            "versions": chapter_versions,
            # Use the last revision as the final version
            "final_version": chapter_versions[f"revision_{len(chapter_versions)}"]["content"]
        }

        # Update character tracking data
        story["characters"] = character_manager.to_dict()

        # Save progress after each chapter
        with open(f"story_output/story_progress.json", "w", encoding="UTF-8") as f:
            json.dump(story, f, indent=2, separators=(',', ': '))
            f.flush()

    with open("story_output/final_story.json", "w", encoding="UTF-8") as f:
        json.dump(story, f, indent=2, separators=(',', ': '))

    # Create a readable text version
    with open("story_output/final_story.txt", "w", encoding="UTF-8") as f:
        # Write premise and character information
        f.write("story Premise:\n")
        f.write("=" * 50 + "\n")
        f.write(story["metadata"]["premise"] + "\n\n")

        f.write("Characters:\n")
        f.write("=" * 50 + "\n")
        for char in story["characters"]["characters"].values():
            f.write(f"\n{char['name']}:\n")
            f.write(f"Role: {char['role']}\n")
            f.write(f"Description: {char['description']}\n")
            f.write(f"Key Traits: {', '.join(char['key_traits'])}\n")
            f.write("\n")
        for chapter_num in range(1, num_chapters + 1):
            chapter_key = f"Chapter_{chapter_num}"
            if "Chapter" not in story[chapter_key]["final_version"]:
                f.write(f"\nChapter {chapter_num}\n")
            f.write("=" * 50 + "\n\n")
            f.write(story[chapter_key]["final_version"])
            f.write("\n\n")
    
if __name__ == "__main__":
    num_chapters = 10
    main()