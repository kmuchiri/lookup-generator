# Athletics Lookup Generator

A set of Python scripts to parse World Athletics scoring table PDFs and generate unified points lookup tables.

## Overview

- **PDF Parser (`pdf_parser.py`)**: Extracts data from the WA scoring tables PDF into individual discipline CSV files in `data/table_subdatasets/`.
- **Lookup Generator (`lookup.py`)**: Merges the discipline subdatasets into a consolidated lookup table (`data/lookup/lookup_table.csv`) covering points 1 to 1400, and generates discipline metadata in `data/lookup/disciplines.json`.

## Requirements

- Python 3
- `pandas`
- `pdftotext` (from `poppler-utils`, required by `pdf_parser.py`)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Extract discipline datasets from the PDF:

```bash
python3 pdf_parser.py
```

1. Build the consolidated lookup table and metadata:

```bash
python3 lookup.py
```

## Outputs

- `data/lookup/lookup_table.csv`: Lookup table mapping points (1400 down to 1) across all track and field disciplines.
- `data/lookup/disciplines.json`: Metadata dictionary for each discipline including display name, gender, category, unit, and scoring direction.
