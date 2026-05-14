# Store Summary Architecture (Crew5Rag Setup)

Welcome to the Store Summary Architecture project, powered by [crewAI](https://crewai.com). This repository is specifically tailored to act as a multi-agent AI system for thorough startup idea validation, market research, competitor analysis, customer segmentation, product visualization, and business model generation. By harnessing RAG (Retrieval-Augmented Generation) and custom tooling, agents collaborate effectively, share context natively via a vector database, and produce comprehensive startup summary reports.

## What Does the Store Summary Architecture Do?

This architecture relies on robust collaboration between specialized AI agents. Each agent handles a key component of business intelligence generation:

1. **Market Research Analyst**: Establishes TAM/SAM/SOM, market growth trends, and opportunities using live internet searching.
2. **Competitor Research Specialist**: Finds direct/indirect competitors and highlights major market gaps.
3. **Customer Research Specialist**: Derives customer personas, pain points, and buyer behaviors by building upon the market and competitor research.
4. **Product Research Specialist**: Formulates MVP requirements, core features, tech stacks, and benchmarks.
5. **Business Analyst**: Synthesizes the generated context using a custom RAG (Retrieval-Augmented Generation) retrieval tool to produce a polished final business report.

The workflow explicitly utilizes a **Vector DB storage callback strategy**: rather than passing giant reports directly in context, agents write full reports, store them into `market_research_db/chroma.sqlite3`, and only pass 5-bullet summaries forward. Downstream agents use a custom RAG tool (`RAGRetrievalTool`) to pull relevant insights natively.

## Installation Tutorial

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

```bash
crewai install
```

### Customizing your Project

**Add your `OPENAI_API_KEY` and `SERPER_API_KEY` into the `.env` file since internet search tools and scraping tools (`SerperDevTool`, `SeleniumScrapingTool`) are used.**

- Modify `src/crew_5_rag/config/agents.yaml` to tweak agent behaviors, backstories, and goals.
- Modify `src/crew_5_rag/config/tasks.yaml` to change specific report requirements and targeted RAG queries.
- Modify `src/crew_5_rag/crew.py` to add your own custom logic, assign different tools from the `tool_kit`, or switch the callback mechanism.
- Modify `src/crew_5_rag/main.py` if you wish to adjust the `startup_idea` input that feeds the crew orchestration.

## Running the Store Summary Architecture

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
crewai run
```

This command initializes the Market Research Crew, assembling the agents and assigning them tasks as defined in your configuration. Wait for the terminal to print execution traces as agents perform live searches, store reports to ChromaDB, pull RAG context, and finally dump out `final_report_2.md`.

## Understanding the RAG and Tooling Flow

The Crew AI architecture relies upon:
* **`search_the_internet_with_serper`**: For live data.
* **`store_report_in_vector_db` / `make_store_callback`**: Enforces tight prompt boundaries. Full reports go to ChromaDB to avoid context-window limits.
* **`retrieve_from_research_reports`**: Allows downstream agents to intelligently search upstream outputs by topic (e.g. "customer pain points competitor gaps").

## Support

For support, questions, or feedback regarding the Crew5Rag Crew or crewAI:
- Visit the [crewAI documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/Sanket22g/store_summary_architecture-)

Let's validate startup ideas seamlessly with the power and simplicity of crewAI!

---

## 🏗️ Deep Dive: The Store Summary Architecture & RAG Tools Tutorial

If you are a CrewAI engineer, developer, or enthusiast wanting to understand the flow and architecture of this complex setup, this section breaks down **how the agents operate**, **how the custom RAG tools are built**, and **how to manage token limits** efficiently using the callback strategy.

### 1. The Core Problem: Token Window Exhaustion
When running sequentially, passing massive outputs from `market_researcher` to `competitor_researcher` to `customer_researcher` overloads the LLM context limits quickly. This architecture solves that by implementing a **Vector Database Strategy with 5-bullet summaries**.

### 2. The Solution: Custom Tooling (`custom_tool.py`)
We built two precise tools wrapped around `chromadb` and `cohere`:

#### Tool A: `store_report_in_vector_db`
- **What it does**: Once an agent finishes their comprehensive report, they pass it to this tool.
- **How it works**: The text is chunked using an overlapping split (500 tokens, 50 overlap). It generates UUIDs and assigns metadata based on the `agent_name`. It then saves this directly into a local Chroma SQLite database (`market_research_db`). 
- **The Magic**: Instead of the agent returning their huge report to the orchestrator, the tool accepts a `summary` argument and the agent returns ONLY a 5-bullet summary.

#### Tool B: `retrieve_from_research_reports`
- **What it does**: Allows downstream agents to intelligently retrieve the precise context they need.
- **How it works**: Uses `chromadb`'s semantic search to grab the top `K` most relevant chunks. Because base semantic search isn't perfect, it passes those results through **Cohere's Reranker API** (`rerank-english-v3.0`). This guarantees that only the top 3 highest-quality, hyper-relevant facts are fed into the LLM context.
- **Agent Filtering**: Agents can optionally filter RAG searches to target specific previous agents (e.g., `agent_filter="competitor_researcher"`).

### 3. The Flow (Step-by-Step execution)

Here is a visual map of the Crew's execution flow defined in `tasks.yaml` and `agents.yaml`:

1. **Market Analyst** 
   - **Action**: Uses internet search (`SerperDevTool`). 
   - **Store**: Uses `store_report_in_vector_db` to save the Market overview.
   - **Output**: Returns a 5-bullet summary to the next agent.
   
2. **Competitor Researcher** 
   - **Action**: Pulls data from DB (`retrieve_from_research_reports`), then researches live data. 
   - **Store**: Writes Competitor Report -> saves to DB. 
   - **Output**: Returns 5-bullet summary.

3. **Customer Researcher** 
   - **Action**: Queries the DB for "market opportunities & competitor gaps". Researches personas.
   - **Store**: Writes Customer Report -> saves to DB. 
   - **Output**: Returns 5-bullet summary.

4. **Product Researcher** 
   - **Action**: Queries the DB for customer pain points. Builds Tech Stack / MVP scope.
   - **Store**: Writes Product Report -> saves to DB. 
   - **Output**: Returns 5-bullet summary.

5. **Business Analyst (The Master Synthesizer)**
   - **Action**: This agent does *no live internet searching*. Instead, it hits the Vector database exclusively. It uses `retrieve_from_research_reports` to grab TAM sizes, competitor gaps, customer willingness to pay, and product features. 
   - **Output**: Compiles the final **Master Business Report** and saves it as `final_report_2.md`. 

### 4. Code Highlight: Task Callbacks
In `crew.py`, we implement a decorator/callback `make_store_callback("agent_name")`. While agents explicitly call the storage tool within their prompts, having a fallback task output handler ensures robustness in our data pipelines. By utilizing the `args_schema` based on Pydantic, the LLMs clearly understand what `report`, `agent_name`, and `summary` are expected.

This architecture showcases the next level of CrewAI capabilities: giving agents long-term shared memory banks over bloated overlapping contexts.
