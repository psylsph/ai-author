from config import get_llm_response
import os

chapter_outlines_file = "story_output/chapter_outlines.txt"
max_revisions = 5

def generate_chapter_outlines(premise, characters, num_chapters):

    # Check if the chapter_outlines file already exists
    if os.path.exists(chapter_outlines_file):
        return parse_chapter_outlines_from_file(num_chapters)
    
    current_feedback = ""

    outline_writer_system_prompt = f"""
You are an expert novel outline writer skilled at crafting compelling and structured chapter outlines that maintain narrative cohesion while developing characters and plot in engaging ways. Your task is to create a **detailed chapter-by-chapter outline** based on the provided story premise and characters.  

### **Key Responsibilities**  
1. Analyze the provided premise and characters to understand core themes and arcs.  
2. Structure the story into **{num_chapters}** coherent chapters, ensuring logical progression.  
3. Ensure each chapter advances the plot, deepens character development, and maintains engagement.  
4. Balance pacing, tone, and conflict to create a compelling narrative experience.  
5. Maintain consistency in story elements, character motivations, and world-building.  

### **Chapter Structure**  
Each chapter outline must include the following elements:  

#### **Chapter Number (Required)**  
- An integer between **1 and {num_chapters}**, sequentially numbered.  

#### **Title (Required)**  
- A concise yet engaging title that reflects the chapter's events or themes.  
- Avoid spoilers while maintaining intrigue.  

#### **Key Events (Required)**  
- List **3-5 pivotal moments** in **chronological order** that drive the story forward.  
- Include both **plot-driven** and **character-driven** events.  

#### **Description (Required)**  
- A comprehensive summary detailing the chapter's events.  
- Clearly establish cause-and-effect relationships.  
- Ensure smooth narrative progression.  

#### **Character Development (Required)**  
- Explain how key characters evolve, react, or reveal new aspects.  
- Note motivations, emotional changes, and relationship developments.  

#### **Start (Required)**  
- Describe the opening scene and its atmosphere.  
- Establish the situation and hook the reader's interest.  

#### **End (Required)**  
- Detail how the chapter concludes, including cliffhangers or resolutions.  
- Connect smoothly to the next chapter.  

#### **Setting (Required)**  
- Describe locations, timeframes, and atmospheric details.  
- Highlight any significant changes in setting.  

#### **Tone (Required)**  
- Define the emotional atmosphere and any shifts in mood.  
- Ensure tonal consistency with the overall narrative.  

#### **Conflicts (Required)**  
- List major **internal** and **external** obstacles faced.  
- Track ongoing and new conflicts introduced in this chapter.  

### **Guidelines for Narrative Cohesion**  

1. **Logical Flow**  
   - Ensure smooth transitions between chapters.  
   - Keep character motivations and actions consistent.  
   - Balance subplot progression alongside the main storyline.  

2. **Pacing & Engagement**  
   - Vary intensity levels across chapters.  
   - Balance action, dialogue, and introspection.  
   - Use well-placed hooks to sustain reader interest.  

3. **Character Focus**  
   - Distribute character development across the narrative.  
   - Ensure natural and consistent relationship growth.  
   - Track individual character arcs effectively.  

4. **World-Building**  
   - Integrate setting details naturally into the story.  
   - Maintain internal logic for world rules and elements.  
   - Use the environment to enhance mood and tension.  

5. **Conflict & Resolution Management**  
   - Escalate conflicts appropriately.  
   - Balance different types of challenges (physical, emotional, ideological).  
   - Use conflict resolutions to fuel further developments.  

### **Important Requirements**  
- ALWAYS provide outlines for **all {num_chapters}** chapters.  
- DO NOT include any narrative text—only structured outlines.  
- Ensure internal consistency in timeline, character presence, and story logic.  
- Keep outlines clear, concise, and engaging.  

"""
    
    outline_reviewer_system_prompt = f"""
You are an experienced book outline reviewer specializing in providing actionable feedback on chapter outlines. Your reviews focus on narrative structure, character development, pacing, continuity, and constructive critique.

Review Criteria
1. Structural Analysis
- Ensure each chapter has a clear beginning, middle, and end.
- Assess scene transitions for smooth narrative flow.
- Verify that every scene advances the story or character development.
- Check for proper setup and payoff of plot elements.

2. Character Consistency
- Ensure character voices, actions, and decisions align with established traits.
- Track believable character arcs and relationships.
- Flag inconsistencies in behavior or development.

3. Plot & Pacing
- Analyze tension and momentum within the chapter.
- Assess the balance between action, dialogue, and exposition.
- Identify pacing issues (rushed, dragged, or uneven sections).
- Verify the placement of key plot points.

4. Story Continuity
- Ensure consistency with prior chapters and the overall story arc.
- Track subplot progression and integration.
- Maintain established story-world rules.
- Monitor timeline consistency.

Feedback Guidelines
- Be constructive, specific, and concise.
- Provide examples and actionable solutions.
- Keep feedback under 300 words, focusing on the most critical points.
- Balance critique with recognition of effective elements.

Tone & Response Format
- Maintain a supportive yet direct tone, prioritizing actionable improvements that align with the author's vision.

Respond ONLY with:
[APPROVED] if fully compliant
[REVISE] [specific issues] if needing changes"""

    for revision in range(1, max_revisions+1): # plus 1 to include the final revision

        outline_writer_user_prompt = f"""Please create detailed chapter outlines based on the following:

Story Premise (ensure you cover all aspects of the premise):
{premise}

Characters:
{characters}

Number of Chapters: {num_chapters}

"""
        if len(current_feedback) > 0:
            outline_writer_user_prompt += f"\n\nFeedback from the previous revision: {current_feedback}"

        print(f"""\nGenerating chapter outlines (revision {revision} of {max_revisions})...""")       
        chapter_outlines = get_llm_response(outline_writer_system_prompt, outline_writer_user_prompt, 1.0, False)

        outline_reviewer_user_prompt = f"""Review the following chapter outline(s): {chapter_outlines}"""
        
        print("\nReviewing chapter outlines...")       
        current_feedback = get_llm_response(outline_reviewer_system_prompt, outline_reviewer_user_prompt, 0.6, True)

        print("\nCurrent Feedback:")
        print(current_feedback)

        if current_feedback.find("[APPROVED]") >= 0 or revision >= max_revisions:
            with open (chapter_outlines_file, "w", encoding="UTF-8") as f:
                f.write(chapter_outlines)
            return None
        
    return None


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
