# The CV template

This directory is the Faculty of Health CV template, kept apart from the CV
that uses it so the two can be worked on separately (see `README.md`).

- **No personal data here.** No names, publications, grants, students or
  narrative from the CV. Examples use the fictional content in `example/`. CI
  fails if `template/` contains the CV owner's surname.
- **Keep the example building.** A template change must leave
  `example/example.tex` and `example/example-apr.tex` compiling. If you add a
  feature, show it in the example.
- **The interface in `README.md` is a contract.** Renaming or removing a
  command, option, category or the `icon` field breaks `main.tex`. Do it only
  when asked, and change `main.tex` in the same PR.
- The CV-data rules in the root `CLAUDE.md` (bib facts, trainee marks,
  narrative sections) govern `main.tex` and `scholar.bib`, not this directory.
  The weekly automated update never changes files here.
