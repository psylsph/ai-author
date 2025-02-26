from generate_characters import get_character_profiles
from generate_outlines import generate_chapter_outlines
from generate_chapter import generate_chapter, summarize_chapter


def main(num_chapters):
    # Create the story_output directory if it doesn't exist
    import os
    os.makedirs("story_output", exist_ok=True)

    premise = open("ideas/Summer Seduction.md", "r", encoding="UTF-8").read()

    # Generate the story using the characters from the character_profiles module
    character_profiles = get_character_profiles(premise)

    # Generate the chapter outlines using the premise and character profiles
    outlines = generate_chapter_outlines(premise.split("Characters:")[0], character_profiles, num_chapters)

    if not outlines:
        exit("Check the outlines then run again to generate chapters.")
    if len(outlines.keys()) != num_chapters:
        exit("Error: The number of chapters generated does not match the number of chapters requested.")

    summary = "This is the first chapter."
 
    for chapter_number in range(1, len(outlines.keys())+1):
        # Write the chapter with revisions
        chapter_outline = outlines[chapter_number]

        chapter = generate_chapter(outline=chapter_outline, chapter_num=chapter_number,
                                   num_chapters=len(outlines.keys()), character_profiles=character_profiles, max_revisions = 10, genre="Erotic Fiction", target_audience="Adults", previous_chapter_summary=summary)
        
        if (chapter_number == 1):
            summary = "This is the first chapter."
        elif (chapter_number == num_chapters):
            #don't summarize the last chapter
            summary = ""
        else:
            summary = summarize_chapter(chapter, chapter_number, num_chapters)
            print(summary)

        # Create a readable text version
        with open("story_output/final_story.txt", "a", encoding="UTF-8") as f:
            if not chapter.lower().startswith("chapter"):
                f.write(f"\nChapter {chapter_number}\n")
            f.write(chapter)
            f.write("=" * 50 + "\n\n")


if __name__ == "__main__":
    num_chapters = input("Number of Chapters:")
    main(int(num_chapters))