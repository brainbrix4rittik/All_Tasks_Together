# research_module.py
# This file contains the core logic of the research agent, refactored into a function
# so it can be imported and used as a tool by other agents.

import os
import json
import litellm # Ensure this is imported
from smolagents import ToolCollection, CodeAgent, Tool, LiteLLMModel, LogLevel
from mcp import StdioServerParameters
from dotenv import load_dotenv # Import load_dotenv
import time # Import time for dynamic filename

# --- Load environment variables from .env file FIRST ---
# This is crucial to ensure API keys are available when the module is imported
load_dotenv()
# --- DEBUG PRINT: Check the loaded API key ---
print(f"DEBUG: research_module.py - ANTHROPIC_API_KEY loaded: {os.environ.get('ANTHROPIC_API_KEY')}")
# --- END DEBUG PRINT ---


# --- Load Firecrawl MCP Configuration ---
# This setup is the same as your original research_agent.py
use_firecrawl = False
firecrawl_tool_collection = None
try:
    with open('browse_mcp.json', 'r') as f:
        mcp_config = json.load(f)

    firecrawl_mcp_params = mcp_config["mcpServers"]["firecrawl-mcp"]

    firecrawl_server_parameters = StdioServerParameters(
        command=firecrawl_mcp_params["command"],
        args=firecrawl_mcp_params["args"],
        env={**firecrawl_mcp_params["env"], **os.environ}, # Merge env vars
    )
    use_firecrawl = True

    # Use a context manager to ensure the MCP server is handled correctly
    # Added a broader exception catch here to diagnose potential issues during MCP setup
    try:
        with ToolCollection.from_mcp(firecrawl_server_parameters, trust_remote_code=True) as collection:
             firecrawl_tool_collection = collection # Assign the collection
        print("Research Module: Firecrawl ToolCollection initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firecrawl ToolCollection: {e}")
        print("Firecrawl browsing will not be available.")
        use_firecrawl = False
        firecrawl_tool_collection = None # Ensure it's None if initialization fails


except FileNotFoundError:
    print("Warning: browse_mcp.json not found. Firecrawl browsing will not be available in research module.")
    use_firecrawl = False
    # firecrawl_tool_collection remains None


# --- Custom Tool for Deeper Analysis (Same as your original) ---
class DataAnalysisTool(Tool):
    name = "data_analysis_tool"
    description = """
    This tool is used for in-depth analysis of provided textual data.
    It can extract key facts, identify trends, synthesize information, and summarize complex texts.
    Input should be a string of text to analyze.
    """
    inputs = {"text": {"type": "string", "description": "The text content to analyze."}}
    output_type = "string"

    def forward(self, text: str):
        if not text:
            return "No text provided for analysis."

        from collections import Counter
        # Basic analysis: find most common words and a simple summary
        words = [word.lower() for word in text.split() if word.isalnum() and len(word) > 3]
        most_common_words = [word for word, _ in Counter(words).most_common(10)]
        keywords = ", ".join(most_common_words)

        sentences = [s.strip() for s in text.split('.') if s.strip()]
        summary = " ".join(sentences[:min(5, len(sentences))]) # Take first 5 sentences as summary

        analysis_report = f"""
--- In-Depth Data Analysis Report ---
Original Text Snippet (first 200 chars): {text[:200]}...

Key Themes/Keywords: {keywords if keywords else "None found"}

Preliminary Summary: {summary if summary else "No comprehensive summary generated from snippet."}
------------------------------------
"""
        return analysis_report

# --- Core function to conduct research ---
def conduct_research_query(query: str) -> str:
    """
    Initializes and runs the research agent with the given query and returns the final report content.
    This function is designed to be called by other agents.
    """
    print(f"\n--- Research Module: Starting research for query: '{query}' ---")

    # Initialize the LiteLLM Model for this research task
    # Using the same model as before
    # LiteLLMModel should pick up the ANTHROPIC_API_KEY from the environment
    model = LiteLLMModel(model_id="claude-3-5-sonnet-20240620", num_retries=3)

    # Collect all tools for the research agent
    all_tools = [DataAnalysisTool()] # Start with the custom analysis tool
    # Only add Firecrawl tools if they were successfully initialized earlier
    if use_firecrawl and firecrawl_tool_collection:
        all_tools.extend(firecrawl_tool_collection.tools)
    else:
        print("Research Module: Firecrawl tools not available for agent instance.")


    # Initialize the CodeAgent instance for research
    research_agent_instance = CodeAgent(
        tools=all_tools, # Pass the collected tools
        model=model,
        add_base_tools=True, # Includes basic tools like web search (DuckDuckGo)
        verbosity_level=LogLevel.INFO # Set verbosity lower for tool calls
    )

    # Construct the prompt for the research agent instance
    # Instructing it to use final_answer to output the report content
    research_query_template = f"""
    Your primary goal is to conduct research on the following topic: "{query}"
    Identify key dates, prominent research institutions, and summarize the most promising approaches related to this topic.
    Utilize the provided tools (web search, web browsing) to gather necessary information.

    **After completing your research and compiling the full report, your FINAL AND ONLY OUTPUT MUST BE a Python code block using the `final_answer` function.**
    The code block should strictly follow this format:
    ```py
    # Thought: [Your concise thought process leading to the final answer.]
    final_answer("[Your comprehensive research report here]")
    ```<end_code>
    Ensure the `final_answer` argument contains the complete, well-structured research findings relevant to the original query.
    """

    try:
        # Run the research agent instance with the query
        # The output of agent.run() will be the content passed to final_answer
        final_report = research_agent_instance.run(research_query_template)
        print("--- Research Module: Research completed. ---")
        return final_report # Return the captured report content

    except Exception as e:
        print(f"\n--- Research Module: An error occurred during research: {e} ---")
        # Return an error message if research fails
        return f"Error during research: {e}"

# --- Standalone execution for testing ---
# This block allows you to run research_module.py directly for testing purposes
if __name__ == "__main__":
    print("--- Running Research Module in Standalone Test Mode ---")
    user_research_query = input("Enter your research query (for standalone test): ")
    report = conduct_research_query(user_research_query)
    print("\n--- Research Module Standalone Test Output ---")
    print(report)

    # Optionally save the standalone test report
    timestamp = int(time.time())
    output_filename = f"research_module_test_report_{timestamp}.txt"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Standalone test report saved to: {output_filename}")
    except IOError as e:
        print(f"Error saving standalone test report: {e}")
