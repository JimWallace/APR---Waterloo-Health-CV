# Put the CV template on TeX's search path, so main.tex, apr.tex and the
# older 2pages.tex / 8pages.tex find uwhealthcv.sty, aprcv.sty, the ACM
# biblatex style and the badge images in template/. latexmk, Overleaf and
# the CI build all read this file.
ensure_path('TEXINPUTS', './template//');
