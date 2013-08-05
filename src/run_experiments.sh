#!/bin/bash

# Defining DATA paths
PATH_INSPEC=../data/inspec/
PATH_DEFT=../data/deft/
PATH_SEMEVAL=../data/semeval/
PATH_REFERENCE_INSPEC=../data/references/inspec.ref
PATH_REFERENCE_DEFT=../data/references/deft.ref
PATH_REFERENCE_SEMEVAL=../data/references/semeval.ref
PATH_OUTPUT_INSPEC=../output/inspec/
PATH_OUTPUT_DEFT=../output/deft/
PATH_OUTPUT_SEMEVAL=../output/semeval/


################################################################################
# PROCESSING INSPEC DATASET
################################################################################
echo 'info - processing Inspec dataset'

echo 'info - extracting keyphrases'
# rm -f $PATH_OUTPUT_INSPEC/*
# python keyphrase-extraction.py $PATH_INSPEC $PATH_OUTPUT_INSPEC 'jj;nnp;nnps;nns;nn'

echo 'info - evaluation keyphrase extraction'
rm -f $PATH_OUTPUT_INSPEC/*.scores
python keyphrase-evaluation_inspec.py $PATH_REFERENCE_INSPEC $PATH_OUTPUT_INSPEC

echo '---'

################################################################################
# PROCESSING DEFT DATASET
################################################################################
echo 'info - processing DEFT dataset'

echo 'info - extracting keyphrases'
# rm -f $PATH_OUTPUT_DEFT/*
# python keyphrase-extraction.py $PATH_DEFT $PATH_OUTPUT_DEFT 'adj;nc;npp'

echo 'info - evaluation keyphrase extraction'
rm -f $PATH_OUTPUT_DEFT/*.scores
python keyphrase-evaluation_deft.py $PATH_REFERENCE_DEFT $PATH_OUTPUT_DEFT

echo '---'

################################################################################
# PROCESSING SEMEVAL DATASET
################################################################################
echo 'info - processing SEMEVAL dataset'

echo 'info - extracting keyphrases'
# rm -f $PATH_OUTPUT_SEMEVAL/*
# python keyphrase-extraction.py $PATH_SEMEVAL $PATH_OUTPUT_SEMEVAL 'jj;nnp;nnps;nns;nn'

echo 'info - evaluation keyphrase extraction'
rm -f $PATH_OUTPUT_SEMEVAL/*.scores
python keyphrase-evaluation_semeval.py $PATH_REFERENCE_SEMEVAL $PATH_OUTPUT_SEMEVAL