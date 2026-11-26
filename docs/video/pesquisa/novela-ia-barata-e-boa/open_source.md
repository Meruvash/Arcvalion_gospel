# Open-source / open-weight AI video and lip-sync for cheap Portuguese micro-dramas (state as of 22 Nov 2026)

Research note: about 16 tool calls. Many timing figures come from secondary blogs and aggregators, and some dated pages carry 2026 dates I could not check against primary sources. Every item is dated where the source gives a date. Conflicts are flagged. Background facts not taken from a fetched source are labeled "(background knowledge)".

## Q1. Which open model gives the best human quality that actually fits a free T4 (16 GB, no bf16)? Are there working Kaggle/Colab notebooks?

### Takeaway
On a T4, the realistic options are Wan 2.1/2.2 14B in GGUF Q4/Q5 or INT8 with CPU offload plus 4-8 step Lightning/lightx2v LoRAs at about 832x480, LTX-Video (older, small and fast), and Wan 2.1 1.3B. None of these reliably gives close-up human faces and hands at the quality of closed models. The 14B Wan I2V at 480p is the best bet for people on a T4, and it is a large step up from TI2V-5B. That fits our own test, where TI2V-5B at 576px on a T4 deformed faces and hands. The practical free pipeline is: make good stills (Wan 2.2 or Qwen-Image at 960px+, already good in our tests), then run 14B I2V at 480p with a Lightning LoRA on short shots, then upscale.

### Cited Findings
- 14 Nov 2026 Colab/Kaggle guide. Lists these models as running on a free T4 (about 15 GB usable):
  - Wan 2.1 T2V 1.3B at 832x480, 81 frames ("native fit")
  - Wan 2.1/2.2 14B through Wan2GP/GGUF at 832x480, which needs INT8/Q4_K_M plus CPU offload
  - FastWan/Turbo LoRAs at 4-8 steps ("best iteration speed on T4")
  - LTX-Video at 768x512, 65-97 frames ("very fast; low memory")
  - CogVideoX-2B/5B
  
  The guide gives no measured render times. Its tips: CPU offload, VAE tiling, ComfyUI `--lowvram`, quantized text encoders (umt5-xxl in bf16 strains system RAM), stay at 480p with 49-81 frames, and run one render worker per GPU on Kaggle's 2xT4. Kaggle quota: about 30 GPU h/week, 12 h max per session. Colab quota is dynamic. — [Ahmed Fayaz, 14 Nov 2026](https://www.ahmedfayaz.com/blog/colab-kaggle-video-generation-setup)
- Free Colab/Kaggle T4 has about a 15 GB VRAM ceiling, and the /kaggle/working disk is capped at 20 GB, so model files and outputs must fit. — [same guide, via search summary](https://www.ahmedfayaz.com/blog/colab-kaggle-video-generation-setup)
- A known Kaggle 2xT4 notebook exists for **Wan 2.2 Animate 14B** in ComfyUI. It uses GGUF files stored as Kaggle Datasets, the ComfyUI-GGUF and WanVideoWrapper nodes, and needs Internet plus the "2 x T4" accelerator. It is an Animate (motion/character replacement) workflow; I2V needs the I2V GGUF files swapped in. — [kelvinweijun/wan-2.2-animate-comfyui-kaggle (GitHub)](https://github.com/kelvinweijun/wan-2.2-animate-comfyui-kaggle)
- Wan 2.2 I2V A14B GGUF quants are published by QuantStack and bullerwins (the latter includes an example workflow). The official ComfyUI "Wan2.2 14B I2V" template links to them. — [QuantStack HF](https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF); [bullerwins HF](https://huggingface.co/bullerwins/Wan2.2-I2V-A14B-GGUF); [ComfyUI docs](https://docs.comfy.org/tutorials/video/wan/wan2_2)
- Wan 2.2 I2V loads two 14B experts (high-noise and low-noise). A reported low-VRAM setup uses Q4 GGUF for both experts, the Lightx2v I2V LoRA, the Wan 2.1 text encoder and the Wan 2.1 VAE, and ran 5-second clips on an 8 GB laptop GPU. A 15 GB T4 should therefore fit, though slowly. — [Runflow, 2026](https://www.runflow.io/blog/comfyui-wan-2-2-image-to-video); [Kombitz, 6 Aug 2025](https://www.kombitz.com/2025/08/06/how-to-use-wan-2-2-image-to-video-with-gguf-in-comfyui/)
- InfiniteTalk has GGUF weights (Kijai/WanVideo_comfy_GGUF) that pair with a Wan 2.1 I2V 14B GGUF base (city96). Suggested starting point is Q4_K_M for about 8 GB. I found no Kaggle- or T4-specific InfiniteTalk notebook. — [Patreon guide](https://www.patreon.com/AIKnowledgeCentral/posts/your-talking-138441616); [Next Diffusion](https://www.nextdiffusion.ai/tutorials/create-lip-sync-videos-from-images-with-infinitetalk-in-comfyui)
- HunyuanVideo 1.5 (8.3B) is described as running on 24 GB consumer GPUs. WanGP claims it can run Hunyuan 1.5 on as little as 6 GB with heavy offload. — [ComfyUI docs](https://docs.comfy.org/tutorials/video/hunyuan/hunyuan-video-1-5); [WanGP README on HF](https://huggingface.co/vidfom/wan2gp/blob/main/README.md)

### Inferences
- (Background knowledge) The T4 is Turing (sm_75). It has no native bf16 and no FP8 tensor cores. FP8 checkpoints are upcast or emulated (slow), and bf16 models must run in fp16 (overflow risk with some Wan/Hunyuan layers) or through GGUF dequantization. GGUF Q4-Q8 is therefore the most reliable route on a T4, and FP8 "speed" claims made on 4090/H100 do not carry over.
- Expect very long renders on a T4 for 14B at 480p and 81 frames, even with 4-step LoRAs plus offload. The 4090 figure is about 1-3 min at 480p (see Q2), and the T4 has roughly 1/4 to 1/6 of a 4090's throughput. That puts a T4 plausibly at about 5-20 min per clip, which is an inference, not a measured number. With 30 h/week, that is roughly 90-360 raw 5 s clips per week before retakes.
- Our TI2V-5B face/hand deformation matches its role as the "small" model. The 14B A14B MoE is the model the community uses for people. Wan-Animate (2.2, and Wan-Animate-2 from Aug 2026) is useful for driving a consistent character from a reference video.

### Gaps
- No independent, measured seconds-per-clip for Wan 2.2 14B GGUF on a Kaggle T4 was found.
- No verified Kaggle notebook for InfiniteTalk, HunyuanVideo 1.5 or LTX-2 on a T4 was found.
- LTX-2/2.5 (19-22B, with audio) on a T4 is unverified. LTX advertises 12 GB local runs, but that claim is about RTX cards with FP8/FP4.

## Q2. Time and cost per 5 s clip on a rented 4090/H100 for Wan 2.2 14B (Lightning), LTX-2/2.5 and HunyuanVideo 1.5

### Takeaway
On a rented RTX 4090 at $0.34/h (RunPod community), raw GPU cost is tiny, on the order of cents per final minute. Retakes and human time dominate. Rough figures per 5 s clip:
- Wan 2.2 14B with the 4-step Lightning LoRA: about 1-3 min at 480p, plausibly 2-6 min at 720p (extrapolated)
- HunyuanVideo 1.5 step-distilled: about 75 s (Tencent's own claim)
- LTX-2 distilled: seconds to a few minutes (community figures)

### Cited Findings
- **RunPod prices (fetched 22 Nov 2026):**

  | GPU | Community | Secure | Serverless |
  |---|---|---|---|
  | RTX 4090 | $0.34/h | $0.89/h | $1.34/h |
  | RTX 5090 | $0.69/h | $1.39/h | $1.89/h |
  | L40S | $0.79/h | $1.09/h | not listed |
  | A100 80GB PCIe | from $1.19/h | $2.09/h | not listed |
  | A100 80GB SXM | from $1.39/h | $2.19/h | not listed |
  | H100 PCIe | from $1.99/h | $2.89/h | not listed |
  | H100 SXM | from $2.69/h | $4.39/h | $5.89/h |

  — [RunPod pricing](https://www.runpod.io/pricing)
- **Vast.ai:** the live price grid did not render. The page only says prices are market-set across 40+ data centres and that interruptible instances are "50%+ cheaper" than on-demand. — [Vast.ai pricing](https://vast.ai/pricing)
- **Modal:** not checked (gap).
- **Wan 2.2 14B with the Lightning 4-step LoRA on an RTX 4090:**
  - About 1-3 min for a 5 s 480p clip, versus 40-50 min without the LoRA. 720p "roughly doubles both VRAM use and render time." — [LocalAIMaster](https://localaimaster.com/blog/wan-video-generation-guide)
  - A separate table reports 44 s per clip for A14B fp8 plus Lightning at 640x640, 16 fps, 81 frames. — [Atomic Chat comparison](https://atomic.chat/blog/guides/best-local-ai-video-generators)
  - CONFLICT: these figures vary about 3x depending on settings and frontend.
- **Wan 2.2 TI2V-5B (no Lightning):** a 5 s 720p clip in under about 9 min on a 4090. — [LocalAIMaster](https://localaimaster.com/blog/wan-video-generation-guide)
- The Lightning LoRAs for Wan 2.2 come from lightx2v. — [lightx2v/Wan2.2-Lightning HF](https://huggingface.co/lightx2v/Wan2.2-Lightning/blob/refs%2Fpr%2F15/README.md)
- **HunyuanVideo 1.5:**
  - 8.3B parameters. Tencent released a 480p I2V step-distilled model (8 or 12 steps), with "up to 75% reduction in end-to-end time" and a single RTX 4090 generating a video "within 75 seconds" (vendor claim; clip settings unstated). — [Tencent HF model card](https://huggingface.co/tencent/HunyuanVideo-1.5); [step-distillation notes](https://huggingface.co/tencent/HunyuanVideo-1.5/blob/main/assets/step_distillation_comparison.md); [tech report arXiv 2511.18870, Nov 2025](https://arxiv.org/html/2511.18870v1)
  - LightX2V publishes 4-step distilled Hy1.5 models and an FP8 version with "50% memory reduction". — [lightx2v/Hy1.5-Distill-Models](https://huggingface.co/lightx2v/Hy1.5-Distill-Models)
- **LTX-2 / LTX-2.5:**
  - About 6 s for 121 frames at 720p on a 4090 with the distilled model (community knowledge base). — [Banodoco KB](https://nathanshipley.github.io/banodoco-kb/kb/ltx2/index.html)
  - 1080p 10 s clips: 2 min 46 s (NVFP8) and 2 min 05 s (NVFP4) on a 4090 (blog; unclear whether distilled). — [WaveSpeed/NemoVideo blog](https://www.nemovideo.com/ja-JP/blog/ltx-2-fp4-vs-fp8-rtx-guide)
  - Distilled at 768x768, batch 4: about 13-15 s. — [WaveSpeed](https://wavespeed.ai/blog/posts/blog-ltx-2-vram-requirements)
  - CONFLICT: aggregator figures range from about 22 s on an RTX Pro 6000 to about 7 min on an A100, with no common settings. — [Apatero](https://apatero.com/blog/ai-video-generation-speed-benchmarks-2025)
- **LTX-2.5 open weights (reported 10 Nov 2026):**
  - 22B distilled transformer, about 66 GiB download, fp8 plus CPU/disk offload for smaller GPUs. LTX advertises 12 GB local generation.
  - Synchronized audio and video, multishot in one pass, 2x latent upscaler, 4K/8K workflows.
  
  — [VP Land, 10 Nov 2026](https://www.vp-land.com/stories/lightricks-releases-ltx-2-5-open-weights-for-custom-lora-training-free-under-10m-in-revenu); [RunPod blog on LTX-2.5](https://runpod.io/blog/ltx-2-5-the-open-weights-world-model-built-for-speed-and-how-to-run-it-on-runpod)
- **LTX-2 launch:** open weights announced 6 Jan 2026, with "native 4K" and synchronized audio. — [Lightricks press release, 6 Jan 2026](https://www.globenewswire.com/news-release/2026/01/06/3213304/0/en/Lightricks-Open-Sources-LTX-2-the-First-Production-Ready-Audio-and-Video-Generation-Model-With-Truly-Open-Weights.html)

### Inferences (my arithmetic, not sourced figures)
- One minute of final video is 12 clips of 5 s.
- **Wan 2.2 14B with Lightning at 720p on a 4090 ($0.34/h community):**
  - At about 4 min per clip, 12 clips take about 48 GPU-min, roughly $0.27 per final minute with no retakes.
  - With 3-4 takes per usable shot (typical for faces and hands), about $0.80-1.10 per minute.
  - On Secure Cloud ($0.89/h), about $2-3 per minute.
  - Add idle and setup time (model download of tens of GB, about 10-20 min per pod start).
- **HunyuanVideo 1.5 distilled at 480p (about 75 s per clip):** about 15 GPU-min per minute, roughly $0.09 per minute before retakes.
- **LTX-2/2.5 distilled at 720p:** GPU cost is negligible (cents). The binding constraint is quality, not cost (see Q3).
- **H100 SXM ($2.69/h):** likely 1.5-2.5x faster than a 4090 for these models (not measured here). The cost per clip is usually similar or higher. An H100 only makes sense for unquantized bf16 runs or for high resolution and long frame counts that do not fit in 24 GB.
- Even with generous retakes, open models on rented GPUs come to roughly $1-5 per finished minute of GPU cost. That is far below closed APIs, but labour (curation, retakes, editing) dominates.

### Gaps
- No single source benchmarks all three models at the same resolution, frame count and GPU.
- No measured H100 or L40S timings were found for Wan 2.2 Lightning or HunyuanVideo 1.5.
- Vast.ai and Modal prices were not retrieved.

## Q3. Quality versus top closed models (faces, hands, motion): leaderboards and the current open-weight landscape

### Takeaway
The freely downloadable, commercially usable models are far behind the closed leaders on Artificial Analysis. LTX-2.5 sits about 250 Elo behind #1 in image-to-video, and Wan 2.2 and HunyuanVideo 1.5 are not even listed in the current I2V top 36. Alibaba stopped releasing Wan weights at 2.2: 2.5, 2.6, 2.7 and 3.0 are API-only. Some "open-weight" high scorers such as MiniMax H3 carry restrictive licences.

### Cited Findings
- **Artificial Analysis image-to-video leaderboard (AA-Video-I2V v2.1, fetched 22 Nov 2026; no snapshot date shown; model release dates Jan-Nov 2026):**

  | Rank | Model | Elo |
  |---|---|---|
  | 1 | Dreamina Seedance 2.5 | 1162 |
  | 5 | MiniMax H3 (768p) | 1136 |
  | 7 | SkyReels V4 | 1125 |
  | 12 | Wan 3.0 | 1110 |
  | 23 | Kling 3.0 Omni Pro | 1005 |
  | 26 | MAGI-2 Preview | 967 |
  | 28 | Veo 3.1 | 955 |
  | 32 | LTX-2.5 Fast | 914 |
  | 33 | LTX-2.5 Pro | 913 |
  | 35 | LTX-2.3 Pro | 841 |
  | 36 | LTX-2.3 Fast | 834 |

  HunyuanVideo and Kandinsky are not listed. The tool's open-weights flags were inferred from HF links. It flagged MiniMax H3, "Hyperflow H3" and "Pika H3 Flex" as open, which I could not verify. Treat this with caution. — [Artificial Analysis I2V leaderboard](https://artificialanalysis.ai/video/leaderboard/image-to-video)
- **Wan open weights status (6 Sep 2026):**
  - Wan 2.1 (Feb 2025) and Wan 2.2 (28 Jul 2025) are Apache 2.0, plus Wan2.2-S2V-14B, Wan-Dancer-14B (Jul 2026) and Wan-Animate-2 (Aug 2026, built on Wan 2.2, Apache 2.0).
  - Wan 2.5-Preview, 2.6, 2.7 and 3.0 have no weights (Alibaba Cloud Model Studio API only).
  - Claims that Wan 2.7 is on HF under Apache are wrong.
  
  — [HowAIWorks, 6 Sep 2026](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2)
  
  CONFLICT: a review site claims Wan 2.6 weights are on HF ([Vibedex](https://vibedex.ai/blog/wan-26-review-2026)), contradicted by [wan27.org](https://wan27.org/blog/wan-2-6-open-source-guide) and [Kenerate, Nov 2026 "Is Wan 3.0 open source"](https://kenerateai.com/blogs/is-wan-3-0-open-source). The majority view is: no.
- **MiniMax H3:** video weights released under a community licence that bars local deployment in the US, EU, UK and South Korea without written authorization (per HowAIWorks). Brazil was not mentioned. — [HowAIWorks, 6 Sep 2026](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2)
- **SkyReels V4 and MAGI-2:** listed on AA without open-weight links. I did not verify whether open SkyReels V2/V3 or MAGI-1 weights remain the latest open versions. — [Artificial Analysis](https://artificialanalysis.ai/video/leaderboard/image-to-video)

### Inferences
- For Portuguese micro-dramas built on talking close-ups, the faces and hands of open models (Wan 2.2 14B, HunyuanVideo 1.5, LTX-2.5) will show visibly more artefacts than Seedance, Kling or Veo. Mitigations: medium shots, short 2-4 s cuts, I2V from strong stills, limited hand action, and lip-sync passes.
- MiniMax H3 might be the strongest "open" model by Elo, but its licence and hardware needs make it unsuitable without a legal check.

### Gaps
- No current VBench numbers were retrieved.
- No AA text-to-video snapshot was retrieved.
- No independent face/hand-specific benchmark was found.
- Mochi, FramePack, SkyReels V2/V3 and MAGI-1 were not researched in detail. They are older (2024-2025) and not on the current AA top list.

## Q4. Open lip-sync / talking avatars for Portuguese audio (language-agnostic?) and quality

### Takeaway
Audio-driven open models (InfiniteTalk, MultiTalk, Wan2.2-S2V, LatentSync, plus the others named in the brief) condition on acoustic features (Whisper or wav2vec), not on text. They are effectively language-agnostic, but no published Portuguese evaluation exists. InfiniteTalk (Wan 2.1 14B based, GGUF available, 8-step distilled in v1.5) is the most practical choice for long dialogue scenes. LatentSync is the lightest option for redubbing an existing clip.

### Cited Findings
- **InfiniteTalk (MeiGen-AI):** unlimited-length talking video, image-to-video and video-to-video. v1.5 switched to Whisper-Large audio features and added an 8-step distilled mode. — [GitHub MeiGen-AI/InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk)
- **InfiniteTalk paper:** reports lip-sync gains but a trade-off between sync scores and visual quality or identity. It also notes that sync metrics miss errors during large head motion. No per-language breakdown. — [arXiv 2508.14033](https://arxiv.org/pdf/2508.14033)
- **LatentSync and LiveSync on HDTF:** LiveSync wins on sync, LatentSync wins on visual quality and identity. — [LiveSync arXiv 2610.23558](https://arxiv.org/pdf/2610.23558); [LatentSync arXiv 2412.09262](https://arxiv.org/pdf/2412.09262)
- **Multilingual evidence:** a 2026 multi-reference benchmark measured Wan lip-sync at 82.6% (English) versus 84.0% (Chinese). That suggests little language dependence, but it is unclear whether S2V was the model tested. — [MultiRef-Compass, arXiv 2607.14189](https://arxiv.org/pdf/2607.14189)
- **Anecdotal single-clip comparison:** InfiniteTalk gives steadier head and background, while Wan 2.2 S2V gives more nuanced expressions. — [infinitetalk.org](https://infinitetalk.org/lip-sync-video-to-video)
- **Licences and VRAM:** LatentSync and InfiniteTalk are listed as Apache 2.0. LatentSync needs about 8-18 GB VRAM depending on version. — [Percify roundup, 2026](https://percify.io/blog/the-best-free-ai-lip-sync-video-generators-for-instant-content-creation)
- **LTX-2 / LTX-2.5:** generate synchronized audio natively. Speech quality in Portuguese is untested in any source found. — [VP Land](https://www.vp-land.com/stories/lightricks-releases-ltx-2-5-open-weights-for-custom-lora-training-free-under-10m-in-revenu)

### Inferences
- Pipeline suggestion: Portuguese TTS (for example the editor's cloned voice), then InfiniteTalk I2V from a consistent character still. LatentSync is the lighter, T4-friendly option for fixing lips on an already-generated Wan clip.
- (Background knowledge) Older LatentSync 1.5 is said to fit in about 8 GB; plausible on a T4 in fp16.

### Gaps
- No Portuguese or PT-BR evaluation of any lip-sync model was found.
- MultiTalk, OmniAvatar, FantasyTalking and HunyuanVideo-Avatar were not individually verified (licences, VRAM) in this pass.

## Q5. Licences for commercial use (video models and character-consistent image models)

### Takeaway
- Safe for commercial use: Wan 2.1/2.2 family (Apache 2.0), Qwen-Image-Edit-2511 (Apache 2.0), InfiniteTalk and LatentSync (Apache 2.0, per a roundup).
- LTX-2.x is free under the LTX-2.x Community License only below $10M annual revenue.
- FLUX.1 Kontext [dev] is non-commercial (background knowledge; verify).
- MiniMax H3 has geographic restrictions.

### Cited Findings
- **Wan 2.1 / 2.2, S2V, Dancer, Animate-2:** Apache 2.0. — [HowAIWorks, 6 Sep 2026](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2)
- **LTX-2.x Community License:** free commercial use below $10M annual revenue (including subsidiaries and affiliates); paid Commercial Use Agreement above that; transferring fine-tunes may need a paid licence; gated HF access. — [VP Land, 10 Nov 2026](https://www.vp-land.com/stories/lightricks-releases-ltx-2-5-open-weights-for-custom-lora-training-free-under-10m-in-revenu); [Digital Applied licence audit 2026](https://www.digitalapplied.com/blog/open-weight-model-licence-audit-2026)
  
  CONFLICT (minor): the Jan 2026 launch release said "<$10M ARR" ([GlobeNewswire](https://www.globenewswire.com/news-release/2026/01/06/3213304/0/en/Lightricks-Open-Sources-LTX-2-the-First-Production-Ready-Audio-and-Video-Generation-Model-With-Truly-Open-Weights.html)), while later sources say total annual revenue. Check the licence text.
- **Qwen-Image-Edit-2511:** Apache 2.0, with "significantly improved" character consistency, multi-person group edits preserving identity, and GGUF available (unsloth). — [HF model card](https://huggingface.co/Qwen/Qwen-Image-Edit-2511); [The Decoder](https://the-decoder.com/qwen-updates-image-editing-model-with-better-character-consistency/); [unsloth GGUF](https://huggingface.co/unsloth/Qwen-Image-Edit-2511-GGUF)
- **HunyuanVideo 1.5:** licence not retrieved this pass.
- **MiniMax H3:** community licence restricting local deployment in the US, EU, UK and South Korea. — [HowAIWorks](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2)

### Inferences
- For a Brazilian creator well under $10M revenue, LTX-2.5 is usable commercially. Wan 2.2 plus Qwen-Image-Edit-2511 plus InfiniteTalk is the cleanest fully permissive stack.
- (Background knowledge) The Tencent Hunyuan community licences historically excluded the EU, UK and South Korea and set a monthly-active-user threshold. They have not excluded Brazil, but the 1.5 licence should be checked.
- Project rule: this project's CLAUDE.md forbids AI people in agro videos and AI images in site articles. Any micro-drama with AI humans needs an explicit editor decision.

### Gaps
- Licence texts for FLUX.1 Kontext [dev], PuLID, IP-Adapter and HunyuanVideo 1.5 / Avatar were not fetched.
- The exact LTX revenue metric (ARR versus revenue) was not confirmed against the licence text.
