%TITLE Edge-AI Federated Learning for Sepsis Risk Stratification Using Privacy-Preserving Wearable Telemetry

%AUTHORS A. N. Author, *Member, IEEE*, B. M. Author, and C. O. Author

%AFFIL Department of Computer Science and Engineering, [University Name], [City], [Country] (e-mail: [corresponding.author@university.edu]). Manuscript prepared 16 November 2026.

%ABSTRACT Sepsis is a life-threatening condition in which the body reacts too strongly to an infection and begins damaging its own organs. Every hour of delayed antibiotic care increases the risk of death. Most machine-learning sepsis tools rely on dense electronic health record (EHR) data inside intensive care units (ICUs). Yet many patients first become ill on general hospital wards or at home, where wired monitors and hourly blood tests do not exist. Lightweight wearable patches can track heart rate, breathing, pulse waves and skin temperature around the clock, but they have tiny batteries, limited wireless bandwidth, and strict privacy laws that stop hospitals from pooling patient records. This paper presents FedWear-Sepsis, a four-tier edge and federated learning system that predicts sepsis risk from wearable streams while keeping raw patient data inside each hospital. The system combines (1) a signal-quality filter for wearable heart, pulse, motion and temperature sensors; (2) a time-aware transformer teacher model compressed into a 0.42 MB 8-bit student model running directly on a wearable microchip; (3) local differential privacy using Rényi accounting paired with cryptographic secure aggregation; (4) adaptive federated training with local batch normalisation and 50-times upload compression; and (5) a conformal alarm rule that limits false alerts to at most one per patient per day. In a 14-cohort simulation calibrated to published clinical statistics, federation lifted the weakest hospital's area under the receiver operating characteristic curve (AUROC) from 0.712 to 0.801, and formal privacy at $(\varepsilon = 3,\ \delta = 10^{-5})$ reached 0.822 AUROC while cutting upload traffic from 345 GB to 6.9 GB. These simulation benchmarks verify end-to-end system behaviour prior to live clinical trials.

%KEYWORDS Sepsis, early warning systems, federated learning, differential privacy, secure aggregation, edge artificial intelligence, wearable sensors, clinical decision support.

# I. INTRODUCTION

Sepsis occurs when an infection triggers a harmful chain reaction throughout the body that damages vital organs such as the lungs, kidneys and heart [@singer2016]. Global health studies estimate roughly 49 million sepsis cases and 11 million deaths each year, with the heaviest toll in low- and middle-income hospitals where monitoring staff are scarce [@rudd2020]. Early recognition saves lives because starting antibiotics and fluids a few hours sooner sharply lowers mortality, and small vital-sign shifts usually appear hours before organ failure becomes obvious [@singer2016; @seymour2019]. Consequently, many researchers have built machine-learning models that read electronic health records (EHRs) to warn clinicians ahead of time [@fleuren2020; @nemati2018; @shashikumar2021].

Past clinical AI studies show both strong promise and clear limits. Models trained on frequent ICU vital signs and lab draws routinely achieve an area under the receiver operating characteristic curve (AUROC) of 0.80--0.90, outperforming simple bedside checklists [@fleuren2020; @reyna2020]. However, hospital staff care less about abstract ranking scores and far more about early lead time, honest probability calibration, and avoiding "alarm fatigue" from constant false beeps [@sendak2020]. Furthermore, models built in one hospital often stumble elsewhere: an external check of a widely deployed commercial sepsis tool found an AUROC of just 0.63 with high false-alarm rates [@wong2021], and clinical trials show that alerts help patients only when paired with clear nursing workflows [@shimabukuro2017; @sendak2020]. Above all, nearly every published sepsis model assumes the patient is already inside an ICU with wired monitors and frequent blood tests.

In everyday care, sepsis frequently begins on general wards—where nurses check vitals every four to eight hours—or at home after hospital discharge. Modern adhesive patches and smartwatches can close these blind spots by continuously recording heart rate, heart-rate variability, breathing rate, pulse-wave perfusion and skin temperature [@allen2007; @weenk2017; @dunn2018], even catching hidden signs of infection before symptoms start [@mishra2020]. Building a multi-hospital sepsis detector from wearables, however, faces three tough barriers. First, **hospitals cannot pool raw data**: wearable streams are sensitive health records governed by strict privacy laws [@gdpr2016], yet single clinics rarely have enough wearable cases to train strong models alone. Second, **patches cannot stream everything to the cloud**: continuous raw waveforms quickly drain coin-cell batteries, overload ward Wi-Fi, and fail during network outages [@zhou2019; @shi2016]. Third, **federated learning alone is not fully private**: although federated learning (FL) shares model weights rather than patient files [@mcmahan2017], attackers can still reconstruct private records or infer patient membership from unprotected gradients [@zhu2019; @nasr2019; @melis2019].

We introduce **FedWear-Sepsis** ({fig:arch}) to solve these three challenges together. Raw wearable data remain inside each hospital, weight updates are shielded by both local differential privacy (DP) and threshold secure aggregation, and a tiny 0.42 MB 8-bit student model runs directly on the wearable chip. We detail the four-tier architecture, time-aware survival model, auditable Rényi DP ledger, 50-fold upload compression, conformal alarm control, and a 14-silo evaluation following TRIPOD+AI and PROBAST guidelines [@collins2024; @wolff2019].

%FIG arch | fig1_architecture.png | Four-tier FedWear-Sepsis architecture. Raw wearable data stay in Tiers 1--2; only clipped, noisy, masked weight updates cross the dashed hospital boundary into Tier 3, and calibrated alerts feed Tier 4 EHRs.

# II. RELATED WORK

Sepsis-3 defines onset as suspected infection accompanied by a two-point rise in the Sequential Organ Failure Assessment (SOFA) score [@singer2016]. Machine-learning models using gradient boosting, survival recurrences and utility-weighted training predict ICU sepsis hours early [@nemati2018; @shashikumar2021; @reyna2020], while optical photoplethysmography (PPG) and single-lead ECG patches bring continuous vital-sign tracking to general wards and homes [@allen2007; @weenk2017; @mishra2020]. Still, motion artefacts, skin-tone optical bias, patch dropouts and battery limits make raw wearable streams hard to model [@dunn2018; @sjoding2020].

Across hospitals, FedAvg [@mcmahan2017] and heterogeneity-aware upgrades—FedProx [@li2020], SCAFFOLD [@karimireddy2020], FedAdam [@reddi2021], local batch normalisation (FedBN) [@fedbn2021], asynchronous weighting [@xie2019], gradient compression [@konecny2016] and robust aggregation [@kairouz2021] via Flower or NVIDIA FLARE [@beutel2020; @roth2023]—enable collaborative healthcare AI [@rieke2020; @dayan2021]. Recently, federated LSTMs reached 0.806 AUROC for ICU sepsis [@duesing2025], but lacked formal DP, microcontroller execution and wearable inputs. Combining DP-SGD [@dwork2014; @abadi2016] tracked via Rényi DP [@mironov2017] with cryptographic secure aggregation [@bonawitz2017] blocks gradient leakage, while TinyML engines like TensorFlow Lite Micro run 8-bit models in kilobytes of RAM [@david2021; @banbury2021] without split-learning radio overhead [@gupta2018]. {tab:related} summarises our contributions against prior work.

%TABLE related | Positioning of FedWear-Sepsis against prior sepsis and clinical federated studies (DP: differential privacy; SA: secure aggregation).
| Study | Input Signals | Federated | Formal Privacy | On-Chip Edge AI | Alarm Rule |
| Nemati *et al.* [@nemati2018] | Hourly ICU EHR | No | No | No | Fixed cutoff |
| Shashikumar *et al.* [@shashikumar2021] | Hourly ICU EHR | No | No | No | Conformal |
| Dayan *et al.* [@dayan2021] | X-ray + EHR | Yes | No | No | Fixed cutoff |
| Düsing & Cimiano [@duesing2025] | Hourly ICU EHR | Yes | No | No | Fixed cutoff |
| **FedWear-Sepsis** | **5-min Wearable + EHR** | **Yes (4-tier)** | **DP + SA Ledger** | **Yes (0.42 MB INT8)** | **Site Conformal** |
%ENDTABLE

# III. PROBLEM FORMULATION AND PRIVACY MODEL

Let $K$ clinical silos hold private datasets $D_{k} = \{(x_{i}, y_{i}, \tau_{i})\}_{i=1}^{n_{k}}$, where $x_{i} \in \mathbb{R}^{T \times d}$ stores $d$ wearable features every 5 minutes over $T = 360$ minutes, $y_{i} \in \{0,1\}$ marks sepsis onset within $H = 6$ hours, and $\tau_{i}$ is time to onset or censoring. Predicting hourly discrete hazards $h_{j}(x)$ retains discharged patients and gives cumulative 6-hour risk:

%EQ cumrisk | p(y = 1 \mid x) = 1 - \prod_{j=1}^{H} \left(1 - h_{j}(x)\right)

Each silo minimises its local discrete survival negative log-likelihood $F_{k}(w) = \frac{1}{n_{k}} \sum_{i=1}^{n_{k}} \ell(f_{w}(x_{i}), y_{i}, \tau_{i})$, and the federation solves a proximal objective that limits client drift from reference weights $w^{\mathrm{ref}}$:

%EQ fedobj | w^{\star} = \arg\min_{w} \; \sum_{k=1}^{K} p_{k} F_{k}(w) + \frac{\lambda}{2} \left\lVert w - w^{\mathrm{ref}} \right\rVert_{2}^{2}, \qquad p_{k} \propto n_{k} \cdot \frac{\bar{\pi}}{\pi_{k}} \cdot \exp\left(-\alpha \tau_{k}\right)

Weighting by the ratio of global to local sepsis rate ($\bar{\pi}/\pi_{k}$) and staleness $\tau_{k}$ prevents large ICUs from overpowering low-prevalence general wards.

A randomised training rule $M$ provides $(\varepsilon,\delta)$-differential privacy if changing one record shifts output probabilities by at most $e^{\varepsilon}$ plus $\delta$ [@dwork2014]:

%EQ dp | \Pr\left[M(D) \in S\right] \;\leq\; e^{\varepsilon}\, \Pr\left[M(D^{\prime}) \in S\right] + \delta, \qquad \varepsilon(\delta) = \min_{\alpha > 1} \left[ \varepsilon_{\mathrm{RDP}}(\alpha) + \frac{\log(1/\delta)}{\alpha - 1} \right]

where privacy loss across 1500 rounds is tracked tightly via Rényi DP [@mironov2017]. Each gateway trains with DP-SGD [@abadi2016], clipping per-sample gradients $g_{i}$ to norm $C = 1.0$ and adding Gaussian noise:

%EQ dpsgd | \tilde{g} = \frac{1}{B} \left( \sum_{i \in \mathcal{B}} \frac{g_{i}}{\max\left(1, \left\lVert g_{i} \right\rVert_{2}/C\right)} + \mathcal{N}\left(0,\, \sigma_{k}^{2} C^{2} \mathbf{I}\right) \right)

Because each patient stays in one silo, privacy loss composes across rounds *within* that silo ($\max_{k} \varepsilon_{k}$ overall). Combining DP-SGD with threshold secure aggregation (`SecAgg+`, $t = 4$ of 5 sampled silos) [@bonawitz2017] protects against curious central servers, network snoopers and partner hospitals, while encrypted on-patch buffers protect lost wearables. Hardware budgets require **$\leq 20$ ms** latency and **$\leq 5$ mJ** energy per patch check, plus **$\leq 1$ MB** upload per round.

# IV. THE FEDWEAR-SEPSIS ARCHITECTURE

As shown in {fig:arch}, **Tier 1 (Wearable Patch)** samples single-lead ECG (250 Hz), dual-wavelength PPG (64 Hz), 3-axis motion (50 Hz) and skin temperature (0.25 Hz). Every 5 minutes, a Signal Quality Index rejects motion-corrupted beats, builds 42 physiological features (heart rate, SDNN, RMSSD, LF/HF ratio, ECG/PPG breathing rate, perfusion index, temperature slope, posture and wear context) alongside missingness masks and *time-since-last-observation* counters, and runs local INT8 inference. **Tier 2 (Ward/Home Gateway)** merges local EHR context (age, surgery, immune status) inside the hospital, runs overnight DP-SGD, and masks updates. **Tier 3 (Orchestrator)** aggregates masked sums, tracks RDP budgets and distils updates. **Tier 4 (Clinical Support)** delivers HL7 FHIR R4 alerts [@hl7fhir] and SHAP/attention explanations [@lundberg2017].

The server **teacher** (11.8 M parameters, 47.2 MB fp32) stacks separable convolutions and four transformer blocks with *time-delta attention* to capture how fast vitals worsen across irregular gaps. Gateways distil and quantise this teacher into a four-block residual convolutional **student** of **0.42 MB (INT8)** fitting in 96 kB SRAM [@david2021]. Each round, 5 of 14 silos run two Adam epochs [@kingma2015] aggregated via FedAdam [@reddi2021], while keeping batch normalisation and temperature scaling local (FedBN) [@fedbn2021; @guo2017]. Top-1% sparsification plus 8-bit quantisation with error feedback [@konecny2016] shrinks uploads 50-fold from 47.2 MB to **0.94 MB**. Spending 0.2 $\varepsilon$ on Laplace prevalence counts and 2.8 $\varepsilon$ on training keeps all 14 silos within $\varepsilon \leq 3.0$ at $\delta = 10^{-5}$ ({tab:budget}).

%TABLE budget | Per-silo Rényi DP ledger (target $\varepsilon = 3.0$, $\delta = 10^{-5}$, 1500 rounds).
| Silo Group | Windows $n_{k}$ | Noise $\sigma_{k}$ | Batch Rate $q_{k}$ | Rounds | $\varepsilon_{k}$ (Train) | $\varepsilon_{k}$ (Total) |
| A, B (Academic ICUs) | 388.5k--412.8k | 1.42--1.44 | 0.009 | 1470--1500 | 2.68--2.71 | 2.88--2.91 |
| C (Community ICU) | 176 200 | 1.51 | 0.010 | 1410 | 2.74 | 2.94 |
| D (General Ward) | 96 400 | 1.58 | 0.011 | 1365 | 2.77 | 2.97 |
| E (Home Cohort) | 41 300 | 1.61 | 0.012 | 1290 | 2.79 | 2.99 |
| F--N (9 Mixed Sites) | 8.2k--132.7k | 1.44--1.63 | 0.009--0.013 | 1150--1500 | 2.62--2.80 | 2.82--3.00 |
%ENDTABLE

On an ARM Cortex-M7 chip (480 MHz), the student scores a window in **11.8 ms** using **2.1 mJ** ({fig:edge})—under 1% of daily patch battery life. Scores feed four risk tiers ({fig:arch}) regulated by **split conformal prediction** [@angelopoulos2021]: weekly rolling site quantiles cap escalations at **$\leq 1$ alert per patient-day** with a 4-hour cool-down.

%FIG edge | fig5_edge_profile.png | Edge hardware profile: (a) $p_{95}$ latency and model size; (b) energy per risk score (log scale).

# V. EVALUATION PROTOCOL

Aligned with TRIPOD+AI and PROBAST [@collins2024; @wolff2019], we report *pooled*, *per-site* and *worst-site* metrics across 14 non-IID silos (96 412 stays, 8.8% sepsis prevalence; {tab:cohorts}) grounded in MIMIC-IV [@johnson2023], eICU [@pollard2018] and PhysioNet 2019 [@reyna2020] waveforms degraded to wearable sampling rates and dropout profiles [@weenk2017; @allen2007]. Across 25 paired runs (5 seeds × 5 folds), we compare **Local-Only**, **Centralised**, **FedAvg** [@mcmahan2017], **FedProx** [@li2020] and **FedWear-Sepsis** ($\varepsilon \in \{1,3,8,\infty\}$) using DeLong and Holm-corrected tests (0.02 non-inferiority margin). *Transparency note:* all Section VI figures come from our end-to-end simulation harness calibrated to {tab:cohorts} and published clinical statistics [@fleuren2020; @duesing2025]; they validate system behaviour rather than live clinical efficacy.

%TABLE cohorts | Summary of the 14-silo non-IID evaluation benchmark (6-hour horizon).
| Silos | Care Setting | Stays | Sepsis Rate | Signals | Benchmark Role |
| A, B | Academic ICUs | 24 180 | 10.4% | Wearable + EHR | Core test & ablations |
| C | Community ICU | 12 940 | 8.1% | Wearable + EHR | External check |
| D | General Ward | 9 460 | 6.2% | Wearable only | Ward deployment target |
| E | Home Care | 640 | 3.8% | Wearable only | Low-rate stress test |
| F--N | 9 Mixed Sites | 49 192 | 4.1%--11.7% | Mixed wearable | Non-IID heterogeneity |
%ENDTABLE

# VI. RESULTS

{tab:results} and {fig:rocpr} show 6-hour discrimination and alarm performance. Isolated **Local-Only** models average 0.781 AUROC and drop to 0.712 at the smallest clinic. **FedAvg** (0.836) and **FedProx** (0.839) recover most of the **Centralised** upper bound (0.842), while **FedWear without DP** reaches **0.847 AUROC** (0.801 worst-site) because local FedBN layers adapt to each hospital's sensor baseline.

%TABLE results | Primary 6-hour results (mean ± SD over 25 runs; sensitivity and lead time at ≤1 alert/patient-day).
| Configuration | AUROC | AUPRC | Sensitivity | Lead Time | ECE | Worst-Site AUROC |
| Local-Only | 0.781 ± 0.041 | 0.284 ± 0.036 | 0.52 | 3.1 h | 0.081 | 0.712 |
| Centralised Pool | 0.842 ± 0.009 | 0.352 ± 0.014 | 0.72 | 6.0 h | 0.047 | 0.793 |
| FedAvg [@mcmahan2017] | 0.836 ± 0.010 | 0.341 ± 0.015 | 0.69 | 5.4 h | 0.052 | 0.786 |
| FedProx ($\mu=0.01$) | 0.839 ± 0.010 | 0.346 ± 0.015 | 0.70 | 5.5 h | 0.050 | 0.789 |
| FedWear (no DP) | 0.847 ± 0.008 | 0.358 ± 0.013 | 0.73 | 6.1 h | 0.043 | 0.801 |
| FedWear ($\varepsilon = 8$) | 0.834 ± 0.010 | 0.339 ± 0.015 | 0.69 | 5.6 h | 0.048 | 0.792 |
| **FedWear ($\varepsilon = 3$)** | **0.822 ± 0.012** | **0.318 ± 0.016** | **0.67** | **5.2 h** | **0.055** | **0.781** |
| FedWear ($\varepsilon = 1$) | 0.803 ± 0.016 | 0.291 ± 0.018 | 0.61 | 4.4 h | 0.067 | 0.758 |
%ENDTABLE

%FIG rocpr | fig3_roc_pr.png | (a) ROC and (b) precision-recall curves (8.8% prevalence) across primary training setups.

With formal privacy enabled ({fig:privacy}), our primary **$\varepsilon = 3, \delta = 10^{-5}$** model reaches **0.822 AUROC**, **0.318 AUPRC**, **67% sensitivity** and a **5.2-hour early warning**, proving non-inferior to non-private FedAvg ($p = 0.018$) and beating isolated models by +0.041 AUROC (+0.069 worst-site). Accuracy drops steeply below $\varepsilon = 2$ and flattens past $\varepsilon = 8$.

%FIG privacy | fig2_privacy_utility.png | Privacy--utility trade-off across $\varepsilon \in [0.5, 32]$ at $\delta = 10^{-5}$: (a) AUROC and (b) AUPRC.

In {fig:convergence}, staleness-weighted FedAdam converges faster than FedAvg (430 vs 610 rounds to 95% peak), and 50× upload compression slashes 1500-round traffic from **345 GB to 6.9 GB** without hurting AUROC ({tab:ablation}). Conformal calibration holds bedside alerts at **0.94/patient-day** versus 1.14 under a fixed probability cutoff. Subgroup checks ({tab:fairness}) show consistent gains over local models, with demographic gaps under 0.022 AUROC [@obermeyer2019] and expected physiological dips in low-sensor home care (0.758) and immunosuppressed patients (0.798). Ablations ({tab:ablation}) confirm that teacher distillation ($-0.016$) and FedBN personalisation ($-0.013$) drive the biggest accuracy gains.

%FIG convergence | fig4_convergence.png | (a) Validation AUROC over 1500 rounds; (b) 50× reduction in cumulative hospital upload traffic.

%TABLE fairness | Subgroup performance of FedWear ($\varepsilon = 3$) vs isolated Local-Only models.
| Subgroup | Windows | FedWear AUROC | Local AUROC | Gap vs Mean |
| Academic / Community ICUs | 589 000 | 0.834 / 0.826 | 0.796 / 0.774 | +0.019 / +0.011 |
| General Ward / Home Care | 137 700 | 0.812 / 0.758 | 0.741 / 0.704 | -0.003 / -0.057 |
| Female / Male | 474 600 | 0.816 / 0.835 | 0.779 / 0.792 | -0.006 / +0.013 |
| Age $<65$ / Age $\geq 65$ | 474 600 | 0.809 / 0.831 | 0.768 / 0.788 | -0.013 / +0.009 |
| Immunosuppressed | 62 300 | 0.798 | 0.752 | -0.024 |
%ENDTABLE

%TABLE ablation | Ablation study at $\varepsilon = 3, \delta = 10^{-5}$ (alarms/day at 0.70 sensitivity).
| Variant | AUROC | AUPRC | $\Delta$AUROC | Alarms/Day | Upload |
| **Full FedWear-Sepsis** | **0.822** | **0.318** | --- | **0.71** | **0.94 MB** |
| No FedBN personalisation | 0.809 | 0.301 | -0.013 | 0.83 | 0.94 MB |
| No teacher distillation | 0.806 | 0.297 | -0.016 | 0.86 | 0.94 MB |
| No time-delta attention | 0.812 | 0.306 | -0.010 | 0.78 | 0.94 MB |
| No 50× compression | 0.823 | 0.319 | +0.001 | 0.70 | 47.20 MB |
| No conformal alarm rule | 0.822 | 0.318 | 0.000 | 1.14 | 0.94 MB |
%ENDTABLE

# VII. DISCUSSION, LIMITATIONS AND CONCLUSION

Keeping batch normalisation and conformal thresholds local lets federated models beat isolated hospital training while holding false alarms below one per patient-day, and on-chip INT8 inference keeps monitoring alive during Wi-Fi drops at under 1% daily battery cost. Because alerts only improve survival inside strong clinical workflows [@sendak2020; @shimabukuro2017], Tier 4 outputs clear HL7 FHIR R4 explanations [@hl7fhir]. Retaining raw waveforms on-site satisfies GDPR data minimisation [@gdpr2016], while versioned registries and drift checks align with EU AI Act [@aiact2024] and FDA SaMD rules [@fda2021]. Clinical rollouts must also audit optical PPG accuracy across skin tones [@sjoding2020] and protect small rural clinics from excess DP noise [@obermeyer2019].

Key limitations include reliance on calibrated simulation benchmarks rather than a live patient trial [@johnson2023; @pollard2018], antibiotic-order label shift [@wong2021], window-level rather than encounter-level DP clipping, and the honest-majority assumption of secure aggregation. Future work will run prospective shadow-mode ward trials [@collins2024] and federated self-supervised pre-training on unlabelled home wearables [@rudd2020]. Overall, **FedWear-Sepsis** provides a practical, privacy-preserving blueprint for moving early sepsis warning from ICUs onto general wards and into patients' homes.
