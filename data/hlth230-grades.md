# HLTH 230 final course grades by term

`hlth230-grades.csv` feeds the figure in `figures/hlth230-grades.tex` (APR version only).
Term-level summaries only; no student data.

- `term`: W = Winter, S = Spring, then the two-digit year.
- `mean`, `median`, `mode`: final course grade (%).
- `mine`: 1 for the terms Jim taught (Winter 2020, Winter 2026, Spring 2026).
- `source`:
  - `IAP`: Institutional Analysis & Planning, request IAP-391 "HLTH 230 Historical Grade
    Data" (V1, 8 July 2026): IAP count-date database based on Quest, Winter 2017 to
    Spring 2025. Means rounded to two decimals.
  - `LEARN`: LEARN Final Adjusted Grade class statistics: Winter 2026 (118 of 122 grades) and
    Spring 2026 (143 of 145 grades). LEARN's mode is taken over unrounded percentages (Winter
    2026 has two: 94.63 and 95.34), so it is not comparable with IAP's whole-number modes and
    is left as `nan`.

If IAP's later extract (V2) covers 2026, its figures can replace the LEARN rows, modes included.
