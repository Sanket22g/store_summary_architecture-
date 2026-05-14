# IEEE Research Paper - Quick Copy-Paste Guide for Overleaf

## Step-by-Step: Getting Your Paper Into Overleaf

### Step 1: Create Overleaf Project
1. Go to https://www.overleaf.com
2. Click **New Project** → **Blank Project**
3. Name it: "Multi-Agent RAG Research Paper"
4. Click **Create**

### Step 2: Copy LaTeX Code
1. Open `research_paper_ieee.tex` from this folder
2. Select **ALL** the text (Ctrl+A)
3. Copy (Ctrl+C)

### Step 3: Paste Into Overleaf
1. In Overleaf, clear the default text in `main.tex`
2. Paste (Ctrl+V) the entire LaTeX code
3. Click **Recompile** (or press Ctrl+S)
4. You should see a PDF preview on the right!

---

## Step 4: Upload Your Diagrams

### Upload Diagram 1 (Detailed Architecture with 5 Agents)
1. In Overleaf left panel, click **Upload** (📁 icon)
2. Select your first diagram image from your computer
3. Name it: `architecture_diagram.png`
4. The LaTeX automatically references it!

### Upload Diagram 2 (Optional Generic Template)
1. Click **Upload** again
2. Select your second diagram
3. Name it: `generic_architecture.png`
4. Uncomment the optional figure code (see below)

---

## Step 5: Customize Critical Sections

### Update Author Info (Line 24-27)
Find:
```latex
\author{\IEEEauthorblockN{Your Name\IEEEauthorrefmark{1}}
```

Replace `Your Name`, institution, city, email with your details.

---

### Add Your Experimental Results (Line 211-220)

The template has placeholder numbers. Replace with **YOUR actual data**:

Find this table:
```latex
\begin{tabular}{|l|c|c|c|c|}
\hline
\textbf{Metric} & \textbf{Single-Agent} & \textbf{No Retrieval} & \textbf{No Reranking} & \textbf{Our System} \\
\hline
Coverage Score (0-10) & 6.2 & 7.8 & 8.3 & \textbf{8.9} \\
```

**Template for your data:**
| Metric | Single-Agent | No Retrieval | No Reranking | Your System |
|--------|--------------|--------------|--------------|-------------|
| Coverage (0-10) | [FILL] | [FILL] | [FILL] | [FILL] |
| Accuracy (%) | [FILL] | [FILL] | [FILL] | [FILL] |
| Coherence (1-10) | [FILL] | [FILL] | [FILL] | [FILL] |
| Retrieval Prec@3 | -- | [FILL] | [FILL] | [FILL] |
| Tokens (K) | [FILL] | [FILL] | [FILL] | [FILL] |
| Latency (min) | [FILL] | [FILL] | [FILL] | [FILL] |
| Expert Score (1-10) | [FILL] | [FILL] | [FILL] | [FILL] |

---

## What Each Section Should Contain (Fill-In Guide)

### Abstract (Lines 18-22)
✅ Already good! Describes your system well.
Optional: Tweak numbers to match your actual results.

### Introduction (Lines 48-68)
Add specific details:
- Why is startup analysis important?
- What problems exist with current methods?
- Why does your approach solve them?

**Example paragraph you can adapt:**
```
The traditional startup research process relies on consultants and analysts 
spending weeks gathering market data. This is costly, time-consuming, and 
often produces siloed reports that lack cross-domain synthesis. Our system 
automates this process while maintaining depth and coherence through 
specialized agent roles and persistent knowledge retrieval.
```

### Related Work (Lines 74-94)
- Review 5-10 papers on: multi-agent systems, RAG, vector databases, business automation
- Cite them in IEEE format
- Explain what's unique about your approach

**Citation format example:**
```
\bibitem{author_year}
First Last, ``Paper title,'' \emph{Journal Name}, vol. X, pp. Y-Z, Year.
```

### Agent Roles (Lines 115-150)
✅ Already matches your 5 agents! No changes needed.

### Experimental Setup (Lines 173-208)
Update:
- Line 173: Describe your 10 (or N) test startup ideas
- Line 188: List the metrics you actually measured

### Results (Lines 211-245)
**MUST UPDATE**:
1. Table with your actual numbers (line 211-220)
2. Ablation study findings (line 227)
3. Qualitative observations (line 237)

### Discussion (Lines 248-290)
**Explain your findings:**
- Why did your system outperform baselines?
- What surprised you?
- What trade-offs did you observe?

### Limitations (Line 295-302)
**Be honest:**
- What didn't work?
- What could be improved?
- What's out of scope?

---

## Uncomment Optional Content (If Adding Generic Diagram)

If you want to add your 2nd diagram, find line 165 and add:

```latex
\begin{figure}[h!]
\centering
\includegraphics[width=0.95\linewidth]{generic_architecture.png}
\caption{Generic store-and-summary multi-agent architecture. This pattern 
generalizes to any number of specialized agents, each storing full reports 
in persistent memory while passing compressed summaries forward to minimize 
context overhead.}
\label{fig:generic_architecture}
\end{figure}
```

Insert after the first figure and before the "Agent Roles" subsection.

---

## Bibliography: How to Add Citations

At the bottom (line 247+), citations are in IEEE format. Add yours like this:

```latex
\bibitem{your_citation_key}
A. Thorne and B. Smith, ``Title of the paper,'' \emph{Journal or Conference Name}, 
vol. X, no. Y, pp. 123--145, Year.

\bibitem{another_citation}
C. Johnson et al., ``Another paper,'' \emph{arXiv preprint arXiv:XXXX.XXXXX}, Year.
```

Then cite in text with:
```latex
See reference~\cite{your_citation_key} for details.
```

---

## Common Formatting in IEEE LaTeX

### Bold text
```latex
\textbf{This is bold}
```

### Italic text
```latex
\textit{This is italic}
```

### References to figures/tables
```latex
Figure~\ref{fig:architecture} shows...
Table~\ref{tab:results} presents...
```

### Equations
```latex
\begin{equation}
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
\end{equation}
```

### Lists
```latex
\begin{itemize}
\item First point
\item Second point
\end{itemize}

\begin{enumerate}
\item Numbered first
\item Numbered second
\end{enumerate}
```

---

## Estimated Sections to Write/Time

| Section | Status | Time |
|---------|--------|------|
| Title & Abstract | ✅ Done | 0 min |
| Introduction | Need to write | 15 min |
| Related Work | Need to write | 30 min |
| Architecture | ✅ Done | 0 min |
| Methodology | ✅ Done | 0 min |
| Experiments | Partial | 20 min |
| Results | Need data | 10 min |
| Discussion | Need to write | 20 min |
| Conclusion | ✅ Done | 0 min |
| **TOTAL** | | **95 min** |

---

## Troubleshooting

### Images Not Showing?
- Make sure file names **exactly** match (lowercase, with extension)
- Upload via Overleaf's **Upload** button, not drag-drop
- Check they're in the same project folder

### Compilation Errors?
- Look for red X next to line numbers
- Most common: Forget backslash or mismatched braces
- Use Overleaf's "Help" menu → Check for help

### References Not Working?
- Use `\cite{key}` in text
- Make sure `\bibitem{key}` matches in bibliography
- Run Recompile twice if needed

---

## Submit to arXiv

Once your PDF is ready:
1. Export from Overleaf (Download → PDF)
2. Go to https://arxiv.org/submit
3. Login or register
4. Upload your `.tex` file (or PDF + images as ZIP)
5. Fill: Title, Abstract, Authors, Category (select "AI" or "Machine Learning")
6. Submit!

---

## Quick Links

- **Overleaf Help**: https://www.overleaf.com/learn
- **IEEE Citation Style**: https://ieee-dataport.org/sites/default/files/analysis/27/IEEE%20Citation%20Style.pdf
- **arXiv Submission**: https://arxiv.org/help/submit
- **IEEE Xplore**: https://ieeexplore.ieee.org (submit full paper later)

---

## Final Checklist Before Submission

- [ ] All placeholder text replaced with your content
- [ ] Both diagrams uploaded and displaying
- [ ] Author names and affiliations correct
- [ ] Experimental data from your runs inserted
- [ ] All citations properly formatted
- [ ] PDF compiles without errors
- [ ] Spell-check done
- [ ] Page count acceptable (typically 4-8 pages)

**Good luck! 🎓**
