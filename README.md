# deltable

CLI tool for comparing table structure across `.html` and `.rtf` files.

## Installation

```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install .
```

## RTF conversion dependency

RTF comparisons require LibreOffice and `soffice` available on `PATH`.

## Usage

```bash
deltable compare --input pairs.csv --output results.csv
```

```bash
Usage: deltable compare [OPTIONS]

  Compare table pairs listed in a CSV file.

  The input CSV must have ``left_path`` and ``right_path`` columns. Each path
  may point to an ``.html`` or ``.rtf`` file.  RTF files are converted to HTML
  automatically before comparison.

Options:
  --input PATH   [required]
  --output PATH  [required]
  --help         Show this message and exit.
```

### Example input (`pairs.csv`)

```csv
left_path,right_path
tests/data/html/baseline/ds_table.html,tests/data/html/variants/ds_table_changed_values.html
tests/data/rtf/ds_table.rtf,tests/data/rtf/ds_table.rtf
tests/data/html/baseline/ds_table.html,tests/data/rtf/ds_table.rtf
```

### Example output (`results.csv`)

```csv
left_path,right_path,structure_match,summary
tests/data/html/baseline/ds_table.html,tests/data/html/variants/ds_table_changed_values.html,True,all tables identical (1 table(s) compared)
tests/data/rtf/ds_table.rtf,tests/data/rtf/ds_table.rtf,True,all tables identical (1 table(s) compared)
tests/data/html/baseline/ds_table.html,tests/data/rtf/ds_table.rtf,True,all tables identical (1 table(s) compared)
```

## Disclaimer

`deltable` currently compares table structure, not full semantic/statistical
equivalence for clinical reporting.
