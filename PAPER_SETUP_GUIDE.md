# How to Use This LaTeX Paper in Overleaf

## Quick Start
1. Copy the entire content of `research_paper_ieee.tex` into Overleaf.
2. Create a new project or paste into an existing one.
3. Follow the instructions below to add your diagrams.

---

## Where to Insert Your Diagrams

### Diagram 1: System Architecture (Page 3)
**Location**: Line 139 in the LaTeX file, inside Figure~\ref{fig:architecture}

**Find this section:**
```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.95\linewidth]{architecture_diagram.png}
\caption{System Architecture: Sequential multi-agent pipeline...}
\label{fig:architecture}
\end{figure}
```

**What to do:**
1. In Overleaf, click the **Upload** button in the left sidebar.
2. Upload your first diagram (the detailed one with the 5 agents, ChromaDB, and data flows).
3. Rename the file to `architecture_diagram.png`.
4. The LaTeX will automatically reference it. No changes needed!

---

### Diagram 2: Generic Store-and-Summary Architecture (Optional - for Appendix)
If you want to add your second diagram (the generic "Agent N" version) as an alternative view:

**Add this to the end of Section~\ref{sec:arch}, after Figure 1:**
```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.95\linewidth]{generic_architecture.png}
\caption{Generic store-and-summary architecture showing how any number of specialized agents can feed into a final synthesis agent. Each agent stores full reports while passing compressed summaries forward, enabling scalability to additional specialized roles.}
\label{fig:generic_architecture}
\end{figure}
```

Then upload your second diagram and rename it to `generic_architecture.png`.

---

## Customization Checklist

### Author Information (Line 24-27)
Replace:
```latex
\author{\IEEEauthorblockN{Your Name\IEEEauthorrefmark{1}}
\IEEEauthorblockA{\IEEEauthorrefmark{1}Your Institution, Your City, Country\\
Email: your.email@institution.edu}}
```

### Results Tables
The results in Table 1 (lines 211-220) are **templates**. Replace with your actual experimental data:
- Coverage Score
- Factual Accuracy
- Coherence
- Retrieval Precision
- Token count
- Latency
- Expert scores

### References
Add your own citations in the Bibliography section (line 247+). Current references are standard papers on multi-agent systems and RAG. You can:
- Keep them as-is to show literature foundation.
- Replace with your own citations if you have specific prior work.
- Add citations to CrewAI, ChromaDB, Cohere, etc. if needed.

### Experiment Section
- Line 173: Modify the 10 startup ideas to match your actual test cases.
- Line 209: Replace the quantitative results with your actual numbers.
- Line 227: Update the ablation study findings.
- Line 237: Adjust qualitative observations based on your actual outputs.

---

## File Structure for Overleaf

Your Overleaf project should look like:
```
main.tex (or research_paper_ieee.tex)
├── architecture_diagram.png    (your first diagram)
├── generic_architecture.png    (optional second diagram)
└── references.bib             (if using external bibliography file)
```

---

## Sections to Write/Customize

### You Need to Add/Update:
1. **Introduction** (Line 48-68): Add context about your specific problem.
2. **Related Work** (Line 74-94): Cite relevant prior work on multi-agent systems, RAG, and vector databases.
3. **Results** (Line 211-245): Insert your actual experimental numbers.
4. **Discussion** (Line 248-290): Reflect on your specific findings and trade-offs.
5. **Limitations** (Line 295-302): Be honest about what doesn't work perfectly.

### Keep As-Is:
- Abstract (captures your system well)
- Architecture Description (matches your implementation)
- Agent Roles (matches your crew setup)
- Methodology (matches your sequential pipeline)
- Experimental Setup (provides a solid evaluation framework)

---

## Compilation Tips

1. **In Overleaf**: Click **Recompile** (or Ctrl+S).
2. **On Your Machine** (if using MiKTeX or TeX Live):
   ```bash
   pdflatex research_paper_ieee.tex
   ```
3. If you have bibliography files, also run:
   ```bash
   bibtex research_paper_ieee
   pdflatex research_paper_ieee.tex
   ```

---

## Paper Length & Structure

- **Current**: ~5 pages (single column, IEEE format).
- **Typical IEEE**: 4-8 pages for conference papers.
- If too long, compress Discussion and Limitations.
- If too short, expand Related Work or add more qualitative analysis.

---

## How to Submit to arXiv

1. Export the compiled PDF from Overleaf.
2. Create a `.zip` with:
   - `research_paper_ieee.tex`
   - `architecture_diagram.png` (and any other images)
   - `references.bib` (if separate)
3. Go to https://arxiv.org
4. Click "Submit an article"
5. Upload the zip file.
6. Fill metadata (title, abstract, authors).
7. Submit!

---

## How to Submit to IEEE Conference

1. Compile to PDF.
2. Check conference requirements (e.g., single/double column, page limits).
3. Customize header/footer if needed (IEEE template allows this).
4. Upload PDF and any supplementary materials.

---

## Key Phrases to Search and Replace (Customization)

Use Ctrl+H (Find & Replace) to update:
- `Your Name` → Your actual name
- `Your Institution` → Your university/company
- `Your City, Country` → Location
- `your.email@institution.edu` → Your email
- 10 diverse startup ideas → Describe your actual test cases

---

## Questions?

- **Overleaf Help**: https://www.overleaf.com/learn
- **IEEE Template**: https://www.ieee.org/publications_services/publications/author_templates.html
- **arXiv Submission**: https://arxiv.org/help/submit

Good luck with your paper! 🚀
