from typing import Dict
from webbrowser import get
import autogen
import re

from character_manager import CharacterManager
from config import get_config, get_user_proxy

llm_config = get_config()

writer = autogen.AssistantAgent("writer",
            system_message="""You are a creative writer who:
1. Transforms outlines into engaging prose
2. Creates vivid descriptions and natural dialogue
3. Maintains consistent character voices
4. Follows the established plot structure while adding creative details Write in a clear, engaging style without excessive description.
5. Incorporates feedback to improve chapters""",
            llm_config=llm_config )
        
reviewer = autogen.AssistantAgent("reviewer",
            system_message="""You are a literary critic who:
1. Reviews completed chapters for quality and consistency
2. Suggests improvements for pacing and style
3. Identifies potential plot holes or character inconsistencies
4. Ensures each chapter advances the story meaningfully Provide specific, actionable feedback.""",
            llm_config=llm_config )

def get_character_context(character_manager: CharacterManager, chapter_num: int) -> str:
        """Get current character context for the chapter."""
        relevant_chars = {
            name: char for name, char in character_manager.characters.items()
            if (not char.last_appearance or  # New characters
                int(re.sub(r'[^0-9]', '', char.last_appearance)) >= chapter_num - 2)  # Recently appeared characters
        }

        context = "Current Character Profiles:\n\n"
        for char in relevant_chars.values():
            context += f"""
            Name: {char.name}
            Role: {char.role}
            Description: {char.description}
            Key Traits: {', '.join(char.key_traits)}
            Recent Activity: Last appeared in Chapter {char.last_appearance or 'N/A'}

            """
        return context

def write_chapter(outline: str, character_manager: CharacterManager, num_chapters: int, chapter_num: int, previous_feedback: str = None) -> str:
        """Transform a chapter outline into prose, incorporating any previous feedback."""

        character_context = get_character_context(character_manager, chapter_num)
        chat_manager = autogen.GroupChat( agents=[get_user_proxy(), writer], messages=[], max_round=2,
                                                     speaker_selection_method="auto", allow_repeat_speaker=False)
        manager = autogen.GroupChatManager(groupchat=chat_manager)

        feedback_prompt = "This is your first draft. Please focus on creating engaging prose."
        if previous_feedback:
            feedback_prompt = f"\nPlease address this feedback in your revision:\n{previous_feedback}"

        prompt = f"""Using this outline for Chapter {chapter_num} of {num_chapters}, write a complete chapter in engaging prose:

{outline}

Character Context:
{character_context}
Editor Feedback:
{feedback_prompt}

Focus on:
1. Natural dialogue and character interactions
2. Vivid but concise descriptions
3. Smooth scene transitions
4. Maintaining consistent pacing Write the chapter now
5. Each chapter MUST contain at least 5000 words
6. Each chapter MUST be self-contained and complete, while advancing the overall story
Write the chapter now, ending with the word TERMINATE
"""

        get_user_proxy().initiate_chat( manager, message=prompt)
        chapter_content = ""
        for message in chat_manager.messages:
            if message["name"] == "writer":
                chapter_content += message["content"]

        _update_character_appearances(character_manager=character_manager, content=chapter_content, chapter=str(chapter_num))
        # Extract the last message from the writer as the chapter
        return chapter_content

def _update_character_appearances(character_manager: CharacterManager, content: str, chapter: str):
        """Update character appearances based on chapter content."""
        for char_name in character_manager.characters.keys():
            if char_name.lower() in content.lower():
                character_manager.update_appearance(char_name, chapter)
                character_manager.track_mention(chapter, char_name)

def review_chapter(character_manager: CharacterManager, chapter: str, chapter_num: int, revision_num: int) -> str:
        """Review a written chapter and provide feedback."""
        character_context = get_character_context(character_manager, chapter_num)
        chat_manager = autogen.GroupChat(
            agents=[get_user_proxy(), reviewer],
            messages=[],
            max_round=2,
            speaker_selection_method="auto",
            allow_repeat_speaker=False
        )

        manager = autogen.GroupChatManager(groupchat=chat_manager)

        prompt = f"""Review this draft (revision {revision_num}) of Chapter {chapter_num}:

{chapter}

Character Context:
{character_context}

Provide specific feedback on:
1. Plot progression and pacing
2. Character development
3. Writing style and dialogue
4. Areas for improvement
5. The number of words, the writer should aiming for at least 5000 words per chapter

Pay special attention to character consistency issues.
If this is revision 5, be extra thorough in your assessment.
End your review with TERMINATE"""

        get_user_proxy().initiate_chat(
            manager,
            message=prompt
        )
        feedback = ""
        for message in chat_manager.messages:
            if message["name"] == "reviewer":
                feedback += message["content"]
        return feedback

def write_chapter_with_revisions(outline: str, chapter_num: int, num_chapters, character_manager) -> Dict[str, str]:
    """Write a chapter with multiple revisions based on feedback."""
    chapter_versions = {}
    current_feedback = None

    for revision in range(5):
        print(f"\nWorking on Chapter {chapter_num}, Revision {revision + 1}...")

        # Write chapter (incorporating previous feedback if it exists)
        chapter = write_chapter(outline=outline, num_chapters=num_chapters, chapter_num=chapter_num, character_manager=character_manager, previous_feedback=current_feedback)

        # Get feedback on the chapter
        current_feedback = review_chapter(character_manager, chapter, chapter_num,  revision + 1)

        # Store this version
        chapter_versions[f"revision_{revision + 1}"] = {
            "content": chapter,
            "feedback": current_feedback
        }

        # Check if the feedback indicates major issues
        if "excellent" in current_feedback.lower() or "outstanding" in current_feedback.lower():
            print(f"Chapter {chapter_num} achieved satisfactory quality after {revision + 1} revisions.")
            break

    return chapter_versions