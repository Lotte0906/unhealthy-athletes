# Development Notes

This document records important decisions, limitations, and planned improvements for the **Olympic Athletes and Longevity** project. It complements `README.md`, which describes the project's purpose and usage.

This is a retrospective record, not a complete development history. Details that have not been verified are explicitly identified.

## 1. Project Direction

**Research goal:** Investigate whether Olympic athletes have different lifespans from comparable individuals in the general population.

**Current priority:** Establish a reliable athlete-level dataset before drawing conclusions about longevity.

**Development principles:**
- Prioritize data quality and reproducibility.
- Preserve earlier results for comparison with improved methods.
- Keep data collection, processing, and analysis separate where practical.
- Use automated tests to check important functionality.

## 2. Data Sources

The current workflow uses three input datasets:

| File | Source | Purpose |
|---|---|---|
| `athlete_events.csv` | [120 Years of Olympic History (Kaggle)](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results) | Olympic participation records |
| `bios.csv` | [KeithGalli/Olympics-Dataset — athletes/bios.csv](https://github.com/KeithGalli/Olympics-Dataset/blob/master/athletes/bios.csv) | Athlete names and identifiers |
| `results.csv` | [KeithGalli/Olympics-Dataset — results/results.csv](https://github.com/KeithGalli/Olympics-Dataset/blob/master/results/results.csv) | Olympic event results and participation years |

The `bios.csv` and `results.csv` datasets originate from Olympedia and were collected by Keith Galli using Python and Beautiful Soup.

### Source verification — 16 November 2026

The original download locations of `bios.csv` and `results.csv` were initially undocumented.

The source was subsequently identified as Keith Galli's `Olympics-Dataset` GitHub repository.

The local datasets were compared with the repository versions using pandas. All checks returned `True` for both files:

- Identical column names and order.
- Identical row counts.
- Identical DataFrame contents (`DataFrame.equals()`).

The local datasets therefore match the published versions at the time of verification. Byte-for-byte file identity was not checked.

The verified local datasets contain:

| File | Rows | Columns |
|---|---:|---:|
| `bios.csv` | 145,500 | 16 |
| `results.csv` | 308,408 | 11 |

All three input datasets are excluded from Git tracking. Generated datasets and scraping results are also excluded.

For stronger long-term reproducibility, the specific source repository commit and dataset file hashes could be recorded in the future.

## 3. Athlete Matching

### Kaggle to Olympedia

The current matching procedure uses normalized athlete names and overlapping Olympic participation years.

A match is accepted only when exactly one Olympedia athlete satisfies both conditions.

**Reason:** Matching by name alone risks confusing athletes who share a name. Olympic participation years provide an additional identifying criterion.

**Known limitations:**
- A unique match does not guarantee correct identification.
- Name normalization removes non-ASCII characters rather than transliterating them.
- Some legitimate matches may be missed because of name variations.

### Olympedia to Wikidata

The current biographical collection procedure searches Wikidata using athlete names, preferring the Olympedia name when available.

The initial Wikidata search procedure selects the first search result.

**Known limitation:** The first result is not necessarily the correct athlete.

**Planned improvement:** Evaluate multiple Wikidata candidates using additional identifying information, and compare the improved method against the original results.

## 4. Biographical Data Collection

The scraping workflow retrieves biographical information, including birthdates, deathdates, and available identifying information.

Important implementation decisions include:

- Scrape each athlete once per batch.
- Merge collected information using athlete IDs rather than names.
- Preserve diagnostic error messages.
- Handle missing and problematic dates explicitly.
- Calculate ages using a specified reference date.

### Batch Processing

The workflow divides athletes into batches to support long-running data collection.

Previously generated batch files can be reused, but only after validation.

The updated implementation uses companion JSON metadata containing information such as:

- Processing version.
- Reference date.
- Batch number and total number of batches.
- Input fingerprint.
- Row count.
- Output file hash.

**Reason:** An existing batch file should not be assumed compatible with the current workflow merely because its filename matches.

Incompatible files are not automatically overwritten.

Older batches without metadata require explicit adoption, and their original processing settings cannot be fully verified.

**Outstanding issue:** Existing batches from earlier runs must be inspected before resuming scraping. Some may not satisfy the newer validation requirements.

## 5. Data Quality

An exploratory analysis of 5,693 athletes investigated the availability and consistency of biographical information.

The preliminary findings include:

- Multiple Wikidata search results are associated with more detected chronological inconsistencies.
- Biographical information availability varies across Olympic generations.
- Chronological inconsistencies are generally more frequent among earlier generations.

These findings help identify potential data-quality problems but do not establish that particular athlete matches are incorrect.

Improving athlete identification is the next major development priority.

## 6. Code Organization

The project originally contained its Python modules directly in the repository root.

In November 2026, the modules were moved into the `unhealthy_athletes/` package, while `main.py` remained in the root.

**Reason:** Separate the core application code from datasets, notebooks, tests, and documentation, while making future expansion easier.

Imports were updated accordingly.

All automated tests passed after the restructuring.

## 7. Testing

The project uses pytest for automated testing.

Tests have been developed for data processing and scraping workflow behavior, including batch validation and resumption.

**Development approach:**
- Run tests after meaningful changes.
- Keep structural refactoring separate from changes to processing logic.
- Add tests for important new behavior and previously identified errors.

## 8. Repository Management

In November 2026, the repository was cleaned up.

Changes included:

- Adding `requirements.txt`.
- Excluding downloaded and generated datasets through `.gitignore`.
- Removing previously tracked CSV files from the current repository state.
- Organizing Python modules into a package.

Local copies of the datasets and earlier results were retained.

Historical Git commits may still contain files removed from the current repository.

### Generated Matching Datasets

The athlete-matching workflow saves two intermediate datasets:

- `data/olympedia_name_matches.csv`: Contains unique matches between
  Kaggle and Olympedia athletes.
- `data/olympedia_all_athletes.csv`: Contains all Kaggle athletes,
  including unmatched or ambiguous cases.

These files are saved to support debugging, data-quality analysis,
and comparisons between different versions of the matching algorithm.

They are generated by `prepare_athletes()` and are not required
as inputs to the current workflow.

During repository cleanup in November 2026, an older copy of
`olympedia_all_athletes.csv` was identified in `notebooks/`.
This redundant copy was removed from Git tracking.

Generated datasets are kept locally in `data/` and excluded
from version control.

### Notebook Cleanup — November 2026

The notebooks were reorganized to distinguish between project documentation and personal development experiments.

**Decision:**
- Keep notebooks containing relevant analyses or useful demonstrations in the GitHub repository.
- Keep personal experiments, exploratory code, and temporary testing notebooks locally, excluding them through `.gitignore`.
- Avoid maintaining multiple published versions of the same analysis.

The revised Wikidata quality report replaced the original and was renamed to `wikidata_quality_report.ipynb`.

**Reason:** Keep the public repository focused on useful, understandable project work while preserving experimental notebooks locally for future reference.

Previously tracked experimental notebooks were removed from Git tracking without deleting their local copies. Earlier versions remain accessible through Git history.

## 9. Planned Development

The current priorities are:

- [x] **Reproducibility:** Verify the exact sources of the Olympedia CSV files and complete the setup documentation. **Completed: 16 November 2026**
- [x] **Repository cleanup:** Review outdated notebooks, remove redundant files, organize published and personal notebooks, and update repository documentation. **Completed: 16 November 2026**- [ ] **Athlete matching:** Improve name normalization and evaluate matching reliability.
- [ ] **Wikidata matching:** Investigate multiple candidates rather than automatically selecting the first result.
- [ ] **Validation:** Compare improved matching results with the original baseline.
- [ ] **Data collection:** Extend biographical coverage using the improved procedure.
- [ ] **Analysis:** Investigate longevity using suitable comparison populations and statistical methods, accounting for athletes who are still alive.

## 10. Maintaining This Document

Add an entry whenever an important technical decision is made or a substantial limitation is discovered.

Record the following where relevant:

- **Date:** When the decision was made.
- **Decision:** What was changed or selected.
- **Reason:** Why this approach was chosen.
- **Alternatives:** Other approaches considered, if relevant.
- **Verification:** Tests, analyses, or other evidence supporting the decision.
- **Outstanding questions:** Anything that remains uncertain.

Small implementation changes do not need individual entries.

The README remains the primary guide for users. This document preserves the reasoning behind important development decisions.