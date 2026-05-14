from dotenv import load_dotenv
load_dotenv()  # MUST be first — loads env vars before anything uses them

from pydantic import BaseModel, Field
from typing import Type, List
from crewai.tools import BaseTool
from crewai.tasks.task_output import TaskOutput
import chromadb
import cohere
import os
import uuid

# ── Cohere client (reranker) ──────────────────────────────────────────────────
cohere_client = cohere.Client(os.environ.get("COHERE_API_KEY"))

# ── ChromaDB — free local embeddings (all-MiniLM-L6-v2 auto) ─────────────────
chroma_client = chromadb.PersistentClient(path="./market_research_db")

collection = chroma_client.get_or_create_collection(
    name="market_research_reports",
    metadata={"hnsw:space": "cosine"}
)


# ── Helper: chunk long text ───────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks so context is not lost at boundaries."""
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end   = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 1 — Store Report in Vector DB
# ─────────────────────────────────────────────────────────────────────────────

class StoreReportInput(BaseModel):
    report: str = Field(
        ...,
        description=(
            "The full detailed report text to store in the vector database. "
            "Pass the entire report content here as a string."
        )
    )
    agent_name: str = Field(
        ...,
        description=(
            "The name/role of the agent storing the report. "
            "Example: 'market_research_analyst', 'competitor_researcher', "
            "'customer_researcher', 'product_researcher'"
        )
    )
    summary: str = Field(
        ...,
        description=(
            "A short 5-bullet summary of the report (max 300 tokens). "
            "This summary will be returned to the crew so other agents "
            "receive a compressed version in their context window."
        )
    )


class StoreReportTool(BaseTool):
    name: str = "store_report_in_vector_db"
    description: str = (
        "Use this tool AFTER completing your research report. "
        "It chunks and stores your full report in a shared vector database "
        "so other agents can retrieve specific sections later via RAG. "
        "You must provide: the full report, your agent name, and a 5-bullet summary. "
        "The tool returns your summary — pass it forward as your task output."
    )
    args_schema: Type[BaseModel] = StoreReportInput

    def _run(self, report: str, agent_name: str, summary: str) -> str:
        try:
            chunks    = chunk_text(report, chunk_size=500, overlap=50)
            ids       = [f"{agent_name}_{uuid.uuid4().hex[:8]}" for _ in chunks]
            metadatas = [{"agent": agent_name, "chunk_index": i}
                         for i in range(len(chunks))]

            collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )

            return (
                f" Report from '{agent_name}' successfully stored in vector DB.\n"
                f"   Chunks stored : {len(chunks)}\n\n"
                f" SUMMARY (pass this forward to the crew):\n{summary}"
            )

        except Exception as e:
            return f" Failed to store report: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 2 — RAG Retrieval Tool with Cohere Reranker
# ─────────────────────────────────────────────────────────────────────────────

class RAGRetrievalInput(BaseModel):
    query: str = Field(
        ...,
        description=(
            "A specific question or topic you want to retrieve from the "
            "stored research reports. Be as specific as possible. "
            "Example: 'What are the top competitor gaps in the market?' "
            "or 'What is the TAM size for this market?'"
        )
    )
    agent_filter: str = Field(
        default="all",
        description=(
            "Filter results by a specific agent's report. "
            "Options: 'market_research_analyst', 'competitor_researcher', "
            "'customer_researcher', 'product_researcher', or 'all' for all reports."
        )
    )
    top_k: int = Field(
        default=5,
        description=(
            "Number of chunks to retrieve before reranking. "
            "Default is 5. Increase to 10 for broader search."
        )
    )


class RAGRetrievalTool(BaseTool):
    name: str = "retrieve_from_research_reports"
    description: str = (
        "Use this tool when you need specific detailed information from "
        "any previous agent's research report stored in the vector database. "
        "It retrieves the most relevant chunks using semantic search, then "
        "reranks them using Cohere Rerank for maximum accuracy. "
        "Use this instead of relying on memory when you need precise data "
        "like market sizes, competitor names, customer personas, or feature lists."
    )
    args_schema: Type[BaseModel] = RAGRetrievalInput

    def _run(self, query: str, agent_filter: str = "all", top_k: int = 5) -> str:
        try:
            # ── Step 1: Semantic search in ChromaDB ───────────────────────
            where_filter = (
                {"agent": agent_filter}
                if agent_filter != "all"
                else None
            )

            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )

            raw_chunks    = results["documents"][0]
            raw_metadatas = results["metadatas"][0]

            if not raw_chunks:
                return "No relevant information found in the vector database for this query."

            # ── Step 2: Rerank with Cohere ────────────────────────────────
            rerank_response = cohere_client.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=raw_chunks,
                top_n=3
            )

            # ── Step 3: Build clean output ────────────────────────────────
            output_lines = [
                f" Query: {query}\n",
                f" Top {len(rerank_response.results)} reranked results:\n",
                "─" * 60
            ]

            for rank, result in enumerate(rerank_response.results, start=1):
                original_index  = result.index
                chunk_text_val  = raw_chunks[original_index]
                source_agent    = raw_metadatas[original_index].get("agent", "unknown")
                relevance_score = round(result.relevance_score, 4)

                output_lines.append(
                    f"\n[Result {rank}] "
                    f"Source: {source_agent} | "
                    f"Relevance Score: {relevance_score}\n"
                    f"{chunk_text_val}\n"
                    f"{'─' * 60}"
                )

            return "\n".join(output_lines)

        except Exception as e:
            return f" RAG retrieval failed: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACK — Force store if agent forgot to call store tool
# ─────────────────────────────────────────────────────────────────────────────

def make_store_callback(agent_name: str):
    """Safety net — force stores task output in ChromaDB if agent forgot."""
    def callback(output: TaskOutput):
        existing = collection.get(where={"agent": agent_name})

        if existing["ids"]:
            print(f"✅ [{agent_name}] already stored — skipping.")
            return

        print(f"[{agent_name}] missed storing — force storing now...")
        chunks    = chunk_text(output.raw)
        ids       = [f"{agent_name}_{uuid.uuid4().hex[:8]}" for _ in chunks]
        metadatas = [{"agent": agent_name, "chunk_index": i}
                     for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        print(f" [{agent_name}] force stored {len(chunks)} chunks.")

    return callback