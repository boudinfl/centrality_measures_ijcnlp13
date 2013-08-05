# Centrality Measures for Graph-Based Keyphrase Extraction

This archive contains the code and data used in the paper:

> A Comparison of Centrality Measures for Graph-Based Keyphrase Extraction  
> Florian Boudin  
> In Proceedings of IJCNLP 2013 

*This code is frozen as of the version used to obtain the results in the paper. 
It will not be maintained.*

To run the system:
    
    cd src/
    ./run_experiments.sh

Archive content:

    data/ <- contains the datasets used in the experiments
    ----/deft/ <- DEFT dataset
    ----/semeval/ <- Semeval dataset
    ----/inspec/ <- Inspec dataset
    ----/references/ <- gold standard for evaluation

    src/ <- code for running the system
    ---/kokako_0.1/ <- module for graph-based keyphrase extraction
    ---/keyphrase-evaluation_XXX.py <- evaluation scripts for XXX dataset
    ---/keyphrase-extraction.py <- script for extracting keyphrases
    ---/run_experiments.sh <- script for running the experiments

    output/ <- ranked keyphrases and evaluation results