

# Font Mirror
![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Local Google Fonts mirroring made easy.**

A utility to create and maintain a mirror of Google Fonts.

## Installation

**Prerequisites:**
- Python 3.11 or higher
- git


Clone the repository and set up a Python virtual environment (recommended):

```bash
git clone https://github.com/darkflib/font-mirror.git
cd font-mirror
# Create a virtual environment named .venv
python3 -m venv .venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows (cmd):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies
pip3 install -r requirements.txt
```

## Usage

The `mirror.py` script downloads and rewrites Google Fonts CSS and font files for local mirroring.

```bash
python3 mirror.py [OPTIONS]
```

## Options

- `--fonts`, `-f`  
  Specify one or more Google Fonts queries (e.g., `'Roboto:wght@100;400;700'`). Can be used multiple times.

- `--fonts-file`  
  Path to a file containing font queries, one per line. Lines starting with `#` are ignored.

- `--output-dir`, `-o`  
  Output base directory for mirrored files (default: `google_fonts_proxy`).

### Examples

Mirror a single font:
```bash
python3 mirror.py -f "Roboto:wght@400;700"
```

Mirror multiple fonts from a file:
```bash
python3 mirror.py --fonts-file fonts.txt
```

Specify a custom output directory:
```bash
python3 mirror.py -f "Roboto" -o my_fonts
```


### Notes
- At least one font must be specified via `--fonts` or `--fonts-file`.
- The script will create `css` and `fonts` subdirectories inside the specified output directory (e.g., `output-dir/css` and `output-dir/fonts`).
- The rewritten CSS will reference the locally downloaded font files.

## License

[MIT License](LICENSE) (SPDX: MIT)