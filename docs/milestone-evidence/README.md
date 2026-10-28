# Version 1 milestone evidence additions

These files preserve selected product and browser evidence alongside the existing RouteVoice hardware release. They were added for the 28 October 2026 milestone report in the [root README](../../README.md).

| File | What it records | How to interpret it |
|---|---|---|
| [Asset provenance](asset-provenance.json) | Original workspace-relative paths, sizes and SHA-256 checksums for 19 imported artifacts | The artifacts were copied without modification; source paths refer to the earlier `route-voice-llm-hardware-v1` workspace |
| [Browser verification, 8 September](browser-verification-2026-09-08.json) | Saved production STT, routing, TTS and pipeline smoke calls, media checks and mobile layout | Historical device-level functional checks, not an accuracy benchmark or ASIC measurement |
| [Helmet tool catalog](helmet-tool-catalog-v1.json) | 26 typed product-interface proposals, schemas and policy requirements | A product contract; the public browser demo exposes a smaller four-tool surface |
| [Helmet reference-fit score](helmet-reference-fit-score.json) | Fit metrics against a reconstructed concept reference | A geometry comparison, not manufacturing tolerance, head-fit or safety validation |
| [Screenshot metadata](../media/milestone/screenshots.json) | Six live website captures on 28 October, plus the input/output of the captured router run | Current presentation evidence; the router result is one smoke call |

The screenshot capture used desktop Chrome through Playwright, a light color theme, a 1440 × 1050 viewport and a device scale factor of 1. The helmet capture waited for the 3D stage to report ready; the playground capture waited for local inference to complete. Captures do not contain a logged-in account, private browser chrome or fabricated model output.

The original two PDF documents and web GLB are indexed in [the design package](../design/README.md). The PDFs retain their original September content. Product renders, including the broader wearable concepts, are illustrative design assets; the V4 model and assembly renders are design geometry rather than production CAD.

The existing [hardware release package](../../routing-voice-chip-design/release-v1/README.md), [paper](../../paper/RouteVoice-paper-draft.pdf), and [lab log](../../OVERNIGHT-PROGRESS.md) remain the sources for numerical, RTL and physical-design claims.
