"""IEEE-formatted reference database keyed by citation handle.

Citation handles are resolved to numbers by order of first appearance in the
manuscript (see build_docx.py), as required by IEEE style.
"""

REFS = {
    # ---- sepsis: definition, epidemiology, clinical context -----------------
    "singer2016": "E. A. Singer, C. S. Deutschman, C. W. Seymour, M. Shankar-Hari, "
    "D. Annane, M. Bauer, R. Bellomo, G. R. Bernard, J.-D. Chiche, C. M. Coopersmith, "
    "R. S. Hotchkiss, M. M. Levy, J. C. Marshall, G. S. Martin, S. M. Opal, "
    "G. D. Rubenfeld, T. van der Poll, J.-L. Vincent, and D. C. Angus, "
    "\u201cThe Third International Consensus Definitions for Sepsis and Septic Shock "
    "(Sepsis-3),\u201d *JAMA*, vol. 315, no. 8, pp. 801\u2013810, Feb. 2016.",

    "rudd2020": "K. E. Rudd, S. C. Johnson, K. M. Agesa, K. A. Shackelford, D. Tsoi, "
    "D. R. Kievlan, D. V. Colombara, K. S. Ikuta, N. Kissoon, S. Finfer, "
    "C. Fleischmann-Struzek, F. R. Machado, K. K. Reinhart, K. Rowan, "
    "C. W. Seymour, R. S. Watson, T. E. West, F. Marinho, S. I. Hay, R. Lozano, "
    "A. D. Lopez, D. C. Angus, C. J. L. Murray, and M. Naghavi, "
    "\u201cGlobal, regional, and national sepsis incidence and mortality, 1990\u20132017: "
    "Analysis for the Global Burden of Disease Study,\u201d *Lancet*, vol. 395, "
    "no. 10219, pp. 200\u2013211, Jan. 2020.",

    "seymour2019": "C. W. Seymour, J. N. Kennedy, S. Wang, C.-C. H. Chang, "
    "C. F. Elliott, Z. Xu, S. Berry, G. Clermont, G. Cooper, H. Gomez, "
    "D. C. Angus, and J. A. Kellum, \u201cDerivation, validation, and potential "
    "treatment implications of novel clinical phenotypes for sepsis,\u201d *JAMA*, "
    "vol. 321, no. 20, pp. 2003\u20132017, May 2019.",

    "fleuren2020": "L. M. Fleuren, T. L. T. Klausch, C. L. Zwager, L. J. Schoonmade, "
    "T. Guo, L. F. Roggeveen, K. Swart, A. R. J. Girbes, P. Thoral, A. Ercole, "
    "M. Hoogendoorn, and P. J. Thoral, \u201cMachine learning for the prediction of "
    "sepsis: A systematic review and meta-analysis of diagnostic test accuracy,\u201d "
    "*Intensive Care Med.*, vol. 46, no. 3, pp. 383\u2013400, Mar. 2020.",

    # ---- clinical early-warning models -------------------------------------
    "nemati2018": "S. Nemati, M. M. Ghassemi, and G. D. Clifford, \u201cAn interpretable "
    "machine learning model for accurate prediction of sepsis in the ICU,\u201d "
    "*Crit. Care Med.*, vol. 46, no. 4, pp. 547\u2013553, Apr. 2018.",

    "shashikumar2021": "S. P. Shashikumar, C. S. Josef, A. Sharma, and S. Nemati, "
    "\u201cDeepAISE\u2014An interpretable and recurrent neural survival model for early "
    "prediction of sepsis,\u201d *Artif. Intell. Med.*, vol. 113, Art. no. 102036, "
    "Mar. 2021.",

    "reyna2020": "M. A. Reyna, C. S. Josef, R. Jeter, S. P. Shashikumar, "
    "M. B. Westover, S. Nemati, G. D. Clifford, and A. Sharma, \u201cEarly prediction of "
    "sepsis from clinical data: The PhysioNet/Computing in Cardiology Challenge 2019,\u201d "
    "*Crit. Care Med.*, vol. 48, no. 2, pp. 210\u2013217, Feb. 2020.",

    "sendak2020": "M. P. Sendak, W. Ratliff, D. Sarro, E. Alderton, J. Futoma, "
    "M. Gao, M. Nichols, A. Bedoya, C. O'Brien, and K. E. Balu, \u201cReal-world "
    "integration of a sepsis deep learning technology into routine clinical care: "
    "Implementation study,\u201d *JMIR Med. Inform.*, vol. 8, no. 7, Art. no. e15182, "
    "Jul. 2020.",

    "wong2021": "A. Wong, E. J. Otles, J. P. Donnelly, A. Krumm, J. McCullough, "
    "O. DeTroyer-Cooley, J. Pestrue, M. Phillips, J. Konye, C. Penoza, M. Ghous, "
    "J. R. K. F. Holzhauser, and K. Singh, \u201cExternal validation of a widely "
    "implemented proprietary sepsis prediction model in hospitalized patients,\u201d "
    "*JAMA Intern. Med.*, vol. 181, no. 8, pp. 1065\u20131070, Aug. 2021.",

    "shimabukuro2017": "D. W. Shimabukuro, C. W. Barton, M. D. Feldman, "
    "S. J. Mataraso, and R. Das, \u201cEffect of a machine learning-based severe sepsis "
    "prediction algorithm on patient survival and hospital length of stay: "
    "A randomised clinical trial,\u201d *BMJ Open Respir. Res.*, vol. 4, no. 1, "
    "Art. no. e000234, Nov. 2017.",

    # ---- wearable telemetry ------------------------------------------------
    "allen2007": "J. Allen, \u201cPhotoplethysmography and its application in clinical "
    "physiological measurement,\u201d *Physiol. Meas.*, vol. 28, no. 3, pp. R1\u2013R39, "
    "Mar. 2007.",

    "weenk2017": "M. Weenk, H. van Goor, B. Frietman, L. J. E. W. C. Engelen, "
    "C. J. H. M. van Laarhoven, J. Smit, S. J. H. Bredie, and T. J. M. Rasing, "
    "\u201cContinuous monitoring of vital signs using wearable devices on the general "
    "ward: Pilot study,\u201d *JMIR mHealth uHealth*, vol. 5, no. 7, Art. no. e91, "
    "Jul. 2017.",

    "mishra2020": "T. Mishra, M. Wang, A. A. Metwally, G. K. Bogu, A. W. Brooks, "
    "A. Bahmani, A. Alavi, A. Celli, E. Higgs, O. Dagan-Rosenfeld, B. Fay, S. Kirkpatrick, "
    "R. Kellogg, M. Gibson, T. Wang, E. B. Rolnik, P. Ganz, S. A. P. H. D. and "
    "M. P. Snyder, \u201cPre-symptomatic detection of COVID-19 from smartwatch data,\u201d "
    "*Nat. Biomed. Eng.*, vol. 4, no. 12, pp. 1208\u20131220, Dec. 2020.",

    "dunn2018": "J. Dunn, R. Runge, and M. Snyder, \u201cWearables and the medical "
    "revolution,\u201d *Per. Med.*, vol. 15, no. 5, pp. 429\u2013448, Sep. 2018.",

    # ---- federated learning ------------------------------------------------
    "mcmahan2017": "B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y Arcas, "
    "\u201cCommunication-efficient learning of deep networks from decentralized data,\u201d "
    "in *Proc. 20th Int. Conf. Artif. Intell. Statist. (AISTATS)*, PMLR, vol. 54, "
    "2017, pp. 1273\u20131282.",

    "kairouz2021": "P. Kairouz, H. B. McMahan, B. Avent, A. Bellet, M. Bennis, "
    "A. N. Bhagoji, K. Bonawitz, Z. Charles, G. Cormode, R. Cummings, and others, "
    "\u201cAdvances and open problems in federated learning,\u201d *Found. Trends Mach. "
    "Learn.*, vol. 14, no. 1\u20132, pp. 1\u2013210, Jun. 2021.",

    "li2020": "T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith, "
    "\u201cFederated optimization in heterogeneous networks,\u201d *Proc. Mach. Learn. "
    "Syst.*, vol. 2, pp. 429\u2013450, 2020.",

    "karimireddy2020": "S. P. Karimireddy, S. Kale, M. Mohri, S. J. Reddi, S. U. Stich, "
    "and A. T. Suresh, \u201cSCAFFOLD: Stochastic controlled averaging for federated "
    "learning,\u201d in *Proc. 37th Int. Conf. Mach. Learn. (ICML)*, 2020, "
    "pp. 5132\u20135143.",

    "reddi2021": "S. J. Reddi, Z. Charles, M. Zaheer, Z. Garrett, K. Rush, J. Kone\u010dn\u00fd, "
    "S. Kumar, and H. B. McMahan, \u201cAdaptive federated optimization,\u201d in "
    "*Proc. Int. Conf. Learn. Represent. (ICLR)*, 2021.",

    "fedbn2021": "X. Li, M. Jiang, X. Zhang, M. Kamp, and Q. Dou, \u201cFedBN: Federated "
    "learning on non-IID features via local batch normalization,\u201d in *Proc. Int. "
    "Conf. Learn. Represent. (ICLR)*, 2021.",

    "konecny2016": "J. Kone\u010dn\u00fd, H. B. McMahan, F. X. Yu, P. Richt\u00e1rik, "
    "A. T. Suresh, and D. Bacon, \u201cFederated learning: Strategies for improving "
    "communication efficiency,\u201d *arXiv:1610.05492*, Oct. 2016.",

    "xie2019": "C. Xie, S. Koyejo, and I. Gupta, \u201cAsynchronous federated "
    "optimization,\u201d *arXiv:1903.03934*, Mar. 2019.",

    "beutel2020": "D. J. Beutel, T. Topal, A. Mathur, X. Qiu, J. Fernandez-Marques, "
    "Y. Gao, L. Sani, K. H. Li, T. Parcollet, P. P. B. de Gusm\u00e3o, and N. D. Lane, "
    "\u201cFlower: A friendly federated learning research framework,\u201d "
    "*arXiv:2007.14390*, Jul. 2020.",

    "roth2023": "H. R. Roth, Y. Cheng, Y. Wen, I. Yang, Z. Xu, Y.-T. Hsieh, K. Kersten, "
    "A. Harouni, C. Zhao, K. Lu, and others, \u201cNVIDIA FLARE: Federated learning from "
    "simulation to real-world,\u201d *IEEE Data Eng. Bull.*, vol. 46, no. 1, "
    "pp. 132\u2013144, Mar. 2023.",

    "rieke2020": "N. Rieke, J. Hancox, W. Li, F. Milletar\u00ec, H. R. Roth, S. Albarqouni, "
    "S. Bakas, M. N. Galtier, B. A. Landman, K. Maier-Hein, S. Ourselin, M. Sheller, "
    "R. M. Summers, A. Trask, D. Xu, M. Baust, and M. J. Cardoso, \u201cThe future of "
    "digital health with federated learning,\u201d *npj Digit. Med.*, vol. 3, "
    "Art. no. 119, Sep. 2020.",

    "dayan2021": "I. Dayan, H. R. Roth, A. Zhong, A. Harouni, A. Gentili, "
    "A. Z. Abidin, A. Liu, A. B. Costa, B. J. Wood, C.-S. Tsai, and others, "
    "\u201cFederated learning for predicting clinical outcomes in patients with "
    "COVID-19,\u201d *Nat. Med.*, vol. 27, no. 10, pp. 1735\u20131743, Oct. 2021.",

    "duesing2025": "C. D\u00fcsing and P. Cimiano, \u201cImproving early sepsis onset "
    "prediction through federated learning,\u201d in *Proc. 1st Workshop Artif. Intell. "
    "Biomed. Data (AIBio)*, 2025, *arXiv:2509.20885*.",

    # ---- privacy mechanisms ------------------------------------------------
    "abadi2016": "M. Abadi, A. Chu, I. Goodfellow, H. B. McMahan, I. Mironov, "
    "K. Talwar, and L. Zhang, \u201cDeep learning with differential privacy,\u201d in "
    "*Proc. ACM SIGSAC Conf. Comput. Commun. Secur. (CCS)*, 2016, pp. 308\u2013318.",

    "dwork2014": "C. Dwork and A. Roth, \u201cThe algorithmic foundations of "
    "differential privacy,\u201d *Found. Trends Theor. Comput. Sci.*, vol. 9, "
    "no. 3\u20134, pp. 211\u2013407, 2014.",

    "mironov2017": "I. Mironov, \u201cR\u00e9nyi differential privacy,\u201d in *Proc. IEEE "
    "30th Comput. Secur. Found. Symp. (CSF)*, 2017, pp. 263\u2013275.",

    "bonawitz2017": "K. Bonawitz, V. Ivanov, B. Kreuter, A. Marcedone, H. B. McMahan, "
    "S. Patel, D. Ramage, A. Segal, and K. Seth, \u201cPractical secure aggregation for "
    "privacy-preserving machine learning,\u201d in *Proc. ACM SIGSAC Conf. Comput. "
    "Commun. Secur. (CCS)*, 2017, pp. 1175\u20131191.",

    "zhu2019": "L. Zhu, Z. Liu, and S. Han, \u201cDeep leakage from gradients,\u201d in "
    "*Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)*, 2019, pp. 14774\u201314784.",

    "nasr2019": "M. Nasr, R. Shokri, and A. Houmansadr, \u201cComprehensive privacy "
    "analysis of deep learning: Passive and active white-box inference attacks against "
    "centralized and federated learning,\u201d in *Proc. IEEE Symp. Secur. Privacy (SP)*, "
    "2019, pp. 739\u2013753.",

    "melis2019": "L. Melis, C. Song, E. De Cristofaro, and V. Shmatikov, \u201cExploiting "
    "unintended feature leakage in collaborative learning,\u201d in *Proc. IEEE Symp. "
    "Secur. Privacy (SP)*, 2019, pp. 691\u2013706.",

    "yousefpour2021": "A. Yousefpour, I. Shilov, A. Sablayrolles, D. Testuggine, "
    "K. Prasad, M. Malek, J. Nguyen, S. Ghosh, A. Bharadwaj, J. Zhao, G. Cormode, and "
    "I. Mironov, \u201cOpacus: User-friendly differential privacy library in PyTorch,\u201d "
    "*arXiv:2109.12298*, Sep. 2021.",

    # ---- edge intelligence -------------------------------------------------
    "zhou2019": "Z. Zhou, X. Chen, E. Li, L. Zeng, K. Luo, and J. Zhang, \u201cEdge "
    "intelligence: Paving the last mile of artificial intelligence with edge "
    "computing,\u201d *Proc. IEEE*, vol. 107, no. 8, pp. 1738\u20131762, Aug. 2019.",

    "shi2016": "W. Shi, J. Cao, Q. Zhang, Y. Li, and L. Xu, \u201cEdge computing: "
    "Vision and challenges,\u201d *IEEE Internet Things J.*, vol. 3, no. 5, "
    "pp. 637\u2013646, Oct. 2016.",

    "david2021": "R. David, J. Duke, A. Jain, V. Janapa Reddi, N. Jeffries, J. Li, "
    "N. Kreeger, I. Nappier, M. Natraj, T. Wang, P. Warden, and R. Rhodes, "
    "\u201cTensorFlow Lite Micro: Embedded machine learning for TinyML systems,\u201d "
    "*Proc. Mach. Learn. Syst.*, vol. 3, pp. 800\u2013811, 2021.",

    "banbury2021": "C. R. Banbury, V. J. Reddi, P. Torelli, J. Holleman, N. Jeffries, "
    "C. Kiraly, P. Montino, D. Kanter, S. Ahmed, D. Pau, U. Thakker, A. N. Jha, "
    "D. Smilkov, and D. H. Woo, \u201cMLPerf Tiny benchmark,\u201d *arXiv:2106.07597*, "
    "Jun. 2021.",

    "gupta2018": "O. Gupta and R. Raskar, \u201cDistributed learning of deep neural "
    "network over multiple agents,\u201d *J. Netw. Comput. Appl.*, vol. 116, "
    "pp. 1\u20138, Aug. 2018.",

    # ---- calibration, explanation, reporting -------------------------------
    "guo2017": "C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, \u201cOn calibration of "
    "modern neural networks,\u201d in *Proc. 34th Int. Conf. Mach. Learn. (ICML)*, "
    "2017, pp. 1321\u20131330.",

    "angelopoulos2021": "A. N. Angelopoulos and S. Bates, \u201cA gentle introduction to "
    "conformal prediction and distribution-free uncertainty quantification,\u201d "
    "*arXiv:2107.07511*, Jul. 2021.",

    "lundberg2017": "S. M. Lundberg and S.-I. Lee, \u201cA unified approach to "
    "interpreting model predictions,\u201d in *Proc. Adv. Neural Inf. Process. Syst. "
    "(NeurIPS)*, 2017, pp. 4765\u20134774.",

    "collins2024": "G. S. Collins, K. G. M. Moons, P. Dhiman, R. D. Riley, "
    "A. L. Beam, B. Van Calster, M. J. Ghassemi, X. Liu, J. B. Reitsma, L. van Smeden, "
    "and others, \u201cTRIPOD+AI statement: Updated guidance for reporting clinical "
    "prediction models that use regression or machine learning methods,\u201d *BMJ*, "
    "vol. 385, Art. no. e078378, Apr. 2024.",

    "wolff2019": "R. F. Wolff, K. G. M. Moons, R. D. Riley, P. F. Whiting, M. Westwood, "
    "G. S. Collins, J. B. Reitsma, J. Kleijnen, and S. Mallett, \u201cPROBAST: A tool to "
    "assess the risk of bias and applicability of prediction model studies,\u201d "
    "*Ann. Intern. Med.*, vol. 170, no. 1, pp. 51\u201358, Jan. 2019.",

    "obermeyer2019": "Z. Obermeyer, B. Powers, C. Vogeli, and S. Mullainathan, "
    "\u201cDissecting racial bias in an algorithm used to manage the health of "
    "populations,\u201d *Science*, vol. 366, no. 6464, pp. 447\u2013453, Oct. 2019.",

    "sjoding2020": "M. W. Sjoding, R. P. Dickson, T. J. Iwashyna, S. E. Gay, and "
    "T. S. Valley, \u201cRacial bias in pulse oximetry measurement,\u201d *N. Engl. J. "
    "Med.*, vol. 383, no. 25, pp. 2477\u20132478, Dec. 2020.",

    # ---- data resources ----------------------------------------------------
    "johnson2023": "A. E. W. Johnson, L. Bulgarelli, L. Shen, A. Gayles, A. Shammout, "
    "S. Horng, T. J. Pollard, S. Hao, B. Moody, and R. G. Mark, \u201cMIMIC-IV, a freely "
    "accessible electronic health record dataset,\u201d *Sci. Data*, vol. 10, no. 1, "
    "Art. no. 1, Jan. 2023.",

    "pollard2018": "T. J. Pollard, A. E. W. Johnson, J. D. Raffa, L. A. Celi, "
    "R. G. Mark, and O. Badawi, \u201cThe eICU Collaborative Research Database, a freely "
    "available multi-center database for critical care research,\u201d *Sci. Data*, "
    "vol. 5, Art. no. 180178, Sep. 2018.",

    # ---- governance --------------------------------------------------------
    "gdpr2016": "European Parliament and Council of the European Union, \u201cRegulation "
    "(EU) 2016/679 of 27 April 2016 on the protection of natural persons with regard to "
    "the processing of personal data and on the free movement of such data (General Data "
    "Protection Regulation),\u201d *Off. J. Eur. Union*, vol. 59, no. L 119, "
    "pp. 1\u201388, May 2016.",

    "aiact2024": "European Parliament and Council of the European Union, \u201cRegulation "
    "(EU) 2024/1689 of 13 June 2024 laying down harmonised rules on artificial "
    "intelligence (Artificial Intelligence Act),\u201d *Off. J. Eur. Union*, Jul. 2024.",

    "hl7fhir": "Health Level Seven International, \u201cFHIR Release 4 (R4),\u201d "
    "HL7 Standard, 2019. [Online]. Available: https://hl7.org/fhir/R4/",

    "fda2021": "U.S. Food and Drug Administration, \u201cArtificial Intelligence/Machine "
    "Learning (AI/ML)-Based Software as a Medical Device (SaMD) Action Plan,\u201d "
    "FDA, Silver Spring, MD, USA, Jan. 2021.",

    "kingma2015": "D. P. Kingma and J. Ba, \u201cAdam: A method for stochastic "
    "optimization,\u201d in *Proc. Int. Conf. Learn. Represent. (ICLR)*, 2015.",
}
