[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL-3.0-only](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Documentation Status](https://readthedocs.org/projects/cryodl/badge/?version=latest)](https://cryodl.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/yagwip.svg)](https://badge.fury.io/py/yagwip)

# **<ins>CryoDL<ins/>**
## A Pypeline for CryoEM Deep Learning Utilities
<p align="center">
  <img src="docs/frenchie_cryoem.png" width="300" alt="Project Hero">
</p>

## Features

- **Configuration Management**: Centralized configuration system with JSON-based storage
- **Dependency Management**: Easy setup and validation of cryo-EM software dependencies
- **CLI Interface**: Command-line tools for configuration management
- **Path Validation**: Automatic validation of dependency paths and executables
- **Cross-platform**: Works on Windows, macOS, and Linux

## Quick Start

### Installation

#### Option 1: Install from source (recommended for development)

1. Clone the repository:
```bash
git clone https://github.com/ndlevinzon/cryoDL
cd cryoDL
```

2. Install in development mode:
```bash
pip install -e .
```

#### Option 2: Install with conda

1. Create and activate a conda environment:
```bash
conda create -n cryodl python=3.8
conda activate cryodl
```

2. Install the package:
```bash
pip install -e .
```

#### Option 3: Install with pip (when published to PyPI)

```bash
pip install cryodl
```

After installation, you can use the `cryodl` command directly from anywhere in your terminal!

#### Quick Installation Scripts

For Linux/macOS:
```bash
chmod +x install.sh
./install.sh
```

For Windows:
```cmd
install.bat
```

### Basic Usage

After installation, you can use the `cryodl` command directly:

1. Initialize the configuration:
```bash
cryodl init
```

2. Add your cryo-EM software dependencies:
```bash
cryodl add-dependency topaz /path/to/topaz 0.2.5
cryodl add-dependency model_angelo /path/to/model_angelo 1.0.0
```

3. Validate your dependencies:
```bash
cryodl validate-dependencies
```

4. View your configuration:
```bash
cryodl show
```

5. Generate SLURM headers:
```bash
cryodl slurm generate --job-name model_angelo
cryodl slurm generate --job-name topaz --nodes 2 --gres-gpu 2
```

## Example Workflow
```mermaid
flowchart TD
  %% ===== 0) Preflight =====
  subgraph S0[0) Preflight]
    A0[Raw cryo-EM movies<br/>+ microscope params (Å/px, volts, dose, gain)]
  end

  %% ===== 1) Motion/CTF/Curation in cryoSPARC =====
  subgraph S1[1) Motion / CTF / Curation (cryoSPARC)]
    A1[Import Movies]
    A2[Patch Motion Correction (Multi)<br/>(dose-weighted micrographs)]
    A3[Patch CTF Estimation (Multi)]
    A4[Curate Exposures<br/>(defocus, CTF fit, motion, ice)]
  end
  A0 --> A1 --> A2 --> A3 --> A4

  %% ===== 2) Picking with Topaz =====
  subgraph S2[2) Picking with Topaz (in cryoSPARC)]
    B1[Blob Picker → Extract (binned) → 2D Class<br/>(select positive classes)]
    B2[Topaz Train<br/>(use positives; auto negatives)]
    B3[Topaz Extract (apply model to all micrographs)]
    B4[Extract (production) → 2D Class<br/>(clean particle stack)]
  end
  A4 --> B1 --> B2 --> B3 --> B4

  %% ===== 3) Initial 3D & Refinement in cryoSPARC =====
  subgraph S3[3) Initial 3D & Refinement (cryoSPARC)]
    C1[Ab-initio Reconstruction (1–3 classes)]
    C2[Heterogeneous Refinement<br/>(separate states/junk)]
    C3[Non-Uniform Refinement (NU-refine)]
    C4[CTF Refinement<br/>(per-particle defocus, tilt/coma)]
    C5[Local Motion Correction → NU-refine]
  end
  B4 --> C1 --> C2 --> C3 --> C4 --> C5

  %% ===== 4) Heterogeneity with cryoDRGN =====
  subgraph S4[4) Heterogeneity with cryoDRGN]
    E1[Export particles + poses/CTF<br/>(.star + .mrcs)]
    D1[cryoDRGN Train<br/>(learn latent space)]
    D2[Reconstruct state-specific volumes]
    D3[Optional: particle assignments per state]
  end
  C4 --> E1
  E1 --> D1 --> D2 --> D3

  %% ===== 5) Bring states back & polish in cryoSPARC =====
  subgraph S5[5) State import & polishing (cryoSPARC)]
    F1[Import state volumes / subsets]
    F2[Heterogeneous or Local Refinement<br/>(per state)]
    F3[NU-refine per state]
    F4[Sharpen/Filter + Local Resolution]
  end
  D2 --> F1
  D3 --> F1
  F1 --> F2 --> F3 --> F4

  %% ===== 6) Model building with ModelAngelo =====
  subgraph S6[6) Model building (ModelAngelo)]
    G1[Prepare map (px size correct), half-maps, mask, FASTA]
    G2[ModelAngelo build / build_no_seq → hmm_search → rebuild]
    G3[Validate & fix (Phenix/Coot/ISOLDE)]
  end
  F4 --> G1 --> G2 --> G3

  %% ===== 7) Deliverables =====
  subgraph S7[7) Deliverables & deposition]
    H1[Final maps (full + half) + masks + FSC]
    H2[Models (PDB/mmCIF) + validation]
    H3[Deposit to EMDB/PDB]
  end
  G3 --> H1 --> H2 --> H3
```

## Supported Dependencies

The configuration manager is pre-configured for common cryo-EM software:

- **Topaz**: Deep learning-based particle picking for cryo-EM
- **ModelAngelo**: AI-powered protein structure modeling from cryo-EM maps

## Development

### Project Structure

```
cryoDL/
├── src/
│   ├── __init__.py
│   ├── config_manager.py    # Main configuration manager
│   ├── cli.py               # Command-line interface
│   ├── topaz_analysis.py    # Topaz analysis functions
│   ├── build_fastas.py      # FASTA building utilities
│   └── resources/
├── docs/
├── config.json              # Generated configuration file
├── pyproject.toml
└── README.md
```

### Adding New Dependencies

To add support for new cryo-EM software:

1. Update the `default_config` in `config_manager.py`
2. Add validation logic if needed
3. Update documentation

### Testing

Run the example usage:

```bash
python src/config_manager.py
```

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please open an issue on the project repository.

## Citation

If you use CryoDL in your research, please cite:

```bibtex
@software{cryoDL2025,
  title={CryoDL: A Pypeline for CryoEM Deep Learning Utilities},
  author={Levinzon, Nate and Shen, Peter},
  year={2025},
  url={https://github.com/ndlevinzon/cryoDL}
}
```

Additionally, we are grateful for the following open-source projects that we build on top of:

### Topaz and Topaz Denoise
<details><summary>Citation</summary><p>
	
```bibtex
@Article{Bepler2019,
author={Bepler, Tristan
and Morin, Andrew
and Rapp, Micah
and Brasch, Julia
and Shapiro, Lawrence
and Noble, Alex J.
and Berger, Bonnie},
title={Positive-unlabeled convolutional neural networks for particle picking in cryo-electron micrographs},
journal={Nature Methods},
year={2019},
issn={1548-7105},
doi={10.1038/s41592-019-0575-8},
url={https://doi.org/10.1038/s41592-019-0575-8}
}
@Article{Bepler2020_topazdenoise,
author={Bepler, Tristan
and Kelley, Kotaro
and Noble, Alex J.
and Berger, Bonnie},
title={Topaz-Denoise: general deep denoising models for cryoEM and cryoET},
journal={Nature Communications},
year={2020},
issn={2041-1723},
doi={10.1038/s41467-020-18952-1},
url={https://doi.org/10.1038/s41467-020-18952-1}
}
```
</p></details>

### Model-Angelo
<details><summary>Citation</summary><p>
	
```bibtex
@article{jamali2024automated,
	author = {Kiarash Jamali and Lukas Kall and Rui Zhang and Alan Brown and Dari Kimanius and Sjors Scheres},
	title = {Automated model building and protein identification in cryo-EM maps},
	year = {2024},
	doi = {10.1038/s41586-024-07215-4},
	URL = {https://www.nature.com/articles/s41586-024-07215-4},
	journal = {Nature}
}
```
</p></details>
