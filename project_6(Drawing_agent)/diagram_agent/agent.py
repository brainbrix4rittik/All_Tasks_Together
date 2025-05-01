# diagram_agent/agent.py
from typing import Dict, Any, Optional, List
import json
import os
# Import both OpenAI and GenerativeModel
from openai import AzureOpenAI
import google.generativeai as genai
from dotenv import load_dotenv
from .diagram_generator import DiagramGenerator
from .tools import Position, Size, ImageSource, DrawingTool
import uuid
import traceback

class DiagramAgent:

    # The constructor now primarily uses api_config to decide which client to initialize.
    # The openai_api_key parameter from the original signature is kept for potential backward compatibility,
    # but the main logic relies on api_config passed from main.py which is built based on API_CHOICE.
    def __init__(self, api_config: Dict[str, Any]):
        if not api_config or "api_type" not in api_config:
            raise ValueError("API configuration is required")

        self.api_type = api_config["api_type"].lower() # Ensure lowercase for consistent comparison

        self.diagram_generator = DiagramGenerator(canvas_width=1200, canvas_height=1000)
        self.story_analysis = None
        self.client = None
        self.model_name = None

        load_dotenv() # Ensure environment variables are loaded

        print(f"DiagramAgent initializing with API: {self.api_type}")

        if self.api_type == "azure":
            api_key = api_config.get("api_key")
            azure_endpoint = api_config.get("azure_endpoint")
            self.model_name = api_config.get("deployment_name", "GPT4o") # Default deployment name

            if not all([api_key, azure_endpoint]):
                raise ValueError("Azure OpenAI API key and endpoint are required in api_config.")

            self.client = AzureOpenAI(
                api_key=api_key,
                api_version="2024-02-01",
                azure_endpoint=azure_endpoint
            )
            print(f"Initialized Azure OpenAI client with deployment: {self.model_name}")

        elif self.api_type == "gemini":
            api_key = api_config.get("api_key")
            self.model_name = api_config.get("model_name", "gemini-2.0-flash-latest") # Default Gemini model

            if not api_key:
                raise ValueError("Gemini API key is required in api_config for api_type='gemini'.")

            # Configure Gemini client
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model_name=self.model_name)
            print(f"Initialized Gemini client with model: {self.model_name}")

        else:
            raise ValueError(f"Unsupported API type in api_config: {self.api_type}. Choose 'azure' or 'gemini'.")


    def analyze_story(self, story_text: str) -> Dict[str, Any]:
        if not story_text:
            raise ValueError("Story text cannot be empty")

        try:
            print("\n--- Analyzing Story ---")

            # System prompt for story analysis remains the same for both APIs
            system_prompt = """You are a comprehensive story analyst. Your task is to deeply analyze the story and provide a structured analysis in JSON format. Include the following components:

1. "summary": A concise but complete summary of the story's main plot points and themes.

2. "characters": Array of character objects, each containing:
   - "name": Character's name or identifier
   - "role": Main role in the story (e.g., protagonist, antagonist, mentor, ally)
   - "description": Physical and personality traits
   - "goals": Character's objectives or motivations
   - "arc": Character's development or journey
   - "relationships": Key relationships with other characters
   - "status": Current state/condition (e.g., alive, dead, transformed)
   - "significance": Impact on the story

3. "groups": Array of group objects (organizations, families, teams, etc.), each containing:
   - "name": Group name
   - "type": Type of group (e.g., family, organization, army)
   - "description": Group's characteristics and purpose
   - "members": Known members
   - "goals": Group's objectives
   - "significance": Role in the story

4. "locations": Array of location objects, each containing:
   - "name": Location name
   - "type": Type of location (e.g., city, building, realm)
   - "description": Physical characteristics and atmosphere
   - "significance": Importance to the story
   - "events": Key events that occur here
   - "inhabitants": Notable characters/groups associated

5. "objects": Array of key object objects (items, artifacts, etc.), each containing:
   - "name": Object name
   - "type": Type of object
   - "description": Physical description
   - "powers": Special properties or abilities (if any)
   - "significance": Role in the story
   - "possessor": Current owner/holder
   - "history": Notable past events involving this object

6. "abstract_concepts": Array of concept objects, each containing:
   - "name": Concept name
   - "type": Type (e.g., theme, curse, prophecy, condition)
   - "description": Detailed explanation
   - "manifestations": How it appears/affects the story
   - "significance": Impact on plot/characters
   - "related_elements": Characters/objects/events involved

7. "relationships": Array of relationship objects, each containing:
   - "type": Type of relationship (e.g., family, rivalry, romance)
   - "participants": Involved parties
   - "description": Nature of the relationship
   - "dynamics": How it evolves
   - "significance": Impact on the story

8. "events": Array of event objects, each containing:
   - "name": Event name/description
   - "type": Type of event (e.g., battle, revelation, journey)
   - "timing": When it occurs in the story
   - "location": Where it takes place
   - "participants": Characters/groups involved
   - "causes": What led to this event
   - "consequences": Results and impact
   - "significance": Importance to the plot

9. "plot_structure": Object containing:
   - "exposition": Initial setup and background
   - "rising_action": Building conflicts and complications
   - "climax": Peak of the story
   - "falling_action": Events following climax
   - "resolution": How the story concludes
   - "subplots": Array of significant secondary plot lines

10. "themes": Array of theme objects, each containing:
    - "name": Theme name
    - "description": Detailed explanation
    - "manifestations": How it appears in the story
    - "significance": Why it matters
    - "related_elements": Characters/events that embody it

11. "conflicts": Array of conflict objects, each containing:
    - "type": Type of conflict (e.g., person vs person, person vs nature)
    - "description": Nature of the conflict
    - "participants": Involved parties
    - "stakes": What's at risk
    - "resolution": How it's resolved (if applicable)

12. "symbolism": Array of symbol objects, each containing:
    - "symbol": What serves as the symbol
    - "meaning": What it represents
    - "occurrences": Where it appears
    - "significance": Impact on themes/plot

Analyze ALL these aspects regardless of story type (fantasy, realistic, historical, etc.). If any category is not explicitly present, consider implicit or subtle manifestations. For each element, provide rich detail and explain connections to other elements.

RESPOND ONLY WITH A VALID JSON OBJECT containing all these categories, even if some are empty arrays. Ensure all strings are properly escaped and all arrays/objects are properly nested."""

            if self.client is None:
                raise RuntimeError("API client was not initialized correctly.")

            if self.api_type == "azure":
                print("\n--- Sending Request to Azure OpenAI for Analysis ---")
                analysis_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": story_text}
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                    response_format={"type": "json_object"}
                )
                raw_content = analysis_response.choices[0].message.content

            elif self.api_type == "gemini":
                print("\n--- Sending Request to Gemini for Analysis ---")
                 # Gemini doesn't have a separate system role in the same way
                # We can combine system and user prompt for Gemini
                gemini_prompt = f"System Instructions: {system_prompt}\n\nStory Text:\n{story_text}"

                generation_config = {
                    "temperature": 0.3,
                    "max_output_tokens": 10000,
                    "response_mime_type": "application/json" # Specify JSON output
                }
                analysis_response = self.client.generate_content(
                    gemini_prompt,
                    generation_config=generation_config
                )
                raw_content = analysis_response.text # Access content based on Gemini response structure

            else:
                 # This case should ideally not be reached if init is correct
                 raise ValueError(f"Unsupported API type for analysis: {self.api_type}")


            if not raw_content:
                raise ValueError(f"No story analysis content received from {self.api_type}")

            print("\n--- Received Raw Response ---")
            print(raw_content)
            print("--- End Raw Response ---\n")

            # --- Added Cleanup for JSON Decoding ---
            # Attempt to find and parse the JSON object from the raw content
            try:
                # A basic approach: find the first '{' and the last '}'
                # This might not be perfect for all malformed JSONs, but handles common wrapping text
                json_start = raw_content.find('{')
                json_end = raw_content.rfind('}')

                if json_start == -1 or json_end == -1:
                     raise ValueError("Could not find valid JSON object in response.")

                # Extract the potential JSON string
                cleaned_content = raw_content[json_start : json_end + 1]

                # Attempt to load the cleaned content as JSON
                analysis = json.loads(cleaned_content)
                print("\n--- Parsed Story Analysis JSON ---")
                print(json.dumps(analysis, indent=2))
                print("--- End Parsed Story Analysis JSON ---\n")


                self.story_analysis = analysis
                analysis_file = 'story_analysis.json'
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2)
                print("Story analysis completed and saved to story_analysis.json")
                return analysis
            except json.JSONDecodeError as e:
                print(f"\nError: Failed to decode JSON from story analysis ({self.api_type}): {e}")
                print(f"Raw content was:\n{raw_content}")
                raise ValueError(f"Story analysis failed due to invalid JSON response ({self.api_type}): {e}")
            except ValueError as e:
                 print(f"\nError: Failed to extract JSON from story analysis ({self.api_type}): {e}")
                 print(f"Raw content was:\n{raw_content}")
                 raise ValueError(f"Story analysis failed due to inability to extract JSON ({self.api_type}): {e}")
            except Exception as e:
                print(f"\nError: Failed to process story analysis JSON ({self.api_type}): {str(e)}\n")
                print(f"Raw content was:\n{raw_content}")
                raise ValueError(f"Story analysis failed ({self.api_type}): {str(e)}")


        except Exception as e:
            print(f"\nError in story analysis step ({self.api_type}): {str(e)}\n")
            raise ValueError(f"Story analysis failed ({self.api_type}): {str(e)}")

    def _validate_tool_call(self, tool_call: Dict[str, Any]) -> bool:
        # This method remains unchanged
        if not isinstance(tool_call, dict) or "tool" not in tool_call or "params" not in tool_call:
            print(f"Warning: Invalid tool call structure: {tool_call}")
            return False

        tool_type = tool_call["tool"]
        params = tool_call["params"]

        if not isinstance(params, dict):
            print(f"Warning: Invalid params structure for tool '{tool_type}': {params}")
            return False

        valid_tools = ["circle", "arrow", "line", "triangle", "star", "text", "image", "rectangle"]
        if tool_type not in valid_tools:
            print(f"Warning: Invalid tool type: {tool_type}")
            return False

        if "position" not in params or not isinstance(params["position"], dict) or \
           "x" not in params["position"] or "y" not in params["position"]:
            print(f"Warning: Missing or invalid position in params for tool '{tool_type}': {params.get('position')}")
            return False

        if "size" not in params or not isinstance(params["size"], dict) or \
           "width" not in params["size"] or "height" not in params["size"]:
            print(f"Warning: Missing or invalid size in params for tool '{tool_type}': {params.get('size')}")
            return False

        if tool_type == "text" and not params.get("text", "").strip():
            print(f"Warning: Skipping empty text tool.")
            return False

        return True

    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> None:
        # This method remains unchanged
        tool_type = tool_call["tool"]
        params = tool_call["params"]

        try:
            self.diagram_generator.add_shape_from_params(tool_type=tool_type, params=params)
        except ValueError as e:
            print(f"Error executing tool call for {tool_type} with params {params}: {e}")
        except Exception as e:
            print(f"Unexpected error executing tool call for {tool_type}: {e}")


    def generate_diagram_from_analysis(self, prompt: str) -> Dict[str, Any]:
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        if not self.story_analysis:
            try:
                with open('story_analysis.json', 'r', encoding='utf-8') as f:
                    self.story_analysis = json.load(f)
            except FileNotFoundError:
                 raise ValueError("No story analysis file found. Please run analyze_story first or ensure 'story_analysis.json' exists.")
            except Exception as e:
                raise ValueError(f"Error loading story_analysis.json: {str(e)}")


        self.diagram_generator = DiagramGenerator(canvas_width=1200, canvas_height=1000)

        try:
            print("\n--- Generating Diagram from Analysis ---")
            analysis_str = json.dumps(self.story_analysis, indent=2)

            # Use the existing DIAGRAM_SYSTEM_PROMPT
            system_prompt = DIAGRAM_SYSTEM_PROMPT

            if self.client is None:
                 raise RuntimeError("API client was not initialized correctly.")

            if self.api_type == "azure":
                print("\n--- Sending Request to Azure OpenAI for Diagram Plan ---")
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Story Analysis:\n```\n{analysis_str}\n```\n\nPrompt:\n```\n{prompt}\n```"}
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                    response_format={"type": "json_object"},
                    seed=42
                )
                raw_content = response.choices[0].message.content

            elif self.api_type == "gemini":
                print("\n--- Sending Request to Gemini for Diagram Plan ---")
                 # Combine system and user prompt for Gemini
                gemini_prompt = f"System Instructions: {system_prompt}\n\nStory Analysis:\n```\n{analysis_str}\n```\n\nPrompt:\n```\n{prompt}\n```"

                generation_config = {
                    "temperature": 0.3,
                    "max_output_tokens": 10000,
                     "response_mime_type": "application/json" # Specify JSON output
                }
                response = self.client.generate_content(
                    gemini_prompt,
                    generation_config=generation_config
                )
                raw_content = response.text # Access content based on Gemini response structure

            else:
                 # This case should ideally not be reached if init is correct
                 raise ValueError(f"Unsupported API type for diagram generation: {self.api_type}")


            if not raw_content:
                raise ValueError(f"No response content received from {self.api_type}")

            print("\n--- Received Raw Response ---")
            print(raw_content)
            print("--- End Raw Response ---\n")

            try:
                # Attempt to decode JSON, including cleanup for markdown fences
                cleaned_content = raw_content.strip().removeprefix("```json").removesuffix("```").strip()

                # Add an additional cleanup step just in case of leading/trailing text outside fences
                # Find the first '{' and the last '}' and slice the string
                json_start = cleaned_content.find('{')
                json_end = cleaned_content.rfind('}')

                if json_start == -1 or json_end == -1:
                     # Fallback to original cleaned_content if braces not found
                     final_json_string = cleaned_content
                     print("Warning: Could not find explicit JSON braces in response, attempting parse with raw cleaned content.")
                else:
                     # Extract content within braces
                     final_json_string = cleaned_content[json_start : json_end + 1]


                plan = json.loads(final_json_string)
                print("\n--- Parsed Diagram Plan ---")
                print(json.dumps(plan, indent=2))
                print("--- End Parsed Plan ---\n")

                if not isinstance(plan, dict) or "tools" not in plan or not isinstance(plan["tools"], list):
                    raise ValueError("Invalid plan format: Must be a JSON object with a 'tools' array.")

                if not plan["tools"]:
                    print("Warning: Received plan with empty 'tools' array.")
                    return json.loads(self.diagram_generator.generate_diagram().to_json())

                print("\n--- Executing Plan ---")
                valid_tool_calls = 0
                # Re-initialize the diagram generator to clear previous shapes if this function is called multiple times
                self.diagram_generator = DiagramGenerator(canvas_width=1200, canvas_height=1000)
                for i, tool_call in enumerate(plan["tools"]):
                    print(f"Processing tool call {i+1}: {tool_call.get('tool')}")
                    if self._validate_tool_call(tool_call):
                        self._execute_tool_call(tool_call)
                        valid_tool_calls += 1
                    else:
                        print(f"Skipping invalid tool call {i+1}.")

                print(f"--- Plan Execution Complete ({valid_tool_calls}/{len(plan['tools'])} valid calls executed) ---")

                final_diagram_obj = self.diagram_generator.generate_diagram()
                return json.loads(final_diagram_obj.to_json())

            except json.JSONDecodeError as e:
                print(f"Error: Failed to decode JSON response from {self.api_type}: {e}")
                print(f"Raw content was:\n{raw_content}")
                raise ValueError(f"Diagram generation failed due to invalid JSON response ({self.api_type}): {e}")
            except Exception as e2:
                    raise ValueError(f"Invalid JSON response from {self.api_type}, even after cleaning: {e2}")

        except Exception as e:
            print(f"Error during diagram generation ({self.api_type}): {traceback.format_exc()}")
            raise ValueError(f"Error generating diagram ({self.api_type}): {str(e)}")


# Define the system prompt content outside the class for better organization
DIAGRAM_SYSTEM_PROMPT = """You are a diagram generation assistant. Your primary goal is to create a detailed, comprehensive, and **CLEARLY READABLE** diagram plan based on the provided story analysis and user prompt. The plan MUST consist of a list of tool calls in a JSON object.

Your diagram plan must visually represent the key narrative elements and their connections. **You MUST identify and represent ALL relevant elements from the following categories if they are present in the story analysis: Characters, Groups, Locations, Key Objects, Abstract Concepts (themes, conditions, pacts, curses), Relationships/Actions, and Events/Plot Points.**

For each element or connection you represent, use the available tools and adhere strictly to the specified JSON format.

**Representing Elements:**

1.  **Characters:** Use `rectangle` or `circle` shapes.
    * **Labels:** Add a separate `text` tool call positioned **precisely centered** within the character's shape. This text label MUST include the character's name and **ALL relevant details** from the story analysis (role, key traits, conditions, status - e.g., "Character Name (Role/Status)"). Use line breaks (`\\n`) in the text tool's `text` parameter for multi-line labels to keep them compact and readable. The shape's size MUST be large enough to comfortably fit the text label plus adequate internal padding. Specifically, ensure the shape's width is at least the estimated text width plus 40 units (20 units padding on each side), and the shape's height is at least the estimated text height plus 40 units (20 units padding on top and bottom). Estimate the required text size first before determining the shape size.
2.  **Groups:** Use `rectangle` or `circle` shapes, or a distinct `text` block if a shape isn't suitable.
    * **Labels:** Use a `text` tool call with the group name and brief description if available. Position the label clearly, preferably centered within or directly below the shape/block. Ensure the shape/block is large enough to fit the text with padding.
3.  **Locations/Settings:** Use `rectangle` shapes or distinct `text` blocks.
    * **Labels:** Use a `text` tool call with the location name and relevant description (e.g., "Setting: Primary Location", "Location: Specific Place"). Position the label clearly, preferably centered within or or directly below the shape/block. Ensure the shape/block is large enough to fit the text with padding.
4.  **Key Objects:** Use `rectangle`, `circle`, or other simple shapes, or a distinct `text` block.
    * **Labels:** Use a `text` tool call with the object name and significance (e.g., "Important Object (Significance)", "Artifact Name (Power/Effect)"). Position the label clearly, preferably centered within or directly below the shape/block. Ensure the shape/block is large enough to fit the text with padding.
5.  **Abstract Concepts:** Use `circle`, `triangle`, `star` shapes, or distinct `text` blocks.
    * **Labels:** Use a `text` tool call with the concept name and brief explanation if needed (e.g., "Main Theme", "Abstract Concept (Explanation)"). Position the label clearly, preferably centered within or directly below the shape/block. Ensure the shape/block is large enough to fit the text with padding.
6.  **Events/Plot Points:** Use distinct `text` blocks or shapes (like rectangles or circles) with associated text labels.
    * **Labels:** Use a `text` tool call describing the event clearly (e.g., "Event: Key Moment", "Plot Point: Turning Point"). Position the label clearly, preferably centered within or directly below the shape/block. Ensure the shape's size is large enough to fit the text with padding.

**Representing Relationships and Actions (Follow STRICTLY):**

* **Visuals:** Use `arrow` or `line` tools to show connections between **ANY** relevant entities (Character to Character, Character to Location, Character to Object, Character to Concept, Event to Event, etc.).
    * Use **`line`** for non-directional, peer relationships such as **Siblings, Spouses, or Couples**. Prioritize a horizontal layout for these peer relationships whenever sufficient horizontal space is available on the canvas. Only use vertical lines if horizontal space is constrained and a vertical arrangement is necessary for clarity. The length of the line MUST be sufficient to allow its text label to be placed near the midpoint without overlapping the connected shapes.
    * Use **`arrow`** for directional relationships like **Parent -> Child**, actions, cause/effect, or flow. The arrow direction MUST be logical. The length of the arrow MUST be sufficient to allow its text label to be placed near the midpoint without overlapping the connected shapes.
* **Labels:** Add a *separate* `text` tool call for the label. Calculate the exact midpoint (mid_x, mid_y) of the connector (line or arrow).
    * **For horizontal or near-horizontal connectors (size.height is small relative to size.width):** Position the label's top-left corner (`position`) near this midpoint but slightly **above** it, precisely centered horizontally relative to the line segment. A good starting point is `{"x": mid_x - (label_width / 2), "y": mid_y - label_height - 5}`. Ensure `textAlignment` is 'center'. Ensure the text label's `size` is large enough to contain the text without clipping and does not overlap the connector line.
    * **For vertical or near-vertical connectors (size.width is small relative to size.height):** Position the label's top-left corner near the midpoint but slightly to the **right** of the connector, precisely centered vertically relative to the line segment. A good starting point is `{"x": mid_x + 5, "y": mid_y - (label_height / 2)}`. Ensure `textAlignment` is 'center'. Ensure the text label's `size` is large enough to contain the text without clipping and does not overlap the connector line.
    * **For diagonal connectors:** Position the label near the midpoint, adjusting slightly to avoid overlapping the line. Ensure `textAlignment` is 'center'. Ensure the text label's `size` is large enough to contain the text without clipping and does not overlap the connector line.
    * Ensure relationship labels are specific and clearly describe the connection.

**Layout and Visual Structure (Follow STRICTLY):**

* **PRIORITIZE CLARITY AND READABILITY.** The diagram should be easy for a human to understand at a glance.
* Use proper positioning (avoid 0,0 coordinates) and ensure shapes and text are well within the 1200x1000 canvas with **AMPLE spacing** for readability. **AVOID OVERCROWDING AT ALL COSTS.** Leave significant margins around shapes and between connected elements.
* **Aim for a logical and readable layout** that visually represents the narrative structure, flow, or key connections.
    * **Group related elements logically:** Place family members near each other, locations in a distinct area, concepts perhaps centrally or influencing relevant entities.
    * **Consider flow:** If the story has a clear progression (e.g., chronological events), arrange elements to reflect this flow using arrows.
* Create clear visual hierarchy through positioning, shape types/sizes, and text formatting (bolding, font size).
* Ensure all elements are within the canvas bounds and **DO NOT overlap text labels with shapes or other text unless `canBeOverlapped` is set to `true` for the text element and the overlap is intentional and doesn't hinder readability.** Relationship labels must NOT obscure the lines/arrows they describe.

Use the following tools and adhere strictly to the specified JSON format for each tool in your response.

Available Tools and **EXACT** Output Format:

1.  **rectangle**: Represents characters, groups, locations, or objects.
    ```json
    {
      "tool": "rectangle",
      "params": {
        "position": {"x": number, "y": number},
        "size": {"width": number, "height": number},
        "color": 4278190080,
        "strokeWidth": 2,
        "rotation": 0.0,
        "strokeType": "solid",
        "canBeOverlapped": boolean
      }
    }
    ```

2.  **circle**: Represents characters, objects, or concepts.
    ```json
    {
      "tool": "circle",
      "params": {
        "position": {"x": number, "y": number},
        "size": {"width": number, "height": number},
        "color": 4278190080,
        "strokeWidth": 2,
        "rotation": 0.0,
        "strokeType": "solid",
        "canBeOverlapped": boolean,
        "controlPoint": {"x": number, "y": number}
      }
    }
    ```

3.  **arrow**: Shows relationships, actions, flow. Label with a SEPARATE 'text' tool (See Rules on Relationships/Actions).
    ```json
    {
      "tool": "arrow",
      "params": {
        "position": {"x": number, "y": number},
        "size": {"width": number, "height": number},
        "color": 4278190080,
        "strokeWidth": 2,
        "rotation": 0.0,
        "strokeType": "solid",
        "canBeOverlapped": true,
        "controlPoint": {"x": number, "y": number}
      }
    }
    ```

4.  **line**: Shows connections (siblings, spouses). Label with a SEPARATE 'text' tool (See Rules on Relationships/Actions).
    ```json
    {
      "tool": "line",
      "params": {
        "position": {"x": number, "y": number},
        "size": {"width": number, "height": number},
        "color": 4278190080,
        "strokeWidth": 2,
        "rotation": 0.0,
        "strokeType": "solid",
        "canBeOverlapped": true,
        "controlPoint": {"x": number, "y": number}
      }
    }
    ```

5.  **triangle**: Represents concepts or markers.
    ```json
    {
      "tool": "triangle",
      "params": {
        "position": {"x": number, "y": number},
        "size": {"width": number, "height": number},
        "color": 4278190080,
        "strokeWidth": 2,
        "rotation": 0.0,
        "strokeType": "solid",
        "canBeOverlapped": boolean
      }
    }
    ```

6.  **star**: Represents concepts or markers.
    ```json
    {
      "tool": "star",
      "params": {
        "position": {"x": number, "y": number},
        "size": {"width": number, "height": number},
        "color": 4278190080,
        "strokeWidth": 2,
        "rotation": 0.0,
        "strokeType": "solid",
        "canBeOverlapped": boolean
      }
    }
    ```

7.  **text**: Used for ALL labels and annotations.
    ```json
    {
      "tool": "text",
      "params": {
        "position": {"x": number, "y": number},
        "size": {"width": number, "height": number},
        "color": 4278190080,
        "strokeWidth": 1,
        "rotation": 0.0,
        "strokeType": "solid",
        "canBeOverlapped": false,
        "text": string,
        "fontSize": number,
        "fontFamily": "Roboto",
        "isBold": boolean,
        "isItalic": boolean,
        "isStrikethrough": boolean,
        "textAlignment": "left" | "center" | "right",
        "isFixedWidth": true
      }
    }
    ```

8.  **image**: To include images (less common).
    ```json
    {
      "tool": "image",
      "params": {
        "position": {"x": number, "y": number},
        "size": {"width": number, "height": number},
        "color": 4278190080,
        "strokeWidth": 1,
        "rotation": 0.0,
        "strokeType": "solid",
        "canBeOverlapped": false,
        "maintainAspectRatio": boolean,
        "imageSource": {
          "sourceType": "network",
          "url": string,
          "imageName": string
        },
        "imageName": string
      }
    }
    ```

RESPOND ONLY WITH A VALID JSON OBJECT containing a "tools" list. Ensure all keys and string values are enclosed in double quotes.

Example response structure (illustrating improved layout):
```json
{
    "tools": [
        {
            "tool": "rectangle",
            "params": {
                "position": {"x": 100, "y": 100},
                "size": {"width": 200, "height": 70}, // Increased size for text + padding
                "color": 4278190080,
                "strokeWidth": 2,
                "rotation": 0.0,
                "strokeType": "solid",
                "canBeOverlapped": true
            }
        },
        {
            "tool": "text",
            "params": {
                "position": {"x": 110, "y": 115}, // Positioned to be centered within the larger rectangle
                "size": {"width": 180, "height": 40}, // Size for the text content
                "color": 4278190080,
                "strokeWidth": 1,
                "rotation": 0.0,
                "strokeType": "solid",
                "canBeOverlapped": false,
                "text": "Protagonist Name\\n(Key Role/Trait)",
                "fontSize": 14,
                "fontFamily": "Roboto",
                "isBold": true,
                "isItalic": false,
                "isStrikethrough": false,
                "textAlignment": "center", // Ensure text is centered
                "isFixedWidth": true
            }
        },
        {
            "tool": "rectangle",
            "params": {
                "position": {"x": 400, "y": 100}, // Sufficient horizontal space from the first shape
                "size": {"width": 200, "height": 70}, // Consistent size
                "color": 4278190080,
                "strokeWidth": 2,
                "rotation": 0.0,
                "strokeType": "solid",
                "canBeOverlapped": true
            }
        },
        {
           "tool": "text",
           "params": {
             "position": {"x": 410, "y": 125}, // Positioned to be centered within the rectangle
             "size": {"width": 180, "height": 30},
             "color": 4278190080, "strokeWidth": 1, "rotation": 0.0, "strokeType": "solid", "canBeOverlapped": false,
             "text": "Antagonist Name",
             "fontSize": 16, "fontFamily": "Roboto", "isBold": false, "isItalic": false, isStrikethrough: false, "textAlignment": "center", "isFixedWidth": true
           }
         },
        {
            "tool": "line",
            "params": {
                "position": {"x": 300, "y": 135 }, // Start point (right edge of first shape)
                "size": {"width": 100, "height": 0}, // Vector to second shape's left edge
                "color": 4278190080, "strokeWidth": 2, "rotation": 0.0, "strokeType": "solid", "canBeOverlapped": true
            }
        },
        // Label for the line (Positioned centered *above* the line's midpoint, with sufficient height for text)
        {
            "tool": "text",
            "params": {
                # Line Midpoint approx: x = 300 + 100/2 = 350, y = 135 + 0/2 = 135
                # Label Position (80x20): x = mid_x - width/2 = 350 - 40 = 310
                #                        y = mid_y - height - 5 = 135 - 20 - 5 = 110
                "position": {"x": 310, "y": 110},
                "size": {"width": 80, "height": 20},
                "color": 4278190080, "strokeWidth": 1, "rotation": 0.0, "strokeType": "solid", "canBeOverlapped": false,
                "text": "Relationship",
                "fontSize": 12, "fontFamily": "Roboto", "isBold": false, "isItalic": false, isStrikethrough: false, "textAlignment": "center", "isFixedWidth": true
            }
        }
    ]
}
```

Important:
1.  ALWAYS identify and include ALL relevant entities from the story analysis: characters, groups, locations, key objects, and abstract concepts.
2.  ALWAYS add descriptive text labels for every entity and relationship, including relevant details from the story analysis such as roles, key traits, conditions, or context. Use separate 'text' tool calls. For shapes, position text labels **precisely centered** inside the shape, ensuring the shape is large enough. For connectors, position labels clearly near the midpoint. Use line breaks (`\\n`) within text tool's `text` parameter for multi-line labels.
3.  Use proper positioning (avoid 0,0 coordinates) and ensure shapes and text are well within the 1200x1000 canvas with **AMPLE spacing** for readability. **AVOID OVERCROWDING AT ALL COSTS.** Leave significant margins around shapes and between connected elements.
4.  Prioritize a logical and readable layout. Group related elements. Consider flow or hierarchy.
5.  Create clear visual hierarchy through positioning, shape types/sizes, and text formatting (bolding, font size).
6.  Show relationships and actions with properly positioned arrows and explicit text labels (using separate 'text' tool calls) that describe the nature and direction of the connection or event (e.g., "Parent of", "Acts on", "Connected to", "Causes"). Ensure relationships involve all relevant parties.
7.  Include additional text elements for important details, feelings, events, or themes not directly tied to a single entity or relationship.
8.  RESPOND ONLY WITH THE JSON OBJECT, NO OTHER TEXT.
9.  For `arrow` and `line` tools, `position` is the start point and `size` is the vector to the end point. For example, to draw a horizontal line from (100, 100) to (300, 100), the position would be {"x": 100, "y": 100} and size would be {"width": 200, "height": 0}.
10. For `circle`, `rectangle`, `triangle`, `star`, `text`, and `image` tools, `position` is the top-left corner and `size` is the width and height."""


# def create_diagram(story_text: str, prompt: str, openai_api_key: str) -> Dict[str, Any]:
#     agent = DiagramAgent(openai_api_key)
#     agent.analyze_story(story_text)
#     return agent.generate_diagram_from_analysis(prompt)

def create_diagram(story_text: str, prompt: str, api_config: Dict[str, Any]) -> Dict[str, Any]:
    agent = DiagramAgent(api_config) # Pass the configuration dictionary
    agent.analyze_story(story_text)
    return agent.generate_diagram_from_analysis(prompt)