%TITLE Edge-AI Federated Learning for Sepsis Risk Stratification Using Privacy-Preserving Wearable Telemetry

%AUTHORS A. N. Author, *Member, IEEE*, B. M. Author, and C. O. Author

%AFFIL This manuscript was prepared as part of a Master's research project. The authors are with the Department of Computer Science and Engineering, [University Name], [City], [Country] (e-mail: [corresponding.author@university.edu]).
%AFFIL Manuscript prepared 16 November 2026. This work was supported by [funding body and grant number]. For the purpose of open access, the authors have applied a CC BY public copyright licence to any Author Accepted Manuscript version arising.

%ABSTRACT Sepsis is the leading cause of death among hospitalised patients and every hour of delayed recognition measurably increases mortality, yet existing machine-learning early-warning systems remain anchored to dense electronic health record data generated inside intensive care units. The clinical shift towards continuous monitoring on general wards and at home exposes a structural mismatch: the only temporally dense signals available are body-worn, they are generated at the edge under tight energy and bandwidth budgets, and they cannot lawfully be pooled into a central repository. This article presents FedWear-Sepsis, a four-tier edge--federated framework that stratifies sepsis risk from wearable telemetry without centralising patient data. The framework couples (i) a signal-quality-aware preprocessing pipeline for electrocardiography, photoplethysmography, accelerometry and skin temperature; (ii) a temporal convolutional transformer with time-delta encoding, trained federatively and distilled into a 0.42 MB INT8 student that runs on a microcontroller; (iii) site-local differentially private stochastic gradient descent with Rényi accounting and threshold secure aggregation, such that no per-site update leaves the hospital trust boundary in the clear; (iv) staleness-weighted adaptive aggregation with local batch-normalisation personalisation and 50-fold uplink compression; and (v) a conformal alarm policy that bounds the false-alarm rate rather than the probability threshold. We formalise the privacy, communication and energy constraints, specify the threat model, and report a complete evaluation protocol for fourteen heterogeneous silos. In the simulation harness used to validate the pipeline end to end, federation recovered most of the gap between single-site training and pooled training, the worst-performing site improved from 0.712 to 0.801 AUROC, and an $(\varepsilon=3,\ \delta=10^{-5})$ guarantee cost 0.025 AUROC relative to the non-private federation while remaining above the best single-site model. Uplink traffic fell from 345 GB to 6.9 GB over 1500 rounds. These quantities are provisional outputs of a calibrated simulation and are not clinical performance estimates; the full multi-site evaluation is specified and will replace them.

%KEYWORDS Sepsis, early warning systems, federated learning, differential privacy, secure aggregation, edge artificial intelligence, wearable sensors, risk stratification, clinical decision support.

# I. INTRODUCTION

Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection, and it remains the dominant pathway to death in hospitalised patients worldwide [@singer2016]. Contemporary Global Burden of Disease estimates attribute approximately 49 million incident cases and 11 million sepsis-related deaths each year, more than half of them in low- and middle-income settings where continuous monitoring infrastructure is scarcest [@rudd2020]. The clinical logic of early recognition is uncompromising: each hour of delay before antimicrobial therapy and source control is associated with a measurable increase in mortality, and the therapeutic window typically opens hours before the diagnostic criteria are satisfied [@singer2016; @seymour2019]. Consequently, a substantial machine-learning literature has been devoted to predicting sepsis onset from electronic health record (EHR) streams several hours before clinical suspicion [@fleuren2020; @nemati2018; @shashikumar2021].

That literature has produced three durable findings, and one uncomfortable one. First, models trained on high-frequency physiological and laboratory data can discriminate impending sepsis with an area under the receiver operating characteristic curve (AUROC) in the 0.80--0.90 range, consistently outperforming aggregate early-warning scores [@fleuren2020]. Second, the performance that matters clinically is not discrimination but *operating behaviour*: sensitivity at an alarm burden that clinicians will tolerate, calibration of the risk estimate, and the lead time gained before the standard of care would have acted. Third, the evaluation landscape is fragile in ways that are now well documented: a proprietary sepsis model deployed at scale was shown on external validation to have an AUROC of 0.63 with a positive predictive value below 5% [@wong2021], and the prospective evidence that alerts improve outcome remains thin and mixed [@shimabukuro2017; @sendak2020]. The uncomfortable finding is that nearly all of this evidence is generated inside intensive care units, from EHR variables that exist only because a patient is already catheterised, ventilated and sampled hourly.

The patients who would benefit most from earlier recognition are frequently not in an intensive care unit. Sepsis often begins on the ward or at home, in patients whose physiology is monitored either intermittently by a nurse or continuously by a consumer-grade wearable. Body-worn sensing has advanced to the point where heart rate, heart-rate variability, respiratory rate, perfusion index and skin temperature can be acquired continuously at clinical fidelity, and pre-symptomatic physiological signatures of infection have been demonstrated from smartwatch streams [@mishra2020; @weenk2017; @dunn2018; @allen2007]. This creates an opportunity and, simultaneously, three hard constraints that the current generation of sepsis models does not address.

*Data cannot be pooled.* Wearable telemetry is generated under the direct control of the patient and is, in most jurisdictions, sensitive personal data whose secondary use requires an explicit legal basis; cross-institution pooling is frequently impossible in practice even where it is nominally lawful [@gdpr2016]. Wearable cohorts are also small at any single institution, which is precisely the regime in which single-site models overfit and transfer poorly.

*Computation cannot be centralised.* Continuous multi-channel telemetry from thousands of patients generates data volumes that outstrip the uplink capacity and power budget of a body-worn patch, and round-trip cloud inference is incompatible with the latency and availability requirements of an alerting device that must remain functional during a connectivity outage [@zhou2019; @shi2016].

*Privacy cannot be assumed from the training topology.* Federated learning (FL) removes the need to move raw records, but it does not by itself provide a privacy guarantee: gradients leak training samples under reconstruction attacks, and repeated server-side observation of per-client updates permits membership and property inference [@zhu2019; @nasr2019; @melis2019]. Reporting a federated system as "privacy-preserving" without a formal mechanism and an accounting method is therefore a substantive omission rather than a stylistic one.

This article addresses these constraints jointly. We propose FedWear-Sepsis, an edge--federated risk-stratification framework in which wearable telemetry is processed and modelled inside the trust boundary in which it was generated, model updates are protected by site-local differential privacy (DP) and threshold secure aggregation, and a distilled student model executes on the sensing hardware itself. The design is evaluated against a pre-registered protocol spanning fourteen heterogeneous silos drawn from public critical-care corpora and a wearable ward cohort, with explicit accounting for communication cost, energy, calibration and subgroup performance.

The contributions are as follows.

- **A four-tier reference architecture** ({fig:arch}) that separates wearable sensing, edge gateways, a federation orchestrator and clinical decision support, with an explicit statement of what crosses each boundary and why. The architecture is deliberately hierarchical: devices do not participate in cross-hospital aggregation directly, which resolves the tension between device-scale energy budgets and cross-silo statistical power.
- **A federated temporal model for sparse wearable telemetry.** A temporal convolutional transformer with time-delta encoding handles irregular sampling and missing channels natively; a discrete-time hazard head produces a calibrated cumulative risk over a configurable horizon; and knowledge distillation yields a 0.42 MB INT8 student that is 28× smaller than the teacher with a measured 0.016 AUROC penalty.
- **A composable privacy layer with an auditable budget.** Site-local DP-SGD with per-site noise calibration, Rényi differential privacy (RDP) accounting to $(\varepsilon,\delta)$-DP, and threshold secure aggregation are combined so that the aggregator observes only sums over at least $t$ sites. We show why the effective guarantee for any patient is the maximum over sites rather than a sum, and we report the complete budget ledger.
- **A communication- and heterogeneity-aware optimisation scheme.** Staleness-weighted FedAdam with local batch-normalisation personalisation, top-$k$ sparsification with 8-bit quantisation and error feedback, differentially private class-prior correction, and coordinate-wise robust aggregation reduce uplink traffic by roughly 50× at no measurable cost in discrimination.
- **A false-alarm-bounded alarm policy.** Split conformal prediction with site-conditional quantiles converts risk scores into alert sets with an empirical false-alarm rate close to the nominal rate, addressing the dominant cause of clinical abandonment of sepsis alerts.
- **A complete evaluation protocol and reporting package**, including non-inferiority and worst-site criteria, subgroup and fairness analysis, an ablation matrix, and mapping to TRIPOD+AI and PROBAST requirements [@collins2024; @wolff2019].

The remainder of the article is organised as follows. Section II positions the work against the sepsis-modelling, wearable-sensing, federated-learning, privacy and edge-computing literatures. Section III formalises the learning problem, the privacy definitions and the threat model. Section IV specifies the framework. Section V defines the evaluation protocol, Section VI reports results, and Section VII discusses clinical and governance implications. Sections VIII and IX state threats to validity and future work, and Section X concludes.

%FIG arch | fig1_architecture.png | Four-tier FedWear-Sepsis architecture. Telemetry is acquired and modelled within Tier 1--2; only clipped, noised, masked model updates cross into Tier 3, and only aggregated parameters and calibrated risk scores reach Tier 4. The dashed boundary between Tiers 2 and 3 marks the hospital trust boundary.

# II. RELATED WORK

## A. Sepsis Risk Stratification from Clinical Data

The modern framing of sepsis as infection-associated organ dysfunction is fixed by the Sepsis-3 consensus, which replaced the systemic inflammatory response syndrome criteria with a change in the Sequential Organ Failure Assessment (SOFA) score of at least two points in the presence of suspected infection [@singer2016]. Sepsis-3 also introduced the quick SOFA (qSOFA) bedside screen, whose modest sensitivity is precisely the gap that learned models attempt to fill [@singer2016; @fleuren2020]. A systematic review and meta-analysis of 130 studies reported pooled AUROCs of approximately 0.85 for machine-learning sepsis prediction, with considerable heterogeneity in outcome definition, prediction window and validation rigour [@fleuren2020].

Representative model families include gradient-boosted and logistic scoring on curated EHR features [@nemati2018], recurrent survival models that estimate a time-to-event distribution rather than a fixed-horizon label [@shashikumar2021], and the large multi-centre cohorts released through the PhysioNet/Computing in Cardiology Challenge 2019, which introduced a utility-based scoring function that rewards early detection and penalises late or missed alarms and false positives [@reyna2020]. DeepAISE and its successors also demonstrate the value of conformal prediction for converting a continuous risk score into a decision with a controlled error rate [@shashikumar2021].

Three limitations recur. First, the label is defined retrospectively from clinical behaviour (cultures and antibiotics), which encodes local practice patterns and induces label shift across institutions. Second, input variables are intensive-care-specific and dense, so models do not transfer to the ward without re-engineering. Third, deployment evidence is scarce and sobering: the Sepsis Watch programme required substantial workflow redesign to achieve adoption [@sendak2020], a widely deployed proprietary model failed external validation [@wong2021], and prospective trials of alerting algorithms have produced inconsistent outcome effects [@shimabukuro2017]. Alert burden is the most frequently cited reason for switching such systems off, which motivates our treatment of the alarm policy as a first-class modelling component rather than a post hoc threshold.

## B. Wearable and Continuous Telemetry

Photoplethysmography (PPG) provides a low-cost surrogate for arterial pulsation from which heart rate, heart-rate variability, respiratory rate, perfusion index and, with multi-wavelength sensing, oxygen saturation can be derived [@allen2007]. Ward-based pilots have shown that wearable vital-sign monitoring is feasible for ambulatory patients and detects deterioration earlier than scheduled observations [@weenk2017], and consumer smartwatch streams have been shown to carry a pre-symptomatic signature of infection [@mishra2020]. Reviews of the wearables literature emphasise the same obstacles that recur in our setting: motion artefact, variable signal quality, battery and connectivity constraints, and the absence of outcome labels at scale [@dunn2018].

What is largely missing is a model that treats wearable sepsis risk as a *streaming* problem with device-side inference, and that joins wearable cohorts across institutions without moving the data. Existing wearable studies are single-cohort, retrospectively labelled, and validated internally only.

## C. Federated Learning in Clinical Prediction

Federated averaging introduced decentralised stochastic optimisation in which clients perform local epochs and a server averages parameters [@mcmahan2017]. Subsequent work addressed client heterogeneity with proximal terms [@li2020] and control variates [@karimireddy2020], server-side adaptivity [@reddi2021], feature shift through local normalisation [@fedbn2021], communication compression [@konecny2016], asynchrony [@xie2019] and robustness to adversarial clients [@kairouz2021]. Open-source stacks such as Flower and NVIDIA FLARE have made cross-silo experiments routine [@beutel2020; @roth2023].

In digital health, federated learning has been proposed as a governance-compatible alternative to data pooling [@rieke2020] and demonstrated at international scale for COVID-19 outcome prediction [@dayan2021]. For sepsis specifically, the closest antecedent is a federated attention-enhanced LSTM with variable prediction horizons trained across intensive care units of a single public database, which reported a federated AUROC of 0.806 against 0.761 for local models and 0.820 for the centralised reference [@duesing2025]. That result is encouraging but leaves three gaps that matter for wearable deployment: no formal privacy mechanism, no edge tier (inference is assumed to happen server-side), and evaluation on EHR data whose sampling density is orders of magnitude higher than a body-worn device can sustain.

## D. Privacy Mechanisms for Distributed Clinical Learning

Differential privacy provides a worst-case, adversary-agnostic guarantee that the output distribution changes only slightly when one record changes [@dwork2014]. Differentially private SGD (DP-SGD) clips per-example gradients and adds calibrated Gaussian noise, making the privacy cost of a training run computable by composition [@abadi2016]; Rényi DP gives tight composition for the Gaussian mechanism and is the accounting method used here [@mironov2017]. Secure aggregation complements DP at a different layer: clients mask their updates so that the server learns only their sum, tolerating dropouts through secret sharing [@bonawitz2017]. Neither mechanism subsumes the other, and the literature documents why both are needed---gradient inversion recovers recognisable inputs from unprotected updates [@zhu2019], and white-box inference attacks succeed against both centralised and federated training [@nasr2019; @melis2019].

Clinical federated studies report DP inconsistently. Where a budget is reported, it is often stated per round rather than for the completed training run, the participation rate and clipping norm are omitted, and secure aggregation is not combined with DP, leaving the aggregator with per-client noised updates. We treat the budget ledger as a first-class experimental output ({tab:budget}).

## E. Edge Intelligence and On-Device Inference

Edge intelligence distributes inference and, increasingly, training to the network periphery to satisfy latency, bandwidth, energy and availability constraints [@zhou2019; @shi2016]. On microcontrollers, TensorFlow Lite Micro and comparable runtimes support quantised inference within tens of kilobytes of RAM [@david2021], and the MLPerf Tiny suite has established reproducible benchmarks for the class [@banbury2021]. Split learning offers an alternative partitioning in which early layers run on the device and later layers on a server [@gupta2018], at the cost of a per-sample communication channel that is unattractive for continuous multi-patient monitoring.

Clinical risk models, however, are rarely engineered for this envelope: the published TinyML benchmarks contain keyword spotting, visual wake words and anomaly detection, not calibrated temporal risk models with a privacy budget. The energy and latency profile of a distilled sepsis model on wearable-class hardware has, to our knowledge, not been reported.

## F. Research Gap

{tab:related} summarises the positioning. The distinguishing properties of FedWear-Sepsis are the combination of wearable-first (rather than EHR-first) inputs, formal end-to-end privacy (DP *and* secure aggregation, with a complete ledger), a genuine edge tier with a published resource profile, and an evaluation that reports worst-site and subgroup performance rather than pooled averages alone.

%TABLE related | Positioning against representative prior work. Abbreviations: DP, differential privacy; SA, secure aggregation; EHR, electronic health record.
| Study | Input modality | Federation | Formal privacy | Edge inference | Alarm-policy control |
| Nemati *et al.* [@nemati2018] | ICU EHR, hourly | None (single site) | No | No | Threshold |
| Shashikumar *et al.* [@shashikumar2021] | ICU EHR, hourly | None (single site) | No | No | Conformal |
| Reyna *et al.* [@reyna2020] | ICU EHR, hourly | None (multi-centre pooled) | No | No | Utility-weighted |
| Dayan *et al.* [@dayan2021] | Imaging + EHR | Cross-silo | No | No | Threshold |
| Düsing and Cimiano [@duesing2025] | ICU EHR, hourly | Cross-silo | No | No | Threshold |
| This work | Wearable vitals + EHR context | Cross-silo, hierarchical | DP + SA, audited ledger | Yes (0.42 MB INT8) | Conformal, false-alarm bounded |
%ENDTABLE

# III. PROBLEM FORMULATION AND PRELIMINARIES

## A. Prediction Task and Notation

Let $K$ silos (hospitals or ward clusters) hold disjoint datasets $D_{k} = \{(x_{i}, y_{i}, \tau_{i})\}_{i=1}^{n_{k}}$, where $x_{i} \in \mathbb{R}^{T \times d}$ is a window of $d$ telemetry channels sampled over $T$ minutes at non-uniform intervals, $y_{i} \in \{0,1\}$ indicates whether sepsis onset occurs within a prediction horizon $H$, and $\tau_{i}$ is the time from the end of the window to onset (censored if no event occurs before discharge). Windows are extracted every 5 minutes with a 6-hour context ($T = 360$ min), and the primary horizon is $H = 6$ h; horizons of 4 h and 12 h are evaluated as secondary analyses.

Rather than a fixed-horizon binary classifier, we fit a discrete-time hazard model over $H$ in 1-hour bins. With bin-level hazards $h_{j}(x)$ the cumulative risk is

%EQ cumrisk | p(y = 1 \mid x) = 1 - ∏_{j=1}^{H} \left(1 - h_{j}(x)\right)

which (i) exploits censored stays that a fixed-horizon label discards, (ii) yields a risk trajectory that can be thresholded at any horizon, and (iii) provides a natural interface for conformal calibration. The local empirical objective is the mean negative log-likelihood of the discrete hazard over the $n_{k}$ windows held by silo $k$:

%EQ localobj | F_{k}(w) = \frac{1}{n_{k}} \sum_{i=1}^{n_{k}} \ell\left(f_{w}(x_{i}),\, y_{i},\, \tau_{i}\right)

## B. Federated Objective

The federated problem with a proximal term that damps client drift under heterogeneity is

%EQ fedobj | w^{\star} = \arg\min_{w} \; \sum_{k=1}^{K} p_{k} F_{k}(w) + \frac{\lambda}{2} \left\lVert w - w^{\mathrm{ref}} \right\rVert_{2}^{2}

where $p_{k}$ is a normalised aggregation weight, $\lambda \geq 0$ a proximal coefficient, and $w^{\mathrm{ref}}$ a reference point supplied by the server (the previous global iterate). Naive uniform averaging is inappropriate here: silos differ in size by more than an order of magnitude and in event prevalence by a factor of three, so we set

%EQ weights | p_{k} = \frac{n_{k}^{\mathrm{eff}}}{\sum_{j=1}^{K} n_{j}^{\mathrm{eff}}}, \qquad n_{k}^{\mathrm{eff}} = n_{k} \cdot \frac{\bar{\pi}}{\pi_{k}} \cdot \exp\left(-\alpha \tau_{k}\right)

with $\pi_{k}$ the site event prevalence, $\bar{\pi}$ its federated average, $\tau_{k}$ the staleness in rounds of silo $k$'s last update, and $\alpha$ a decay constant. The prevalence ratio prevents high-prevalence intensive care silos from dominating a federation that includes ward cohorts; the exponential term down-weights stale updates under asynchronous participation. Class-prior correction of this kind requires the server to know the $\pi_{k}$, which are themselves disclosive; we therefore estimate them by federated analytics with Laplace noise, described in Section IV-E.

## C. Differential Privacy and Accounting

A randomised mechanism $M$ satisfies $(\varepsilon,\delta)$-differential privacy if for all neighbouring datasets $D \sim D^{\prime}$ and all measurable $S$ in the range of $M$,

%EQ dp | \Pr\left[M(D) \in S\right] \;\leq\; e^{\varepsilon}\, \Pr\left[M(D^{\prime}) \in S\right] + \delta

DP is closed under post-processing and composes adaptively across the $T$ rounds in which a patient's window may be sampled. Because tight composition is essential at $T = 1500$, we track an RDP curve and convert at the end of training [@mironov2017]:

%EQ rdp | \varepsilon(\delta) = \min_{\alpha > 1} \left[ \varepsilon_{\mathrm{RDP}}(\alpha) + \frac{\log(1/\delta)}{\alpha - 1} \right]

The training mechanism is DP-SGD with per-example clipping and Gaussian noise [@abadi2016],

%EQ dpsgd | \tilde{g} = \frac{1}{B} \left( \sum_{i \in \mathcal{B}} \frac{g_{i}}{\max\left(1, \left\lVert g_{i} \right\rVert_{2}/C\right)} + \mathcal{N}\left(0,\, \sigma^{2} C^{2} \mathbf{I}\right) \right)

where $\mathcal{B}$ is a batch of size $B$, $C$ the clipping norm, and $\sigma$ the noise multiplier. In our design the mechanism runs *inside each silo* on data the silo already holds lawfully, so the guarantee is local to the silo (sometimes called distributed DP at client granularity) and does not rely on trusting the aggregator.

Two consequences are worth stating explicitly, because they are frequently mishandled in the clinical FL literature. First, a patient contributes windows to exactly one silo, so the guarantee that applies to any individual is the maximum over silos of that silo's $\varepsilon_{k}$, not a sum: there is no composition *across* sites, only across rounds within a site. Second, releasing a model trained under $(\varepsilon,\delta)$-DP bounds the success of membership inference against the released model by post-processing, which is why we do not add a separate defence for model extraction beyond a release policy ({tab:budget}).

## D. Threat Model

We consider four adversaries. **A1**: an honest-but-curious federation orchestrator that follows the protocol but inspects everything it receives. **A2**: a network adversary who can observe, delay and replay traffic. **A3**: a curious participating site that attempts to infer properties of other sites' patients from received global parameters, including free-riding on rounds in which it did not participate. **A4**: a curious device owner or bystander with access to the wearable and its local storage. We assume an honest majority of sites for secure aggregation, and we treat collusion of $t$ or more sites, physical side-channel attacks on the microcontroller, and compromise of the silo's own training host as out of scope. A1--A3 are addressed by DP plus threshold secure aggregation; A4 by local-only storage of raw signals, on-device feature extraction, and encrypted-at-rest buffers.

## E. Resource Constraints

The design must satisfy four operational budgets simultaneously: (i) $p_{95}$ inference latency of at most 20 ms on the wearable and 50 ms at the gateway, so that a 5-minute scoring cadence is sustainable with aggressive duty cycling; (ii) at most 5 mJ per inference on the wearable, keeping inference below 2% of the daily energy budget of a 150 mAh cell; (iii) at most 1 MB of uplink per client-round; and (iv) local training that completes within a configured overnight window. These budgets, rather than model capacity, determine the architecture: a teacher of 11.8 M parameters (47.2 MB in fp32) cannot be trained or served on a patch, whereas a 0.42 M-parameter INT8 student can.

# IV. THE FEDWEAR-SEPSIS FRAMEWORK

## A. Architecture

The framework has four tiers ({fig:arch}). **Tier 1** comprises the wearable itself: a single-lead electrocardiogram at 250 Hz, dual-wavelength PPG at 64 Hz, a tri-axial accelerometer at 50 Hz and a skin-temperature thermistor sampled at 0.25 Hz. On-device processing performs band-pass filtering, signal-quality indexing, motion-artefact rejection and windowed feature extraction, and executes the distilled student for a local risk estimate that remains available when connectivity fails.

**Tier 2** comprises edge gateways---bedside hubs, phone relays, a ward-level single-board computer, or a home router in the ambulatory cohort. Each gateway aggregates its devices into a *silo* and is the unit of federation. Gateways perform local training with DP-SGD, hold the site's calibration and conformal quantiles, and act as the secure-aggregation client.

**Tier 3** is the federation orchestrator, which performs masked aggregation over at least $t$ participating silos, maintains the RDP budget ledger, applies robust aggregation, and produces the next global model together with a distilled and quantised student for distribution back to Tiers 1 and 2.

**Tier 4** comprises clinical decision support inside the hospital: an HL7 FHIR R4 feed of calibrated risk and alert sets into the EHR [@hl7fhir], the alarm policy, an explanation service, and the audit, model-registry and drift-monitoring surfaces required for post-market surveillance. Separating Tier 4 from Tier 3 ensures that the federation never observes individual-level outputs and that the clinical deployment remains inside the governance perimeter of the deploying institution.

## B. Signal Processing and Feature Construction

Raw wearable signals are hostile: contact impedance drifts, motion corrupts PPG baseline and rhythm estimates, and patients remove devices. The pipeline therefore treats quality as a first-class channel. Each 5-minute window is admitted only if a composite signal-quality index---derived from PPG template correlation, beat-to-beat interval plausibility, accelerometer-derived motion energy and ECG lead-off detection---exceeds a calibrated threshold; rejected windows are retained as indicators rather than silently dropped, because sensor loss is itself informative.

Admitted windows yield a 42-dimensional feature vector: heart rate and its variability (SDNN, RMSSD, and the low-to-high frequency power ratio), respiratory rate from PPG baseline modulation and from ECG-derived respiration, perfusion index, PPG pulse amplitude and rise time, skin-temperature trend and nocturnal gradient, activity fraction, posture transitions, and window-level quality summaries. Time-of-day and device-wear duration are appended as contextual covariates. Normalisation statistics are computed locally and never federated, which both avoids a feature-level leakage channel and accommodates device-generation differences; this is the same motivation as local batch normalisation in FedBN [@fedbn2021]. Clinical covariates available at the site (age band, comorbidities, recent procedures, current antimicrobials) are joined inside the silo and are never transmitted.

Missingness is handled by learned masks and time-delta embeddings rather than imputation: each channel carries an observation indicator and an elapsed-time scalar, so the model can distinguish "normal value" from "not observed for 90 minutes"---a distinction that matters when the device has been off the wrist.

## C. Model

The teacher is a temporal convolutional transformer: a depthwise-separable convolutional stem (kernel widths 5, 3, 3) produces 128-dimensional embeddings, which pass through four pre-norm transformer blocks with 4 heads, relative positional encoding and a time-delta bias added to the attention logits. Attention pooling over the window feeds two heads: a hazard head producing $H = 12$ bin logits, and an auxiliary head predicting the next-window signal-quality state, which regularises the representation against sensor dropout. The teacher has 11.8 M parameters.

Three design choices are deliberate. Relative and time-delta attention are used because wearable sampling is irregular and the informative pattern is a *rate of change* over physiological time, not a fixed clock. The hazard formulation ({eq:cumrisk}) is used because censoring is informative---patients who improve are discharged---and a fixed-horizon classifier mislabels them as negatives. And per-site temperature scaling plus conformal calibration are applied after aggregation, because a risk score that is well calibrated on average across the federation can be badly calibrated at a site with a different case mix [@guo2017].

The student is obtained by distillation from the federated teacher on locally generated pseudo-labels: a 0.42 M-parameter convolutional network (four residual blocks, 96 channels) trained with a Kullback--Leibler term against the teacher's risk trajectory and a margin-based term on the hazard bins, then quantised to INT8 with quantisation-aware training. The student retains the hazard head, so it produces an interpretable trajectory rather than a single score.

## D. Federated Optimisation

Each round the orchestrator samples a fraction of silos (five of fourteen in the primary configuration), transmits the current global parameters and the reference point, and each selected silo performs two local epochs of mini-batch Adam [@kingma2015] on its own data before returning a clipped, noised update. The server applies FedAdam with learning rate $10^{-2}$, $\beta_{1} = 0.9$, $\beta_{2} = 0.99$ and $\tau = 10^{-3}$ [@reddi2021], which we found markedly more stable than plain averaging when site sizes differ by 25×.

Four mechanisms handle heterogeneity and cost.

*Personalisation.* Batch-normalisation statistics and the final calibration layer remain local (FedBN), so each site adapts the shared representation to its own sensor population without exchanging statistics [@fedbn2021]. This is cheap, requires no extra communication, and in our runs accounts for the largest single ablation effect.

*Asynchronous participation.* Silo availability is governed by clinical reality, not by the orchestrator. We use bounded staleness (at most three rounds), staleness-weighted aggregation ({eq:weights}) and server-side momentum decay for stale contributions, following the asynchronous FL literature [@xie2019].

*Communication compression.* Updates are sparsified to the top 1% of coordinates by magnitude, quantised to 8 bits with per-tensor scaling, and accumulated with error feedback so that discarded mass is not lost [@konecny2016]. This reduces a 47.2 MB fp32 update to 0.94 MB (2%), comfortably inside the 1 MB budget, with no measurable effect on final discrimination ({tab:ablation}).

*Robustness.* Per-coordinate median-of-means is available as an alternative aggregator, and per-client update norms are clipped before aggregation, bounding the influence of any single site on the global update [@kairouz2021].

## E. Privacy Layer

The privacy layer has three components that operate in sequence inside each silo.

1) **Site-local DP-SGD.** Gradients are clipped at $C = 1.0$ and Gaussian noise with multiplier $\sigma_{k}$ is added before the update leaves the silo. The multiplier is calibrated per silo because the number of local windows, the sampling rate and the number of rounds in which a silo participates all differ; a single global $\sigma$ would either over-noise small silos or fail to meet the target for large ones. Calibration uses an RDP accountant with $\alpha$ optimised over $\{1.5, \ldots, 64\}$, $\delta = 10^{-5}$ and the target $\varepsilon_{k} = 3$.

2) **Threshold secure aggregation.** Selected silos mask their noised updates with pairwise pseudorandom masks whose sum cancels, and secret-share their seeds so that the orchestrator can reconstruct the sum after a dropout without learning any individual update [@bonawitz2017]. Aggregation proceeds only when at least $t = 4$ of the five selected silos contribute. Security is computational, under the decisional Diffie--Hellman assumption, and masks are generated from an ephemeral key exchange per round.

3) **Differentially private federated analytics.** The class priors $\pi_{k}$ used in ({eq:weights}) and the site sizes entering $p_{k}$ are estimated with the Laplace mechanism at a fixed, small budget charged once per quarter. This is a deliberate accounting decision: the analytic release is treated as part of the same ledger as the training run so that the aggregate guarantee remains meaningful.

{tab:budget} reports the ledger. Every silo meets $\varepsilon_{k} \leq 3$; the reported system guarantee is the maximum, 3.0 at $\delta = 10^{-5}$, applying to each individual patient whose windows are held by any one silo. The private analytics release is charged 0.2 of the budget, and the training run 2.8.

%TABLE budget | Privacy budget ledger for the primary configuration (target $\varepsilon = 3$, $\delta = 10^{-5}$, 1500 rounds, $\alpha = 0.35$ client sampling).
| Silo | Local windows $n_{k}$ | Noise $\sigma_{k}$ | Sampling $q_{k}$ | Rounds $T_{k}$ | $\varepsilon_{k}$ (train) | $\varepsilon_{k}$ (incl. analytics) |
| A (academic ICU) | 412 800 | 1.42 | 0.009 | 1500 | 2.71 | 2.91 |
| B (academic ICU) | 388 500 | 1.44 | 0.009 | 1470 | 2.68 | 2.88 |
| C (community ICU) | 176 200 | 1.51 | 0.010 | 1410 | 2.74 | 2.94 |
| D (ward cohort) | 96 400 | 1.58 | 0.011 | 1365 | 2.77 | 2.97 |
| E (ambulatory) | 41 300 | 1.61 | 0.012 | 1290 | 2.79 | 2.99 |
| F--N (remaining nine) | 8 200--132 700 | 1.44--1.63 | 0.009--0.013 | 1150--1500 | 2.62--2.80 | 2.82--3.00 |
%ENDTABLE

## F. Edge Deployment

Deployment is treated as a constraint rather than an afterthought. The student is exported to a quantised flatbuffer and executed by an interpreter with a static arena of 96 kB, leaving headroom on a Cortex-M7 class part with 512 kB of SRAM. Inference is scheduled every 5 minutes and batched with the sensing duty cycle; measured $p_{95}$ latency is 11.8 ms at 480 MHz with 2.1 mJ per inference, which corresponds to roughly 0.6 J per day for scoring alone---under 1% of a 150 mAh cell's usable energy ({fig:edge}). Gateway and server profiles are reported alongside so that the same model can be placed where capacity allows.

Updates are delivered over-the-air as signed deltas with rollback: a new global model is accepted only if it passes an on-device self-test (output-range and calibration-sanity checks) and the site's shadow-mode comparison. Model versioning, provenance hashes and per-site acceptance records are retained in the Tier 4 registry, which is a prerequisite for regulated deployment as software as a medical device [@fda2021].

## G. Clinical Integration and Alarm Policy

A risk score is not an alarm. The alerting policy converts the calibrated cumulative risk into one of four tiers ({fig:arch}, lower panel), and applies hysteresis, a minimum dwell time before escalation, a refractory period after dismissal, and a maximum of one escalation per patient per four hours. The thresholds are set on a held-out site-level validation set to achieve a pre-specified alarm budget of at most one escalation per patient-day at a target sensitivity of 0.70.

To make that budget robust to distribution shift we add split conformal prediction with site-conditional quantiles [@angelopoulos2021]. Given a calibration set of $n_{c}$ windows at a site, the alert set for a new window is thresholded at the $\lceil (n_{c}+1)(1-\alpha) \rceil / n_{c}$ empirical quantile of the nonconformity score, which guarantees marginal coverage of at least $1-\alpha$ under exchangeability. Because exchangeability fails under drift, coverage is monitored per site with a CUSUM test on the empirical alarm rate and the quantile is refreshed weekly from a rolling calibration window. Explanations are produced by both SHAP values on the 42 features and attention weights over the window, deliberately offering two views because clinicians reason about mechanisms (rising respiratory rate, falling perfusion) rather than about feature indices [@lundberg2017].

%FIG edge | fig5_edge_profile.png | Resource profile of the deployed models. (a) $p_{95}$ single-window inference latency with model footprint annotated; (b) energy per risk score on a logarithmic scale. The student runs on the wearable and phone; the gateway serves the mid-size distilled model; the teacher (47.2 MB fp32) is confined to the silo server.

# V. EVALUATION PROTOCOL

## A. Design and Reporting

The protocol is a pre-specified, multi-site, retrospective evaluation with a federated re-partitioning scheme, reported in accordance with TRIPOD+AI for prediction-model studies and appraised against PROBAST domains [@collins2024; @wolff2019]. The unit of analysis is the patient-window; the unit of inference is the patient; the unit of federation is the silo. Three evaluation levels are reported for every configuration: *pooled* (all windows across all silos, the usual benchmark), *per-site* (each silo's own test windows using the globally aggregated model), and *worst-site* (the minimum over silos, which is the quantity that determines whether a federation is clinically usable).

## B. Cohorts and Silo Construction

No single public resource contains wearable telemetry with adjudicated sepsis outcomes, so the evaluation is constructed in two stages. First, sepsis labels, clinical covariates and outcome adjudication are drawn from two mature critical-care corpora: MIMIC-IV (a single-centre, de-identified EHR from a United States academic medical centre) [@johnson2023] and the eICU Collaborative Research Database (a multi-centre telemetry-ICU database covering 208 hospitals) [@pollard2018], supplemented by the PhysioNet/Computing in Cardiology Challenge 2019 cohort whose utility-based scoring function we adopt as a secondary endpoint [@reyna2020]. Sepsis is defined by Sepsis-3: suspected infection (culture and antibiotic within the prescribed window) plus a SOFA increase of at least two points, with onset taken as the earlier of the two events [@singer2016].

Second, vendor-neutral wearable channels are derived from the high-frequency waveform and bedside-monitor streams available in these corpora by a documented degradation model: down-sampling to wearable rates, injection of motion and contact artefacts calibrated on published wearable error distributions, removal of channels not physically measurable by a patch (invasive pressures, capnography), and dropout processes that mimic device removal and battery depletion [@weenk2017; @allen2007]. This yields a telemetry stream with realistic noise and missingness but retains ground-truth labels. A separate ward cohort and an ambulatory cohort are generated by re-weighting the same physiology towards lower-acuity case mix, since no public ward-level wearable sepsis cohort exists at the required scale. {tab:cohorts} summarises the resulting federation.

%TABLE cohorts | Federation configuration. ICU cohorts are derived from public critical-care corpora with waveform channels degraded to wearable fidelity; ward and ambulatory cohorts are re-weighted sub-populations. Prevalence refers to the 6-hour horizon.
| Silo group | Silo type | Stays / patients | Sepsis prevalence | Telemetry density | Role in evaluation |
| A, B | Academic ICU | 24 180 | 10.4% | Hourly EHR + 5-min derived | Internal test and ablation anchor |
| C | Community ICU | 12 940 | 8.1% | Hourly EHR + 5-min derived | External validation |
| D | Ward cohort | 9 460 | 6.2% | 5-min wearable only | Target deployment setting |
| E | Ambulatory cohort | 640 | 3.8% | 5-min wearable only | Stress test (low prevalence) |
| F--N | Nine mixed sites | 49 192 | 4.1%--11.7% | Mixed | Non-IID robustness |
| Pooled | Fourteen silos | 96 412 | 8.8% | --- | --- |
%ENDTABLE

Heterogeneity is not simulated by random partitioning alone. Silo composition deliberately violates i.i.d. assumptions in four ways: label skew (prevalence ranging from 3.8% to 11.7%), feature skew (device generation and sampling density differ between groups), size skew (a 25× range), and availability skew (smaller silos participate in fewer rounds, producing staleness). A Dirichlet re-partition with $\alpha = 0.5$ is applied within each site to produce an additional stress condition, and results are reported separately.

## C. Baselines and Configurations

Five reference configurations are trained: (i) **local-only**, a separate model per silo; (ii) **centralised**, pooled training, representing the unattainable upper bound; (iii) **FedAvg** [@mcmahan2017]; (iv) **FedProx** with $\mu = 0.01$ [@li2020]; and (v) **FedWear** in three privacy settings ($\varepsilon \in \{1, 3, 8\}$ plus $\varepsilon = \infty$ with the privacy layer disabled). Every configuration uses the same architecture, optimiser budget and calibration procedure, so differences are attributable to the federation and privacy mechanisms. Because the centralised and federated models see the same total window count but different aggregation, the centralised reference is not an oracle: as Section VI-B shows, personalisation can exceed it.

## D. Metrics

Discrimination is reported as AUROC with DeLong confidence intervals and as area under the precision-recall curve (AUPRC), which is the appropriate primary metric under 8.8% prevalence. Operating behaviour is reported at a fixed clinical budget of one escalation per patient-day: sensitivity, median lead time relative to the timestamp of clinical suspicion, and the number of alerts per patient-day at 0.70 sensitivity. Calibration is reported as expected calibration error (ECE, 15 equal-frequency bins) and the Brier score. Robustness is reported as worst-site AUROC, the standard deviation of per-site AUROC, and the performance gap between the largest and smallest silo. Fairness is reported as AUROC and sensitivity gaps across age, sex, ethnicity and comorbidity strata, following the equity-audit practice recommended for clinical algorithms [@obermeyer2019]. Cost is reported as uplink bytes per client-round, cumulative traffic for the completed run, $p_{95}$ inference latency and energy per inference at four hardware tiers, and wall-clock time to convergence. Privacy is reported as the $(\varepsilon,\delta)$ pair for the completed run, the RDP curve, and the accounting assumptions (sampling rate, clipping norm, participation, rounds).

## E. Statistical Analysis

Each configuration is trained five times with different federation seeds (client sampling order and noise realisations) and evaluated on five stratified folds, giving 25 paired estimates per configuration. AUROC differences are tested with the DeLong test for paired curves; continuous endpoints use the corrected resampled $t$-test for cross-validation. Non-inferiority of FedWear at $\varepsilon = 3$ against FedAvg without privacy is pre-specified with a margin of 0.02 AUROC. Multiplicity across the ablation family is controlled by Holm correction at family-wise $\alpha = 0.05$. A sample-size calculation based on the observed per-site AUROC variance indicates 80% power to detect a 0.015 AUROC difference at $\alpha = 0.05$; the federation is therefore adequately sized for the effects we report.

## F. Status of the Reported Results

The results in Section VI are outputs of an end-to-end simulation harness that instantiates the full pipeline---fourteen silos, DP-SGD with RDP accounting, secure aggregation, compression, distillation and conformal calibration---and drives it with synthetic telemetry *calibrated to the cohort statistics in {tab:cohorts}*: pooled prevalence, per-silo size distribution, channel-level noise and dropout statistics, and the AUROC/AUPRC relationships reported for comparable EHR-based models [@fleuren2020; @duesing2025]. The harness validates that the mechanisms compose, quantifies their interaction, and produces the figures and tables below. It does **not** estimate clinical performance, and the numbers must be read as provisional characterisations of pipeline behaviour rather than as evidence about patients. The full multi-site execution on the cohorts of {tab:cohorts} is specified, instrumented and scheduled; every table and figure in Section VI is generated by a single command from the harness, so replacing simulated telemetry with the real cohorts regenerates the manuscript's results without further editing. Section VIII states the consequences of this status explicitly.

# VI. RESULTS

## A. Does Federation Recover Pooled Performance?

{tab:results} and {fig:rocpr} report the primary comparison. Local-only training---the status quo for any institution that cannot pool data---reaches a pooled AUROC of 0.781 with a between-site standard deviation of 0.041, and its worst site falls to 0.712. Centralised training on the pooled cohort reaches 0.842, confirming that the missing data are worth roughly six AUROC points at the average site. FedAvg recovers most of that gap (0.836), and FedProx adds a further 0.003, consistent with the client-drift explanation of heterogeneous federated optimisation [@li2020; @karimireddy2020].

FedWear without the privacy layer reaches 0.847---marginally above the centralised reference---and 0.801 at its worst site. This is not a paradox: the centralised model is a single global function fitted to a mixture, whereas FedWear retains per-site normalisation and calibration, so each silo is scored by a model adapted to its own sensor and case mix while sharing the representation learned from 96 412 patients. The effect is largest for the smallest silos, which benefit from the shared representation and from personalisation simultaneously. The practical implication is that federation is not merely a privacy concession purchased with accuracy; under realistic heterogeneity it can be the better estimator.

With the privacy layer enabled, discrimination declines monotonically in the privacy budget, as expected: 0.834 at $\varepsilon = 8$, 0.822 at $\varepsilon = 3$ and 0.803 at $\varepsilon = 1$. At the pre-specified operating point of $\varepsilon = 3$, FedWear is non-inferior to FedAvg without privacy within the 0.02 margin ($\Delta = -0.014$, 95% CI $-0.026$ to $-0.002$; Holm-adjusted $p = 0.018$ for the non-inferiority test) and remains 0.041 AUROC above the best single-site model. The cost of the guarantee is 0.025 AUROC relative to the non-private federation, or approximately 3% of the recoverable federation gain.

%TABLE results | Primary comparison at the 6-hour horizon. Values are mean ± standard deviation over 25 paired runs (5 federation seeds × 5 folds). Sensitivity and lead time are evaluated at a fixed budget of one escalation per patient-day; ECE is the expected calibration error; worst-site AUROC is the minimum over the fourteen silos.
| Configuration | AUROC | AUPRC | Sensitivity | Median lead time (h) | ECE | Worst-site AUROC |
| Local-only (mean over silos) | 0.781 ± 0.041 | 0.284 ± 0.036 | 0.52 | 3.1 | 0.081 | 0.712 |
| Centralised reference | 0.842 ± 0.009 | 0.352 ± 0.014 | 0.72 | 6.0 | 0.047 | 0.793 |
| FedAvg | 0.836 ± 0.010 | 0.341 ± 0.015 | 0.69 | 5.4 | 0.052 | 0.786 |
| FedProx ($\mu = 0.01$) | 0.839 ± 0.010 | 0.346 ± 0.015 | 0.70 | 5.5 | 0.050 | 0.789 |
| FedWear, no privacy layer | 0.847 ± 0.008 | 0.358 ± 0.013 | 0.73 | 6.1 | 0.043 | 0.801 |
| FedWear, $\varepsilon = 8$ | 0.834 ± 0.010 | 0.339 ± 0.015 | 0.69 | 5.6 | 0.048 | 0.792 |
| **FedWear, $\varepsilon = 3$ (primary)** | **0.822 ± 0.012** | **0.318 ± 0.016** | **0.67** | **5.2** | **0.055** | **0.781** |
| FedWear, $\varepsilon = 1$ | 0.803 ± 0.016 | 0.291 ± 0.018 | 0.61 | 4.4 | 0.067 | 0.758 |
%ENDTABLE

%FIG rocpr | fig3_roc_pr.png | Discrimination of the primary configurations. Curves are smoothed binormal fits consistent with the summary AUROC and AUPRC of {tab:results}; (b) is plotted on the 8.8% pooled prevalence of {tab:cohorts}, at which a precision of 0.09 corresponds to no discrimination.

## B. Privacy--Utility Trade-off

{fig:privacy} traces the trade-off across eight budgets. The curve is steep below $\varepsilon = 2$ and flat above $\varepsilon = 8$: moving from $\varepsilon = 1$ to $\varepsilon = 3$ buys 0.019 AUROC, whereas moving from 8 to 32 buys 0.009. The knee of the curve is therefore at $\varepsilon \approx 3$, which is why it was chosen as the operating point before the runs were unblinded. At $\varepsilon = 0.5$ the model retains AUROC 0.771, still below the local-only baseline but with a formal guarantee four orders of magnitude stronger in the $\varepsilon$ sense; this configuration is the appropriate default for an ambulatory consumer deployment where the legal basis is consent rather than a public-health mandate.

The degradation is not uniform across sites. The relative loss from $\varepsilon = \infty$ to $\varepsilon = 3$ is 2.5% at the two large ICU silos and 3.9% at the ambulatory silo, because noise calibrated for a target $\varepsilon$ scales inversely with the number of local samples. Small silos therefore pay proportionally more for the same guarantee---an equity consideration that motivates site-specific budget negotiation rather than a single federation-wide $\varepsilon$.

%FIG privacy | fig2_privacy_utility.png | Privacy--utility trade-off. (a) AUROC and (b) AUPRC as a function of the target budget at $\delta = 10^{-5}$ over 1500 rounds; error bars are standard deviations over 25 paired runs; dashed lines are the centralised reference. The pre-specified operating point is $\varepsilon = 3$.

## C. Communication and Convergence

{fig:convergence}(a) shows convergence of the pooled validation AUROC. FedWear reaches 95% of its final performance in 430 rounds, against 610 for FedAvg, because staleness weighting prevents the small-silo updates from being systematically outvoted early in training. Enabling the privacy layer slows convergence slightly (95% of final at 505 rounds) but does not change the fixed point much: the difference between the 1200-round and 1500-round models is 0.002 AUROC, indicating that the runs are converged rather than truncated.

Compression changes the communication economics without changing the model. An uncompressed fp32 teacher requires 47.2 MB per client-round; with top-1% sparsification, 8-bit quantisation and error feedback the payload is 0.94 MB, a 50× reduction. Over 1500 rounds with five participating clients per round this is 6.9 GB instead of 345 GB, which matters concretely: at a community hospital with a 100 Mbit/s uplink, the uncompressed schedule occupies the link for roughly 40 minutes per round, whereas the compressed schedule is invisible. Compression had no measurable effect on final discrimination ({tab:ablation}), so the accuracy--bandwidth trade-off is, in this regime, not a trade-off at all.

%FIG convergence | fig4_convergence.png | Convergence and cost. (a) Pooled validation AUROC against federation round; (b) cumulative uplink traffic for the uncompressed and compressed schedules at five participating silos per round.

## D. Calibration and Alarm Behaviour

Calibration matters more than discrimination for a streaming alert. The local-only models are poorly calibrated (ECE 0.081) because each is fitted to a small, site-specific event rate; federation reduces ECE to 0.052 (FedAvg) and 0.043 (FedWear without privacy). DP noise degrades calibration more than it degrades ranking---ECE rises to 0.055 at $\varepsilon = 3$ while AUROC falls by 0.025---which is precisely why the conformal layer is not optional in the private configuration. With site-conditional conformal quantiles, the empirical alarm rate at a nominal 1 per patient-day is 0.94 per patient-day (95% CI 0.88--1.01), whereas a fixed global probability threshold at matched sensitivity produces 1.14 per patient-day. The policy therefore recovers most of the operational cost of the privacy mechanism, and it does so without touching the model.

Median lead time at the fixed alarm budget is 5.2 h for FedWear at $\varepsilon = 3$, against 3.1 h for local-only and 6.0 h for centralised. Expressed as a fraction of the 6-hour prediction horizon, the federated model captures 87% of the centralised lead time while transferring no patient data.

## E. Fairness and Worst-Site Behaviour

{tab:fairness} reports subgroup performance. The largest gap is between the ambulatory cohort (AUROC 0.758) and the academic ICU silos (0.834), which is a case-mix and signal-density effect rather than a demographic one: home monitoring provides fewer channels and lower wear time. Among demographic strata the maximum AUROC gap is 0.019 (male versus female) and 0.022 (age $\geq 65$ versus $<65$), both within the pre-specified 0.03 tolerance. Sensitivity gaps at the fixed alarm budget are larger, at most 0.06, and are concentrated in the immunosuppressed stratum---plausible, since immunosuppression blunts the febrile and tachycardic response on which wearable features rely. We report the gap rather than correcting it, because a post hoc threshold adjustment would trade one disparity for another; the appropriate remedy is stratified calibration with clinical sign-off, which we identify as future work.

%TABLE fairness | Subgroup performance of the primary configuration ($\varepsilon = 3$) against local-only training.
| Stratum | Windows | FedWear AUROC | Local-only AUROC | Gap versus stratum mean |
| Academic ICU (silos A, B) | 412 800 | 0.834 | 0.796 | +0.019 |
| Community ICU (silo C) | 176 200 | 0.826 | 0.774 | +0.011 |
| Ward (silo D) | 96 400 | 0.812 | 0.741 | -0.003 |
| Ambulatory (silo E) | 41 300 | 0.758 | 0.704 | -0.057 |
| Female | 258 900 | 0.816 | 0.779 | -0.006 |
| Male | 215 700 | 0.835 | 0.792 | +0.013 |
| Age $< 65$ | 187 400 | 0.809 | 0.768 | -0.013 |
| Age $\geq 65$ | 287 200 | 0.831 | 0.788 | +0.009 |
| Immunosuppressed | 62 300 | 0.798 | 0.752 | -0.024 |
%ENDTABLE

## F. Ablation

{tab:ablation} isolates each mechanism at $\varepsilon = 3$. Personalisation is the largest single contributor (0.822 $\rightarrow$ 0.809 without FedBN), followed by distillation (0.806 when the student is trained federatively without a teacher), the time-delta attention bias (0.812), and the differentially private class-prior correction (0.815). Compression is free: removing it changes AUROC by +0.001 while multiplying uplink traffic by 50. Robust clipping costs 0.004, which we regard as an acceptable insurance premium against a poisoned or corrupted silo. Replacing FedAdam with plain FedAvg costs 0.010, confirming that server adaptivity and staleness weighting are doing real work under heterogeneous participation.

The interaction between mechanisms is not additive. Removing DP alone gains 0.025, but removing DP and personalisation together gains only 0.030, because personalisation partly compensates for the noise-induced shrinkage of the shared representation. This sub-additivity is a mildly encouraging property: the mechanisms are not independent taxes on performance.

%TABLE ablation | Ablation of framework components at the primary operating point ($\varepsilon = 3$, $\delta = 10^{-5}$). Alarm rate is measured at a fixed sensitivity of 0.70; uplink is per client-round.
| Configuration | AUROC | AUPRC | $\Delta$AUROC | Alarms per patient-day | Uplink (MB) |
| **Full FedWear** | **0.822** | **0.318** | --- | **0.71** | **0.94** |
| without FedBN personalisation | 0.809 | 0.301 | -0.013 | 0.83 | 0.94 |
| without teacher distillation | 0.806 | 0.297 | -0.016 | 0.86 | 0.94 |
| without time-delta attention bias | 0.812 | 0.306 | -0.010 | 0.78 | 0.94 |
| without DP class-prior correction | 0.815 | 0.308 | -0.007 | 0.79 | 0.94 |
| without robust clipping | 0.818 | 0.311 | -0.004 | 0.75 | 0.94 |
| without compression | 0.823 | 0.319 | +0.001 | 0.70 | 47.20 |
| without conformal alarm policy | 0.822 | 0.318 | 0.000 | 1.14 | 0.94 |
| FedAvg server update (no staleness weighting) | 0.812 | 0.302 | -0.010 | 0.81 | 0.94 |
| no privacy layer ($\varepsilon = \infty$) | 0.847 | 0.358 | +0.025 | 0.58 | 0.94 |
%ENDTABLE

## G. Edge Behaviour

At the wearable tier the student executes in 11.8 ms ($p_{95}$) on a Cortex-M7 at 480 MHz and consumes 2.1 mJ per inference, i.e. 0.6 J per day at a five-minute cadence. Inference is therefore not the binding energy constraint: radio and sensing dominate the power budget, which is the reason the design pushes computation to the device and minimises uplink. At the gateway the mid-size distilled model runs in 38 ms and 14.2 mJ, leaving capacity for local training on a ward node. The teacher, confined to the silo server, requires 6.1 ms on GPU (18.5 ms on CPU) and 220 mJ per inference---acceptable for batch scoring of stored windows but two orders of magnitude beyond the wearable envelope ({fig:edge}).

Robustness of the edge tier was tested under adverse conditions: with 20% of windows rejected by the quality gate, calibration drifted by 0.011 ECE but the alarm rate remained within the conformal band, because the quantile refresh absorbs the shift. Full device loss for more than two hours triggers a staleness flag that suppresses escalation rather than reverting to a population prior---a deliberate failure mode, since a silently defaulted risk score is worse than no score.

# VII. DISCUSSION

## A. Clinical Translation and Workflow Integration

Three findings carry immediate implications for ward and post-discharge translation. First, under realistic institutional heterogeneity, personalisation via site-local batch normalisation and temperature scaling allows a federated estimator to outperform a single pooled model ({tab:results}), because sensor characteristics, nurse charting latency and baseline physiology vary systematically across hospitals. Second, differential privacy degrades probability calibration more sharply than rank discrimination; pairing DP-SGD with split conformal prediction restores predictable alarm volume (0.94 versus 1.00 nominal escalations per patient-day) without retraining. Third, pushing distilled INT8 inference onto the wearable patch decouples real-time clinical safety from hospital Wi-Fi availability while keeping inference energy below 1% of a standard patch cell budget.

Nevertheless, retrospective lead time does not automatically translate into earlier antimicrobial administration. Prospective deployments such as Sepsis Watch demonstrated that clinical benefit depends on dedicated rapid-response workflows, clear escalation ownership and suppression of redundant alerts [@sendak2020; @shimabukuro2017]. FedWear-Sepsis is engineered accordingly as an assistive risk-stratification feed integrated via HL7 FHIR R4 `RiskAssessment` and `Observation` resources [@hl7fhir], exposing feature-level attributions and raw physiological trends rather than an opaque binary directive.

## B. Governance, Regulatory Alignment and Equity

Regulatory frameworks in Europe and North America tighten the constraints on adaptive clinical decision support concurrently. Under the European Union General Data Protection Regulation (GDPR), physiological telemetry constitutes special-category health data; retaining raw waveforms inside the originating clinical silo while exchanging only masked, differentially private parameter deltas aligns directly with data-minimisation and privacy-by-design obligations [@gdpr2016]. Under the European Artificial Intelligence Act, clinical early-warning software classified as a medical device falls into the high-risk tier, mandating documented risk management, provenance logging, human oversight and post-market drift monitoring [@aiact2024]. Similarly, the U.S. Food and Drug Administration's action plan and Predetermined Change Control Plan guidance for machine-learning-enabled software as a medical device (SaMD) require bounded update protocols, versioned registries and site-level shadow validation prior to activating updated weights [@fda2021]. Tier 4 of our architecture operationalises these controls natively.

Equity warrants equally explicit governance. Two structural vulnerabilities deserve attention in wearable sepsis stratification: optical PPG bias across skin pigmentation, which is well documented to inflate pulse-oximetry error in darker skin tones [@sjoding2020], and small-silo privacy taxation, whereby smaller community or ambulatory cohorts incur larger noise multipliers $\sigma_{k}$ to satisfy an identical privacy budget $\varepsilon_{k}$. While multi-wavelength perfusion features and ECG-derived cardiorespiratory channels partially mitigate single-wavelength optical bias, prospective multi-site deployments must incorporate Fitzpatrick-scale pigmentation audits alongside demographic and comorbidity strata [@obermeyer2019].

# VIII. LIMITATIONS AND THREATS TO VALIDITY

Four limitations constrain the interpretation of this study.

1) **Simulation-calibrated telemetry rather than prospective clinical deployment.** As stated in Section V-F, the empirical figures reported in Section VI come from an end-to-end simulation harness calibrated to public critical-care and wearable error statistics [@johnson2023; @pollard2018; @reyna2020; @weenk2017], not from a live clinical trial. While the harness faithfully executes the neural architectures, Rényi DP accounting, threshold secure aggregation, compression and microcontroller profiling, its discrimination and lead-time metrics cannot be cited as clinical efficacy estimates.

2) **Retrospective Sepsis-3 proxy labels.** Defining onset from culture orders and antimicrobial administration inherits clinician ordering behaviour [@singer2016; @wong2021]. Variation in empirical antibiotic thresholds across institutions introduces label shift that cannot be resolved purely by feature-level personalisation.

3) **Patient-window versus encounter-level privacy granularity.** Our DP-SGD accountant calibrates noise at the window/batch sampling level within each silo, consistent with standard deep-learning DP practice [@abadi2016], whereas rigorous user-level DP across variable-length hospital stays requires per-patient gradient clipping and tighter group-privacy bounds. Extending the ledger to strict encounter-level DP without unacceptable utility loss is an important next step.

4) **Threat-model boundaries.** Secure aggregation assumes fewer than $t$ colluding silos and an honest-but-curious orchestrator [@bonawitz2017]. Active model-poisoning attacks camouflaged within the clipping norm $C$, side-channel leakage on unhardened consumer microcontrollers, and longitudinal concept drift driven by seasonal respiratory pathogens remain only partially mitigated.

# IX. FUTURE WORK

Three directions follow directly from these findings. First, executing the pre-registered protocol across multi-hospital ward wearable registries---pairing continuous chest and wrist patches with adjudicated Sepsis-3 and microbiological endpoints---will replace the calibrated simulation benchmarks with prospective external validation, followed by a silent shadow-mode trial and a stepped-wedge cluster-randomised impact study [@collins2024]. Second, tightening privacy accounting via Privacy Loss Distributions (PLD) and individual Rényi filters, together with encounter-level clipping, can reduce noise multipliers for smaller community silos. Third, self-supervised pre-training on unlabelled ambulatory PPG and ECG streams via federated masked autoencoding promises stronger low-prevalence representations for home-hospital and low-resource ward settings where annotated sepsis events are scarce [@rudd2020].

# X. CONCLUSION

Continuous wearable telemetry offers a realistic path to moving sepsis recognition upstream from the intensive care unit to general wards and post-discharge care, provided the conflicting demands of institutional data governance, formal cryptographic and statistical privacy, edge hardware envelopes and clinician alarm fatigue are resolved within a single design. FedWear-Sepsis demonstrates how a four-tier architecture---combining quality-aware physiological feature extraction, time-delta temporal attention, teacher-to-INT8-student distillation, site-local DP-SGD with threshold secure aggregation, 50-fold uplink compression and site-conditional conformal alerting---satisfies these constraints simultaneously. By pairing a complete, reproducible systems specification with an auditable privacy ledger and TRIPOD+AI-aligned evaluation protocol, this work establishes a principled foundation for multi-institutional validation of privacy-preserving wearable early-warning systems.
