# Story Generator

## Overview
This Python application generates a story based on a given premise and character profiles. It uses several modules to create chapter outlines and individual chapters, which are then compiled into a final story.

## Installation
```
pip install -r requirements.txt
```

## Prerequisites
- Python 3.x
- Required modules: `generate_characters`, `generate_outlines`, `generate_chapter`

## Usage

### Step 1: Prepare the Premise
Create a markdown file with the story premise. For example, `ideas/Minecraft Adventures.md`.

### Step 2: Run the Application
Execute the `app.py` script to generate the story. The script will prompt you to enter the number of chapters you want to generate.

```sh
python app.py
```

### Step 3: View the Generated Story
The generated story will be saved in the `story_output` directory as `final_story.txt`.

## Modules

### `generate_characters`
This module is responsible for generating character profiles based on the premise.

### `generate_outlines`
This module generates chapter outlines based on the premise and character profiles.

### `generate_chapter`
This module generates individual chapters based on the chapter outlines and character profiles.

## Example
Here is an example of how to use the application:

1. Create a premise file `ideas/Minecraft Adventures.md` with the following content:

```markdown
# Minecraft Adventures

## Story Outline
**Genre:** Adventure

**Setting:**
1. The vast and mysterious world of Minecraft.
2. Various biomes and dimensions within the Minecraft universe.
3. The player's base and surrounding areas.

## Characters
- **Alex:** The protagonist, a young adventurer exploring the Minecraft world.
- **Steve:** Alex's loyal companion, a friendly villager.
- **Zombie:** A hostile mob that Alex must defeat.
- **Creeper:** Another hostile mob that Alex must avoid.
- **Enderman:** A mysterious mob that can teleport and cause chaos.
- **Dragon:** The final boss that Alex must confront in the End dimension.
```

2. Run the application:

```sh
python app.py
```

3. Enter the number of chapters when prompted.

4. The generated story will be saved in `story_output/final_story.txt`.

## Configuration
You can configure the application by modifying the `config.py` file.

## License
This project is licensed under the MIT License.