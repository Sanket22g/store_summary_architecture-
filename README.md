# Store-and-Summary Architecture: Context-Efficient Multi-Agent LLM Pipelines

A practical design pattern for sequential multi-agent LLM pipelines that solves context accumulation through two-path output: full reports stored in a shared vector database while compact summaries travel through inter-agent context chains.

**Paper**: Ghadge, S. (2026). "Store-and-Summary Architecture: A Context-Efficient Pattern for Sequential Multi-Agent LLM Pipelines with On-Demand Retrieval-Augmented Generation"

---

## The Problem: Context Accumulation

In sequential multi-agent pipelines built on frameworks like CrewAI, a critical but under-addressed problem emerges: **context accumulation**. 

When Agent N begins execution, its input context contains:
- The original pipeline input
- The **full execution trace of Agent 1**: system prompt, task description, all tool calls with full outputs, and final answer
- The **full execution trace of Agent 2**: the same structure
- ... continuing for all prior agents

This snowball effect results in:

1. **Context Overflow**: Accumulated context exceeds model limits, particularly when agents make multiple web searches
2. **Rate Limit Exhaustion**: Large accumulated contexts burn through API quotas rapidly (e.g., a 5-agent pipeline may require 35+ LLM calls, exceeding free-tier limits)
3. **Lost-in-the-Middle Degradation**: Massive context causes the model's effective attention to degrade on important information buried in the middle

Our experimental 5-agent pipeline required ~35 LLM calls per run, exceeding the 20-call daily free tier limit on Gemini 2.5 Flash.

---

## The Solution: Store-and-Summary Architecture

### Core Principle

**The information that should travel between agents is not the same as the information that should be stored.**

- **Persistent Storage**: Full detailed reports, search results, intermediate reasoning → stored in a shared vector database
- **Inter-Agent Context**: Only compact summaries (typically 5 bullet points) travel between agents

### Two-Path Output Model

Each agent (except the final agent) executes two output operations:

#### Path 1: Persistent Storage
- Full output is chunked into overlapping segments (500 tokens, 50-token overlap)
- Chunks are embedded using a local embedding model
- All chunks stored in ChromaDB tagged with agent identifier
- Full output is **never passed directly** to another agent

#### Path 2: Context Transmission
- Agent generates a compact 5-bullet summary of key findings
- This summary **only** travels through CrewAI's context chain to subsequent agents
- Downstream agents begin with clean, targeted context

**Result**: Each agent starts with minimal context—only the summaries of prior agents—not their full execution traces.

### On-Demand RAG Retrieval

Any agent requiring deeper information from a prior agent's stored output queries the vector database using a two-stage retrieval pipeline:

#### Stage 1: Semantic Search
- Vector database retrieves top-K most similar chunks using cosine similarity
- Query and stored embeddings compared

#### Stage 2: Reranking
- Local CrossEncoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`) jointly encodes query with each candidate chunk
- Produces relevance scores reflecting query-document relationship
- Only top-N chunks (typically 3) after reranking returned to agent

**Result**: Agents receive small sets of highly targeted chunks rather than large sets of weakly similar results.

### Force-Store Callback: Reliability Layer

Because LLM agents follow instructions probabilistically, there's a non-zero probability an agent completes research without calling the store tool—especially under resource pressure (e.g., approaching max_iter limits).

**Solution**: A force-store callback fires automatically after each task completes:
1. Checks if agent's output is already in vector database
2. If missing, performs chunking, embedding, and storage automatically
3. Ensures **complete persistence of all agent outputs** regardless of agent behavior

In our experimental system, the callback triggered once for the competitor research agent, successfully recovering output that would otherwise have been lost.

---

## Installation & Setup

### Prerequisites
- Python >=3.10 <3.14
- UV for dependency management

### Installation

```bash
# Install uv if needed
pip install uv

# Clone and navigate to project
git clone https://github.com/Sanket22g/store_summary_architecture-.git
cd crew_5_rag

# Install dependencies
crewai install
```

### Configuration

Create a `.env` file with required API keys:

```
OPENAI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
```

Keys are used for:
- **OPENAI_API_KEY**: LLM calls (GPT-4 recommended)
- **SERPER_API_KEY**: Web search via SerperDevTool
- **COHERE_API_KEY**: Reranking in retrieval pipeline

---

## Architecture Overview

### Pipeline Structure

The reference implementation validates the architecture on a **5-agent market research pipeline**:

| Agent | Role | Tools | Input Context | Output |
|-------|------|-------|----------------|--------|
| Agent 1 | Market Research Analyst | Web search, Store | Pipeline input | 5-bullet summary |
| Agent 2 | Competitor Researcher | Web search, Store, RAG | Summary from Agent 1 | 5-bullet summary |
| Agent 3 | Customer Researcher | Web search, Store, RAG | Summaries from Agents 1-2 | 5-bullet summary |
| Agent 4 | Product Researcher | Web search, Store, RAG | Summaries from Agents 1-3 | 5-bullet summary |
| Agent 5 | Business Analyst | RAG only | Summaries from Agents 1-4 | Final investor-ready report |

### Agent Flow

```
INPUT (startup idea)
  ↓
Agent 1: Market Research
  ├─ Search internet (2 max)
  ├─ Write full report
  ├─ Store in ChromaDB
  └─ Return 5-bullet summary
  ↓
Agent 2: Competitor Research
  ├─ Query RAG: "market size, trends, opportunities"
  ├─ Search internet (2 max)
  ├─ Write full report
  ├─ Store in ChromaDB
  └─ Return 5-bullet summary
  ↓
Agent 3: Customer Research
  ├─ Query RAG: "competitor gaps, market opportunities"
  ├─ Search internet (2 max)
  ├─ Write full report
  ├─ Store in ChromaDB
  └─ Return 5-bullet summary
  ↓
Agent 4: Product Research
  ├─ Query RAG: "customer pain points, competitor gaps"
  ├─ Search internet (2 max)
  ├─ Write full report
  ├─ Store in ChromaDB
  └─ Return 5-bullet summary
  ↓
Agent 5: Business Analyst
  ├─ Query RAG: "TAM/SAM/SOM market size numbers"
  ├─ Query RAG: "top competitor gaps and opportunities"
  ├─ Query RAG: "customer personas, pain points, WTP"
  └─ Synthesize into final business report
  ↓
OUTPUT: final_report.md (investor-ready analysis)
```

---

## Running the Pipeline

```bash
crewai run
```

This initializes all agents and tasks as defined in `config/agents.yaml` and `config/tasks.yaml`. The pipeline will:

1. Execute agents sequentially
2. Store full reports in `market_research_db/` (ChromaDB SQLite)
3. Pass only summaries between agents
4. Generate final report to `final_report.md`

### Expected Output

For input "agentic AI tools for market research", the pipeline produces:

- TAM/SAM/SOM estimates with CAGR projections
- Five named direct competitors with gap analysis
- Four customer segments with detailed personas and willingness-to-pay ranges
- Prioritized MVP feature list with technology stack
- 3-year revenue projections with assumptions
- Risk analysis and mitigation strategies
- Final viability score (1-10) with Build It / Pivot / Avoid recommendation

---

## Implementation Details

### Custom Tools

#### StoreReportTool (`store_report_in_vector_db`)

```python
class StoreReportTool(BaseTool):
    name: str = "store_report_in_vector_db"
    description: str = "Store full report in vector DB; return only summary"
    args_schema: Type[BaseModel] = StoreReportInput
    
    def _run(self, report: str, agent_name: str, summary: str) -> str:
        chunks = chunk_text(report, chunk_size=500, overlap=50)
        collection.add(
            documents=chunks,
            ids=[f"{agent_name}_{uuid.uuid4().hex[:8]}" for _ in chunks],
            metadatas=[{"agent": agent_name, "chunk_index": i} for i in range(len(chunks))]
        )
        return f"Stored {len(chunks)} chunks.\n\nSummary:\n{summary}"
```

**Parameters**:
- `report`: Full detailed report text
- `agent_name`: Source agent identifier (e.g., "market_research_analyst")
- `summary`: Compact 5-bullet summary for inter-agent transmission

#### RAGRetrievalTool (`retrieve_from_research_reports`)

```python
class RAGRetrievalTool(BaseTool):
    name: str = "retrieve_from_research_reports"
    
    def _run(self, query: str, agent_filter: str = "all", top_k: int = 5) -> str:
        # Stage 1: Semantic search
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"agent": agent_filter} if agent_filter != "all" else None
        )
        
        # Stage 2: Reranking
        rerank_response = cohere_client.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=results["documents"][0],
            top_n=3
        )
        
        return formatted_results
```

**Parameters**:
- `query`: Specific question or topic to retrieve (e.g., "What are the top competitor gaps?")
- `agent_filter`: Optional filter to specific agent's reports (default: "all")
- `top_k`: Number of chunks to retrieve before reranking (default: 5)

### Key Implementation Findings

1. **Mandatory Instructions Matter**: LLM agents require explicit, structured, mandatory instructions to reliably use tools. Permissive language ("you may use") resulted in inconsistent behavior. Imperative step-by-step instructions ("You MUST call...") produced consistent tool usage.

2. **Task Description Structure**: Agents 1-4 follow a strict 5-step pattern:
   - STEP 1: Mandatory RAG query for prior context
   - STEP 2: Mandatory web searches with explicit maximum count
   - STEP 3: Write full report
   - STEP 4: Mandatory store call
   - STEP 5: Return only 5-bullet summary as final output

3. **Rate Control Layers**:
   - Explicit search count cap in task instructions
   - `max_iter` parameter on each agent limiting total tool invocations
   - `max_rpm` on crew limiting LLM requests per minute

---

## Experimental Results

### Context Size Reduction

| Agent | Baseline Context | Store-and-Summary Context | Reduction |
|-------|------------------|--------------------------|-----------|
| Agent 1 | Small (input only) | Small (input only) | None |
| Agent 2 | Large (Agent 1 full history) | Small (1 summary) | ~90% |
| Agent 3 | Very large (Agents 1-2 history) | Small (2 summaries) | ~95% |
| Agent 4 | Very large (Agents 1-3 history) | Small (3 summaries) | ~95% |
| Agent 5 | **Enormous** (Agents 1-4 history) | Small (4 summaries) | **~99%** |

**Context reduction is most significant at Agent 5**, which in baseline received accumulated traces of four agents each making multiple web searches.

### API Call Reduction

- **Baseline** (no optimization): 35-40 calls per run → exceeds free tier limit
- **Optimized** (with architecture): 25-30 calls per run → manageable with paid tier or higher-quota provider

### RAG Retrieval Precision

| Query | Top Result Source | Relevance Score | 2nd Score |
|-------|------------------|-----------------|-----------|
| TAM/SAM/SOM market size | market_research_analyst | 0.9805 | 0.9703 |
| Competitor gaps | competitor_researcher | 0.4429 | 0.0048 |
| Customer personas / WTP | customer_researcher | 0.9573 | 0.5848 |

High relevance scores confirm the two-stage retrieval pipeline surfaces correct source agent content for domain-specific queries.

### Force-Store Callback Effectiveness

In 5 complete pipeline runs:
- **4 runs**: Agent called store tool explicitly → callback skipped
- **1 run**: Competitor research agent completed but didn't call store → callback triggered and recovered 3 chunks automatically

---

## Customization Guide

### Modify Agents

Edit `src/crew_5_rag/config/agents.yaml` to adjust:
- Agent roles, goals, and backstories
- Verbose output settings
- Delegation permissions

### Modify Tasks

Edit `src/crew_5_rag/config/tasks.yaml` to:
- Change research requirements and report structures
- Adjust RAG query patterns
- Modify expected outputs
- Set context dependencies between tasks

### Extend the Pipeline

To add a 6th agent:

1. Add agent definition in `agents.yaml`
2. Add corresponding task in `tasks.yaml`
3. Add `@agent` method in `crew.py`
4. Add `@task` method with `callback=make_store_callback("agent_name")`
5. Add agent to task dependencies in downstream agents
6. Add agent to crew's `self.agents` list

### Customize Tools

Modify `src/crew_5_rag/tools/custom_tool.py`:
- Adjust chunk size and overlap for different content types
- Switch embedding models (currently: `sentence-transformers/all-MiniLM-L6-v2`)
- Replace Cohere reranker with alternative (e.g., local CrossEncoder)
- Add domain-specific preprocessing

---

## Generalization Beyond Market Research

The Store-and-Summary Architecture is domain-agnostic and applies to any sequential multi-agent pipeline:

- **Legal analysis**: Store court opinions, retrieve by precedent
- **Scientific literature review**: Store papers by topic, retrieve by research question
- **Code review**: Store code changes, retrieve by functionality
- **Medical diagnosis**: Store patient histories, retrieve by symptom patterns
- **Business intelligence**: Store analyses, retrieve by strategic question

The specific agent roles, tool configurations, and summary formats differ by domain, but the two-path output model and force-store callback apply universally.

---

## Limitations & Future Work

### Current Limitations

1. **Vector DB dependency**: Adds infrastructure complexity (chromadb, embeddings)
2. **Chunk quality sensitivity**: Critical facts at chunk boundaries may be split and retrieved incompletely (50-word overlap partially mitigates)
3. **Reranking latency**: CrossEncoder adds ~100-200ms per retrieval operation
4. **Summary quality dependency**: Poor 5-bullet summaries may omit information subsequent agents need
5. **Embedding model fixed**: Currently uses `sentence-transformers/all-MiniLM-L6-v2`; may not be optimal for all domains

### Future Research

- Hierarchical chunking strategies for nested document structures
- Dynamic embedding model selection per domain
- Learned reranking policies optimized for specific domains
- Integration with long-context models (Claude 200K, GPT-4 Turbo)
- Comparison with alternative context compression techniques

---

## Support & Contributing

For questions, issues, or contributions:
- **Paper**: See reference in this README
- **GitHub**: [https://github.com/Sanket22g/store_summary_architecture-](https://github.com/Sanket22g/store_summary_architecture-)
- **CrewAI Docs**: [https://docs.crewai.com](https://docs.crewai.com)

---

## References

Based on the academic paper:

> Ghadge, S. (2026). "Store-and-Summary Architecture: A Context-Efficient Pattern for Sequential Multi-Agent LLM Pipelines with On-Demand Retrieval-Augmented Generation." *Independent Research*.

Key related work:
- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
- Liu et al. (2023). Lost in the Middle: How Language Models Use Long Contexts
- Wu et al. (2023). AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation
- Nogueira & Cho (2019). Passage Re-ranking with BERT

---

## License

MIT License - See LICENSE file for details

---

**Built with**: CrewAI • ChromaDB • Cohere Reranker • Sentence-Transformers • OpenAI
