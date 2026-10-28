# RouteVoice paper (draft)

`main.tex` includes the files in `sections/`. Figures are TikZ and live in `figures/`; the bibliography is `refs.bib`.

To build:

    tectonic -X compile --outdir build main.tex

Research notes behind the text are in `notes/`. Every number in the paper traces to a repository path listed there:
- `architecture-method.md`
- `results-history.md`
- `related-work.md`

Red `[TODO: ...]` markers flag open items. Claims about other work come from `notes/related-work.md`; entries marked UNVERIFIED there are not cited.
