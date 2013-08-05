#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
:Name:
    kokako

:Authors:
    Florian Boudin (florian.boudin@univ-nantes.fr)

:Version:
    0.1

:Date:
    Mar. 2013

:Description:
    kokako is a graph-based keyphrase extraction module. Given a document, a 
    word-graph is built in which a node represent a word and and edge between 
    two nodes represent their co-occurrences in the document (computed using a 
    fixed-size window of n words). The importance of each word is then 
    determined using a centrality measure. Lastly, keyphrase candidates are 
    generated and ranked based on the words they contain.

    This module was used in the following article(s):

    - Florian Boudin, A Comparison of Centrality Measures for Graph-Based 
      Keyphrase Extraction, *International Joint Conference on Natural
      Language Processing (IJCNLP)*, 2013.

:History:
    - 0.1 (Mar. 2013), first version

:Dependencies:
    - *networkx* for the graph construction (v1.2+)

:Misc:
    The Kōkako (Callaeas cinereus) is a forest bird which is endemic to New 
    Zealand. It is slate-grey with wattles and a black mask. It is one of three 
    species of New Zealand Wattlebird, the other two being the endangered Tieke 
    (saddleback) and the extinct Huia.
    (Wikipedia, http://en.wikipedia.org/wiki/Kōkako)
"""

import re
import math
import bisect
import networkx as nx

#~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
# [ Class graph
#~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
class graph:
    """
    The graph class builds a weighted word graph from the document given as 
    input. The document is a list of sentences that are tokenized and POS-tagged
    (e.g. ``"Saturn/NNP is/VBZ the/DT sixth/JJ planet/NN from/IN the/DT Sun/NNP
    in/IN the/DT Solar/NNP System/NNP"``).
    Four optional parameters can be specified:

    - window is the word window used to compute word co-occurrences, default is 
      10.
    - tags is the set of Part-of-Speech tags used for word filtering, default is
      ('JJ', 'NNP', 'NNS', 'NN').
    - tag_delim is the separator used between a word and its POS, default is 
      '/'.
    - use_tags activates the use of POS tags in the graph, default is true.
    """

    #-T-----------------------------------------------------------------------T-
    def __init__( self, 
                  sentences, 
                  window=10, 
                  tags=['JJ', 'NNP', 'NNS', 'NN'],
                  tag_delim='/',
                  use_tags=True):

        self.graph = nx.Graph()
        """ The weighted graph used for representing the document. """

        self.sentences = list(sentences)
        """ The document as a list of sentences. """

        self.window = window
        """ Window size for computing co-occurrences, default is 10. """

        self.tags = set(tags)
        """ A set of Part-of-Speech tags used for word filtering. """

        self.tag_delim = tag_delim
        """ The separator used between a word and its POS. """

        self.use_tags = use_tags
        """ Variable for the use of POS tags in the graph, default is true. """

        self.keyphrase_candidates = set([])
        """ The keyphrase candidates generated from the document. """

        # 1. Build the graph from sentences
        self.build_graph()

        # 2. Generates the keyphrase candidates
        self.generate_candidates()
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def build_graph(self):
        """
        Build a word graph from a list of sentences. Each node in the graph 
        represents a (word, POS) tuple. An edge is created between two nodes if 
        they co-occur in a given window (default is 2 words).

        POS-tags are ignored if self.use_tags is set to false.
        """

        # For each sentence
        for i in range(len(self.sentences)):

            # Splitting the sentence in words
            words = self.sentences[i].split(' ')

            #-T---------------------------------------------------------------T-
            # Step 1 : syntactic filtering + node creation
            for j in range(len(words)):

                # Get (word, POS) tuple
                word, POS = self.wordpos_to_tuple(words[j], self.tag_delim)

                # Check POS of current word
                if POS in self.tags:

                    if not self.use_tags:
                         words[j] = word

                    # Add the word to the graph
                    if not self.graph.has_node(words[j]):
                        self.graph.add_node(words[j])
                else:
                    words[j] = ''
            #-B---------------------------------------------------------------B-

            #-T---------------------------------------------------------------T-
            # Step 2 : adding edges between nodes
            for j in range(len(words)):

                # Get first word in window
                word1 = words[j]

                if word1 == '':
                    continue

                # For the other words in the window
                for k in range(j+1, min(len(words), j+self.window)):

                    # Get the next node from the window
                    word2 = words[k]

                    if word2 == '':
                        continue 

                    # Add edge if not exists
                    if not self.graph.has_edge(word1, word2):
                        self.graph.add_edge(word1, word2, weight=0)
                    self.graph[word1][word2]['weight'] += 1

            #-B---------------------------------------------------------------B-

            # Replacing raw sentence by tokenized sentence
            self.sentences[i] = words

        # Loop over edges to compute inverse weights, required for weighted
        # closeness and betweenness
        for node1, node2 in self.graph.edges_iter():
            self.graph[node1][node2]["inv_weight"] = \
                1.0 / self.graph[node1][node2]['weight']
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def wordpos_to_tuple(self, word, delim='/'):
        """
        This function converts a word/POS to a (word, POS) tuple. The character
        used for separating word and POS can be specified by the delim parameter
        (default is /).
        """

        # Splitting word, POS using regex
        m = re.match("^(.+)"+delim+"(.+)$", word)

        # Extract the word information
        token, POS = m.group(1), m.group(2)

        # Return the tuple 
        return (token.lower(), POS)
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def tuple_to_wordpos(self, wordpos_tuple, delim='/'):
        """
        This function converts a (word, POS) tuple to word/POS. The character 
        used for separating word and POS can be specified by the delim parameter
        (default is /).
        """

        # Return the word +delim+ POS
        return wordpos_tuple[0]+delim+wordpos_tuple[1]
    #-B-----------------------------------------------------------------------B-

    #-T-----------------------------------------------------------------------T-
    def remove_pos(self, candidate):
        """ Function that removes the POS tags from a candidate. """

        words = []
        for wordpos in candidate.split(' '):
            words.append(wordpos[0:wordpos.rfind("/")])
        return ' '.join(words)
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def generate_candidates(self):
        """
        Generate the keyphrase candidates from the content of the document. 
        Sequences of adjacent words, restricted to the specified POS tags, are 
        considered as keyphrase candidates.
        """

        # Buffer for constructing keyphrase candidates
        candidate = []

        # For each sentence in the document
        for i in range(len(self.sentences)):

            # Get the words from the sentence
            words = self.sentences[i]

            # For each word in the sentence
            for j in range(len(words)):

                # If word is to be included in a candidate
                if words[j] != '':

                    # Adds word to candidate
                    candidate.append(words[j])

                # If a candidate keyphrase is in the buffer
                elif len(candidate) > 0:

                    # Add the keyphrase to keyphrase candidates
                    self.keyphrase_candidates.add(' '.join(candidate))

                    # Flush the buffer
                    candidate = []
               
            # Handle the last possible candidate
            if len(candidate) > 0:

                # Add the keyphrase to keyphrase candidates
                self.keyphrase_candidates.add(' '.join(candidate))
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def score_candidates(self, scores):
        """
        Compute candidate scores according to the word scores given in 
        parameter and return an ordered list of (score, keyphrase) tuples. The 
        score of a candidate keyphrase is computed by summing the scores of the 
        words it contains normalized by its length + 1 to favor longer n-grams.
        """

        scored_candidates = []

        # Compute the score of each candidate according to its words
        for keyphrase in self.keyphrase_candidates:

            score = 0
            for word in keyphrase.split(' '):
                score += scores[word]
            score /= ( len(keyphrase.split(' ')) + 1.0 )

            if self.use_tags:
                keyphrase = self.remove_pos(keyphrase)

            bisect.insort(scored_candidates, (score, keyphrase))

        scored_candidates.reverse()

        return scored_candidates
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def degree_centrality(self):
        """
        Degree centrality is defined as the number of edges incident upon a 
        node.
        """

        degree = {}
        for node1 in self.graph.nodes():
            degree[node1] = self.graph.degree(node1)
            
        return self.score_candidates(degree)
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def weighted_degree_centrality(self, alpha=0.5):
        """
        Weighted degree centrality is defined as a mixture between the number of
        edges incident upon a node and their edge weights.
        """

        degree = {}
        for node1 in self.graph.nodes():
            k_i = 0.0
            s_i = 0.0
            for node2 in self.graph.neighbors(node1):
                k_i += 1.0
                s_i += self.graph[node1][node2]['weight']
            degree[node1] = math.pow(k_i, (1 - alpha)) * math.pow(s_i, alpha)

        return self.score_candidates(degree)
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def undirected_TextRank(self, d=0.85, f_conv=0.0001, max_iter=100):
        """
        TextRank is based on the eigenvector centrality measure and implements 
        the concept of voting, more details can be found in:

        - Rada Mihalcea and Paul Tarau. Textrank: Bringing order into texts. *In
          Proceedings of 2004 conference on Empirical methods in natural 
          language processing*, pages 404–411, 2004.
        """

        # Initialise the maximum node difference for checking stability
        max_node_difference = f_conv
    
        # Initialise node scores to 1
        node_scores = {}
        for node in self.graph.nodes():
            node_scores[node] = 1.0

        # Initialize the number of iterations
        iter_number = 0

        # While the node scores are not stabilized
        while (max_node_difference >= f_conv and iter_number < max_iter):

            # Create a copy of the current node scores
            current_node_scores = node_scores.copy()

            # For each node I in the graph
            for node_i in self.graph.nodes():

                sum_Vj = 0

                # For each node J connected to I
                for node_j in self.graph.neighbors_iter(node_i):

                    wji = self.graph[node_j][node_i]['weight']
                    WSVj = current_node_scores[node_j]
                    sum_wjk = 0.0

                    # For each node K connected to J
                    for node_k in self.graph.neighbors_iter(node_j):
                        sum_wjk += self.graph[node_j][node_k]['weight']

                    sum_Vj += ( (wji * WSVj) / sum_wjk )

                # Modify node score
                node_scores[node_i] = (1 - d) + (d * sum_Vj)

                # Compute the difference between old and new score
                score_difference = math.fabs(node_scores[node_i] \
                                   - current_node_scores[node_i])

                max_node_difference = max(score_difference, score_difference)

                # Increase the number of iterations
                iter_number += 1

        return self.score_candidates(node_scores)
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def betweenness(self):
        """
        Betweenness centrality quantifies the number of times a node acts as a 
        bridge along the shortest path between two other nodes.
        """

        scores = nx.betweenness_centrality(self.graph,
                                           weight = "inv_weight",
                                           normalized = False)

        return self.score_candidates(scores)
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def closeness(self):
        """
        Closeness centrality is defined as the inverse of farness, i.e. the sum
        of the shortest distances between a node and all the other nodes.
        """

        scores = nx.closeness_centrality(self.graph, 
                                         distance='inv_weight', 
                                         normalized=False)

        return self.score_candidates(scores)
    #-B-----------------------------------------------------------------------B-


    #-T-----------------------------------------------------------------------T-
    def eigenvector_centrality(self):
        """
        Eigenvector centrality measures the centrality of a node as a function 
        of the centralities of its neighbors. Unlike degree, it accounts for the
        notion that connections to high-scoring nodes are more important than 
        those to low-scoring ones.
        """

        scores = nx.eigenvector_centrality(self.graph,
                                           max_iter=1000)

        return self.score_candidates(scores)
    #-B-----------------------------------------------------------------------B-

    
#~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
# ] Ending graph class
#~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~























