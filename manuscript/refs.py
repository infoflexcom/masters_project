"""IEEE-formatted reference database keyed by citation handle, with DOIs.

Citation handles are resolved to numbers by order of first appearance in the
manuscript (see build_docx.py). Per IEEE style, author lists with more than six
authors use *et al.*, and every entry concludes with an explicit `doi: 10....`.
"""

REFS = {
    "singer2016": (
        "M. Singer *et al.*, \u201cThe Third International Consensus Definitions for "
        "Sepsis and Septic Shock (Sepsis-3),\u201d *JAMA*, vol. 315, no. 8, "
        "pp. 801\u2013810, Feb. 2016, doi: 10.1001/jama.2016.0287."
    ),
    "rudd2020": (
        "K. E. Rudd *et al.*, \u201cGlobal, regional, and national sepsis incidence and "
        "mortality, 1990\u20132017: Analysis for the Global Burden of Disease Study,\u201d "
        "*Lancet*, vol. 395, no. 10219, pp. 200\u2013211, Jan. 2020, "
        "doi: 10.1016/S0140-6736(19)32989-7."
    ),
    "seymour2019": (
        "C. W. Seymour *et al.*, \u201cDerivation, validation, and potential treatment "
        "implications of novel clinical phenotypes for sepsis,\u201d *JAMA*, vol. 321, "
        "no. 20, pp. 2003\u20132017, May 2019, doi: 10.1001/jama.2019.5791."
    ),
    "fleuren2020": (
        "L. M. Fleuren *et al.*, \u201cMachine learning for the prediction of sepsis: "
        "A systematic review and meta-analysis of diagnostic test accuracy,\u201d "
        "*Intensive Care Med.*, vol. 46, no. 3, pp. 383\u2013400, Mar. 2020, "
        "doi: 10.1007/s00134-019-05872-y."
    ),
    "nemati2018": (
        "S. Nemati, A. Holder, F. Razmi, M. D. Stanley, G. D. Clifford, and "
        "T. G. Buchman, \u201cAn interpretable machine learning model for accurate "
        "prediction of sepsis in the ICU,\u201d *Crit. Care Med.*, vol. 46, no. 4, "
        "pp. 547\u2013553, Apr. 2018, doi: 10.1097/CCM.0000000000002936."
    ),
    "shashikumar2021": (
        "S. P. Shashikumar, C. S. Josef, A. Sharma, and S. Nemati, "
        "\u201cDeepAISE\u2014An interpretable and recurrent neural survival model for early "
        "prediction of sepsis,\u201d *Artif. Intell. Med.*, vol. 113, Art. no. 102036, "
        "Mar. 2021, doi: 10.1016/j.artmed.2021.102036."
    ),
    "reyna2020": (
        "M. A. Reyna *et al.*, \u201cEarly prediction of sepsis from clinical data: "
        "The PhysioNet/Computing in Cardiology Challenge 2019,\u201d *Crit. Care Med.*, "
        "vol. 48, no. 2, pp. 210\u2013217, Feb. 2020, doi: 10.1097/CCM.0000000000004145."
    ),
    "sendak2020": (
        "M. P. Sendak *et al.*, \u201cReal-world integration of a sepsis deep learning "
        "technology into routine clinical care: Implementation study,\u201d *JMIR Med. "
        "Inform.*, vol. 8, no. 7, Art. no. e15182, Jul. 2020, doi: 10.2196/15182."
    ),
    "wong2021": (
        "A. Wong *et al.*, \u201cExternal validation of a widely implemented proprietary "
        "sepsis prediction model in hospitalized patients,\u201d *JAMA Intern. Med.*, "
        "vol. 181, no. 8, pp. 1065\u20131070, Aug. 2021, "
        "doi: 10.1001/jamainternmed.2021.2626."
    ),
    "shimabukuro2017": (
        "D. W. Shimabukuro, C. W. Barton, M. D. Feldman, S. J. Mataraso, and R. Das, "
        "\u201cEffect of a machine learning-based severe sepsis prediction algorithm on "
        "patient survival and hospital length of stay: A randomised clinical trial,\u201d "
        "*BMJ Open Respir. Res.*, vol. 4, no. 1, Art. no. e000234, Nov. 2017, "
        "doi: 10.1136/bmjresp-2017-000234."
    ),
    "allen2007": (
        "J. Allen, \u201cPhotoplethysmography and its application in clinical "
        "physiological measurement,\u201d *Physiol. Meas.*, vol. 28, no. 3, pp. R1\u2013R39, "
        "Mar. 2007, doi: 10.1088/0967-3334/28/3/R01."
    ),
    "weenk2017": (
        "M. Weenk *et al.*, \u201cContinuous monitoring of vital signs using wearable "
        "devices on the general ward: Pilot study,\u201d *JMIR mHealth uHealth*, vol. 5, "
        "no. 7, Art. no. e91, Jul. 2017, doi: 10.2196/mhealth.7208."
    ),
    "mishra2020": (
        "T. Mishra *et al.*, \u201cPre-symptomatic detection of COVID-19 from smartwatch "
        "data,\u201d *Nat. Biomed. Eng.*, vol. 4, no. 12, pp. 1208\u20131220, Dec. 2020, "
        "doi: 10.1038/s41551-020-00640-6."
    ),
    "dunn2018": (
        "J. Dunn, R. Runge, and M. Snyder, \u201cWearables and the medical revolution,\u201d "
        "*Per. Med.*, vol. 15, no. 5, pp. 429\u2013448, Sep. 2018, "
        "doi: 10.2217/pme-2018-0044."
    ),
    "mcmahan2017": (
        "B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. Ag\u00fcera y Arcas, "
        "\u201cCommunication-efficient learning of deep networks from decentralized data,\u201d "
        "in *Proc. 20th Int. Conf. Artif. Intell. Statist. (AISTATS)*, vol. 54, "
        "2017, pp. 1273\u20131282, doi: 10.48550/arXiv.1602.05629."
    ),
    "kairouz2021": (
        "P. Kairouz *et al.*, \u201cAdvances and open problems in federated learning,\u201d "
        "*Found. Trends Mach. Learn.*, vol. 14, no. 1\u20132, pp. 1\u2013210, Jun. 2021, "
        "doi: 10.1561/2200000083."
    ),
    "li2020": (
        "T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith, "
        "\u201cFederated optimization in heterogeneous networks,\u201d *Proc. Mach. Learn. "
        "Syst.*, vol. 2, pp. 429\u2013450, 2020, doi: 10.48550/arXiv.1812.06127."
    ),
    "karimireddy2020": (
        "S. P. Karimireddy, S. Kale, M. Mohri, S. J. Reddi, S. U. Stich, and "
        "A. T. Suresh, \u201cSCAFFOLD: Stochastic controlled averaging for federated "
        "learning,\u201d in *Proc. 37th Int. Conf. Mach. Learn. (ICML)*, 2020, "
        "pp. 5132\u20135143, doi: 10.48550/arXiv.1910.06378."
    ),
    "reddi2021": (
        "S. J. Reddi *et al.*, \u201cAdaptive federated optimization,\u201d in *Proc. Int. "
        "Conf. Learn. Represent. (ICLR)*, 2021, doi: 10.48550/arXiv.2003.00295."
    ),
    "fedbn2021": (
        "X. Li, M. Jiang, X. Zhang, M. Kamp, and Q. Dou, \u201cFedBN: Federated "
        "learning on non-IID features via local batch normalization,\u201d in *Proc. Int. "
        "Conf. Learn. Represent. (ICLR)*, 2021, doi: 10.48550/arXiv.2102.07623."
    ),
    "konecny2016": (
        "J. Kone\u010dn\u00fd, H. B. McMahan, F. X. Yu, P. Richt\u00e1rik, A. T. Suresh, and "
        "D. Bacon, \u201cFederated learning: Strategies for improving communication "
        "efficiency,\u201d in *NIPS Workshop Private Multi-Party Mach. Learn.*, Oct. 2016, "
        "doi: 10.48550/arXiv.1610.05492."
    ),
    "xie2019": (
        "C. Xie, S. Koyejo, and I. Gupta, \u201cAsynchronous federated optimization,\u201d "
        "*OPT2020 Workshop*, Mar. 2019, doi: 10.48550/arXiv.1903.03934."
    ),
    "beutel2020": (
        "D. J. Beutel *et al.*, \u201cFlower: A friendly federated learning research "
        "framework,\u201d Jul. 2020, doi: 10.48550/arXiv.2007.14390."
    ),
    "roth2023": (
        "H. R. Roth *et al.*, \u201cNVIDIA FLARE: Federated learning from simulation to "
        "real-world,\u201d *IEEE Data Eng. Bull.*, vol. 46, no. 1, pp. 132\u2013144, "
        "Mar. 2023, doi: 10.48550/arXiv.2210.13291."
    ),
    "rieke2020": (
        "N. Rieke *et al.*, \u201cThe future of digital health with federated learning,\u201d "
        "*npj Digit. Med.*, vol. 3, Art. no. 119, Sep. 2020, "
        "doi: 10.1038/s41746-020-00323-1."
    ),
    "dayan2021": (
        "I. Dayan *et al.*, \u201cFederated learning for predicting clinical outcomes in "
        "patients with COVID-19,\u201d *Nat. Med.*, vol. 27, no. 10, pp. 1735\u20131743, "
        "Oct. 2021, doi: 10.1038/s41591-021-01506-3."
    ),
    "duesing2025": (
        "C. D\u00fcsing and P. Cimiano, \u201cImproving early sepsis onset prediction "
        "through federated learning,\u201d in *Proc. 1st Workshop Artif. Intell. Biomed. "
        "Data (AIBio)*, Sep. 2025, doi: 10.48550/arXiv.2509.20885."
    ),
    "abadi2016": (
        "M. Abadi *et al.*, \u201cDeep learning with differential privacy,\u201d in *Proc. "
        "ACM SIGSAC Conf. Comput. Commun. Secur. (CCS)*, Oct. 2016, pp. 308\u2013318, "
        "doi: 10.1145/2976749.2978318."
    ),
    "dwork2014": (
        "C. Dwork and A. Roth, \u201cThe algorithmic foundations of differential "
        "privacy,\u201d *Found. Trends Theor. Comput. Sci.*, vol. 9, no. 3\u20134, "
        "pp. 211\u2013407, Aug. 2014, doi: 10.1561/0400000042."
    ),
    "mironov2017": (
        "I. Mironov, \u201cR\u00e9nyi differential privacy,\u201d in *Proc. IEEE 30th Comput. "
        "Secur. Found. Symp. (CSF)*, Aug. 2017, pp. 263\u2013275, "
        "doi: 10.1109/CSF.2017.11."
    ),
    "bonawitz2017": (
        "K. Bonawitz *et al.*, \u201cPractical secure aggregation for privacy-preserving "
        "machine learning,\u201d in *Proc. ACM SIGSAC Conf. Comput. Commun. Secur. "
        "(CCS)*, Oct. 2017, pp. 1175\u20131191, doi: 10.1145/3133956.3133982."
    ),
    "zhu2019": (
        "L. Zhu, Z. Liu, and S. Han, \u201cDeep leakage from gradients,\u201d in *Proc. Adv. "
        "Neural Inf. Process. Syst. (NeurIPS)*, vol. 32, Dec. 2019, "
        "pp. 14774\u201314784, doi: 10.5555/3454287.3455610."
    ),
    "nasr2019": (
        "M. Nasr, R. Shokri, and A. Houmansadr, \u201cComprehensive privacy analysis of "
        "deep learning: Passive and active white-box inference attacks against "
        "centralized and federated learning,\u201d in *Proc. IEEE Symp. Secur. Privacy "
        "(SP)*, May 2019, pp. 739\u2013753, doi: 10.1109/SP.2019.00065."
    ),
    "melis2019": (
        "L. Melis, C. Song, E. De Cristofaro, and V. Shmatikov, \u201cExploiting "
        "unintended feature leakage in collaborative learning,\u201d in *Proc. IEEE Symp. "
        "Secur. Privacy (SP)*, May 2019, pp. 691\u2013706, doi: 10.1109/SP.2019.00029."
    ),
    "zhou2019": (
        "Z. Zhou, X. Chen, E. Li, L. Zeng, K. Luo, and J. Zhang, \u201cEdge "
        "intelligence: Paving the last mile of artificial intelligence with edge "
        "computing,\u201d *Proc. IEEE*, vol. 107, no. 8, pp. 1738\u20131762, Aug. 2019, "
        "doi: 10.1109/JPROC.2019.2918951."
    ),
    "shi2016": (
        "W. Shi, J. Cao, Q. Zhang, Y. Li, and L. Xu, \u201cEdge computing: Vision and "
        "challenges,\u201d *IEEE Internet Things J.*, vol. 3, no. 5, pp. 637\u2013646, "
        "Oct. 2016, doi: 10.1109/JIOT.2016.2579198."
    ),
    "david2021": (
        "R. David *et al.*, \u201cTensorFlow Lite Micro: Embedded machine learning on "
        "TinyML systems,\u201d *Proc. Mach. Learn. Syst.*, vol. 3, pp. 800\u2013811, 2021, "
        "doi: 10.48550/arXiv.2010.08678."
    ),
    "banbury2021": (
        "C. R. Banbury *et al.*, \u201cMLPerf Tiny benchmark,\u201d in *Proc. NeurIPS "
        "Track Datasets Benchmarks*, Jun. 2021, doi: 10.48550/arXiv.2106.07597."
    ),
    "gupta2018": (
        "O. Gupta and R. Raskar, \u201cDistributed learning of deep neural network over "
        "multiple agents,\u201d *J. Netw. Comput. Appl.*, vol. 116, pp. 1\u20138, Aug. 2018, "
        "doi: 10.1016/j.jnca.2018.05.003."
    ),
    "guo2017": (
        "C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, \u201cOn calibration of modern "
        "neural networks,\u201d in *Proc. 34th Int. Conf. Mach. Learn. (ICML)*, 2017, "
        "pp. 1321\u20131330, doi: 10.48550/arXiv.1706.04599."
    ),
    "angelopoulos2021": (
        "A. N. Angelopoulos and S. Bates, \u201cA gentle introduction to conformal "
        "prediction and distribution-free uncertainty quantification,\u201d *Found. "
        "Trends Mach. Learn.*, Jul. 2021, doi: 10.48550/arXiv.2107.07511."
    ),
    "lundberg2017": (
        "S. M. Lundberg and S.-I. Lee, \u201cA unified approach to interpreting model "
        "predictions,\u201d in *Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)*, "
        "vol. 30, Dec. 2017, pp. 4765\u20134774, doi: 10.48550/arXiv.1705.07874."
    ),
    "collins2024": (
        "G. S. Collins *et al.*, \u201cTRIPOD+AI statement: Updated guidance for "
        "reporting clinical prediction models that use regression or machine learning "
        "methods,\u201d *BMJ*, vol. 385, Art. no. e078378, Apr. 2024, "
        "doi: 10.1136/bmj-2023-078378."
    ),
    "wolff2019": (
        "R. F. Wolff *et al.*, \u201cPROBAST: A tool to assess the risk of bias and "
        "applicability of prediction model studies,\u201d *Ann. Intern. Med.*, vol. 170, "
        "no. 1, pp. 51\u201358, Jan. 2019, doi: 10.7326/M18-1376."
    ),
    "obermeyer2019": (
        "Z. Obermeyer, B. Powers, C. Vogeli, and S. Mullainathan, \u201cDissecting "
        "racial bias in an algorithm used to manage the health of populations,\u201d "
        "*Science*, vol. 366, no. 6464, pp. 447\u2013453, Oct. 2019, "
        "doi: 10.1126/science.aax2342."
    ),
    "sjoding2020": (
        "M. W. Sjoding, R. P. Dickson, T. J. Iwashyna, S. E. Gay, and T. S. Valley, "
        "\u201cRacial bias in pulse oximetry measurement,\u201d *N. Engl. J. Med.*, "
        "vol. 383, no. 25, pp. 2477\u20132478, Dec. 2020, doi: 10.1056/NEJMc2029240."
    ),
    "johnson2023": (
        "A. E. W. Johnson *et al.*, \u201cMIMIC-IV, a freely accessible electronic health "
        "record dataset,\u201d *Sci. Data*, vol. 10, no. 1, Art. no. 1, Jan. 2023, "
        "doi: 10.1038/s41597-022-01899-x."
    ),
    "pollard2018": (
        "T. J. Pollard, A. E. W. Johnson, J. D. Raffa, L. A. Celi, R. G. Mark, and "
        "O. Badawi, \u201cThe eICU Collaborative Research Database, a freely available "
        "multi-center database for critical care research,\u201d *Sci. Data*, vol. 5, "
        "Art. no. 180178, Sep. 2018, doi: 10.1038/sdata.2018.178."
    ),
    "gdpr2016": (
        "P. Voigt and A. von dem Bussche, *The EU General Data Protection Regulation "
        "(GDPR): A Practical Guide*, 1st ed. Cham, Switzerland: Springer, 2017, "
        "doi: 10.1007/978-3-319-57959-7."
    ),
    "aiact2024": (
        "M. Aboy, T. Minssen, and E. Vayena, \u201cNavigating the EU AI Act: "
        "Implications for regulated digital medical products,\u201d *npj Digit. Med.*, "
        "vol. 7, no. 1, Art. no. 237, Sep. 2024, doi: 10.1038/s41746-024-01232-3."
    ),
    "hl7fhir": (
        "D. Bender and K. Sartipi, \u201cHL7 FHIR: An agile and RESTful approach to "
        "healthcare information exchange,\u201d in *Proc. 26th IEEE Int. Symp. "
        "Comput.-Based Med. Syst. (CBMS)*, Jun. 2013, pp. 326\u2013331, "
        "doi: 10.1109/CBMS.2013.6627810."
    ),
    "fda2021": (
        "S. Benjamens, P. Dhunnoo, and B. Mesk\u00f3, \u201cThe state of artificial "
        "intelligence-based FDA-approved medical devices and algorithms: An online "
        "database,\u201d *npj Digit. Med.*, vol. 3, no. 1, Art. no. 118, Sep. 2020, "
        "doi: 10.1038/s41746-020-00324-0."
    ),
    "kingma2015": (
        "D. P. Kingma and J. Ba, \u201cAdam: A method for stochastic optimization,\u201d "
        "in *Proc. Int. Conf. Learn. Represent. (ICLR)*, May 2015, "
        "doi: 10.48550/arXiv.1412.6980."
    ),
}
