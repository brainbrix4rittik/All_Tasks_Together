import os
import json
import sys # Import sys to read command line arguments
from dotenv import load_dotenv
from diagram_agent import create_diagram

def main():
    # Load environment variables
    load_dotenv(override=True)  # Add override=True to ensure .env values take precedence
    
    # Debug prints
    # print("Environment variables loaded:")
    # print(f"API_CHOICE from env: {os.getenv('API_CHOICE')}")
    # print(f"All env vars: {dict(os.environ)}")

    # Get API choice from command line first, then environment variable, default to Azure
    if len(sys.argv) > 1:
        api_choice = sys.argv[1].lower()  # Command line argument takes precedence
    else:
        api_choice = os.getenv('API_CHOICE')  # Fall back to environment variable

    if api_choice is None:
        api_choice = 'azure'  # Default to azure if neither is set
        print("No API_CHOICE environment variable or command line argument found. Defaulting to 'azure'.")

    api_choice = api_choice.strip().lower()  # Ensure it's lowercase and remove any whitespace

    print(f"Using API: {api_choice}")

    if api_choice == 'azure':
        # Get Azure OpenAI configuration
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'GPT4o')

        if not all([api_key, azure_endpoint]):
            print("Error: Required Azure OpenAI configuration not found in environment variables")
            print("Please ensure AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are set for Azure")
            return

        # Pass all relevant Azure parameters
        api_config = {
            "api_type": "azure",
            "api_key": api_key,
            "azure_endpoint": azure_endpoint,
            "deployment_name": deployment_name
        }

    elif api_choice == 'gemini':
        # Get Gemini configuration
        api_key = os.getenv('GEMINI_API_KEY')
        model_name = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.0-flash-latest')

        if not api_key:
            print("Error: Required Gemini API configuration not found in environment variables")
            print("Please ensure GEMINI_API_KEY is set for Gemini")
            return

        # Pass all relevant Gemini parameters
        api_config = {
            "api_type": "gemini",
            "api_key": api_key,
            "model_name": model_name
        }

    else:
        print(f"Error: Invalid API choice '{api_choice}'. Please choose 'azure' or 'gemini'.")
        return

    # Read story from file
    try:
        with open('my_story.txt', 'r', encoding='utf-8', errors='replace') as f:
            story_text = f.read()
    except FileNotFoundError:
         print("Error: my_story.txt not found. Please create this file with your story.")
         return
    except Exception as e:
        print(f"Error reading story file: {str(e)}")
        return

    # Create diagram
    try:
        diagram = create_diagram(
            story_text=story_text,
            prompt="Generate a diagram showing the main characters and their relationships (if relationship exists) in the story.",
            api_config=api_config
        )

        # Save diagram to file
        try:
            with open('diagram.json', 'w', encoding='utf-8') as f:
                json.dump(diagram, f, indent=2)

            # Verify the file was created and contains valid JSON
            try:
                with open('diagram.json', 'r', encoding='utf-8') as f:
                    json.load(f)  # Verify JSON is valid
                print("Diagram created successfully and saved to diagram.json")
                print(f"Diagram contains {len(diagram.get('shapes', []))} shapes")
            except json.JSONDecodeError:
                print("Error: Saved diagram.json contains invalid JSON")
            except Exception as e:
                print(f"Error verifying diagram.json: {str(e)}")

        except Exception as e:
            print(f"Error saving diagram to file: {str(e)}")

    except Exception as e:
        print(f"Error creating diagram: {str(e)}")

if __name__ == "__main__":
    main()