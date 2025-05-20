# script_agent.py
# This is the main agent for generating movie script outlines.
# It uses the research_module as a tool.

import os
import json
import litellm # Ensure this is imported
from smolagents import ToolCollection, CodeAgent, Tool, LiteLLMModel, LogLevel
from dotenv import load_dotenv # Import load_dotenv
import time # Import time for dynamic filename

# --- Load environment variables from .env file FIRST ---
# This is crucial to ensure API keys are available for LiteLLM and other configurations
load_dotenv()
# --- DEBUG PRINT: Check the loaded API key ---
print(f"DEBUG: script_agent.py - ANTHROPIC_API_KEY loaded: {os.environ.get('ANTHROPIC_API_KEY')}")
# --- END DEBUG PRINT ---


# --- Import the research function from research_module.py ---
# Ensure research_module.py is in the same directory or accessible in the Python path
try:
    # When research_module is imported, its top-level code runs,
    # including its own load_dotenv() call.
    from research_module import conduct_research_query
    print("Successfully imported conduct_research_query from research_module.")
except ImportError:
    print("Error: Could not import conduct_research_query from research_module.")
    print("Please ensure research_module.py is in the same directory.")
    # Set to None if import fails so the rest of the script can still load
    conduct_research_query = None


# --- Initialize LiteLLM Model for the Script Agent ---
# Using Claude 3.5 Sonnet, optimized for creative tasks
# LiteLLMModel should pick up the ANTHROPIC_API_KEY from the environment
script_model = LiteLLMModel(model_id="claude-3-5-sonnet-20240620", num_retries=3)

# --- Define Internal Tools for Script Generation ---

class PlotOutlineTool(Tool):
    name = "plot_outline_generator"
    description = """
    Generates a detailed plot outline based on a story concept.
    Input should be a string describing the core story idea.
    Output is a structured plot outline including setup, rising action, climax, falling action, and resolution.
    """
    inputs = {"story_concept": {"type": "string", "description": "The core idea or summary of the story."}}
    output_type = "string"

    def forward(self, story_concept: str):
        # This tool would ideally use the LLM to generate a structured outline.
        # For demonstration, we'll simulate a response or make a simple LLM call.
        print(f"--- Script Agent: Generating plot outline for: {story_concept} ---")
        # In a real scenario, you'd make an LLM call here:
        # outline_prompt = f"Create a detailed movie plot outline for the story: {story_concept}"
        # outline = script_model.run(outline_prompt) # Example LLM call
        simulated_outline = f"""
        Plot Outline for "{story_concept[:50]}...":
        1. Setup: Introduce characters and world.
        2. Inciting Incident: The event that kicks off the main plot.
        3. Rising Action: Conflicts and challenges escalate.
        4. Climax: The peak of the conflict.
        5. Falling Action: Events after the climax.
        6. Resolution: The conclusion of the story.
        """
        print("--- Script Agent: Plot outline generated. ---")
        return simulated_outline

class CharacterDevelopmentTool(Tool):
    name = "character_developer"
    description = """
    Develops detailed character profiles including backstory, motivations, personality traits, and potential arcs.
    Input should include character name, role in the story, and overall story context.
    Output is a detailed character profile.
    """
    inputs = {
        "character_name": {"type": "string", "description": "The name of the character."},
        "role": {"type": "string", "description": "The character's role (e.g., protagonist, antagonist, sidekick)."},
        "story_context": {"type": "string", "description": "A brief summary of the story the character is in."}
    }
    output_type = "string"

    def forward(self, character_name: str, role: str, story_context: str):
        # This tool would also use the LLM to generate a character profile.
        print(f"--- Script Agent: Developing character profile for {character_name} ({role}) ---")
        # profile_prompt = f"Create a detailed profile for a character named {character_name} who is the {role} in a story about: {story_context}"
        # profile = script_model.run(profile_prompt) # Example LLM call
        simulated_profile = f"""
        Character Profile: {character_name}
        Role: {role}
        Story Context: {story_context[:50]}...
        Backstory: [Generated backstory]
        Motivations: [Generated motivations]
        Personality: [Generated traits]
        Arc: [Potential character arc]
        """
        print(f"--- Script Agent: Profile generated for {character_name}. ---")
        return simulated_profile

# --- Integrate the Research Agent as a Tool ---
# This tool wraps the conduct_research_query function from research_module.py
class ResearchAgentTool(Tool):
    name = "research_tool"
    description = """
    This tool leverages a dedicated research agent to find information on any given query.
    Useful for historical facts, scientific concepts, cultural details, geographical information, etc.
    Input should be a clear research question as a string.
    Output is a comprehensive research report string.
    """
    inputs = {"query": {"type": "string", "description": "The research question to answer."}}
    output_type = "string"

    def forward(self, query: str):
        if conduct_research_query:
            # Call the function from research_module.py
            return conduct_research_query(query)
        else:
            return "Research module not loaded. Cannot perform research."


# --- Initialize the Script Agent with all tools ---
all_script_tools = [
    PlotOutlineTool(),
    CharacterDevelopmentTool(),
    ResearchAgentTool() # Add the research tool here
    # You can add more tools as needed, e.g., DialogueTool, SceneDescriptionTool
]

# Only initialize the agent if the research module was imported successfully,
# or if you want the agent to run even without the research tool.
# If you want the script to fail hard if research_module doesn't load,
# remove the `if conduct_research_query:` check around the agent initialization.
if conduct_research_query is not None:
    script_agent = CodeAgent(
        tools=all_script_tools, # Pass the collected tools
        model=script_model,
        add_base_tools=True, # Includes basic tools like write_file (if available)
        verbosity_level=LogLevel.DEBUG # Keep DEBUG for now to see tool usage
    )
else:
    script_agent = None
    print("Script Agent not initialized due to research module import failure.")


def generate_movie_script(sample_story: str):
    """
    Runs the script agent to generate a movie script outline based on a sample story.
    The output will be in Hindi, following a specific screenplay format.
    """
    if script_agent is None:
        print("Cannot generate script: Script Agent failed to initialize.")
        return

    print("\n--- Starting Movie Script Generation Process ---")
    prompt = f"""
    आप एक पेशेवर फिल्म पटकथा लेखक हैं। आपका कार्य निम्नलिखित छोटी कहानी को एक विस्तृत फिल्म पटकथा रूपरेखा में विस्तारित करना है। रूपरेखा में मुख्य पात्र, सेटिंग्स, महत्वपूर्ण कथानक बिंदु और संभावित विषय शामिल होने चाहिए।

    कहानी का उदाहरण: "{sample_story}"

    यदि कहानी के किसी भी हिस्से में विशिष्ट तथ्यात्मक जानकारी (जैसे ऐतिहासिक विवरण, वैज्ञानिक अवधारणाएं, भौगोलिक डेटा, सांस्कृतिक संदर्भ) की आवश्यकता है, तो आपको उस जानकारी को इकट्ठा करने के लिए `research_tool` का उपयोग करना होगा, इससे पहले कि आप इसे पटकथा रूपरेखा में शामिल करें।

    निम्नलिखित चरणों का पालन करें:
    1. नमूना कहानी का विश्लेषण करें।
    2. एक उच्च-स्तरीय संरचना बनाने के लिए `plot_outline_generator` टूल का उपयोग करें।
    3. मुख्य पात्रों की पहचान करें और प्रत्येक के लिए `character_developer` टूल का उपयोग करें, उनकी भूमिका और कहानी का संदर्भ प्रदान करें।
    4. जैसे-जैसे आप कथानक और पात्रों का विकास करते हैं, उन क्षेत्रों की पहचान करें जहाँ तथ्यात्मक शोध की आवश्यकता है। आवश्यक जानकारी प्राप्त करने के लिए एक स्पष्ट प्रश्न के साथ `research_tool` का उपयोग करें। शोध निष्कर्षों को अपनी रूपरेखा में शामिल करें।
    5. सभी उत्पन्न रूपरेखाओं, चरित्र प्रोफाइल और शोध निष्कर्षों को एक एकल, व्यापक फिल्म पटकथा रूपरेखा में संश्लेषित करें।

    **अंतिम आउटपुट हिंदी भाषा में होना चाहिए और निम्नलिखित पटकथा प्रारूप का कड़ाई से पालन करना चाहिए:**

    **प्रारूप:**
    * दृश्य शीर्षक (Scene Heading) `EXT. <स्थान> - <समय>` या `INT. <स्थान> - <समय>` (उदाहरण: `EXT. सबवे स्टेशन - शाम`)
    * दृश्य विवरण (Action/Description) सामान्य पैराग्राफ में।
    * पात्र का नाम (Character Name) बड़े अक्षरों में, केंद्र में।
    * कोष्ठक में भाव/निर्देश (Parenthetical) जैसे `(स्वयं से)`, `(हंसते हुए)`।
    * संवाद (Dialogue) सामान्य पैराग्राफ में।

    **उदाहरण आउटपुट प्रारूप (जैसा आपने प्रदान किया है):**
    ```
    EXT. सबवे स्टेशन - शाम
    यात्रियों की भीड़ के बीच, राहगीर जल्दी से आते-जाते हैं। लेओनार्ड (65), एक सेवानिवृत्त वायलिनिस्ट, थका हुआ और उदास, धीरे-धीरे सीढ़ियों से उतरता है।
    अचानक, सुरीली वायलिन की आवाज़ उसके कानों में पड़ती है। वह रुक जाता है, उसके चेहरे पर आश्चर्य।
    लेओनार्ड
    (स्वयं से)
    ये... ये पगानिनी का कैप्रिस नंबर 24 है... लेकिन इतना अद्भुत...
    वह आवाज़ की दिशा में मुड़ता है।
    एक कोने में, एम्मा (16), एक किशोरी, पुरानी वायलिन पर अद्भुत संगीत बजा रही है। उसके पैरों के पास एक खाली टोपी है जिसमें कुछ सिक्के हैं।
    लेओनार्ड धीरे-धीरे उसके पास जाता है, मंत्रमुग्ध।
    ```

    **आपका FINAL AND ONLY OUTPUT MUST BE a Python code block using the `final_answer` function.**
    The code block should strictly follow this format:
    ```py
    # Thought: [Your concise thought process leading to the final script outline.]
    final_answer("[Your comprehensive movie script outline here, including character profiles, plot points, setting details, and incorporated research findings, ALL IN HINDI AND FOLLOWING THE SPECIFIED FORMAT.]")
    ```<end_code>
    सुनिश्चित करें कि `final_answer` तर्क में मूल क्वेरी के लिए प्रासंगिक, पूर्ण, अच्छी तरह से संरचित शोध निष्कर्ष शामिल हैं।
    """
    try:
        # Run the script agent with the detailed prompt
        # The output will be the content passed to final_answer
        final_script_outline_content = script_agent.run(prompt)

        print("\n--- Agent's Final Movie Script Outline ---")
        print(final_script_outline_content)

        # --- Save the captured content to a file using standard Python ---
        # Generate a dynamic filename based on timestamp
        timestamp = int(time.time())
        output_filename = f"movie_script_outline_hindi_{timestamp}.txt" # Changed filename for Hindi output
        output_filepath = os.path.join(os.getcwd(), output_filename) # Path in the current directory

        try:
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(final_script_outline_content)
            print(f"Script outline successfully saved to: {output_filepath}")
        except IOError as e:
            print(f"Error saving script outline to file {output_filepath}: {e}")


    except Exception as e:
        print(f"\nAn error occurred during script generation: {e}")
        print("Please review the agent's thoughts and execution for debugging.")

# --- Main execution block ---
if __name__ == "__main__":
    user_story_prompt = input("Enter a small sample story/idea for the movie script (in English or Hindi): ")
    if user_story_prompt:
        generate_movie_script(user_story_prompt)
    else:
        print("No story prompt entered. Exiting.")
