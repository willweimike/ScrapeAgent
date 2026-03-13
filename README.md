# ScrapeAgent - Multi-Engine AI Search Agent

A search assistant that orchestrates multiple search tools (Google, Bing, Perplexity, Reddit, Tavily, and DuckDuckGo) to deliver thorough and cited answers.

## Demo


https://github.com/user-attachments/assets/9934fef7-50d4-4ca8-959d-bccbe964675f




## Features

* **Diverse Search Toolset**: Integrates 6 distinct search capabilities:
* **Intelligent Orchestration**: Uses a **ReAct agent** strategy to decide which tools to use and how to aggregate the information.
* **Stateful Workflow**: Built on **LangGraph**, allowing for structured execution and easy expansion of the agent's logic.
* **Local LLM Support**: Configured to run with `ChatOllama` using the `qwen3:8b` model for privacy and local processing.
* **Automatic Summarization**: The agent is prompted to summarize all gathered data and provide a clear list of source links.

## 🛠️ Tech Stack

* **Frameworks**: LangChain, LangGraph
* **LLM**: Ollama (Qwen3 8B)
* **APIs**: BrightData, Tavily, DuckDuckGo (via `ddgs`)

## ⚙️ Setup

1. **Clone the repository** and navigate to the project directory.
2. **Install dependencies**:
```bash
pip install langchain langchain-ollama langgraph tavily-python ddgs requests python-dotenv

```

3. **Configure Environment Variables**: Create a `.env` file in the root directory and add your credentials:
```env
BRIGHTDATA_API_KEY=your_brightdata_key
BRIGHTDATA_SERP_ZONE=your_serp_zone
BRIGHTDATA_PERPLEXITY_DATASET_ID=your_perplexity_dataset_id
TAVILY_KEY=your_tavily_key

```

## 🕹️ Usage

Run the agent directly from your terminal:

```bash
python run.py

```

Once prompted with `Query>`, enter your research question. The agent will print its progress as it triggers different tools and finally output a summarized response with all source links included.
