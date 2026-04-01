# Accessibility Metrics for Desktop Applications

> **Official repository for the CHI 2023 paper:**
> [*A Probabilistic Model and Metrics for Estimating Perceived Accessibility of Desktop Applications in Keystroke-Based Non-Visual Interactions*](https://dl.acm.org/doi/full/10.1145/3544548.3581400)
> Md Touhidul Islam, Donald E. Porter, Syed Masum Billah — CHI '23, Hamburg, Germany

---

## Overview

Blind users navigate desktop applications exclusively through screen readers and keyboards. The logical structure of a UI — how elements are grouped and how many keystrokes are required to move between them — has an outsized effect on their experience. Yet there has been no principled, user-independent way to measure this.

This repository provides the implementation for a **probabilistic interaction model** and three derived **accessibility metrics** that quantify the perceived accessibility of desktop applications from their UI element hierarchy alone, without requiring direct user involvement.

---

## How It Works

### Step 1 — UI Hierarchy Collection (Pre-collected `.log` files)

The UI element hierarchies of target desktop applications were extracted using the **Windows Accessibility API** (via Microsoft's [Inspect tool](https://learn.microsoft.com/en-us/windows/win32/winauto/inspect-objects)), which exposes an application's logical element tree — the same representation that screen readers navigate. These hierarchy dumps are stored as `.log` files in `accessibility_api_files/`.

Each `.log` file captures the full tree of UI elements (menus, buttons, ribbons, sub-menus, etc.) for a given application, encoding parent–child relationships and sibling ordering exactly as a screen reader would encounter them.

### Step 2 — Navigation Cost Modeling

From the UI element tree, the model computes the **navigation cost** — the number of keystrokes required for a screen reader user to move from one arbitrary UI element to another. Screen reader navigation is modeled as a sequential traversal of the element tree (e.g., via Tab and arrow keys), so the cost between any two elements is a function of their positions and relationships within the hierarchy.

Two variants of the model are implemented:

- **Uniform model**: Assumes a user is equally likely to want to navigate from any element to any other. This gives an unweighted baseline.
- **Staircase model**: Weighted by user-reported usage frequency of different UI elements (e.g., how often a user accesses the "Format" menu). Frequencies are collected via a simple survey-style question and translated into a discrete staircase probability distribution, refining the model to better reflect realistic usage.

### Step 3 — Metric Computation

Three metrics are derived from the navigation cost model:

| Metric | Definition |
|---|---|
| **Complexity** | The expected number of keystrokes to navigate between any two UI elements, averaged over the probability distribution of source–destination pairs. Lower is more accessible. |
| **Coverage(k)** | The fraction of all possible UI element transitions achievable within a budget of *k* keystrokes. |
| **Reachability(p)** | The minimum number of keystrokes required to reach at least *p*% of the application's UI elements from any starting point. |

These metrics are computed in the Jupyter notebooks under `my_work/` and `mac_work/`, with results processed and visualized in `result_processing/` and `plotly_works/`.

---

## Applications Benchmarked

The metrics were computed and validated across **11 commonly used desktop applications** in the blind community, including applications in the Microsoft Office suite, Notepad, Calculator, and others. Results are cross-referenced against perceived accessibility ratings collected from the 11 blind participants in the formative study.

As a concrete example: Notepad has a complexity of **1.63 keystrokes** while Microsoft Word has a complexity of **3.51 keystrokes**, consistent with participant ratings placing Notepad as more accessible.

---

## Five Use Cases

The paper demonstrates five concrete uses of the metrics:

1. **Benchmarking** — Comparing perceived accessibility across similar applications (e.g., text editors, media players).
2. **Shortcut Optimization** — Identifying which UI elements, if assigned a keyboard shortcut, would most reduce overall complexity.
3. **Design Feedback** — Providing developers with actionable structural changes to reduce navigational complexity.
4. **User Self-Assessment** — Helping blind users estimate the efficiency gain of learning application-specific shortcuts.
5. **Accessibility Testing** — Integrating the metrics into automated testing pipelines as a proxy for user experience.

---

## Repository Structure

```
Accessibility-Metrics/
├── accessibility_api_files/    # Pre-collected UI element hierarchy .log files
│                               # (extracted via Windows Accessibility API / Inspect)
├── my_work/                    # Jupyter notebooks: metric computation (Windows apps)
├── mac_work/                   # Jupyter notebooks: metric computation (macOS apps)
├── result_processing/          # Post-processing and statistical analysis of results
├── plotly_works/               # Interactive visualizations of metric outputs
├── data/                       # Intermediate data files
├── data.txt                    # List of benchmarked applications
└── requirements.txt            # Python dependencies
```

---

## Installation & Usage

```bash
git clone https://github.com/Shohan29531/Accessibility-Metrics.git
cd Accessibility-Metrics
pip install -r requirements.txt
```

To compute metrics for a new application:
1. Use Microsoft's [Inspect tool](https://learn.microsoft.com/en-us/windows/win32/winauto/inspect-objects) to dump the application's UI element hierarchy as a `.log` file and place it in `accessibility_api_files/`.
2. Open the relevant notebook in `my_work/` and point it to your `.log` file.
3. Run the notebook to compute Complexity, Coverage, and Reachability scores.

---

## Citation

If you use this code or build on this work, please cite:

```bibtex
@inproceedings{islam2023probabilistic,
  title     = {A Probabilistic Model and Metrics for Estimating Perceived Accessibility
               of Desktop Applications in Keystroke-Based Non-Visual Interactions},
  author    = {Islam, Md Touhidul and Porter, Donald E. and Billah, Syed Masum},
  booktitle = {Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems},
  articleno = {43},
  numpages  = {20},
  year      = {2023},
  publisher = {Association for Computing Machinery},
  address   = {New York, NY, USA},
  doi       = {10.1145/3544548.3581400},
  url       = {https://doi.org/10.1145/3544548.3581400}
}
```
