---
name: rtf-clinical-tables
description: Generate and manipulate RTF tables for clinical trial study reports (CSRs), regulatory submissions, and pharmaceutical TLFs. Use when the user mentions RTF tables, clinical study reports, TLFs (tables/listings/figures), regulatory submissions, adverse event tables, disposition tables, efficacy tables, demographic tables, CSR outputs, ICH E3, eCTD, r2rtf, pharmaRTF, or asks to create/edit/debug RTF files for pharma or clinical trial reporting. Also use when asked to write raw RTF control words for tables, or to understand RTF table structure.
---

# RTF Clinical Trial Tables

Generate production-ready RTF tables for clinical trial study reports following pharmaceutical industry conventions and ICH E3 guidance.

## When This Skill Applies

- Creating RTF table output for clinical study reports (CSRs)
- Writing or debugging raw RTF control words for tables
- Building R scripts that generate RTF tables (r2rtf, pharmaRTF, gt, huxtable)
- Formatting TLFs (Tables, Listings, Figures) for regulatory submissions
- Converting data into pharma-standard RTF table layouts
- Understanding RTF table structure and control word syntax

## RTF Table Fundamentals

### Core Concept

There is no RTF "table group." A table is a sequence of paragraphs partitioned into cells. Each row is defined by control words, not by a container element.

### Table Row Lifecycle

```
\trowd          ← Reset row defaults, begin row definition
  [row props]   ← Row-level settings (height, alignment, borders)
  [cell defs]   ← Cell definitions (\cellx with borders, merge, shading)
\pard\intbl     ← Paragraph inside table
  [content]     ← Cell text with character/paragraph formatting
\cell           ← End of cell
  ...repeat for each cell...
\row            ← End of row
```

### Critical Rules

1. **`\cellx` values are cumulative right boundaries**, not individual widths. For 3 equal columns of 3000tw each: `\cellx3000 \cellx6000 \cellx9000`
2. **Number of `\cellx` must equal number of `\cell`** in each row — mismatch corrupts the table
3. **`\intbl` is required** on every paragraph inside a table (or inherited from the preceding paragraph)
4. **`\trowd` resets row properties** — omit it only when intentionally inheriting from the previous row
5. **Font sizes are in half-points**: `\fs20` = 10pt, `\fs16` = 8pt, `\fs18` = 9pt
6. **1 inch = 1440 twips** (twip = 1/20 of a point, 72 points/inch)

### Measurement Quick Reference

| Inches | Twips | Common Use |
|--------|-------|------------|
| 0.1"   | 144   | Cell padding |
| 0.5"   | 720   | Narrow column |
| 1.0"   | 1440  | Standard margin, medium column |
| 1.25"  | 1800  | Default margin |
| 8.5"   | 12240 | Letter width (portrait) / height (landscape) |
| 11.0"  | 15840 | Letter height (portrait) / width (landscape) |

## Document Template for Clinical Trial RTF

Every clinical trial RTF table document follows this structure:

```rtf
{\rtf1\ansi\deff0
{\fonttbl{\f0\fmodern Courier New;}{\f1\froman Times New Roman;}}
{\colortbl;\red0\green0\blue0;\red192\green192\blue192;\red255\green255\blue255;}
\paperw15840\paperh12240\landscape
\margl1440\margr1440\margt1440\margb1440
\widowctrl

{\header\pard\qc\fs20\b Table 14.X.X\b0\par
\pard\qc\fs20 Table Title Here\par
\pard\qc\fs18\i (Analysis Population)\i0\par
\par}

{\footer\pard\ql\fs16 Source: program_name.R \tab Run date: YYYY-MM-DD\par
\pard\qr\fs16 Page {\field{\*\fldinst PAGE}} of {\field{\*\fldinst NUMPAGES}}\par}

[TABLE CONTENT HERE]

}
```

### Key Document Properties

| Property | Standard Value | Control Words |
|----------|---------------|---------------|
| Orientation | Landscape | `\paperw15840\paperh12240\landscape` |
| Margins | 1 inch all | `\margl1440\margr1440\margt1440\margb1440` |
| Body font | Courier New 9pt | `\f0\fs18` |
| Header font | Courier New 10pt bold | `\f0\fs20\b` |
| Title font | 10pt, centered | `\qc\fs20` |
| Footnote font | 8pt, left-aligned | `\ql\fs16` |

## Generating Table Content

### Standard Column Header (repeating on each page)

Use `\trhdr` to make a header row repeat on each page:

```rtf
\trowd\trhdr\trgaph108\trql
\clbrdrt\brdrs\clbrdrb\brdrs\cellx3600
\clbrdrt\brdrs\clbrdrb\brdrs\cellx6000
\clbrdrt\brdrs\clbrdrb\brdrs\cellx8400
\clbrdrt\brdrs\clbrdrb\brdrs\cellx10800
\pard\intbl\ql\b\fs18 Variable\b0\cell
\pard\intbl\qc\b\fs18 Placebo\line (N=86)\b0\cell
\pard\intbl\qc\b\fs18 Low Dose\line (N=84)\b0\cell
\pard\intbl\qc\b\fs18 High Dose\line (N=84)\b0\cell
\row
```

### Spanning Column Headers (Merged Cells)

Use `\clmgf` / `\clmrg` for horizontal merge. Merge control words must precede the `\cellx` for that cell:

```rtf
\trowd\trhdr\trgaph108
\clbrdrt\brdrs\cellx3600
\clmgf\clbrdrt\brdrs\clbrdrb\brdrs\cellx6000
\clmrg\clbrdrt\brdrs\clbrdrb\brdrs\cellx8400
\clmrg\clbrdrt\brdrs\clbrdrb\brdrs\cellx10800
\pard\intbl\ql\fs18\cell
\pard\intbl\qc\b\fs18 Treatment Group\b0\cell
\pard\intbl\cell
\pard\intbl\cell
\row
```

Note: Every merged cell still requires a matching `\cell` control word. Content in `\clmrg` cells is ignored by Word.

### Data Rows

```rtf
\trowd\trgaph108
\cellx3600\cellx6000\cellx8400\cellx10800
\pard\intbl\ql\fs18   Age (years)\cell
\pard\intbl\qc\fs18 65.3 (10.2)\cell
\pard\intbl\qc\fs18 63.8 (9.7)\cell
\pard\intbl\qc\fs18 64.1 (10.5)\cell
\row
```

### Indented Category Rows

Use `\li` for left indent (in twips). 360tw ~ 0.25 inch:

```rtf
\pard\intbl\ql\li360\fs18 Male\cell
```

### Bottom Border on Last Row

Apply `\clbrdrb\brdrs` to each cell definition in the final data row:

```rtf
\trowd\trgaph108
\clbrdrb\brdrs\cellx3600
\clbrdrb\brdrs\cellx6000
\clbrdrb\brdrs\cellx8400
\clbrdrb\brdrs\cellx10800
```

## Pharma Table Border Conventions

Clinical trial tables use **minimal borders** — horizontal only, no vertical:

- **Top border** on first header row
- **Bottom border** below header row(s)
- **Bottom border** on last data row
- **No vertical borders** between columns
- **No internal horizontal borders** between data rows

This produces the clean "open" table standard in pharma:

```
────────────────────────────────────────────────────
 Variable     Placebo       Low Dose      High Dose
────────────────────────────────────────────────────
 Age          65.3 (10.2)   63.8 (9.7)    64.1 (10.5)
 Sex, n (%)
   Male       50 (58.1)     44 (52.4)     46 (54.8)
   Female     36 (41.9)     40 (47.6)     38 (45.2)
────────────────────────────────────────────────────
```

## Cell Merging

### Horizontal Merge

`\clmgf` on the first cell, `\clmrg` on subsequent cells in the span. All merged cells still need matching `\cell` control words — content in `\clmrg` cells is ignored by the renderer.

### Vertical Merge

`\clvmgf` on the first row's cell, `\clvmrg` on subsequent rows' cells in the same column position.

**Compatibility warning**: Vertical merge (`\clvmgf`/`\clvmrg`) was introduced in Word 97 and only renders reliably in Microsoft Word. LibreOffice has historically had issues with vertical RTF merges. If cross-platform rendering matters, consider alternative layouts.

## Special Characters and Superscripts

### Superscript Footnote References

```rtf
Treatment{\super a}
```

### Common Symbols in Clinical Tables

| Symbol | RTF Code | Use Case |
|--------|----------|----------|
| ≤      | `\u8804?` | Lab thresholds |
| ≥      | `\u8805?` | Lab thresholds |
| ±      | `\u177?`  | Mean ± SD |
| ×      | `\u215?`  | Multiplication |
| α      | `\u945?`  | Significance level |
| β      | `\u946?`  | Beta coefficient |
| —      | `\emdash` | Missing data |
| –      | `\endash` | Ranges |
| †      | `\u8224?` | Footnote marker |
| ‡      | `\u8225?` | Footnote marker |

The `?` after `\u` escapes is the fallback character for readers that don't support Unicode.

## R Package Guidance

### r2rtf Workflow (Merck)

The standard pipe-based workflow for generating TLFs:

```r
library(r2rtf)
library(dplyr)

data_frame %>%
  rtf_page(orientation = "landscape",
           width = 11, height = 8.5) %>%
  rtf_title("Table 14.1.1",
            "Summary of Demographics",
            "(Safety Analysis Population)") %>%
  rtf_colheader(" | Placebo | Low Dose | High Dose",
                col_rel_width = c(3, 2, 2, 2)) %>%
  rtf_colheader(" | n | (%) | n | (%) | n | (%)",
                col_rel_width = c(3, rep(c(0.7, 1.3), 3)),
                border_top = c("", rep("single", 6)),
                border_left = c("single", rep(c("single", ""), 3))) %>%
  rtf_body(col_rel_width = c(3, rep(c(0.7, 1.3), 3)),
           text_justification = c("l", rep("c", 6)),
           border_left = c("single", rep(c("single", ""), 3))) %>%
  rtf_footnote("Note: Percentages based on N in column header.") %>%
  rtf_source("Program: t-14-01-01.R") %>%
  rtf_encode() %>%
  write_rtf("tlf/t_14_01_01.rtf")
```

**Key r2rtf functions:**

| Function | Purpose |
|----------|---------|
| `rtf_page()` | Orientation, size, margins |
| `rtf_title()` | Vector of title lines (placed in RTF header) |
| `rtf_colheader()` | `\|`-separated column headers; call multiple times for multi-row headers |
| `rtf_body()` | Data rows with cell-level formatting |
| `rtf_footnote()` | Footnotes (placed in RTF footer) |
| `rtf_source()` | Data source line |
| `rtf_encode()` | Convert attributes to RTF encoding |
| `write_rtf()` | Write to .rtf file |

**Cell-level formatting arguments (vectorized — one value per column):**
- `col_rel_width` — Relative column widths (numeric vector)
- `text_justification` — `"l"` (left), `"c"` (center), `"r"` (right), `"d"` (decimal)
- `text_format` — `"b"` (bold), `"i"`, `"u"`, or combinations like `"bi"`
- `border_top`, `border_bottom`, `border_left`, `border_right` — `"single"`, `"double"`, `""` (none)
- `text_font_size` — Numeric, per-cell font sizes
- `text_color`, `background_color` — Per-cell colors

**Advanced features:**
- `page_by` / `new_page` — Pagination by grouping variable
- Pass a `list()` of encoded tables to `rtf_encode()` to concatenate multiple tables
- `subline_by` — Sublines for listings (subject/site info repeating)

### pharmaRTF Workflow (Atorus Research)

Wraps huxtable or GT tables with pharma-required RTF document metadata:

```r
library(pharmaRTF)
library(huxtable)

doc <- rtf_doc(huxtable_table,
  titles = list(
    hf_line("Table 14.1.1", bold = TRUE),
    hf_line("Summary of Demographics"),
    hf_line("(Safety Analysis Population)", italic = TRUE)
  ),
  footnotes = list(
    hf_line("Source: t-14-01-01.R", align = "left")
  )
)
font(doc) <- "Courier New"
font_size(doc) <- 9
orientation(doc) <- "landscape"
write_rtf(doc, file = "output.rtf")
```

### Other R Packages

| Package | Best For |
|---------|----------|
| `rtables` | Hierarchical tables with cell-level multi-values, complex grouping |
| `huxtable` | Flexible formatting; consumed by pharmaRTF for RTF output |
| `gt` | Grammar of tables; can output RTF via `gtsave(..., "file.rtf")` |
| `flextable` | Tables for Word/HTML/PDF with consistent styling |

## Common Clinical Trial Table Patterns

### Disposition Table
- Rows: Randomized, Completed, Discontinued (with indented reasons)
- Columns: Treatment arms with n and (%)

### Demographics / Baseline Characteristics
- Rows: Age, Sex, Race, BMI, etc.
- Columns: Treatment arms with N, Mean (SD) or n (%)
- Continuous variables: Mean (SD), Median, Min–Max
- Categorical variables: n (%)

### Adverse Event Summary
- Rows: AE categories (TEAEs, SAEs, Drug-related, by SOC/Preferred Term)
- Columns: Treatment arms with n (%) or n/N (%)
- Indentation: SOC level → Preferred Term level

### Efficacy Results (ANCOVA)
- Rows: Treatment groups
- Columns: N, Baseline Mean (SD), Endpoint Mean (SD), LS Mean Change (SE), Difference vs Placebo (95% CI), p-value

### Laboratory Shift Table
- Rows: Lab parameters
- Columns: Baseline category (Normal/Low/High) × Post-baseline category (Normal/Low/High)

## Debugging RTF Tables

### Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Columns misaligned | `\cellx` count ≠ `\cell` count | Ensure exact match in every row |
| Content outside table | Missing `\intbl` | Add `\pard\intbl` before cell content |
| Row properties wrong | Missing `\trowd` | Add `\trowd` to reset row defaults |
| Font size unexpected | Half-point confusion | `\fs18` = 9pt, not 18pt |
| Borders missing | No style after border control | Add `\brdrs` after `\clbrdrt`, `\clbrdrb`, etc. |
| Headers not repeating | Missing `\trhdr` | Add `\trhdr` after `\trowd` on header rows |
| Merged cells separate | Missing merge words | `\clmgf`/`\clmrg` must precede `\cellx` for that cell |
| Vertical merge broken | Non-Word reader | `\clvmgf`/`\clvmrg` only reliable in Microsoft Word |
| Page overflows right | Column widths exceed margins | Last `\cellx` must be ≤ page width minus margins |

### Validation Checklist

1. Document opens correctly in Microsoft Word
2. Titles appear on every page (in `\header`)
3. Column headers repeat on every page (`\trhdr`)
4. Footnotes appear on every page (in `\footer`)
5. "Page X of Y" is correct
6. Column widths are proportional and within page margins
7. Font type and size are consistent
8. Borders follow pharma minimal style (horizontal only)
9. Indentation levels are consistent for category rows
10. Special characters render correctly (≤, ≥, ±)

## Reference

For the complete RTF control word reference covering all row, cell, border, merge, character, and paragraph control words, see `REFERENCE.md` in this skill directory.
