> Historical research notes. For reviewed claims and corrected accounting, see [the 28 October review](../REVIEW-2026-10-28.md) and [artifact index](../ARTIFACTS.md). Earlier estimates below are retained as history.

# RouteVoice related-work notes

Compiled 2026-10-24. BibTeX keys refer to `paper/refs.bib`.

**How things were checked.**
- arXiv entries: title, authors, date and abstract were pulled from the arXiv API.
- DOIs for conference and journal papers: checked against Crossref.
- Product pages, patents and blogs: opened directly, either with WebFetch or with curl and a text extraction step.
- Labels used below:
  - **UNVERIFIED** marks a claim taken only from a secondary source or from memory.
  - **(vendor claim)** marks a number that comes from a company and has not been independently reproduced.
- All quantitative claims are given as reported by the source. None were re-measured.

**RouteVoice facts used for the comparison.** These come from the repository's own commits and `routing-voice-chip-design/STATUS.md`, so the paper should restate them from the primary evidence.
- Process and model: GF180MCU, running a Moonshine encoder–decoder.
- Weight encoding: weights are 4-bit indices into small per-matrix codebooks. Radix-16 partial products of each activation are computed once and shared, and the fixed indices select from them.
- Engine block: a fixed 1280×320 array.
  - Routed at 150 ns across 9 corners, with DRC and LVS clean (commit a6b679794).
  - Routed SAIF power estimate: 0.188 W, or 287 pJ/MAC.
- Not yet established:
  - No full-chip signoff and no silicon.
  - Some immutable model data was still served from the host harness in October: a measured inventory of 28,641,280 bytes.
- RTL audio verification is partial. At v49, 53 of 83 original segments matched exactly.

---

## 1. Hardwired-weight / model-specific inference silicon

### Taalas HC1, "Hardcore Models" — `taalas2026hc1`, `zota2026heise`
Taalas has announced HC1 (announcement post by Ljubisa Bajic). HC1 is a technology-demonstrator chip with Llama 3.1 8B built into the silicon. Weights and compute share one die at what the company calls DRAM-level density, with no HBM.
- **Quantization:** a custom 3-bit base data type mixing 3-bit and 6-bit parameters. Taalas acknowledges some quality loss.
- **Turnaround:** the company says a previously unseen model can become hardware in two months.
- **Flexibility retained:** context size is configurable, and LoRA fine-tuning is supported.
- **Roadmap:** HC2 is to use standard 4-bit floating-point formats for a frontier-scale model.
- **Independence of the figures:** the throughput numbers are measured by Taalas. Heise's report adds die and process figures that do not appear on the company's own page.

Key claims:
- About 17k tokens/s per user on Llama 3.1 8B (1k/1k input), 10× less power, 20× lower build cost, 24 engineers, $30M spent of more than $200M raised (vendor claims) — https://taalas.com/the-path-to-ubiquitous-ai/
- TSMC N6, 815 mm², about 53 billion transistors; almost 16k tokens/s seen in the public "Jimmy" chatbot test. Comparison figures cited for Llama 3.1 8B: H200 about 230, Cerebras about 1,936, SambaNova 916, Groq 609 tokens/s — https://heise.de/-11185112 (secondary, 21 Feb 2026)
- An independent tester reportedly measured 14,357 tokens/s — **UNVERIFIED** (seen only in search-result summaries of Substack and Cambrian AI coverage; not opened).

*RouteVoice relation:* RouteVoice applies the same thesis, that fixed weights make the model the chip, to an ASR model three orders of magnitude smaller, on a 180 nm open PDK, with fully open tooling and verification evidence. It is not a datacenter LLM part.

### Taalas patents — `taalas2025patent802`, `taalas2026patent566`, `taalas2025wo724`
- **US20250123802A1**, "Large Parameter Set Computation Accelerator Using Configurable Connectivity Mesh." Priority 2023-10-11, published 2025-04-17.
  - Provides one multiplier per possible parameter value. Each multiplier computes input × that value once.
  - A mask-configured connectivity mesh routes each product to the accumulators whose stored parameter equals that value.
  - The mesh can be set in customised upper-metal (back-end-of-line) masks.
- **US20260023566A1**, "Hardware Implemented Codebook Pointers." Priority 2024-07-19, published 2026-01-22.
  - Weights are stored as hardware pointers (mesh wiring or address cells) into a register-held codebook.
  - Values can be changed by rewriting the small codebook rather than every weight.
- **WO2025217724A1**, "Mask Programmable ROM Using Shared Connections." Priority 2024-04-15, published 2025-10-23.
  - A mask ROM whose bit terminal fans out to several bit lines through mask-defined vias.
  - It uses the same transistors and metals as logic, so density is limited by metal pitch.

Source: https://patents.google.com/patent/US20250123802A1/en, …/US20260023566A1/en, …/WO2025217724A1/en. Claims sections were truncated in the fetched pages; the summaries above come from the summary and abstract text.

*RouteVoice relation:* RouteVoice's "compute shared products once, select them with fixed 4-bit indices into a per-matrix codebook" is architecturally very close to the claims of '802 and '566. The project's own notes call its shared-product primitive "Taalas-inspired". The paper must cite these patents prominently and must not claim the mechanism as new. (Freedom-to-operate is a legal question outside this note.)

### HNLPU — Hardwired-Neurons Language Processing Unit — `liu2025hnlpu`
- **Design:** an academic design that hardwires LLM weights (gpt-oss 120B) into the compute fabric.
- **Problem it addresses:** naïve hardwiring would need photomask sets costing more than $6B.
- **Method ("Metal-Embedding"):** weights are encoded in the 3D topology of metal wires rather than in silicon device cells. This lets 60 of 70 mask layers, including all EUV layers, be shared across chips.
- **Status:** results are architectural and physical estimates at 5 nm. No silicon.

Key claims (v2 abstract):
- 15× density gain, 112× lower photomask cost
- 249,960 tokens/s; 36 tokens/J
- 13,232 mm² total die area
- $59.46M–$123.5M NRE
- 41.7–80.4× cost-effectiveness versus H100 clusters

Source: https://arxiv.org/abs/2508.16151

*RouteVoice relation:* HNLPU is the closest academic statement of hardwired LLM economics. RouteVoice differs by targeting a mature, cheap node where NRE is a few thousand dollars, and by providing RTL plus physical-flow evidence rather than projections.

### Ankhdjet — open-PDK mask-programmed ternary compute-in-ROM — `pai2026ankhdjet`
- **What it is:** a single-author 2026 arXiv paper describing an open-source compiler.
- **Flow:** a HuggingFace BitNet b1.58 ternary checkpoint is lowered to the via-mask program of a fixed compute-in-ROM macro on SKY130.
- **Signoff:** open tools only. KLayout DRC 0 and Netgen LVS 0, with timing clean, for two weight matrices where only the mask differs.
- **Fabrication:** a macro was submitted to a TinyTapeout/ChipFoundry SKY130 shuttle (ttsky26c), with silicon expected in 2027.
- **Other contributions:** reports three silent shorts that DRC could not see but adversarial verification caught.
- **Energy:** read energy of 0.98–1.73 pJ per sensed weight, from extracted-parasitic simulation. No measured energy is claimed.

Source: https://arxiv.org/abs/2608.26206

*RouteVoice relation:* This is the most direct prior art for "hardwired weights on an open PDK with open signoff", and it claims "first" for both the compiler and the fabrication submission. RouteVoice must not claim to be the first open-PDK hardwired-weight design. Its differences:
- a full ASR transformer rather than one matrix macro;
- 4-bit codebook indices with shared radix-16 products rather than ternary ROM sensing;
- GF180MCU rather than SKY130;
- end-to-end audio-to-text RTL verification.

### Etched Sohu — transformer-only ASIC — `mann2024etched`
- **What it is:** Sohu, a transformer-specific ASIC (programmable weights in HBM, not hardwired).
- **Launch status:** at the June 2024 launch it existed only in FPGA emulation.
- **Later status (UNVERIFIED):** search summaries say the "Sohu" name has since been retired.

Key claims, reported by The Register (26 Jun 2024):
- More than 500k tokens/s on Llama 70B with an 8-chip server (vendor claim)
- Replaces 160 H100s (vendor claim)
- 144 GB HBM3 per chip

Source: https://www.theregister.com/2024/06/26/etched_asic_ai/. Etched's own announcement page returned 404 and was not re-read.

*RouteVoice relation:* Sohu specialises to an architecture class. RouteVoice specialises to one set of weights, which is a more extreme point on the flexibility–efficiency curve.

### ROM compute-in-memory: YOLoC, Hidden-ROM, ROMA — `chen2022yoloc`, `chen2022hiddenrom`, `wang2025roma`
- **YOLoC (DAC 2022):**
  - Proposes computing-in-ROM for density.
  - Adds a small SRAM "residual branch" so ROM-fixed networks can be fine-tuned.
  - Reports 14.8× (Darknet-19) and 4.8× (ResNet-18) better energy efficiency than all-SRAM CiM at equal area in 28 nm, with less than 8% latency overhead.
- **Hidden-ROM (ICCAD 2022):** the same group's follow-up on task transfer after fabrication. Only existence and venue were verified; contents are UNVERIFIED.
- **ROMA (2025):**
  - Puts a quantized LLaMA base model in ROM and LoRA weights plus the KV cache in SRAM.
  - Introduces a "B-ROM" cell fused with compute.
  - Claims a 4-bit 3B or 2-bit 8B model fully on-chip at more than 20,000 tokens/s.

Sources: https://arxiv.org/abs/2206.00379 · https://doi.org/10.1145/3508352.3549335 · https://arxiv.org/abs/2503.12988

*RouteVoice relation:* All three keep weights in a ROM array that is read at run time. RouteVoice instead fixes indices in logic and selects precomputed products, and like YOLoC and ROMA it currently relies on a non-ROM path (the host harness) for some model data.

### Bespoke / hardwired-coefficient classifiers — `mubarik2020printed`, `iordanou2023tiny`
- **Printed Machine Learning Classifiers (MICRO 2020):**
  - Builds "bespoke" printed-electronics classifiers with the model coefficients hardwired into the circuit.
  - Bespoke EGT decision trees: 48.9× less area and 75.6× less power on average. Bespoke SVMs: 12.8× and 12.7×.
  - These figures come from the abstract as reproduced in search results; full text not opened.
- **Tiny Classifier Circuits:** evolves classifiers of 300 gates or fewer for tabular data.

Sources: https://doi.org/10.1109/MICRO50266.2020.00019 · https://arxiv.org/abs/2303.00031

*RouteVoice relation:* This line of work shows that hardwired coefficients pay off at very coarse feature sizes. RouteVoice brings the idea to a 10⁷-parameter-class transformer.

---

## 2. Codebook / index quantization, LUT GEMM, shared partial products

### Deep Compression and EIE — `han2016deepcompression`, `han2016eie`
- **Deep Compression:**
  - Prunes the network, clusters weights into a shared codebook (trained quantization), then Huffman-codes the result.
  - Achieves 35–49× compression: AlexNet 240 MB → 6.9 MB and VGG-16 552 MB → 11.3 MB, with no accuracy loss. Each connection drops from 32 to 5 bits.
- **EIE:**
  - Hardware that runs the compressed model.
  - Each weight is stored as a 4-bit index. It is decoded through a 16-entry table to a 16-bit fixed-point value before the multiply.
  - In 45 nm, each PE is 0.638 mm² and 9.16 mW. 64 PEs take 40.8 mm² and about 590–600 mW.
  - Reported energy savings: weight sharing gives 8× and DRAM→SRAM gives 120×.

Sources: https://arxiv.org/abs/1510.00149 · https://arxiv.org/abs/1602.01528 (PDF text checked for the 4-bit index and 45 nm figures)

*RouteVoice relation:* RouteVoice uses the same storage format, 4-bit indices into a small codebook. Instead of looking up the weight and then multiplying, it multiplies the activation by every codebook-relevant digit once and lets the fixed index select the result.

### UCNN — `hegde2018ucnn`
- Exploits weight repetition: when the same weight value appears many times, the activations that share it are summed first and multiplied once ("factorized dot products").
- Improves throughput-normalised energy by 1.2–4× over an Eyeriss-style sparse baseline on three CNNs.

Source: https://arxiv.org/abs/1804.06508

*RouteVoice relation:* UCNN groups by weight value at run time. RouteVoice fixes that grouping at fabrication time, where it costs nothing, and applies it to digit-level partial products.

### Mokey — `zadeh2022mokey`
- Quantizes all transformer weights and activations to 4-bit indices into dictionaries of 16-bit fixed-point centroids, without fine-tuning.
- Centroids are fitted to an exponential curve, so most MACs become narrow 3-bit additions.
- Claims about 10× energy efficiency and 4–15× speed over a Tensor-Core-style accelerator.

Source: https://arxiv.org/abs/2203.12758

*RouteVoice relation:* This is the closest accelerator precedent for 4-bit codebook indices in transformers. Mokey's dictionaries are programmable and stored in memory, whereas RouteVoice's indices are wired.

### LLM vector / codebook quantization: AQLM, QuIP#, VPTQ, GPTVQ, SqueezeLLM — `egiazarian2024aqlm`, `tseng2024quipsharp`, `liu2024vptq`, `vanbaalen2024gptvq`, `kim2024squeezellm`
| Method | Codebook approach | Reported result |
|---|---|---|
| AQLM | Multi-codebook additive quantization | Pareto-optimal below 3 bits per parameter |
| QuIP# | Randomized Hadamard incoherence plus E8 lattice codebooks | Best results at ≤4 bits |
| VPTQ | Second-order-optimised vector quantization | Perplexity reductions of 0.01–0.34 on LLaMA-2 versus prior extreme-low-bit methods |
| GPTVQ | Hessian-guided VQ | 3–11 h to quantize Llama-2-70B on one H100 |
| SqueezeLLM | Sensitivity-weighted non-uniform (k-means) per-channel LUT plus a sparse outlier set | Near-lossless at 3 bits |

Sources: arXiv 2401.06118, 2402.04396, 2409.17066, 2402.15319, 2306.07629

*RouteVoice relation:* RouteVoice's per-matrix 16-entry codebooks are a scalar, SqueezeLLM-like non-uniform quantizer. They are not vector quantization. These papers set the accuracy expectations, and their VQ formats suggest denser future hardwired encodings.

### LUT-based GEMM and ternary models: LUT-GEMM, T-MAC, BitNet b1.58 — `park2024lutgemm`, `wei2025tmac`, `ma2024bitnet158`
- **LUT-GEMM:** precomputes the partial sums of activations for every binary-coded weight pattern and then looks them up. This removes dequantisation. Reports a 2.1× token-latency improvement on OPT-175B at 3 bits.
- **T-MAC:** moves the same idea to CPUs with bit-wise table lookup.
  - Up to 4× throughput and 70% less energy than llama.cpp.
  - BitNet-b1.58-3B runs at 30 tokens/s on one M2-Ultra core and 71 tokens/s on eight.
- **BitNet b1.58:** uses ternary weights {−1, 0, 1} and matches FP16 at equal size and training tokens, according to the authors. It explicitly calls for dedicated hardware.

Sources: https://arxiv.org/abs/2206.09557 · https://arxiv.org/abs/2407.00088 · https://arxiv.org/abs/2402.17764

*RouteVoice relation:* LUT-GEMM and T-MAC are software analogues of "precompute the activation side, then let the weight bits select". RouteVoice is a hardwired-silicon instance of that pattern with radix-16 digits.

### Classic DSP prior art: computation-sharing multipliers, MCM, distributed arithmetic — `park2002cshm`, `voronenko2007mcm`, `white1989da`
- **CSHM (ISLPED 2002):**
  - In a transposed FIR filter, one input is multiplied by many coefficients.
  - A shared precomputer bank forms a small "alphabet" of odd multiples (1x, 3x, 5x, 7x).
  - Each coefficient's product is assembled by mux-selecting and shifting those shared multiples.
  - On a 10-tap filter in 0.25 µm, this was 19% faster and used 17% less power than a Wallace-tree design (read from the PDF).
- **Voronenko & Püschel (ACM TALG 2007):** formalise multiplierless multiple-constant multiplication for fixed coefficients.
- **White (1989):** reviews distributed arithmetic, which uses precomputed LUTs of coefficient sums for fixed-coefficient inner products.
- For the last two, only the bibliographic data was verified; the paper bodies were not opened.

Sources: PDF https://www.cecs.uci.edu/~papers/compendium94-03/papers/2002/islped02/pdffiles/11_3.pdf · https://doi.org/10.1145/1240233.1240234 · https://doi.org/10.1109/53.29648

*RouteVoice relation:* RouteVoice's shared radix-16 partial products selected by fixed indices are a direct descendant of the CSHM alphabet idea and of fixed-coefficient MCM. The paper should credit this 20-plus-year DSP lineage alongside the Taalas patents.

---

## 3. Small / edge ASR models and voice chips

### Moonshine family — `jeffries2024moonshine`, `usefulsensors2024moonshinehf`, `king2025flavors`, `kudlur2026moonshinev2`
- **Moonshine (Useful Sensors, 2024):**
  - An encoder–decoder transformer with RoPE, trained on variable-length segments without zero-padding, so encoder cost scales with the length of the audio.
  - Moonshine Tiny needs 5× less compute than Whisper tiny.en for a 10-second segment, with no WER increase.
  - The model card lists Tiny at 27M parameters and Base at 61M, under the MIT licence.
- **Flavors of Moonshine (2025):** monolingual 27M models for six languages. Error rates are 48% lower on average than Whisper Tiny, and the models often match the 28× larger Whisper Medium.
- **Moonshine v2 (2026):** uses a sliding-window-attention streaming encoder for bounded time-to-first-token. Claims accuracy on par with models 6× its size.

Sources: https://arxiv.org/abs/2410.15608 · https://huggingface.co/UsefulSensors/moonshine · https://arxiv.org/abs/2509.02523 · https://arxiv.org/abs/2602.12241

*RouteVoice relation:* RouteVoice hardwires a Moonshine model. Moonshine v2's bounded-window encoder would remove the full-utterance attention dependency and is a natural next target for fixed silicon.

### Whisper and Distil-Whisper — `radford2022whisper`, `gandhi2023distilwhisper`
- **Whisper:** trained on 680k hours of weakly supervised multilingual data. Robust zero-shot ASR, and the de facto baseline.
- **Distil-Whisper:** distils Whisper with large-scale pseudo-labelling.

Sources: https://arxiv.org/abs/2212.04356 · https://arxiv.org/abs/2311.00430

*RouteVoice relation:* These are the accuracy and compute baselines that Moonshine, and therefore RouteVoice, is measured against.

### Speech-recognition ASICs — `price2015wfst`, `price2018speech`, `tambe2021sm6`
- **Price, Glass & Chandrakasan (MIT):**
  - JSSC 2015: a 6 mW, 5k-word WFST recogniser.
  - JSSC 2018: a 65 nm DNN-HMM recogniser with a neural VAD.
    - Vocabularies range from 11 to 145k words, and full-chip power from 172 µW to 7.78 mW.
    - The VAD uses 22.3 µW.
    - Memory bandwidth is identified as the dominant power driver.
    - These 2018 figures come from the abstract via a search excerpt of the MIT-hosted PDF.
- **Tambe et al. (ISSCC 2021) "SM6":**
  - A 25 mm² SoC in 16 nm FinFET combining a Cortex-A53, a Bayesian denoising accelerator and the FlexASR attention seq2seq accelerator.
  - 18 ms end-to-end latency and 2.24 mJ per frame.

Sources: https://doi.org/10.1109/JSSC.2014.2367818 · https://doi.org/10.1109/JSSC.2017.2752838 (PDF https://people.csail.mit.edu/jrg/2018/Price-JSSC-18.pdf) · https://doi.org/10.1109/ISSCC42613.2021.9366062

*RouteVoice relation:* These are the closest silicon ASR precedents. Both keep weights in memory and pay bandwidth or energy to fetch them. RouteVoice removes weight fetch for the hardwired portion, but uses a transformer instead of an HMM or RNN, at a far older node than SM6.

### Always-on KWS chips — `shan2020kws`, `giraldo2018laika`, `zhang2017helloedge`
- **Shan et al. (ISSCC 2020):** 510 nW at 0.41 V in 28 nm, using serial-FFT MFCC and a binarized depthwise-separable CNN.
- **Laika (ESSCIRC 2018):** a programmable LSTM KWS accelerator at about 5 µW in 65 nm.
- **Hello Edge:** shows DS-CNN KWS fits on microcontrollers at 95.4% accuracy.

Sources: https://doi.org/10.1109/ISSCC19947.2020.9063000 · https://doi.org/10.1109/ESSCIRC.2018.8494342 · https://arxiv.org/abs/1711.07128

*RouteVoice relation:* KWS chips reach nanowatts by restricting the task to a handful of words. RouteVoice targets open-vocabulary transcription, which is a different power class. A KWS or VAD front-end gating RouteVoice is the natural system pairing.

---

## 4. Edge and datacenter transformer accelerators; energy reference points

### Energy per operation (reference numbers) — `horowitz2014energy`, `sze2017tutorial`, `chen2017eyeriss`
**Horowitz, ISSCC 2014, Fig. 1.1.9 (45 nm, 0.9 V).** Read and decoded from the PDF; the table text is font-shifted.

| Operation | Energy |
|---|---|
| 8-bit add | 0.03 pJ |
| 32-bit add | 0.1 pJ |
| 8-bit multiply | 0.2 pJ |
| 32-bit multiply | 3.1 pJ |
| FP16 add | 0.4 pJ |
| FP32 add | 0.9 pJ |
| FP16 multiply | 1.1 pJ |
| FP32 multiply | 3.7 pJ |
| 8 KB cache read | 10 pJ |
| 32 KB cache read | 20 pJ |
| 1 MB cache read | 100 pJ |
| 64-bit DRAM access | 1.3–2.6 nJ |

The paper also gives about 70 pJ of instruction overhead.
- **Sze et al. tutorial:** the standard survey framing data movement as the dominant cost.
- **Eyeriss:** the canonical 65 nm dataflow accelerator. No numbers are cited here because they were not re-read.

Sources: PDF https://www.gwern.net/doc/cs/hardware/2014-horowitz-2.pdf (DOI 10.1109/ISSCC.2014.6757323) · https://arxiv.org/abs/1703.09039 · https://doi.org/10.1109/JSSC.2016.2616357

**Our own first-order estimate (not a citation).** Scaling Horowitz's 45 nm / 0.9 V numbers to 180 nm / 3.3 V by C·V² gives a factor of about 4 × (3.3/0.9)² ≈ 54×:
- 8-bit multiply: about 11 pJ.
- FP32 multiply plus add: about 250 pJ.

This is a rough sanity band only. RouteVoice's routed estimate of 287 pJ/MAC (SAIF, engine block) should be discussed against it with care. The paper should explain which arithmetic (FP32 affine, codebook select, accumulation) dominates that figure.

### Groq LPU / TSP — `abts2020tsp`, `abts2022groq`
- **Architecture:** a deterministic, compiler-scheduled tensor streaming processor. Removing arbiters and caches makes timing fully deterministic, and weights live in on-chip SRAM across many chips.
- **ISCA 2020 figures:** a 25×29 mm, 14 nm chip at 900 MHz, with more than 1 TeraOp/s per mm². Batch-1 ResNet-50 runs at 20.4k images/s.
- **ISCA 2022:** describes the multi-chip, software-defined scale-out.

Sources: https://doi.org/10.1109/ISCA45697.2020.00023 · https://doi.org/10.1145/3470496.3527405. The ISCA 2020 figures came from search excerpts of Groq's hosted PDF, which returned 404 when fetched directly, so treat them as UNVERIFIED by direct read.

*RouteVoice relation:* Groq removes DRAM from the loop by spreading weights across SRAM in many chips. RouteVoice removes even SRAM reads for hardwired weights, at the cost of zero reprogrammability.

### Cerebras WSE-3 — `cerebras2024wse3`, `lie2023cerebras`
- **WSE-3 specifications (vendor claims):** a wafer-scale TSMC 5 nm device with 4 trillion transistors, 900k cores, 44 GB of on-chip SRAM and 125 PF peak.
- **Current product page (vendor claims):** lists a "WSE-3 Turbo" at 250 PF and 46,225 mm².
- **IEEE Micro 2023:** describes the architecture.

Sources: https://www.cerebras.ai/press-release/cerebras-announces-third-generation-wafer-scale-engine · https://www.cerebras.ai/chip · https://doi.org/10.1109/MM.2023.3256384

*RouteVoice relation:* Cerebras is the extreme of "keep all weights in on-die SRAM". Hardwiring is the extreme beyond it, where weights are not memory at all.

### ISSCC/VLSI transformer processors — `tu2022trancim`, `wang2022transformer28nm`, `tambe2023transformer12nm`, `tambe2021edgebert`, `wang2021spatten`
| Work | Node | Approach | Headline figure |
|---|---|---|---|
| TranCIM (ISSCC 2022) | 28 nm | Full-digital bitline-transpose SRAM CIM sparse transformer | 15.59 µJ/token (in title) |
| Wang et al. (ISSCC 2022) | 28 nm | Approximate-computing transformer processor | 27.5 TOPS/W |
| Tambe et al. (ISSCC 2023) | 12 nm | Sparse transformer processor with entropy early exit | 18.1 TFLOPS/W |
| EdgeBERT | 12 nm (design) | Algorithm–hardware co-design for latency-bounded BERT, using eNVM | — |
| SpAtten (HPCA 2021) | — | Token and head pruning | — |

Only titles and DOIs were verified via Crossref, so the figures are the ones stated in the titles.

Sources: https://doi.org/10.1109/ISSCC42614.2022.9731645 · https://doi.org/10.1109/ISSCC42614.2022.9731686 · https://doi.org/10.1109/ISSCC42615.2023.10067817 · https://arxiv.org/abs/2011.14203 · https://arxiv.org/abs/2012.09852

*RouteVoice relation:* All of these are programmable, weight-in-memory designs at advanced nodes. RouteVoice trades all programmability for no weight fetch, and should not compare headline TOPS/W across 180 nm and 12–28 nm without node normalisation.

### MCU NPUs — `arm2024ethosu55`, `st2024stm32n6`
- **Arm Ethos-U55:** a micro-NPU of about 0.1 mm² paired with Cortex-M55/M85. Claims up to 480× ML uplift and up to 90% energy reduction (vendor claims).
- **ST STM32N6:** a Neural-ART NPU rated at 600 GOPS. The 288 MAC/cycle, Cortex-M55 at 800 MHz and 4.2 MB RAM figures are only partly verified.

Sources: https://www.arm.com/products/silicon-ip-cpu/ethos/ethos-u55 · https://blog.st.com/stm32n6/

*RouteVoice relation:* These are the commercial "programmable edge" alternative. A Moonshine-Tiny deployment on such an MCU or NPU is the obvious baseline that RouteVoice must beat on energy per utterance.

---

## 5. Open-source silicon: PDKs, EDA, shuttles

### OpenROAD, OpenLane, LibreLane — `ajayi2019openroad`, `shalan2020openlane`, `librelane`
- **OpenROAD (DAC 2019):** the DARPA-IDEA project's first learnings toward a no-human-in-the-loop RTL-to-GDS flow.
- **OpenLane (ICCAD 2020):** packages OpenROAD, Yosys, Magic, Netgen and KLayout into a flow proven on SKY130 tapeouts.
- **LibreLane:** the FOSSi-Foundation-trademarked successor based on OpenLane 2. It followed Efabless's closure; the OpenLane 2 assets are now owned by UmbraLogic.

Sources: https://doi.org/10.1145/3316781.3326334 · https://doi.org/10.1145/3400302.3415735 · https://github.com/librelane/librelane

*RouteVoice relation:* RouteVoice's physical results (routing at 150 ns over 9 corners, DRC/LVS clean on the engine) were produced with this stack on GF180MCU.

### Point tools — `wolf_yosys`, `snyder_verilator`, `ousterhout1984magic`, `edwards_magic`, `edwards_netgen`, `koefferlein_klayout`, `hauser_hardfloat`
- **Yosys:** open synthesis suite.
- **Verilator:** compiles Verilog/SystemVerilog to multithreaded C++ or SystemC; more than 700 contributors per its site.
- **Magic:** layout tool (Ousterhout et al., DAC 1984), now maintained by Tim Edwards.
- **Netgen:** LVS.
- **KLayout:** viewer, editor and DRC engine.
- **Berkeley HardFloat:** parameterised IEEE-754 Verilog by J. Hauser; Release 1, July 2019.

Sources: https://yosyshq.net/yosys/ · https://www.veripool.org/verilator/ · https://doi.org/10.1109/DAC.1984.1585789 · http://opencircuitdesign.com/magic/ · http://opencircuitdesign.com/netgen/ · https://www.klayout.de/ · http://www.jhauser.us/arithmetic/HardFloat.html

### PDKs and shuttles — `google_gf180mcu`, `google2022gfshuttle`, `google_skywater`, `venn2024tinytapeout`, `tinytapeout2025efabless`, `waferspace`
- **GF180MCU PDK:**
  - Apache-2.0, released August 2022 by Google with GlobalFoundries.
  - Includes 7- and 9-track standard cells, 3.3/5/6/10 V devices and 64×8 to 512×8 SRAM macros.
  - The repository calls itself an experimental preview "not intended" for production, and is now archived.
- **Google-sponsored no-cost shuttles:** began with GF-MPW-0 (submissions 31 Oct – 5 Dec 2022), at 40 projects per run.
- **SKY130:** the earlier open 130 nm PDK.
- **Tiny Tapeout:** a shared-tile shuttle platform (IEEE SSC Magazine 2024). It now runs SKY, IHP and GF shuttles, and it continued after Efabless shut down in March 2025.
- **wafer.space:** a GF180MCU budget shuttle; Run 1 delivered 24–29 open designs (the page is inconsistent).
  - Run 3 pricing per slot of 1,000 dies: about $3,000 for a 1.94×2.53 mm slot and $8,000 for a 3.93×5.12 mm slot (standard pricing). Early-bird prices were $2,000 and $7,000.
  - Run 3 dates: GDS due 16 Dec 2026, parts in Q2 2027.

Sources: https://github.com/google/gf180mcu-pdk · https://opensource.googleblog.com/2022/10/announcing-globalfoundries-open-mpw-shuttle-program.html · https://github.com/google/skywater-pdk · https://doi.org/10.1109/MSSC.2024.3381097 · https://tinytapeout.com/news/efabless-shutsdown/ · https://wafer.space

*RouteVoice relation:* These numbers anchor the paper's cost argument. A hardwired model on a mature open node can be fabricated in the low-thousands-of-dollars range per 1,000 dies. The cost is die area, which for RouteVoice is dominated by the fixed engine and remains the open question.

---

## 6. LLMs and AI agents for chip design

### Domain LLMs and RTL benchmarks — `liu2023chipnemo`, `liu2023verilogeval`, `liu2024rtlcoder`, `chang2023chipgpt`
- **ChipNeMo (NVIDIA):** domain-adaptive tokenisation, continued pretraining and retrieval on LLaMA-2. The 70B model beats GPT-4 on the engineering-assistant and EDA-scripting tasks.
- **VerilogEval:** 156 HDLBits problems, checked by simulation.
- **RTLCoder:** a 7B open model that beats GPT-3.5 on all representative RTL benchmarks and GPT-4 on VerilogEval-Machine.
- **ChipGPT:** a zero-code LLM flow from natural language to Verilog.

Sources: arXiv 2311.00176, 2309.07544, 2312.08617, 2305.14019

### Agentic RTL and flow automation — `blocklove2023chipchat`, `he2024chateda`, `ho2024verilogcoder`, `zhao2024mage`, `jiang2024iicpilot`, `wang2025mcp4eda`, `lu2025autoeda`
- **Chip-Chat:** a human co-designed an 8-bit accumulator CPU with ChatGPT-4 and taped it out on a SkyWater 130 nm shuttle. The authors believe this was the first wholly AI-written HDL to reach tapeout.
- **ChatEDA (TCAD 2024):** an LLM agent that orchestrates RTL-to-GDSII tool scripts.
- **VerilogCoder:** 94.2% pass rate on VerilogEval-Human v2.
- **MAGE:** 95.7% on VerilogEval-Human v2, 23.3% above Claude-3.5-Sonnet.
- **IICPilot:** multi-agent backend flow on OpenROAD and iEDA.
- **MCP4EDA:** an MCP server driving Yosys, OpenLane and KLayout from Claude Desktop or Cursor. Reports 15–30% timing and 10–20% area improvements.
- **AutoEDA:** an MCP microservice agent with up to 9.9× accuracy over naive approaches.

Sources: arXiv 2305.13243, 2308.10204, 2408.08927, 2412.07822, 2407.12576, 2507.19570, 2508.01012

### Coding agents on full flows (2026) — `deng2026rtl2gds`, `ghose2026audopeda`, `tieu2026edatracer`
- **Deng et al.:** benchmarks general coding agents on a PicoRV32 RTL-to-GDS flow with commercial tools. Findings:
  - EDA "skills" do not ensure long-horizon completion.
  - Token ROI varies by up to 141× between agents.
  - Tcl and tool-version mismatches dominate the failures.
- **AuDoPEDA (Kahng group):** uses a Codex-class agent to modify OpenROAD itself, with up to 5.9% wirelength, 10.0% clock-period and 19.4% power improvements.
- **EDATracer:** outperforms Cursor and Claude Code by 6.4 and 7.2 points on EDA artifact Q&A.

Sources: https://arxiv.org/abs/2607.17528 · https://arxiv.org/abs/2601.06268 · https://arxiv.org/abs/2608.04032

### Surveys and RL placement — `zhong2023llm4eda`, `pan2025llmedasurvey`, `mirhoseini2021alphachip`
- **LLM4EDA (2023) and Pan et al. (2025):** survey LLM-for-EDA work.
- **AlphaChip (Nature 2021):** RL macro placement that produces placements comparable to or better than human experts in under 6 hours. An addendum was published in Nature in 2024.

Sources: arXiv 2401.12224, 2501.09655 · https://doi.org/10.1038/s41586-021-03544-w (preprint arXiv 2004.10746)

*RouteVoice relation (whole section):* Prior work evaluates agents on benchmark-scale RTL (HDLBits, PicoRV32) or on single flow stages. RouteVoice is a case study of a heterogeneous agent team (Claude Code as lead, Codex CLI workers) carrying a 10⁷-parameter-class ASR accelerator through RTL generation, audio-level equivalence, and open-PDK physical design with multi-corner timing. Its contribution here is an experience report with evidence logs, not a benchmark. Deng et al.'s failure taxonomy (long-horizon, tool-interface) is directly comparable to the failures RouteVoice hit, such as the d4-full routing non-convergence and lint and timescale regressions.

---

## 7. Local / on-device LLM trends and token demand

### Small open models — `abdin2024phi3`, `gemmateam2025gemma3`, `grattafiori2024llama3`, `meta2024llama32`, `qwen2024qwen25`, `yang2025qwen3`, `liu2024mobilellm`, `gunter2024apple`
- **Phi-3-mini:** 3.8B parameters trained on 3.3T tokens, 69% MMLU, small enough for a phone.
- **Gemma 3:** 1–27B, at least 128K context, with more local than global attention layers to cut KV cache.
- **Llama 3.2 1B/3B:** pruned and distilled from Llama 3.1 8B/70B, 128K context, with day-one Qualcomm, MediaTek and Arm support (September 2024).
- **Qwen2.5:** trained on 18T tokens. **Qwen3:** 0.6–235B, dense and MoE, with thinking and non-thinking modes.
- **MobileLLM:** sub-billion deep-thin models.
- **Apple:** an on-device foundation model of about 3B parameters.

Sources: arXiv 2404.14219, 2503.19786, 2407.21783, 2412.15115, 2505.09388, 2402.14905, 2407.21075 · https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/

### On-device runtimes — `ggml_llamacpp`, `mlc_llm`, `chen2018tvm`, `alizadeh2023flash`, `xue2024powerinfer2`, `lu2024slmsurvey`
- **llama.cpp:** C/C++ inference engine.
- **MLC LLM (built on TVM):** compiler-based deployment, including in-browser via WebLLM.
- **LLM in a flash:** runs models larger than DRAM by streaming from flash.
- **PowerInfer-2:** smartphone inference that splits work between NPU and CPU by neuron cluster.
- **Lu et al.:** survey and benchmark of 70 small language models (100M–5B) for on-device cost.

Sources: https://github.com/ggml-org/llama.cpp · https://llm.mlc.ai/ · arXiv 1802.04799, 2312.11514, 2406.06282, 2409.15790

### Token demand — `pichai2025q3tokens`
- Google reported more than 1.3 quadrillion tokens per month across its surfaces. That is up from 980 trillion announced in July 2025, and more than 20× growth in a year (Q3 2025 remarks, 29 Oct 2025).
- A later 3.2 quadrillion/month figure from I/O 2026 appeared only in secondary coverage and is **UNVERIFIED**.
- Critics (e.g., The Decoder) note that reasoning-model internal tokens inflate such counts. Not cited in the bib.

Source: https://blog.google/inside-google/message-ceo/alphabet-earnings-q3-2025/

*RouteVoice relation (whole section):* Small models are now good enough, and stable enough across release cycles, that freezing one into silicon for a fixed function (STT for a voice front-end) is defensible. Token-volume growth is the economic argument for moving high-volume, fixed-model inference off GPUs. Neither point is evidence that RouteVoice itself is cost-effective.

---

## Positioning: what is and is not novel in RouteVoice

**Not novel (cite, do not claim):**
1. **Hardwiring a specific model's weights into silicon.** Taalas HC1 has shipped it commercially for Llama 3.1 8B. HNLPU studies it academically at 5 nm. Bespoke printed classifiers and ROM-CiM (YOLoC, ROMA) predate both.
2. **Doing it on an open PDK with open signoff.** Ankhdjet (August 2026) explicitly claims the first open-source weights-to-mask compiler on SKY130, with DRC/LVS-clean signoff and a TinyTapeout submission.
3. **4-bit indices into small per-matrix codebooks.** This is the Deep Compression / EIE format, Mokey applies it to transformers, and SqueezeLLM-style non-uniform quantization is equivalent.
4. **Computing shared multiples of the input once and selecting them per fixed coefficient.** This is CSHM/MCM/DA in DSP since the 1980s–2000s, LUT-GEMM/T-MAC in software, and is claimed in Taalas's US20250123802A1 (one multiplier per possible value plus mask-configured routing) and US20260023566A1 (hardware codebook pointers). The project's own notes describe its primitive as Taalas-inspired.
5. **LLM agents driving open RTL-to-GDS flows.** ChatEDA, IICPilot, MCP4EDA, AutoEDA, Chip-Chat (taped out), AuDoPEDA and Deng et al. already do this.

**Plausibly novel (claim carefully, with evidence):**
1. **Scope.** To our knowledge (search date 2026-10-24), this is the first complete encoder–decoder ASR transformer (Moonshine) implemented as a hardwired-codebook engine on an open PDK. It is verified at the RTL level from audio to end-of-sequence against the reference model on real recordings, rather than a single matrix macro (Ankhdjet) or a projection (HNLPU).
2. **Node and PDK choice.** GF180MCU at 180 nm instead of SKY130 or an advanced node, with concrete routed, multi-corner (9-corner, 150 ns) timing and SAIF power for the fixed engine on an open 180 nm flow.
3. **Shared radix-16 partial products as the multiplier-less datapath for codebook-indexed transformer matrices.** The building blocks are known. Their combination with per-matrix codebooks inside a hardwired transformer engine, with bit-exact verification, appears undocumented in the open literature. The Taalas patents are the nearest disclosure and must be discussed.
4. **Agent-orchestration case study.** A multi-vendor agent team (Claude Code lead, Codex CLI workers) carried a large ML accelerator through open-PDK physical design, with audit trails, independent re-verification, and about $10.84 of cloud GPU spend against a $15 cap (per STATUS.md). Prior agentic-EDA work is benchmark-scale or single-stage.

**Must be stated as limitations (they bound the novelty claims):**
- No silicon.
- No full-chip signoff. The earlier full-array route (d4-full) did not converge, and current timing closure covers the engine block.
- Some model data was host-served in October (28.6 MB measured).
- Audio-level verification is partial: 53/83 segments exact at v49.
- The WER figures are on development recordings, not held-out data.
- Energy figures are post-route SAIF estimates, not measurements, and should be compared with node-scaled references (§4) rather than with advanced-node TOPS/W.

**Not verified / open items for the authors:**
- The independent HC1 measurement (14,357 tokens/s).
- The I/O 2026 3.2-quadrillion token figure.
- Hidden-ROM contents.
- Exact numbers from Groq's ISCA 2020 PDF (the hosted copy 404'd).
- Etched's primary Sohu page (404).
- The full author lists marked "and others".
- Venue strings marked "from author knowledge" in `refs.bib`.
