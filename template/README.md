# Faculty of Health CV template (with APR highlighting)

A LaTeX template for the University of Waterloo Faculty of Health CV format. It
also produces an APR (Annual Performance Review) version that colours
review-period items in the colours the Faculty asks for. The directory holds no
one's CV. It is kept separate so it can change on its own schedule and could
move to its own repository later.

## What is here

| File | Role |
|---|---|
| `uwhealthcv.sty` | The only package a CV loads. Reads the files below in the right order. |
| `NSERC-formatting.tex` | Page, fonts, header and table setup. |
| `biblatex-formatting.tex` | biblatex tweaks: badge icons in the margin, the `inproceedings` driver. |
| `ACM-Reference-Format.{bbx,cbx,dbx,bst}` | ACM bibliography style (vendored). |
| `aprcv.sty` | APR highlighting. Its header documents every command. |
| `cv-records.tex` | Grants and supervision as biblatex records: the table, the student lists, sorting and highlighting. |
| `uwhealthcv.dbx` | The biblatex data model for `@grant` and `@supervision` (fields documented in its header). |
| `cv-layout.tex` | Page-break rules: `\keepwithnext`, `\sectionbreak`, widow and club control. |
| `images/` | Badge images a bib entry can show in the margin with `icon = {images/<file>}`. `icon = {award}` draws the award rosette instead (`biblatex-formatting.tex`); in the APR version it is filled with the award colour when the entry is in the review period. |
| `example/` | A fictional CV that uses every feature. Build it to test a template change. |

## Using it

A CV directory holds the content and puts this directory on TeX's search path
with a `latexmkrc`:

```perl
ensure_path('TEXINPUTS', './template//');
```

latexmk, Overleaf and the GitHub Actions LaTeX build all read that file.

The CV's main file:

```latex
\documentclass[12pt]{article}
\usepackage{uwhealthcv}
\addbibresource{mycv.bib}
\setreviewperiod{2025}{2026}
\cvowner{Your Name}
% \DeclareBibliographyCategory and \addtocategory lists for each heading
\begin{document}
...
\end{document}
```

The APR version is a two-line file next to it:

```latex
\PassOptionsToPackage{apr}{aprcv}
\input{main}
```

A CV can also provide `apr-formatting.tex` beside its main file. `aprcv.sty`
reads it in the APR version only, after the rest of the template, so it can
change settings such as `\sethighlightstrength` and `\sethighlightstyle`
without affecting the plain CV.

## Interface

These are the names a CV relies on. Changing one is a breaking change for
every CV that uses the template.

- Package: `uwhealthcv` (options `apr`, `plain`), `aprcv` (options `apr`, `plain`).
- Commands: `\setreviewperiod`, `\hlteaching`, `\hlresearch`, `\hlservice`,
  `\hlaward`, `\hlboth`, `\hl…row`, `\aprsample`, `\ifAPR`,
  `\sethighlightstrength`, `\sethighlightstyle`, `\keepwithnext`,
  `\sectionbreak`, `\usvardate`, `\monthyear`, `\extlink`.
- Section markup: `\cvsection`, `\cvsubheading`, `cvlist` with `\cvitem`, `cvparts`
  with `\cvpart`, `\printcategory`. Documented in the `uwhealthcv.sty` header.
- Records: `\cvowner`, `\printgrants`, `\printsupervision{degree}`, `\printawards`, the
  entry types `@grant`, `@supervision` and `@award` with the fields in `uwhealthcv.dbx`, and `\me` inside a
  grant's `investigators`. Documented in `cv-records.tex`.
- For other record types: `\aprtypecategory{type}{colour}` and `\aprsetentrycolour`
  (`aprcv.sty`).
- biblatex categories: `aprteaching`, `aprservice`, `apraward`, `aprnone`,
  `aprinclude`, `apralsoteaching`, `apralsoresearch`, `apralsoservice`,
  `apralsoaward`.
- Bib field: `icon` (an image path, or `award` for the rosette).
- File the template reads from the CV: `apr-formatting.tex` (optional).

## Building the example

```bash
cd template/example
latexmk -pdf example.tex
latexmk -pdf example-apr.tex
```

CI builds both on every pull request.

## Moving to its own repository

Everything the template needs is inside this directory, so it can be split out
with its history:

```bash
git subtree split --prefix=template -b template-only
```

Overleaf does not support git submodules, so a CV that syncs with Overleaf
should keep a copy of the template in its `template/` directory (for example
with `git subtree pull`) rather than a submodule.
