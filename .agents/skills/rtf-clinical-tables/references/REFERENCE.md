# RTF Control Word Reference for Clinical Trial Tables

Complete reference for RTF control words used in pharmaceutical table generation. Organized by category.

## Document-Level Control Words

| Control Word | Meaning | Default | Example |
|---|---|---|---|
| `\rtf1` | RTF version 1 | Required | `{\rtf1\ansi ...}` |
| `\ansi` | ANSI character set | — | `{\rtf1\ansi ...}` |
| `\deff0` | Default font index | 0 | `\deff0` |
| `\paperw` N | Paper width in twips | 12240 (8.5") | `\paperw15840` (11") |
| `\paperh` N | Paper height in twips | 15840 (11") | `\paperh12240` (8.5") |
| `\landscape` | Landscape orientation | Portrait | `\landscape` |
| `\margl` N | Left margin in twips | 1800 | `\margl1440` (1") |
| `\margr` N | Right margin in twips | 1800 | `\margr1440` (1") |
| `\margt` N | Top margin in twips | 1440 | `\margt1440` (1") |
| `\margb` N | Bottom margin in twips | 1440 | `\margb1440` (1") |
| `\widowctrl` | Enable widow/orphan control | Off | `\widowctrl` |
| `\deftab` N | Default tab width in twips | 720 | `\deftab720` |

## Font Table

Required in every RTF document. Defines fonts by index.

```rtf
{\fonttbl
  {\f0\fmodern Courier New;}
  {\f1\froman Times New Roman;}
  {\f2\fswiss Arial;}
}
```

| Font Family | Code | Typical Use |
|---|---|---|
| Modern (monospace) | `\fmodern` | Courier New — primary pharma font |
| Roman (serif) | `\froman` | Times New Roman — alternative body font |
| Swiss (sans-serif) | `\fswiss` | Arial — occasional use |

## Color Table

Required for any text or background coloring. Index 0 is always auto/default (the entry before the first semicolon is empty).

```rtf
{\colortbl;
  \red0\green0\blue0;         % index 1: black
  \red192\green192\blue192;   % index 2: light gray
  \red255\green255\blue255;   % index 3: white
  \red255\green0\blue0;       % index 4: red
}
```

Reference colors with `\cf` N (text) or `\cb` N / `\clcbpat` N (background).

## Row-Level Control Words

| Control Word | Meaning | Notes |
|---|---|---|
| `\trowd` | Reset row defaults | Resets all row/cell properties; begin every new row definition |
| `\row` | End of row | Must appear after last `\cell` in the row |
| `\trgaph` N | Half-space between cells (twips) | Typical: 108 (0.075") |
| `\trrh` N | Row height (twips) | Positive = minimum; negative = exact |
| `\trleft` N | Left edge position relative to left margin | Default 0; negative values allowed |
| `\trkeep` | Prevent page break within row | Use for multi-line cells |
| `\trql` | Left-align row | Default |
| `\trqc` | Center-align row | |
| `\trqr` | Right-align row | |
| `\trautofit1` | Auto-fit row to content | |
| `\trhdr` | Header row — repeats on each page | Critical for pharma tables |
| `\trpaddl` N | Left cell padding (twips) | Requires `\trpaddfl3` for twip unit |
| `\trpaddr` N | Right cell padding (twips) | Requires `\trpaddfr3` for twip unit |
| `\trpaddt` N | Top cell padding (twips) | Requires `\trpaddft3` for twip unit |
| `\trpaddb` N | Bottom cell padding (twips) | Requires `\trpaddfb3` for twip unit |
| `\trpaddfl` N | Left padding unit type | 3 = twips |
| `\trpaddfr` N | Right padding unit type | 3 = twips |
| `\trpaddft` N | Top padding unit type | 3 = twips |
| `\trpaddfb` N | Bottom padding unit type | 3 = twips |

## Row Border Control Words

Applied after `\trowd`, these set default borders for the entire row:

| Control Word | Meaning |
|---|---|
| `\trbrdrt` | Top border for the row |
| `\trbrdrb` | Bottom border for the row |
| `\trbrdrl` | Left border for the row |
| `\trbrdrr` | Right border for the row |
| `\trbrdrh` | Horizontal border between cells |
| `\trbrdrv` | Vertical border between cells |

Each must be followed by a border style (e.g., `\trbrdrt\brdrs\brdrw10`).

## Cell Definition Control Words

Cell definitions appear between `\trowd` and the first `\pard\intbl`. One definition per cell, in left-to-right order.

| Control Word | Meaning | Notes |
|---|---|---|
| `\cellx` N | Right boundary of cell (twips) | **Cumulative from left margin**, not width |
| `\clvertalt` | Top vertical alignment | Default |
| `\clvertalc` | Center vertical alignment | |
| `\clvertalb` | Bottom vertical alignment | |
| `\cltxlrtb` | Text flows left-to-right, top-to-bottom | Default |
| `\clcbpat` N | Cell background color | Index into color table |
| `\clshdng` N | Cell shading in 0.01% | 0 = no shading, 10000 = solid |
| `\clftsWidth` N | Cell width type | 1=auto, 2=pct (50ths of %), 3=twips |
| `\clwWidth` N | Preferred cell width | Units from `\clftsWidth` |

## Cell Border Control Words

Applied per-cell in the cell definition block, before `\cellx`:

| Control Word | Meaning |
|---|---|
| `\clbrdrt` | Top border of cell |
| `\clbrdrb` | Bottom border of cell |
| `\clbrdrl` | Left border of cell |
| `\clbrdrr` | Right border of cell |

Each must be followed by a border style. Example: `\clbrdrt\brdrs\brdrw10`

## Border Style Control Words

Used after any border control word (row-level or cell-level):

| Control Word | Meaning |
|---|---|
| `\brdrs` | Single-thickness border |
| `\brdrth` | Thick border |
| `\brdrdb` | Double border |
| `\brdrdot` | Dotted border |
| `\brdrdash` | Dashed border |
| `\brdrdashsm` | Small dashed border |
| `\brdrdashd` | Dot-dashed border |
| `\brdrdashdd` | Double-dot-dashed border |
| `\brdrtriple` | Triple border |
| `\brdrsh` | Shadow border |
| `\brdrnone` | No border |
| `\brdrw` N | Border width in twips | Max 75; use `\brdrth` to double effective width |
| `\brdrcf` N | Border color | Index into color table |

**Pharma convention**: Use `\brdrs` (single) for all borders. Typical width: `\brdrw10` (0.5pt).

## Cell Merging Control Words

### Horizontal Merge

| Control Word | Meaning | Placement |
|---|---|---|
| `\clmgf` | First cell in horizontal merge | Before `\cellx` of first merged cell |
| `\clmrg` | Subsequent merged cells | Before `\cellx` of each additional cell |

Content goes in the `\clmgf` cell. `\clmrg` cells still need `\cell` but content is ignored.

### Vertical Merge

| Control Word | Meaning | Placement |
|---|---|---|
| `\clvmgf` | First cell in vertical merge (top row) | Before `\cellx` |
| `\clvmrg` | Subsequent merged cells (lower rows) | Before `\cellx` in same column position |

**Compatibility**: Word 97+. Limited support in LibreOffice/OpenOffice.

## Cell Content Control Words

| Control Word | Meaning |
|---|---|
| `\cell` | End of cell content |
| `\intbl` | Marks paragraph as part of a table |
| `\nestcell` | End of nested cell (nested tables) |
| `\nestrow` | End of nested row (nested tables) |
| `\itap` N | Nesting level (1 = outermost) |

## Character Formatting Control Words

| Control Word | Meaning | Toggle Off |
|---|---|---|
| `\b` | Bold | `\b0` |
| `\i` | Italic | `\i0` |
| `\ul` | Underline | `\ul0` |
| `\strike` | Strikethrough | `\strike0` |
| `\super` | Superscript | `\nosupersub` |
| `\sub` | Subscript | `\nosupersub` |
| `\fs` N | Font size in **half-points** | — |
| `\f` N | Font index from font table | — |
| `\cf` N | Text color (color table index) | — |
| `\cb` N | Text background color | — |
| `\plain` | Reset all character formatting | — |

### Font Size Reference

| `\fs` Value | Point Size | Pharma Use |
|---|---|---|
| `\fs14` | 7pt | — |
| `\fs16` | 8pt | Footnotes |
| `\fs18` | 9pt | Body text (standard) |
| `\fs20` | 10pt | Titles, headers |
| `\fs22` | 11pt | — |
| `\fs24` | 12pt | — |

## Paragraph Formatting Control Words

| Control Word | Meaning | Notes |
|---|---|---|
| `\pard` | Reset paragraph formatting | Always use before `\intbl` in table cells |
| `\ql` | Left-align | Default |
| `\qc` | Center-align | Numeric columns in pharma tables |
| `\qr` | Right-align | Numeric columns (alternative) |
| `\qj` | Justify | Rarely used in tables |
| `\li` N | Left indent (twips) | 360tw = ~0.25"; used for category indentation |
| `\ri` N | Right indent (twips) | |
| `\fi` N | First-line indent (twips) | Negative = hanging indent |
| `\sa` N | Space after paragraph (twips) | |
| `\sb` N | Space before paragraph (twips) | |
| `\sl` N | Line spacing | Positive = at least; negative = exact |
| `\line` | Line break (no new paragraph) | Multi-line cell content |
| `\tab` | Tab character | |
| `\par` | Paragraph break | |

## Headers and Footers

| Control Word | Meaning |
|---|---|
| `{\header ...}` | Page header (all pages) |
| `{\footer ...}` | Page footer (all pages) |
| `{\headerl ...}` | Left-page header (with `\facingp`) |
| `{\headerr ...}` | Right-page header (with `\facingp`) |
| `{\footerl ...}` | Left-page footer |
| `{\footerr ...}` | Right-page footer |

### Page Fields

```rtf
{\field{\*\fldinst PAGE}}       % Current page number
{\field{\*\fldinst NUMPAGES}}   % Total page count
```

## Section Control Words

| Control Word | Meaning |
|---|---|
| `\sect` | Section break |
| `\sectd` | Reset section defaults |
| `\sbknone` | No section break |
| `\sbkpage` | Page break before section |
| `\sbkcol` | Column break before section |

## Unicode and Special Characters

### Encoding Pattern

```rtf
\u<decimal_code>?
```

The `?` is the fallback character for non-Unicode readers. For multi-byte fallbacks, precede with `\uc` N where N is the number of fallback bytes.

### Common Clinical Symbols

| Symbol | Decimal | RTF Code | Use |
|---|---|---|---|
| ≤ | 8804 | `\u8804?` | Less than or equal |
| ≥ | 8805 | `\u8805?` | Greater than or equal |
| ± | 177 | `\u177?` | Plus-minus (Mean ± SD) |
| × | 215 | `\u215?` | Multiplication |
| ÷ | 247 | `\u247?` | Division |
| α | 945 | `\u945?` | Alpha (significance level) |
| β | 946 | `\u946?` | Beta |
| γ | 947 | `\u947?` | Gamma |
| δ | 948 | `\u948?` | Delta |
| μ | 956 | `\u956?` | Mu (micro) |
| σ | 963 | `\u963?` | Sigma (std deviation) |
| χ | 967 | `\u967?` | Chi (chi-square test) |
| † | 8224 | `\u8224?` | Dagger (footnote) |
| ‡ | 8225 | `\u8225?` | Double dagger (footnote) |
| ° | 176 | `\u176?` | Degree |
| ² | 178 | `\u178?` | Superscript 2 |
| ³ | 179 | `\u179?` | Superscript 3 |
| ½ | 189 | `\u189?` | One half |

### Built-in Special Characters

| Character | RTF Code |
|---|---|
| Em dash (—) | `\emdash` |
| En dash (–) | `\endash` |
| Non-breaking space | `\~` |
| Non-breaking hyphen | `\_` |
| Optional hyphen | `\-` |
| Bullet | `\bullet` |
| Left single quote (') | `\lquote` |
| Right single quote (') | `\rquote` |
| Left double quote (") | `\ldblquote` |
| Right double quote (") | `\rdblquote` |

## Landscape US Letter Dimensions (Clinical Trial Standard)

```
Paper: \paperw15840 \paperh12240 \landscape
       (11" wide × 8.5" tall in landscape)

Margins: \margl1440 \margr1440 \margt1440 \margb1440
         (1" all sides)

Usable width: 15840 - 1440 - 1440 = 12960 twips (9 inches)
Usable height: 12240 - 1440 - 1440 = 9360 twips (6.5 inches)

Maximum \cellx value for last column: 12960
(assuming \trleft is 0 / default)
```

## Complete Minimal Example

A demographics table with spanning header, pharma-style borders:

```rtf
{\rtf1\ansi\deff0
{\fonttbl{\f0\fmodern Courier New;}}
{\colortbl;\red0\green0\blue0;}
\paperw15840\paperh12240\landscape
\margl1440\margr1440\margt1440\margb1440
\widowctrl\f0

{\header\pard\qc\b\fs20 Table 14.1.1\b0\par
\pard\qc\fs20 Summary of Demographics\par
\pard\qc\fs18\i (Safety Analysis Population)\i0\par\par}

{\footer\pard\ql\fs16 Source: t-14-01-01.R  Run: 2025-06-15\par
\pard\qr\fs16 Page {\field{\*\fldinst PAGE}} of {\field{\*\fldinst NUMPAGES}}\par}

\trowd\trhdr\trgaph108
\clbrdrt\brdrs\brdrw10\cellx4320
\clmgf\clbrdrt\brdrs\brdrw10\clbrdrb\brdrs\brdrw10\cellx7560
\clmrg\clbrdrt\brdrs\brdrw10\clbrdrb\brdrs\brdrw10\cellx10800
\pard\intbl\ql\b\fs18\cell
\pard\intbl\qc\b\fs18 Treatment Group\cell
\pard\intbl\cell
\row

\trowd\trhdr\trgaph108
\clbrdrb\brdrs\brdrw10\cellx4320
\clbrdrb\brdrs\brdrw10\cellx7560
\clbrdrb\brdrs\brdrw10\cellx10800
\pard\intbl\ql\b\fs18 Variable\b0\cell
\pard\intbl\qc\b\fs18 Placebo\line (N=86)\b0\cell
\pard\intbl\qc\b\fs18 Active\line (N=84)\b0\cell
\row

\trowd\trgaph108
\cellx4320\cellx7560\cellx10800
\pard\intbl\ql\fs18 Age (years), Mean (SD)\cell
\pard\intbl\qc\fs18 65.3 (10.2)\cell
\pard\intbl\qc\fs18 63.8 (9.7)\cell
\row

\trowd\trgaph108
\cellx4320\cellx7560\cellx10800
\pard\intbl\ql\fs18 Sex, n (%)\cell
\pard\intbl\qc\fs18\cell
\pard\intbl\qc\fs18\cell
\row

\trowd\trgaph108
\cellx4320\cellx7560\cellx10800
\pard\intbl\ql\li360\fs18 Male\cell
\pard\intbl\qc\fs18 50 (58.1)\cell
\pard\intbl\qc\fs18 44 (52.4)\cell
\row

\trowd\trgaph108
\clbrdrb\brdrs\brdrw10\cellx4320
\clbrdrb\brdrs\brdrw10\cellx7560
\clbrdrb\brdrs\brdrw10\cellx10800
\pard\intbl\ql\li360\fs18 Female\cell
\pard\intbl\qc\fs18 36 (41.9)\cell
\pard\intbl\qc\fs18 40 (47.6)\cell
\row

}
```
