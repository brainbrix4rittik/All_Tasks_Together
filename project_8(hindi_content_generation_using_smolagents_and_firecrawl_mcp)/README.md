# Movie Script Generation Agent
![Alt text for your image](https://github.com/brainbrix4rittik/All_Tasks_Together/blob/main/project_8(hindi_content_generation_using_smolagents_and_firecrawl_mcp)/git_image.png)
This project implements a multi-agent system using **smolagents** to generate detailed movie script outlines from a brief story idea. It leverages a dedicated research agent as a tool to gather factual information, ensuring the generated content is well-informed and accurate. The project is designed for extensibility and uses **uv** for dependency management and **Firecrawl MCP** for advanced web research.

---

## Features

- **Story Expansion**: Takes a short story concept and expands it into a comprehensive movie script outline.
- **Modular Agent Design**: Utilizes two specialized agents:
  - **Script Agent**: Orchestrates the scriptwriting process, handling plot, characters, and overall structure.
  - **Research Agent**: Acts as a tool for the Script Agent to perform web searches and browsing for factual information.
- **External Knowledge Integration**: Dynamically fetches relevant information (historical context, scientific concepts, cultural details) using the integrated research capabilities.
- **Output Generation**: Produces a structured script outline as a text file in Hindi, following professional screenplay formatting.
- **Configurable LLM**: Uses LiteLLM for flexible integration with various Large Language Models (defaulting to Anthropic's Claude 3.5 Sonnet).
- **Firecrawl MCP Integration**: Utilizes Firecrawl for advanced web browsing capabilities within the research agent.

---

## Project Structure

```
hindi_content_generation/
├── .env
├── browse_mcp.json
├── research_module.py
├── script_agent.py
├── requirements.txt
└── movie_script_outline_hindi_*.txt
```

- **.env**: Stores environment variables, primarily your Anthropic API key.
- **browse_mcp.json**: Configuration file for the Firecrawl MCP (Multi-Agent Communication Protocol) server.
- **research_module.py**: Contains the `conduct_research_query` function, which encapsulates the logic of the research agent. This file is imported and used as a tool by `script_agent.py`.
- **script_agent.py**: The main script. It defines the Movie Script Generation Agent, its internal tools, and integrates the research_module as an external tool.
- **requirements.txt**: Lists all Python dependencies required for the project.
- **movie_script_outline_hindi_*.txt**: Output files containing generated Hindi script outlines.

---

## Setup

### 1. Clone the Repository (or create the files)
If you haven't already, ensure you have the project structure as described above with all the files.

### 2. Install Dependencies

This project uses **uv** for fast and reliable dependency management. If you don't have `uv` installed, you can get it from [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv) or via pip:

```
pip install uv
```

Then, install the dependencies:

```
uv pip install -r requirements.txt
```

#### Using a Virtual Environment with uv

It is recommended to use a virtual environment for project isolation. You can create and activate a virtual environment using uv as follows:

1. **Create a virtual environment:**
   ```
   uv venv
   ```
   This will create a `.venv` directory in your project.

2. **Activate the virtual environment:**
   - On Windows:
     ```
     .\.venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```

3. **Install packages using uv add:**
   To add a new package to your environment and requirements file, use:
   ```
   uv add package_name
   ```
   This will install the package and update your `requirements.txt` automatically.

---

### 3. Configure Environment Variables

Create a `.env` file in the root of your project directory (if it doesn't exist) and add your Anthropic API key.

**.env example:**
```
# .env
ANTHROPIC_API_KEY="sk-ant-YOUR_ACTUAL_ANTHROPIC_API_KEY_HERE"

# Firecrawl API key is also configured in browse_mcp.json,
# but can be set here if you prefer to manage it via .env
# FIRECRAWL_API_KEY="fc-YOUR_FIRECRAWL_API_KEY_HERE"
```

> **Important:** Replace `sk-ant-YOUR_ACTUAL_ANTHROPIC_API_KEY_HERE` with your real Anthropic API key. This key is crucial for the LLM to function.

### 4. Configure Firecrawl MCP

The `browse_mcp.json` file configures the Firecrawl server. Ensure it's present in the root directory. The `FIRECRAWL_API_KEY` within this JSON should also be valid if you intend to use Firecrawl's web browsing capabilities.

**browse_mcp.json example:**
```
{
    "mcpServers": {
      "firecrawl-mcp": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-0f60a3cabe8543a1880cc108b3509e2b"
      }
    }
    }
  }
```

---

## How to Run

1. Open your terminal or command prompt.
2. Navigate to the project directory:
   ```
   cd path/to/your/hindi_content_generation
   ```
3. Run the main script:
   ```
   python script_agent.py

   or

   uv run script_agent.py
   ```
4. The script will prompt you to "Enter a small sample story/idea for the movie script:". Type your story idea and press Enter.
5. The agent will then begin processing, printing its progress and tool usage to the console. Once completed, the generated movie script outline will be printed to the console and saved as a `.txt` file (e.g., `movie_script_outline_hindi_1678888888.txt`) in the same directory.

---

## How it Works

The project operates through a hierarchical agent system:

- **script_agent.py (Main Agent):**
  - Takes the user's story prompt.
  - Uses its internal tools (`plot_outline_generator`, `character_developer`) to structure the script and develop characters.
  - When it identifies a need for external factual information (e.g., historical details, scientific accuracy), it calls the `research_tool`.

- **research_module.py (Research Tool/Agent):**
  - The `research_tool` in `script_agent.py` is a wrapper around the `conduct_research_query` function from `research_module.py`.
  - When invoked, `conduct_research_query` initializes its own CodeAgent instance.
  - This research agent is equipped with web search (via smolagents base tools) and web browsing (via Firecrawl) capabilities.
  - It performs the requested research and returns a summarized report to the `script_agent.py`.

- **Integration:** The `script_agent.py` then incorporates the research findings back into the evolving movie script outline, creating a richer and more accurate narrative.

This modular approach allows for clear separation of concerns, making the system more robust and extensible.

---

## Potential Improvements

- **More Sophisticated Internal Tools:** Develop more specialized tools within `script_agent.py` for dialogue generation, scene formatting, genre-specific writing, etc.
- **Iterative Refinement:** Implement a feedback loop where the agent can refine its script outline based on additional prompts or critiques.
- **Multi-turn Conversation:** Allow for a more conversational interaction with the user to guide the script generation process.
- **Advanced Research Queries:** Enhance the `research_tool` to handle more complex research needs or to perform multi-step research.
- **Output Format:** Explore generating the script in industry-standard formats (e.g., Fountain, Celtx-compatible).
- **Error Handling and Resilience:** Add more specific error handling for API calls and tool executions to make the agent more robust.

---

## Sample Input & Output

Below is a sample output generated by the system (from sample input: `The train doors slid open with a hiss. Aarav hesitated, foot hovering over the gap. “Come on,” Meera called from inside, clutching the pole. He stepped in just as the doors closed. “I almost stayed.” Meera raised an eyebrow. “But you didn’t.” Aarav smiled faintly, eyes on the fading platform. “Yeah. I didn’t.`):

Sample Output:
```
EXT. मुंबई मेट्रो स्टेशन - शाम

शाम के धुंधलके में, मुंबई मेट्रो स्टेशन पर भीड़ उमड़ रही है। यात्री अपने-अपने गंतव्यों की ओर भाग रहे हैं। प्लेटफॉर्म पर, आरव (28), एक युवा सॉफ्टवेयर इंजीनियर, अपने बैग को कसकर पकड़े हुए, चिंतित नज़रों से ट्रेन को देख रहा है।

INT. मेट्रो ट्रेन - शाम

ट्रेन के अंदर, मीरा (26), एक आत्मविश्वास से भरी पत्रकार, खड़ी है। वह खिड़की से बाहर देखती है और आरव को देखती है।

मीरा
(चिल्लाकर)
आरव! जल्दी करो!

EXT. मुंबई मेट्रो स्टेशन - शाम

आरव सुनता है, लेकिन हिचकिचाता है। उसके चेहरे पर संघर्ष की भावना है।

आरव
(स्वयं से)
क्या मैं सच में ये कर सकता हूँ?

अचानक, ट्रेन की सीटी बजती है। दरवाज़े बंद होने लगते हैं।

INT. मेट्रो ट्रेन - शाम

मीरा चिंतित होकर देखती है।

मीरा
(चिल्लाकर)
आरव! अब या कभी नहीं!

EXT. मुंबई मेट्रो स्टेशन - शाम

आरव गहरी साँस लेता है और एक क्षण में निर्णय लेता है। वह दौड़ता है और ठीक वक्त पर ट्रेन में कूद जाता है।

INT. मेट्रो ट्रेन - शाम

दरवाज़े बंद हो जाते हैं। आरव हाँफता हुआ खड़ा है, मीरा उसे देखकर मुस्कुराती है।

मीरा
तुमने कर दिखाया।

आरव
(हल्की मुस्कान के साथ)
हाँ, मैंने कर दिया।

ट्रेन चलने लगती है, प्लेटफॉर्म पीछे छूटता जाता है।

आरव
(गंभीरता से)
मैं लगभग रुक गया था।

मीरा
(आँख मारते हुए)
लेकिन तुम रुके नहीं।

आरव मुस्कुराता है, उसकी आँखों में एक नया उत्साह है।

आरव
नई शुरुआत की ओर।

मीरा सहमति में सिर हिलाती है। ट्रेन तेज़ी से आगे बढ़ती है, शहर की रोशनी खिड़कियों से झलकती है।

MONTAGE - आरव और मीरा का सफर

-- आरव और मीरा एक स्टार्टअप ऑफिस में काम करते हुए
-- दोनों मुंबई की गलियों में घूमते हुए
-- समुद्र तट पर शाम को बातें करते हुए
-- एक छोटे से अपार्टमेंट में योजनाएँ बनाते हुए

INT. मेट्रो ट्रेन - एक साल बाद - शाम

आरव और मीरा फिर से उसी ट्रेन में हैं, लेकिन इस बार दोनों साथ में खड़े हैं, हाथों में सफलता के प्रमाणपत्र।

आरव
(मुस्कुराते हुए)
याद है, एक साल पहले?

मीरा
(प्यार से)
हाँ, जब तुमने अपने डर को हराया।

वे एक-दूसरे की ओर देखते हैं, उनकी आँखों में भविष्य के लिए उम्मीद और प्यार झलकता है।

FADE OUT.

THE END

पात्र प्रोफाइल:

1. आरव (28):
   - एक प्रतिभाशाली सॉफ्टवेयर इंजीनियर
   - स्वभाव: संकोची, आत्म-संदेह से भरा, लेकिन अंदर से महत्वाकांक्षी
   - पृष्ठभूमि: मध्यमवर्गीय परिवार से, हमेशा सुरक्षित विकल्प चुनता रहा
   - लक्ष्य: अपने comfort zone से बाहर निकलना और अपने सपनों को पूरा करना
   - विकास: डर और अनिश्चितता से लड़ना सीखता है

2. मीरा (26):
   - एक उत्साही और आत्मविश्वासी पत्रकार
   - स्वभाव: साहसी, प्रेरक, जीवन को पूरी तरह से जीने वाली
   - पृष्ठभूमि: छोटे शहर से मुंबई आई, अपने दम पर सफलता हासिल की
   - लक्ष्य: अपनी कहानियों के माध्यम से दुनिया को बदलना
   - भूमिका: आरव के लिए प्रेरणा और सहयोगी

कथानक बिंदु:
1. आरव का निर्णय लेने का क्षण: ट्रेन में कूदना या पीछे रह जाना
2. नए शहर और नए अवसरों की खोज
3. स्टार्टअप की शुरुआत और उसकी चुनौतियाँ
4. आरव और मीरा के बीच रोमांस का विकास
5. व्यक्तिगत और पेशेवर चुनौतियों का सामना करना
6. सफलता की ओर बढ़ना और अपने लक्ष्यों को प्राप्त करना

थीम:
- परिवर्तन का साहस
- आत्म-खोज और विकास
- प्यार और सहयोग की शक्ति
- सपनों को पूरा करने के लिए comfort zone से बाहर निकलना

सेटिंग विवरण:
मुंबई मेट्रो सिस्टम: आधुनिक, तेज़, और व्यस्त। यह शहर की धड़कन है, जो लाखों लोगों को जोड़ती है। मेट्रो ट्रेनें स्वचालित दरवाज़ों, एयर-कंडीशनिंग, और डिजिटल डिस्प्ले के साथ अत्याधुनिक हैं। स्टेशन व्यस्त हैं, विभिन्न सामाजिक-आर्थिक पृष्ठभूमि के लोगों से भरे हुए, जो शहर के तेज़ जीवन को दर्शाते हैं।

यह कहानी आधुनिक भारत के युवाओं के सपनों, आकांक्षाओं और चुनौतियों को दर्शाती है, जहाँ पारंपरिक मूल्य और आधुनिक महत्वाकांक्षाएँ एक साथ चलती हैं।
```

---

## License

This project is for educational and research purposes. Please check the terms of use for any third-party APIs or models you use with this code.
