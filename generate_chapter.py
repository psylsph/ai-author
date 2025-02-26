from typing import Dict
from config import get_llm_response

writer_system_prompt = """You are a specialized writing assistant focused on novel development. Your core purpose is transforming chapter outlines into polished, engaging prose while maintaining narrative cohesion and artistic quality.
Primary Functions:
Transform structural outlines into natural, flowing narrative prose that captures human emotions and experiences
Create sensory-rich descriptions that immerse readers without overwhelming them
Craft authentic dialogue that reveals character personality and advances the plot
Maintain distinct and consistent character voices throughout the narrative

Writing Approach:
Follow the established plot structure while thoughtfully integrating creative details that enhance the story
Write in a clear, engaging style that prioritizes impact over unnecessary elaboration
Balance showing and telling to maintain narrative momentum
Ensure descriptions serve the story rather than existing for their own sake

Chapter Structure:
Craft chapters with clear narrative arcs (start, middle, end)
Begin chapters with hooks that pull readers forward
Build tension and pacing throughout the middle
End chapters with satisfying resolution or compelling cliffhangers that drive continued reading

When writing, you will:
Analyze the provided chapter outline to understand its role in the larger narrative
Identify key emotional beats and character development moments
Transform outline points into natural scene progression
Maintain consistent tone and style throughout
Ensure all added details serve the story's themes and character arcs
Review for pacing and narrative flow

You excel at:
Converting bullet points into organic narrative flow
Adding meaningful sensory details that enhance immersion
Writing dialogue that sounds natural while revealing character
Maintaining narrative tension
Balancing action, dialogue, and description
Creating smooth transitions between scenes

Avoid:
Purple prose or overwrought descriptions
Dialogue that feels stilted or expository
Inconsistent character voices
Pacing that drags or rushes
Adding plot elements that contradict the outline
Losing focus on the chapter's core purpose

Your goal is to produce professional-quality prose that engages readers while staying true to the author's vision and outline."""
        
reviewer_system_prompt = """You are a concise but insightful literary critic specializing in chapter-by-chapter novel analysis. For each chapter review, you will:
Analyze the following key elements:

Plot progression and narrative momentum
Character development and consistency
Writing style and technical execution
Pacing and engagement
Continuity with previous chapters

Provide actionable feedback in these areas:

Structural improvements needed
Character motivation clarity
Scene pacing adjustments
Style enhancement suggestions
Plot hole identification
Thematic consistency

Format your review in exactly 150 words, structured as follows:

One sentence summarizing the chapter's effectiveness
Two sentences highlighting major strengths
Three specific areas for improvement with actionable solutions
One closing recommendation for revision priority

Focus on being constructive and specific, avoiding generalities. Each piece of feedback should be immediately actionable by the author. Address both technical and creative aspects while maintaining a supportive, professional tone."""

def write_chapter(chapter_outline:str, chapter_num:int, num_chapters:int, character_profiles:str, current_feedback:str, genre:str, target_audience:str, num_words:int, previous_chapter_summary: str) -> str:
    """Transform a chapter outline into prose, incorporating any previous feedback."""

    if not current_feedback:
        current_feedback = "This is your first draft. Please focus on creating engaging prose."
    else:
        current_feedback = f"Here is the feedback from the previous revision: {current_feedback} take this into account when writing this chapter."

    user_prompt = f"""Chapter Writing Request
Character Details
{character_profiles}
Previous Chapter Summary
{previous_chapter_summary}
Chapter Outline
{chapter_outline}
Specific Requirements
Tone: {genre}
Target Audience: {target_audience}
Word Count Target: 2000-3000 works (previous draft was {num_words} words), quality is more important than quantity.

Feedback on Previous Draft (if applicable):
{current_feedback}
"""
    if chapter_num == num_chapters:
        user_prompt += "\nThis is the final chapter. Ensure a satisfying conclusion to the story."

    return get_llm_response(system_prompt=writer_system_prompt, user_prompt=user_prompt)


def review_chapter(chapter: str, chapter_num: int, num_chapters: int,  character_profiles:str,  genre:str, previous_chapter_summary: str) -> str:
    """Review a written chapter and provide feedback."""

    user_prompt = f"""Please review the following chapter from my novel. This is Chapter {chapter_num} of {num_chapters}.
Brief context for the reviewer:

Genre: {genre}
Target audience: Adults
Character development goals for this chapter: {character_profiles}
Previous chapter summary: {previous_chapter_summary}

Chapter text:
{chapter}

Please provide your 150-word review following the structured format outlined in your instructions.

If the chapter is NOT ready to publish, provide specific, actionable feedback on how to improve the chapter, and write "Ready to publish: No" at the end of your feedback.
If the chapter is ready to publish, write "Ready to publish: Yes" at the end of your feedback.
"""
    return get_llm_response(system_prompt=reviewer_system_prompt, user_prompt=user_prompt)


def generate_chapter(outline: str, chapter_num: int, num_chapters, character_profiles, max_revisions, genre:str, target_audience:str, previous_chapter_summary: str) -> Dict[str, str]:

    current_feedback = ""

    num_words = 0

    for revision in range(1, max_revisions+1): # plus 1 to include the final revision
        print(f"Writing Chapter {chapter_num}, revision {revision}...")

        # Write chapter (incorporating previous feedback if it exists)
        chapter = write_chapter(chapter_outline=outline, chapter_num=chapter_num, num_chapters=num_chapters, character_profiles=character_profiles, current_feedback=current_feedback, genre=genre, target_audience=target_audience, num_words=num_words, previous_chapter_summary=previous_chapter_summary)

        # Get feedback on the chapter, skip if this is the final revision
        if revision < max_revisions:
            print(f"Reviewing Chapter {chapter_num}, revision {revision}...")
            current_feedback = review_chapter(chapter,  chapter_num,  num_chapters,  character_profiles, genre, previous_chapter_summary)
            num_words = len(chapter.split())
            if num_words < 1750:
                current_feedback += f"\nThe chapter is too short at {num_words}. Please expand it to at least 1750 words.\n"
            elif num_words > 3000:
                current_feedback += f"\nThe chapter is too long at {num_words}. Please trim it to 3000 words.\n"
            else:
                current_feedback += f"\nThe chapter is {num_words} words long. This is a good length.\n"
            # Print feedback for the writer to review
            print(f"\nFeedback for Chapter {chapter_num}, revision {revision}:\n{current_feedback}\n")
        else:
            current_feedback = ""

        # doesn't seem to by any sensible and repeatable way to check if the chapter is good enough, so we'll just publish it after the final revision
        # Check if the feedback indicates major issues, if not, publish the chapter, but alway do at least 3 revisions
        if "ready to publish: yes" in current_feedback.lower() and revision >= 3 and num_words > 1750:
            print(f"Chapter {chapter_num} achieved satisfactory quality after {revision} revisions.")
            return chapter

    return chapter

def summarize_chapter(chapter: str ,chapter_num: int, num_chapters: int) -> str:
    """Summarize a chapter."""

    summerizer_system_prompt = """You are a chapter summarizer who creates clear, focused summaries that capture both plot and meaning. For each chapter:

PROVIDE TWO SECTIONS

Brief Overview (2-3 sentences capturing the main event)
Key Points (3 bullet points highlighting important developments)
"""
    user_prompt = f"""Please summarize the following chapter from my novel. This is Chapter {chapter_num} of {num_chapters}.
Chapter text:
{chapter}

Please provide your 100-word summary following the structured format outlined in your instructions.
"""
    return get_llm_response(system_prompt=summerizer_system_prompt, user_prompt=user_prompt)