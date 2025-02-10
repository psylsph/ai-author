from config import get_llm_response
import os
import re

chapter_outlines_file = "story_output/chapter_outlines.txt"
max_revisions = 3

def generate_chapter_outlines(premise, characters, num_chapters):

    # Check if the chapter_outlines file already exists
    if os.path.exists(chapter_outlines_file):
        return parse_chapter_outlines_from_file(num_chapters)
    
    current_feedback = ""

    outline_writer_system_prompt = f"""Based on the following story premise: {premise} and characters: {characters}
Create detailed chapter outlines each of {num_chapters} chapters.
Each chapter outline should include the following:
- chapter_number: int (1-indexed)
- title: a brief, engaging title for the chapter
- key_events: a list of brief descriptions of key events
- description: a long summary of the chapter
- character_development: a description of the character development in the chapter
- setting: description of the chapters setting
- tone: description of the tone of the chapter
- conflicts: a brief descriptions of conflicts in the chapter
- resolutions: a brief description of resolutions in the chapter"""
    
    outline_reviewer_system_prompt = f"""You are a skilled book outline reviewer who:
1. Reviews chapter outlines for clarity, flow, and provides constructive feedback
2. Ensures plot consistency and character development
3. Suggests improvements for pacing and tension
4. Please be constructive and specific in your feedback.
5. Ensure all character appearances and actions align with their established profiles.
6. Provide specific, actionable feedback, limiting your response to 300 words."""

    for revision in range(1, max_revisions+1): # plus 1 to include the final revision

        outline_writer_user_prompt = """You are a chapter outline writer who:
    Creates detailed chapter outlines based on the story premise and characters.
    Take the description of the story and the number of chapters and generate a detailed outline for each chapter.
    Ensures each chapter advances the plot and develops characters."""
        
        if current_feedback:
            outline_writer_user_prompt += f"\n\nHere is the feedback from the previous revision: {current_feedback}"

        print(f"""Generating chapter outlines (revision {revision} of {max_revisions})...""")       
        chapter_outlines = get_llm_response(outline_writer_system_prompt, outline_writer_user_prompt)

        if "</think>" in chapter_outlines:
            chapter_outlines = chapter_outlines.split("</think>")[1]

        if revision == max_revisions:
            with open (chapter_outlines_file, "w", encoding="UTF-8") as f:
                f.write(chapter_outlines)
            return parse_chapter_outlines_from_file(num_chapters)
       
        outline_reviewer_user_prompt = f"""Review the following chapter outlines and provide feedback on how to improve them: {chapter_outlines}"""
        
        print("Reviewing chapter outlines...")       
        current_feedback = get_llm_response(outline_reviewer_system_prompt, outline_reviewer_user_prompt)

        if "</think>" in current_feedback:
            current_feedback = current_feedback.split("</think>")[1]


def parse_chapter_outlines_from_file(num_chapters):
    
    with open(chapter_outlines_file, "r", encoding="UTF-8") as f:
        chapter_outlines_text = f.readlines()

    chapter_outlines = {}
    chapter_number = 0

    for line in chapter_outlines_text:
        if chapter_number > 0:
            chapter_outlines[chapter_number] = chapter_outlines[chapter_number] + line
        if len(re.findall("chapter.*\d", line.lower())) > 0:
            chapter_number = chapter_number + 1
            chapter_outlines[chapter_number] = ""

    if len(chapter_outlines) < num_chapters:
        exit("Not enough chapters in the chapter outlines file")

    return chapter_outlines
