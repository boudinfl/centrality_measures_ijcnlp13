#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import nltk
import codecs

# Création du stemmer
stemmer = nltk.stem.porter.PorterStemmer()

# Fonction de transformation terme clé -> stems
def keyphrase_to_stems(text):
	words = text.split(' ')
	for i in range(len(words)):
		words[i] = stemmer.stem_word(words[i])
	return ' '.join(words)

# Fonction de lecture de fichier
def read_file(path, stemming=False):
	dictionary = {}
	for line in codecs.open(path, "r", "utf-8"):
		line = line.strip()
		if line != '':
			document_id, text = line.split('\t')
			keyphrases = text.lower().split(';')
			if stemming:
				for i in range(len(keyphrases)):
					keyphrases[i] = re.sub(' +', ' ', keyphrases[i])
					keyphrases[i] = keyphrase_to_stems(keyphrases[i].strip())
			dictionary[document_id] = keyphrases
	return dictionary

def evaluate(candidates, reference_set):
	"""
	Function evaluating a ranked list of candidate keyphrases against a list of 
	reference keyphrases. Reference and candidate keyphrases can be stemmed.

	  - candidates is an ordered list of candidate keyphrases
	  - reference_set is a set of reference keyphrases

	Returns a dictionary containing the P-R-F scores at 5-10, the MAP and the 
	maximum recall (R-MAX).
	"""

	ranks = []
	scores = {}

	average_precision = 0.0
	for i in range(len(candidates)):
		if candidates[i] in reference_set:
			ranks.append(i+1)
			average_precision += len(ranks) / float(i+1)

	# Compute P-R-F@5
	keys_at_5 = 0
	for i in range(len(ranks)):
		if ranks[i] <= 5:
			keys_at_5 += 1
		else:
			break

	scores['P5'] = keys_at_5 / 5.0
	scores['R5'] = keys_at_5 / float(len(reference_set))
	if (scores['P5']+scores['R5']) > 0:
		scores['F5'] = 2.0 * (scores['P5']*scores['R5']) / (scores['P5']+scores['R5'])
	else:
		scores['F5'] = 0.0

	# Compute P-R-F@10
	keys_at_10 = 0
	for i in range(len(ranks)):
		if ranks[i] <= 10:
			keys_at_10 += 1
		else:
			break

	scores['P10'] = keys_at_10 / 10.0
	scores['R10'] = keys_at_10 / float(len(reference_set))
	if (scores['P10']+scores['R10']) > 0:
		scores['F10'] = 2.0 * (scores['P10']*scores['R10']) / (scores['P10']+scores['R10'])
	else:
		scores['F10'] = 0.0

	# Compute the recall maximum
	scores['R-MAX'] = len(ranks) / float(len(reference_set))

	# Compute the MAP
	scores['MAP'] = average_precision / len(reference_set)

	return scores

# Lecture du fichier de référence passé en paramètre
references = read_file(sys.argv[1], stemming=False)

# Lecture des fichiers de termes-cles candidats
fichiers = os.listdir(sys.argv[2])

for fichier in fichiers:

	if fichier[0] == '.':
		continue

	candidats = read_file(sys.argv[2]+fichier, stemming=True)

	# Dictionaire de scores
	scores = {}
	score_ind = []

	for docid in references:

		### Suppression de la redondance
		non_redundant_keyphrases = []
		for keyphrase in candidats[docid]:
			if not keyphrase in non_redundant_keyphrases:
				non_redundant_keyphrases.append(keyphrase)

		document_scores = evaluate(non_redundant_keyphrases, references[docid])

		for measure in document_scores:
			if not scores.has_key(measure):
				scores[measure] = 0.0
			scores[measure] += document_scores[measure]

		score_ind.append(document_scores)

	print "P10: %.3f" % (scores['P10'] / len(references)),
	print "R10: %.3f" % (scores['R10'] / len(references)),
	print "F10: %.3f" % (scores['F10'] / len(references)),
	print "|",
	print "R-MAX: %.3f" % (scores['R-MAX'] / len(references)),
	print "|",
	print "MAP: %.3f" % (scores['MAP'] / len(references)),
	print '->', fichier

	fh = codecs.open(sys.argv[2]+fichier+".scores", "w", "utf-8")
	measures = ["P10", 'R10', 'F10']
	fh.write( ' '.join(measures)+'\n' )
	for i in range(len(score_ind)):
		current_scores = []
		for m in measures:
			current_scores.append(score_ind[i][m])
		fh.write( ' '.join("%.3f" % s for s in current_scores)+'\n')
	fh.close()

	