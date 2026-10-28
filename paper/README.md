# RouteVoice paper — reviewed research draft

[Read the PDF](RouteVoice-paper-draft.pdf) · [Artifact index](ARTIFACTS.md) · [Corrections and review scope](REVIEW-2026-10-28.md) · [Public evidence](https://huggingface.co/datasets/sanjuhs/routevoice-v1-paper-evidence-20261028)

The 28 October revision reconciles the paper with the frozen quality evaluation, W11 storage accounting, final engine metrics and W13–W15 integration limits. It reports an RTL/open-flow physical-design milestone, not fabricated silicon or an integrated real-time recognizer.

`main.tex` includes `sections/`; TikZ and raster/vector figures are in `figures/`, and the bibliography is `refs.bib`.

## Build

```sh
mkdir -p build
tectonic -X compile --keep-intermediates --outdir build main.tex
cp build/main.pdf RouteVoice-paper-draft.pdf
```

`sh make-arxiv.sh` builds `build/routevoice-arxiv.tar.gz`, including the generated bibliography. The public PDF is committed; generated build intermediates are ignored.

## Evidence

[ARTIFACTS.md](ARTIFACTS.md) provides working public entry points, pinned Hugging Face revisions and restoration instructions. The small [evidence supplement](evidence/) preserves 25 original files and their hashes. Its scripts are snapshots with original workspace dependencies, not a new standalone evaluation package.

The `notes/` directory records historical research and intermediate estimates. Use the reviewed manuscript and correction ledger for current claims. The review did not rerun inference, RTL, physical design or foundry signoff.
