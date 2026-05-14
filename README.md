# Multi-Agent RAG System for Startup Analysis via Store-and-Summary Architecture

This repository hosts the implementation logic for our research paper: **"A Multi-Agent RAG System for Startup Idea Validation using Store-and-Summary Architecture"**. This project leverages [CrewAI](https://crewai.com) alongside ChromaDB and Cohere to overcome the context window exhaustion frequently seen in large-scale, sequential multi-agent operations.

## Abstract / Research Focus
The traditional startup research process relies on human analysis taking weeks to gather market, competitor, customer, and product data. While sequential multi-agent pipelines can automate this, retaining state across 5+ LLM agents leads to massive contextual bloat, latency, and hallucinations. 

Our custom **Store-and-Summary Architecture** introduces a paradigm where each autonomous agent produces a comprehensive output report, persists it completely within a Vector Database (ChromaDB), and passes only a highly compressed 5-bullet summary to the next agent in the pipeline. Downstream agents dynamically retrieve high-fidelity facts using a specialized RAG retrieval tool coupled with Cohere Reranking.

## The Sequential Multi-Agent Pipeline

The implementation orchestrates five specialized agents:
1. **Market Research Analyst**: Establishes TAM/SAM/SOM, market growth trends, and opportunities.
2. **Competitor Research Specialist**: Uncovers competitor weaknesses and maps market gaps.
3. **Customer Research Specialist**: Derives detailed customer personas and pinpoints buyer behaviors.
4. **Product Research Specialist**: Formulates MVP requirements, core features, tech stacks, and benchmarks.
5. **Business Analyst (Synthesizer)**: Relies exclusively on high-precision RAG queries over the vector database to synthesize the final end-to-end business report.

## Baseline vs. Proposed Architecture

As outlined in the experimental setups within our paper:
- **Baseline 1 (Single Agent)**: Struggles to differentiate specific roles, culminating in superficial reports.
- **Baseline 2 (No Retrieval)**: Agents rely only on the compressed 5-bullet summaries, lacking statistical depth and actionable specifics.
- **Baseline 3 (No Reranking)**: Uses standard semantic search, resulting in suboptimal vector retrieval.
- **Our System**: Achieves ~8.9/10 average coverage score and > 85% factual accuracy across testing by utilizing the Store-and-Summary flow with Cohere Reranking.

## Installation & Setup

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

`ash
pip install uv
crewai install
`

### Environment Variables
To reproduce our results, configure your .env file with the required API keys for internet scraping and reranking:
`env
OPENAI_API_KEY="sk-..."
SERPER_API_KEY="..."
COHERE_API_KEY="..."
`

### Running Experiments
To trigger the multi-agent pipeline:

`ash
crewai run
`
You can alter the startup_idea directly within src/crew_5_rag/main.py. The resulting artifact will be generated as inal_report.md (or inal_report_2.md), and the complete logs footprinted within market_research_db/.

## Key Technologies Used
- **[CrewAI](https://crewai.com)**: For the underlying collaborative multi-agent orchestration.
- **ChromaDB**: Free local vector embeddings for intermediate report persistency.
- **Cohere / rerank-english-v3.0**: For maximizing the RAG Retrieval Precision@3.
- **Serper & Selenium**: For real-time web scraping integration.

## Paper Artifacts
- **Latex Guides**: PAPER_SETUP_GUIDE.md and OVERLEAF_QUICK_START.md provide full instructions to port our findings onto the IEEE format LaTeX document using Overleaf.
- **Data Collection Guidelines**: See DATA_COLLECTION_GUIDE.md for our methodology to reproduce the 7 key quantitative metrics.
