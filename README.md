# Accessibility Metrics for Desktop Applications

> **Official repository for the CHI 2023 paper:**
> [*A Probabilistic Model and Metrics for Estimating Perceived Accessibility of Desktop Applications in Keystroke-Based Non-Visual Interactions*](https://dl.acm.org/doi/full/10.1145/3544548.3581400)
> Md Touhidul Islam, Donald E. Porter, Syed Masum Billah — CHI '23, Hamburg, Germany

---

## Overview

Blind and low-vision users rely on screen readers and keyboards to navigate desktop applications. Yet how *accessible* a given application feels to those users — its **perceived accessibility** — has historically resisted quantification. This repository provides the full implementation of a probabilistic interaction model and three derived metrics that estimate perceived accessibility automatically, without requiring direct user involvement.

The work is grounded in a formative study with **11 blind participants**, which identified **low navigational complexity** — the average number of keystrokes required to move between UI elements — as the primary driver of whether users experience an application as accessible. The model and metrics operationalize this insight computationally.

---

## Key Contributions

### 1. Formative User Study
A qualitative and quantitative study with 11 blind participants explored how they perceive accessibility while using screen readers and keyboards on everyday desktop applications. The study surfaces fine-grained factors that shape perceived accessibility, including application learnability, behavioral determinism of shortcuts, and ease of describing the interface to others.

### 2. Probabilistic Interaction Model
A probabilistic model of non-visual interaction is constructed from the application's logical UI element tree (analogous to a DOM). The model treats navigation as a random walk over UI elements and computes the expected number of keystrokes required to move between any two arbitrary elements, capturing realistic usage patterns through configurable probability distributions.

### 3. Three Accessibility Metrics

| Metric | Definition |
|---|---|
| **Complexity** | Average number of keystrokes needed to navigate between any two UI elements — a lower value indicates a more accessible layout. |
| **Coverage** | The percentage of all possible UI transitions that are achievable within a specified keystroke budget. |
| **Reachability** | The minimum number of keystrokes required to access a given percentage of an application's features. |

Together, these three metrics provide a multidimensional profile of an application's navigational accessibility that correlates meaningfully with user-perceived accessibility scores.

### 4. Benchmarking Suite
The metrics are applied to **11 commonly used desktop applications**, producing a ranked benchmark that matches participant ratings from the user study and reveals concrete optimization targets for developers.

---

## How It Works

The pipeline proceeds in four stages:

```
Screenshot(s) of UI
        │
        ▼
┌─────────────────────┐
│  1. Text Detection  │  EAST-based OCR detects text regions and groups
│     (detect_text_east)│  words into lines and paragraphs
└─────────────────────┘
        │
        ▼
┌──────────────────────────┐
│  2. UI Component Detection│  CNN-based region proposal detects non-text
│     (detect_compo)        │  interactive elements (buttons, icons, etc.)
└──────────────────────────┘
        │
        ▼
┌────────────────────────────┐
│  3. Merge & Representation │  Text and component detections are fused into
│     (merge.py)             │  a unified JSON element representation
└────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│  4. Metric Computation           │  Complexity, Coverage, and Reachability
│     (my_work / result_processing)│  are computed from the element graph
└──────────────────────────────────┘
```

The `accessibility_api_files/` directory contains supplementary scripts for extracting UI element hierarchies directly via the Windows Accessibility API (using Microsoft's Inspect tool), which can serve as an alternative to the vision-based pipeline for supported applications.

---

## Repository Structure

```
Accessibility-Metrics/
├── run_single.py               # Process a single application screenshot
├── run_batch.py                # Batch-process multiple screenshots
├── merge.py                    # Fuse OCR and component detection outputs
├── detect_text_east/           # EAST-based text detection module
├── detect_compo/               # CNN-based UI component detection module
├── cnn/                        # Trained CNN classifier for UI elements
├── accessibility_api_files/    # Windows Accessibility API extraction scripts
├── my_work/                    # Metric computation notebooks and scripts
├── result_processing/          # Post-processing and analysis of metric outputs
├── plotly_works/               # Visualization of metric results
├── input/                      # Input screenshots (populate before running)
├── data/                       # Output directory for detection results
├── config/                     # Configuration files
├── utils/                      # Shared utility functions
└── requirements.txt            # Python dependencies
```

---

## Installation & Usage

### Prerequisites
- Python 3.7+
- OpenCV
- TensorFlow / Keras (for CNN classifier)

### Setup

```bash
git clone https://github.com/Shohan29531/Accessibility-Metrics.git
cd Accessibility-Metrics
pip install -r requirements.txt
```

### Running on a Single Application

1. Place screenshot(s) of the target application in the `input/` directory.
2. Run the pipeline:

```bash
python run_single.py
```

Detection outputs (OCR JSON, component JSON, merged representation) are written to `data/output/`.

### Running in Batch Mode

```bash
python run_batch.py
```

Processes all images in the configured input directory sequentially.

### Computing Metrics

After the detection pipeline completes, use the notebooks and scripts in `my_work/` and `result_processing/` to compute Complexity, Coverage, and Reachability scores from the merged element representations.

---

## Citation

If you use this code or build on this work, please cite the paper:

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

---

## Related Work

This project is part of an ongoing line of accessibility research at the [A11y Lab, Penn State University](https://a11y.ist.psu.edu/). Related projects include:

- **Wheeler** — A novel three-wheeled input device for BLV users that reduces navigation time by 40% (UIST 2024, Best Paper Honorable Mention)
- **SpaceXMag** — Layout-aware screen magnification for low-vision users (IMWUT 2023)

---

## License

This repository is provided for research and academic use. Please refer to the [ACM publication](https://dl.acm.org/doi/full/10.1145/3544548.3581400) for full details of the methods described herein.
