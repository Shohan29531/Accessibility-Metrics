
# A Probabilistic Model and Metrics for Estimating Perceived Accessibility

This repository provides the code and resources for our probabilistic model and metrics designed to estimate the perceived accessibility of desktop applications in keystroke-based, non-visual interactions. This work addresses the challenges faced by blind users navigating desktop applications via assistive technologies such as screen readers and keyboards.

---

## Overview

### Key Contributions:
- **Study with 11 Blind Participants:**
  - Investigates how blind users perceive accessibility.
  - Identifies low navigational complexity as a key factor for high accessibility.

- **Probabilistic Interaction Model:**
  - Models user interactions with desktop applications using a logical DOM representation.
  - Introduces a navigation cost model to calculate the number of keystrokes required for specific actions.

- **Metrics for Accessibility:**
  - **Complexity:** Measures the average number of keystrokes needed to navigate between UI elements.
  - **Coverage:** Calculates the percentage of UI transitions achievable within a set number of keystrokes.
  - **Reachability:** Assesses how many keystrokes are required to access a given percentage of application features.

- **Applications:**
  - Benchmarking accessibility for 11 commonly used applications.
  - Providing actionable feedback for developers to optimize UI layouts.

---

## Features

1. **Automated Accessibility Assessment:**
   - Measures perceived accessibility without requiring direct user involvement.
2. **Quantifiable Metrics:**
   - Enables comparison of applications based on their navigational complexity and accessibility.
3. **Optimization Suggestions:**
   - Helps developers refine UI layouts to improve accessibility for screen reader users.

---

## Installation
git clone https://github.com/your-repo/Accessibility-Metrics.git
cd Accessibility-Metrics
python run_single.py 
or
python run_batch.py

## Citing 
If you find the repo useful, please cite our paper:

@inproceedings{islam2023probabilistic,
  title={A Probabilistic Model and Metrics for Estimating Perceived Accessibility of Desktop Applications in Keystroke-Based Non-Visual Interactions},
  author={Islam, Md Touhidul and Porter, Donald E and Billah, Syed Masum},
  booktitle={Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems},
  pages={1--20},
  year={2023}
}
