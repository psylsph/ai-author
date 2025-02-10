from typing import Dict
from config import get_llm_response

writer_system_prompt = """You are a novel writer who:
1. Transforms chapter outlines into human like engaging prose
2. Creates vivid descriptions and natural dialogue
3. Maintains consistent character voices
4. Follows the established plot structure while adding creative details
5. Write in a clear, engaging style without excessive description.
6. Writes detailed chapters with at least 3 significant story threads.
7. Ensures each chapter has a clear beginning, middle, and end."""
        
reviewer_system_prompt = """You are a literary critic who:
1. Reviews completed chapters for quality and consistency
2. Suggests improvements for pacing and style
3. Identifies potential plot holes or character inconsistencies
4. Ensures each chapter advances the story meaningfully
5. Provide specific, actionable feedback, limiting your response to no more than 150 words."""

def write_chapter(chapter_outline, chapter_num, num_chapters, character_profiles, current_feedback) -> str:
    """Transform a chapter outline into prose, incorporating any previous feedback."""

    if not current_feedback:
        current_feedback = "This is your first draft. Please focus on creating engaging prose."
    else:
        current_feedback = f"Here is the feedback from the previous revision: {current_feedback} take this into account when writing this chapter."

    user_prompt = f"""Using the outline below for Chapter {chapter_num}, write a detailed chapter that advances the story
    for ONLY chapter {chapter_num}:

{chapter_outline}

Character Profiles:
{character_profiles}

{current_feedback}

Focus on:
1. Each story thread MUST aim to be least 1000 words long.
2. Each chapter MUST contain between 2000 and 4000 words.
3. Each chapter MUST be self-contained and complete, while advancing the overall story.
Take your time thinking and write the chapter now.
"""
    if chapter_num == num_chapters:
        user_prompt += "\nThis is the final chapter. Ensure a satisfying conclusion to the story."

    return get_llm_response(system_prompt=writer_system_prompt, user_prompt=user_prompt)


def review_chapter(chapter: str, chapter_num: int, revision_num: int, max_revisions:int, character_profiles: str ) -> str:
    """Review a written chapter and provide feedback."""

    print(f"""\nReviewer: The current word count for the chapter is {len(chapter.split())} words.""")

    user_prompt = f"""Review this draft (revision {revision_num}) of Chapter {chapter_num}:

Character Profiles:
{character_profiles}

The current word count for the chapter is {len(chapter.split())} words.

{chapter}

Please provide your feedback in a clear and concise manner, formatted as follows:
- Plot progression and pacing: [Your feedback here]
- Character development: [Your feedback here]
- Writing style and dialogue: [Your feedback here]
- Areas for improvement: [Your feedback here]
- Word count: [Your feedback here]
- Character consistency: [Your feedback here]
- Ready to publish: [Yes/No]

If this is Revision {max_revisions}, be extra thorough in your assessment.
If the chapter is ready to publish, write "Ready to publish: Yes" at the end of your feedback.
"""
    return get_llm_response(system_prompt=reviewer_system_prompt, user_prompt=user_prompt)


def generate_chapter(outline: str, chapter_num: int, num_chapters, character_profiles, max_revisions) -> Dict[str, str]:

    current_feedback = ""

    for revision in range(1, max_revisions+1): # plus 1 to include the final revision
        print(f"Writing Chapter {chapter_num}, Revision {revision}...")

        # Write chapter (incorporating previous feedback if it exists)
        chapter = write_chapter(chapter_outline=outline, chapter_num=chapter_num, num_chapters=num_chapters, character_profiles=character_profiles, current_feedback=current_feedback)

        if "</think>" in chapter:
            chapter = chapter.split("</think>")[1]

        # Get feedback on the chapter, skip if this is the final revision
        if revision < max_revisions:
            print(f"Reviewing Chapter {chapter_num}, Revision {revision}...")
            current_feedback = review_chapter(chapter,  chapter_num,  revision, max_revisions, character_profiles)
            if "</think>" in current_feedback:
                current_feedback = current_feedback.split("</think>")[1]
        else:
            current_feedback = ""

        # Print feedback for the writer to review
        print(f"\nFeedback for Chapter {chapter_num}, Revision {revision}:\n{current_feedback}\n")

        # doesn't seem to by any sensible and repeatable way to check if the chapter is good enough, so we'll just publish it after the final revision
        # Check if the feedback indicates major issues
        if "Ready to publish: Yes" in current_feedback.lower():
            print(f"Chapter {chapter_num} achieved satisfactory quality after {revision} revisions.")
        #    return chapter

    return chapter