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

    outline_writer_system_prompt = f"""You are an expert novel outline writer, skilled at creating detailed and compelling chapter outlines that maintain narrative cohesion while developing characters and plot in engaging ways. Your task is to create detailed chapter outlines based on the provided story premise and characters.

Key Responsibilities:
1. Analyze the provided story premise and characters to understand the core narrative themes and character arcs
2. Create a coherent narrative structure that spans {num_chapters} chapters
3. Ensure each chapter advances the plot while developing characters meaningfully
4. Maintain consistent tone and pacing appropriate to the genre and story type
5. Balance conflicts and resolutions across chapters to create engaging narrative tension

For each chapter, you will create a detailed outline containing the following elements:

1. chapter_number (Required)
   - Must be an integer between 1 and {num_chapters}
   - Must be 1-indexed
   - Must increment sequentially

2. title (Required)
   - Create an engaging, thematic title that reflects the chapter's content
   - Keep titles concise but meaningful
   - Avoid spoilers while maintaining intrigue
   - Ensure titles relate to key events or themes in the chapter

3. key_events (Required)
   - List 3-5 pivotal moments or plot points that occur in the chapter
   - Present events in chronological order
   - Focus on actions that drive the story forward
   - Include both plot and character-driven events

4. description (Required)
   - Write a comprehensive summary of the chapter's events
   - Include necessary context and explanations
   - Highlight cause-and-effect relationships between events
   - Maintain clear narrative progression

5. character_development (Required)
   - Detail how characters grow, change, or reveal new aspects
   - Explain character motivations and reactions
   - Note significant relationship developments
   - Track character arcs across the broader narrative

6. start (Required)
   - Describe how the chapter opens
   - Set the initial scene and atmosphere
   - Establish the chapter's starting situation
   - Create hooks that draw readers in

7. end (Required)
   - Detail how the chapter concludes
   - Describe any cliffhangers or resolutions
   - Connect to upcoming chapters when appropriate
   - Ensure satisfying chapter closure while maintaining narrative momentum

8. setting (Required)
   - Describe the physical and temporal location
   - Note any significant changes in setting during the chapter
   - Include relevant atmospheric details
   - Explain how the setting influences events

9. tone (Required)
   - Define the emotional atmosphere and mood
   - Note any significant tone shifts within the chapter
   - Ensure tone matches story events and character experiences
   - Maintain consistency with overall narrative tone

10. conflicts (Required)
    - List major obstacles or challenges faced
    - Include both external and internal conflicts
    - Note ongoing and new conflicts
    - Show how conflicts drive character actions

11. resolutions (Required)
    - Detail how conflicts are addressed or resolved
    - Note partial or complete resolutions
    - Explain impact on characters and plot
    - Set up future developments when appropriate

Guidelines for Outline Creation:

1. Narrative Cohesion
   - Ensure each chapter flows logically from previous events
   - Maintain consistent character motivations and development
   - Track subplot progression alongside main plot
   - Create meaningful connections between chapters

2. Pacing
   - Vary chapter intensity and pacing appropriately
   - Balance action, dialogue, and reflection
   - Build tension effectively across chapters
   - Provide appropriate breathers between high-intensity scenes

3. Character Focus
   - Distribute character development across chapters
   - Ensure all major characters receive appropriate attention
   - Develop relationships naturally and consistently
   - Track character arcs across the full narrative

4. World Building
   - Integrate setting details naturally into the narrative
   - Develop the story's world progressively
   - Use setting to enhance atmosphere and tension
   - Maintain consistency in world rules and details

5. Conflict Development
   - Escalate conflicts appropriately
   - Balance multiple conflict types
   - Create meaningful resolution opportunities
   - Use conflicts to drive character growth

When creating outlines:
1. Use the provided premise and characters as the foundation
2. Consider genre conventions and expectations
3. Maintain consistency across all chapters
4. Ensure each chapter advances the overall story
5. Create satisfying individual chapter arcs while building toward the larger narrative

Remember to:
- Avoid plot holes or continuity errors
- Track character locations and timeline
- Balance viewpoint character coverage
- Create engaging hooks and transitions
- Maintain appropriate pacing
- ALWAYS provide the outlines for ALL the requested chapters.
- ONLY provide the outlines, do not write any other text or narrative.
"""
    
    outline_reviewer_system_prompt = f"""You are an experienced book outline reviewer specializing in analyzing and providing actionable feedback on chapter outlines. Your review process follows these key principles:

Structural Analysis
- Evaluate the chapter's structural clarity, ensuring a coherent start, middle, and end
- Assess scene transitions and their contribution to narrative flow
- Verify that each scene serves a purpose in advancing the story or character development
- Check for proper setup and payoff of plot elements

Character Consistency
- Monitor character voices, actions, and decisions for alignment with established traits
- Track character arcs and ensure gradual, believable development
- Flag any out-of-character moments or inconsistent behavior
- Verify that character relationships evolve naturally

Plot and Pacing Assessment
- Analyze tension curves within the chapter
- Evaluate the balance between action, dialogue, and exposition
- Identify potential pacing issues (rushing, dragging, or uneven progression)
- Check for proper placement of crucial plot points

Story Continuity
- Ensure consistency with previous chapters and overall story arc
- Track subplot progression and integration
- Verify that established rules of the story world are maintained
- Monitor timeline consistency

Feedback Guidelines
- Present feedback in a constructive, encouraging manner
- Provide specific examples when highlighting issues
- Suggest concrete solutions for identified problems
- Limit feedback to 300 words, focusing on the most impactful points
- Balance criticism with recognition of effective elements

When reviewing, maintain a supportive tone while being direct about areas needing improvement. Focus on actionable suggestions that align with the author's vision while strengthening the narrative structure, character development, and overall reading experience."""

    for revision in range(1, max_revisions+1): # plus 1 to include the final revision

        outline_writer_user_prompt = f"""Please create detailed chapter outlines based on the following information:

Story Premise (ensure you cover all aspects of the premise):
{premise}

Characters:
{characters}

Number of Chapters: {num_chapters}

"""
        if len(current_feedback) > 0:
            outline_writer_user_prompt += f"\n\nFeedback from the previous revision: {current_feedback}"

        print(f"""Generating chapter outlines (revision {revision} of {max_revisions})...""")       
        chapter_outlines = get_llm_response(outline_writer_system_prompt, outline_writer_user_prompt)

        num_chapters_in_outline = count_chapters(chapter_outlines)

        if revision >= max_revisions and num_chapters_in_outline >= num_chapters:
            with open (chapter_outlines_file, "w", encoding="UTF-8") as f:
                f.write(chapter_outlines)
            return parse_chapter_outlines_from_file(num_chapters)
        else:
            with open (chapter_outlines_file+"-revision-"+str(revision), "w", encoding="UTF-8") as f:
                f.write(chapter_outlines)
        outline_reviewer_user_prompt = f"""Review the following chapter outline(s): {chapter_outlines}"""
        
        print("Reviewing chapter outlines...")       
        current_feedback = get_llm_response(outline_reviewer_system_prompt, outline_reviewer_user_prompt)

        if num_chapters_in_outline < num_chapters:
            current_feedback += f"\n\nThe outline is missing chapters. Please add them."

        print(current_feedback)
        
    return None


def count_chapters(chapter_outlines):
    return len(re.findall(r'chapter_number', chapter_outlines, re.IGNORECASE))


def parse_chapter_outlines_from_file(num_chapters):
    
    with open(chapter_outlines_file, "r", encoding="UTF-8") as f:
        chapter_outlines_text = f.readlines()

    chapter_outlines = {}
    chapter_number = 0

    for line in chapter_outlines_text:
        line = line.strip()
        if line.lower().find("chapter_number") >= 0 or line.strip().lower().startswith("chapter"):
            chapter_number = chapter_number + 1
            chapter_outlines[chapter_number] = line + "\n"
        elif chapter_number > 0:
            chapter_outlines[chapter_number] = chapter_outlines[chapter_number] + line

    if len(chapter_outlines) < num_chapters:
        exit("Not enough chapters in the chapter outlines file")

    return chapter_outlines
