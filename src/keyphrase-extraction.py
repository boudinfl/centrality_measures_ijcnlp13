#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import codecs

# Import kokako vesrion 0.1
sys.path.append('kokako_0.1')
import kokako

# The list of runs to compute
runs = ["textrank", 
        "betweenness", 
        "degree", 
        "closeness", 
        "eigenvector"]


################################################################################
if __name__ == "__main__":

    if len(sys.argv) != 4:
        print "Usage : keyphrase-extraction.py path_data path_output tagset"
        sys.exit()

    termes_cles = {}
    for run_name in runs:
        termes_cles[run_name] = {}

    # Listing files in path_data
    fichiers = os.listdir(sys.argv[1])

    # Splitting tagset
    tagset = sys.argv[3].split(';')

    # Extracting keyphrases for each file
    for document in fichiers:

        if document[0] == '.':
            continue

        # Lecture du fichier passé en paramètre
        sentences = []
        for line in codecs.open(sys.argv[1]+document, "r", "utf-8"):
            line = line.strip()
            if len(line) > 0:
                sentences.append(line)

        # Construction du graphe
        ke = kokako.graph( sentences, 
                           window=10, 
                           use_tags=False, 
                           tags=tagset,
                           tag_delim='/' )

        for run_name in runs:

            if run_name == 'textrank':
                keyphrases = ke.undirected_TextRank()
                termes_cles[run_name][document[:-4]] = ';'.join( u[1] for u in keyphrases)

            elif run_name == 'betweenness':
                keyphrases = ke.betweenness()
                termes_cles[run_name][document[:-4]] = ';'.join( u[1] for u in keyphrases)

            elif run_name == 'degree':
                keyphrases = ke.degree_centrality()
                termes_cles[run_name][document[:-4]] = ';'.join( u[1] for u in keyphrases)

            elif run_name == 'closeness':
                keyphrases = ke.closeness()
                termes_cles[run_name][document[:-4]] = ';'.join( u[1] for u in keyphrases)

            elif run_name == 'eigenvector':
                keyphrases = ke.eigenvector_centrality()
                termes_cles[run_name][document[:-4]] = ';'.join( u[1] for u in keyphrases)

    for run_name in runs:
        fh = codecs.open(sys.argv[2]+"candidats."+run_name, "w", "utf-8")
        for document_id in termes_cles[run_name]:
            fh.write(document_id + '\t' + termes_cles[run_name][document_id]+'\n')
        fh.close()

################################################################################









    


