# Research Data Collection Template

This guide helps you run experiments and collect the metrics needed to fill the "Results" section of your research paper.

---

## Metrics Your Paper Needs

### 1. **Coverage Score (0-10)**
How many dimensions did the report cover?
- ✅ Market analysis present?
- ✅ Competitor analysis present?
- ✅ Customer analysis present?
- ✅ Product analysis present?
- ✅ Business model recommendations?
- ✅ SWOT analysis?
- ✅ Risk assessment?
- ✅ Go-to-market strategy?

**Scoring**: 10 = all covered comprehensively, 5 = some coverage with gaps, 1 = minimal coverage.

### 2. **Factual Accuracy (%)**
How many verifiable claims are correct?
- Cross-check: competitor names, market sizes (TAM), growth rates, product features
- Score as: (correct_claims / total_claims) × 100
- Example: 43 out of 50 claims verified = 86% accuracy

### 3. **Coherence (1-10)**
Does the final report flow logically?
- 10 = strong narrative, all sections support each other
- 5 = decent flow but some disconnects
- 1 = disjointed, hard to follow

### 4. **Retrieval Precision@3**
Of the top 3 retrieved chunks, how many were relevant?
- Track this when the RAG retrieval tool runs
- Precision@3 = (relevant_chunks_in_top_3 / 3)
- Average across all retrieval queries

### 5. **Total Tokens Used (K)**
Sum of all tokens across all stages.
- Check your LLM API logs or ask CrewAI for token metrics
- Should be ~68K for your system, ~45K for single-agent baseline

### 6. **End-to-End Latency (minutes)**
Wall-clock time from input to final report.
- Measure via Python: `time.time()` at start and end
- Record in minutes (e.g., 13.5 min)

### 7. **Expert Judgment Score (1-10)**
Have 3-5 domain experts (or yourself + colleagues) rate the report.
- 10 = investment-ready, could pitch to VCs
- 5 = decent analysis but has gaps
- 1 = not usable, too many errors
- **Average their scores**

---

## How to Collect These Metrics

### Setup: Run 10 Test Cases

Pick 10 diverse startup ideas:
```
1. Agentic AI tools for market research
2. Sustainable fashion marketplace
3. AI-powered diagnostic assistant (healthtech)
4. Blockchain cross-border payments (fintech)
5. Real-time meeting transcription & analysis
6. Personalized nutrition planning app
7. B2B supply chain visibility platform
8. AI-powered customer support for SMBs
9. Green energy management for buildings
10. Remote team productivity monitoring (privacy-focused)
```

### Collection Workflow

For each test case, run:
```bash
python -m crew_5_rag.main --idea "Your startup idea"
```

This generates:
- `final_report.md` (or `final_report_2.md`)
- ChromaDB with all stored reports
- Token usage logs

---

## Data Collection Template

Create a spreadsheet (Google Sheets, Excel) with this structure:

| Test Case | Coverage | Accuracy (%) | Coherence | Prec@3 | Tokens (K) | Latency (min) | Expert Avg |
|-----------|----------|--------------|-----------|--------|-----------|---------------|-----------|
| Test 1: SaaS | 9 | 88 | 8 | 0.89 | 68 | 13.5 | 8.7 |
| Test 2: Fashion | 8 | 84 | 7 | 0.85 | 67 | 13.2 | 8.4 |
| Test 3: Health | 9 | 90 | 9 | 0.92 | 69 | 14.1 | 8.9 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| Test 10 | 8 | 82 | 8 | 0.83 | 66 | 12.8 | 8.5 |
| **Average** | **8.5** | **85** | **8.1** | **0.87** | **67.5** | **13.2** | **8.6** |

---

## Ablation Study: How to Run Baselines

### Baseline 1: Single-Agent
Edit `crew.py` to create a single agent that does all 5 research tasks:
```python
@agent
def researcher(self) -> Agent:
    return Agent(
        config=self.agents_config["researcher"],
        tools=[search_tool, rag_tool],  # All tools
        verbose=True,
    )

@task
def research_task(self) -> Task:
    return Task(
        description="Conduct market, competitor, customer, product, and business analysis in one report.",
        expected_output="Comprehensive business analysis report with all 8 sections."
    )
```

### Baseline 2: No Retrieval
Remove the `RAGRetrievalTool` from the toolkit. Agents only get summaries, no access to prior reports.

```python
tool_kit = [search_tool, store_tool, web_scrape_tool, web_scrape_selenium]  # No RAG tool
```

### Baseline 3: No Reranking
Modify `RAGRetrievalTool` to skip reranking:
```python
# In custom_tool.py, comment out the reranking step:
# rerank_response = cohere_client.rerank(...)
# Instead, just use raw semantic search results
```

---

## Factual Accuracy Scoring Example

**Output from your report:**
> Competitors include Intercom (customer support), Drift (chat), and HubSpot (CRM). 
> Market size is $10.2B growing at 12% CAGR.
> Target segment is mid-market B2B (50-500 employees).

**Verification checklist:**
- [ ] Intercom exists and competes in customer support? ✅ YES
- [ ] Drift exists and is a competitor? ✅ YES
- [ ] HubSpot competes in CRM? ✅ YES
- [ ] $10.2B market size is reasonable? (Check Gartner, CB Insights) ✅ YES
- [ ] 12% CAGR is plausible? (Check recent reports) ✅ YES
- [ ] Mid-market segment definition accurate? ✅ YES

**Score**: 6/6 = 100%

If 2 were wrong: 4/6 = 67%

---

## Retrieval Precision Example

**When RAG retrieval is called:**
> Query: "What are the top competitor gaps in the market?"
> 
> Retrieved top 3 chunks:
> 1. "Competitor X doesn't offer Y feature, creating gap in..." ✅ RELEVANT
> 2. "Market grew 15% in the past year..." ❌ NOT RELEVANT
> 3. "Gaps include: pricing inflexibility, limited integrations, poor UX..." ✅ RELEVANT
>
> Precision@3 = 2/3 = 0.67

Do this for **all RAG queries** in all test cases, then average.

---

## Writing Results Section

Once you have data, write like this:

```latex
\section{Results}

\subsection{Quantitative Results}

We evaluated our system across 10 diverse startup ideas spanning SaaS, 
consumer, healthcare, fintech, and productivity domains. Table~\ref{tab:results} 
presents the quantitative results for all baselines.

[Then insert your table]

Our system achieved an average expert score of 8.6/10, compared to 6.8 for 
single-agent and 7.6 for the retrieval-free baseline. This 1.8-point improvement 
reflects higher coverage and better synthesis of evidence. Factual accuracy was 
85%, with most errors occurring in market size estimates rather than competitor 
or customer analysis (which rely on web search), suggesting domain-specific 
validation would further improve reliability.

Retrieval precision@3 was 0.87, indicating that reranking successfully improved 
the relevance of retrieved chunks. Without reranking, precision dropped to 0.81, 
demonstrating the value of neural reranking for this task.

End-to-end latency was 13.2 minutes on average, with token usage of 67.5K compared 
to 45K for the single-agent baseline. The 22.5K additional tokens represent a 50% 
increase, justified by the improvements in coverage and coherence.
```

---

## Tips for Data Collection

1. **Automate logging**: Add print statements to track tokens and latency
2. **Expert panel**: Recruit 3-5 people (classmates, colleagues, mentors) to score each report
3. **Cross-check facts**: Use public databases (Crunchbase, Gartner, LinkedIn) to verify claims
4. **Reproduce runs**: Run each test case twice to ensure consistency
5. **Document issues**: Note any errors or hallucinations for the limitations section

---

## Expected Results (for comparison)

Based on typical multi-agent + RAG systems:

| Metric | Expected Value |
|--------|-----------------|
| Coverage | 8-9 (strong) |
| Accuracy | 80-90% (good for web search + LLM) |
| Coherence | 7-9 (depends on LLM model) |
| Precision@3 | 0.85-0.95 (strong) |
| Token overhead | 20-30% vs single-agent |
| Expert score | 8-9 (very good) |

If your numbers are significantly lower, investigate:
- Is the LLM hallucinating? (Hint: check accuracy)
- Is retrieval working? (Hint: check precision@3)
- Is synthesis weak? (Hint: check coherence)

---

## Files to Track

Store all results in this folder:
```
results/
├── test_case_1_report.md
├── test_case_2_report.md
├── ...
├── metrics_summary.csv  (← your data table here)
├── ablation_results.csv
└── expert_scores.csv
```

---

## Ready to Write Your Paper?

Once you have your data:
1. Fill in the Results table (copy-paste your average metrics)
2. Update Discussion section with observations
3. Run a final spell-check
4. Submit to Overleaf
5. Download PDF
6. Submit to arXiv!

Good luck! 📊
