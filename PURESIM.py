#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 11:44:54 2020

@author: jorge
"""




import time
import csv
import sys
import os
import numpy as np
import collections
import multiprocessing as mp
import argparse
import json





def checkProblemAttributes(attributes_to_read, star_type):
    letters = [l[0].upper() for l in attributes_to_read] + [star_type.upper()]
    if len(letters) != len(set(letters)):
        print ("There are attributes to read which start with the same letter.")
        print ("Attribute letters are:", letters)
        print ("Note that 'P' is a reserved letter for the star type!")
        quit()
    
def readDict(f, attributes_to_read, star_type):
    """
    read the file into a dict

    """
    G  = dict()


    with open(f, "r") as fp:
        for line in fp: ##each line represents the metadata of a publication
            json_data = json.loads(line)
            G[star_type + "_" + str(json_data['id'])] = dict()
            w = 0
            nodes_to_add = list()
            for attr in attributes_to_read:
                if attr not in json_data or len(json_data[attr]) == 0:
                    continue
                w += 1 / len(json_data[attr])
                for attr_node in json_data[attr]:
                    nodes_to_add.append(attr[0].upper() + "_" + str(attr_node))
 
            if len(nodes_to_add) > 0:
                w = 1 / len(nodes_to_add) ##all nodes have the same importance
                for n in nodes_to_add:
                    if n not in G:
                        G[n] = dict()
                    G[star_type + "_" + str(json_data['id'])][n] = w
                    G[n][star_type + "_" + str(json_data['id'])] = w
    return G

    
def removeUselessMetadata(g, star_type):
    """
    removes metadata that is only connected to a single publication
    """
    nodes_to_remove = list()
    for node in g.keys():
        if node[0] == star_type: ##we do not want to remove star types, for example for journals it's normal to connect to a single node
            continue
        if len(g[node]) <= 1:
            for p_node in g[node]:
                g[p_node].pop(node, None) ##remove the metadata node from the publication it is connected to
            nodes_to_remove.append(node)
    print ("Number of nodes removed per type:")
    countTypes(nodes_to_remove)
    

    for m_node in nodes_to_remove: ##for all the metadata nodes to be removed
        g.pop(m_node, None)
          
    
def metadataNormalization(g, star_type):
    """
    Applied the metadata normalization weighting scheme
    """
    for node in g:
        if node[0] == star_type: ##we want to normalize for metadata
            continue
        for n2 in g[node]:
            g[node][n2] = 1 / len(g[node])


def countTypes(nodes):
    """
    Prints the number of nodes per type
    """
    counts = dict()
    for n in nodes:
        if n[0].upper() not in counts:
            counts[n[0].upper()] = 0
        counts[n[0].upper()] += 1
    print (counts)
    
def idsToInt(G):
    mapping = dict()
    i = 0
    for n in G:
        mapping[n] = i
        i+= 1
    return mapping

def nodeTransProbability(n):
    global G
    total = sum([G[n][x] for x in G[n]])
    return (n , {n2 : G[n][n2]/ total for n2 in G[n]})

def estimateTransactionProbabilities(G, n_cpus):
    """
    Estimate transaction probabilities in parallel
    """
    pool = mp.Pool(n_cpus)
    results = pool.map(nodeTransProbability, [n for n in G.keys()])
    pool.close()

    trans_probs = dict()
    for r in results:
        trans_probs[r[0]] = r[1]
    
    return trans_probs


def computeNodeWalks(node):
    global n_walks
    global trans_prob
    
    self_loops = 0
    sims = dict()
    walks_1 = np.random.choice(list(trans_probs[node].keys()), n_walks, list(trans_probs[node].values()))
    ##count the times each neigbhour was selected
    c_1 = collections.Counter(walks_1)
    walks = list()
    for n2 in c_1: ##select neighbours of neighbours
        walks_2 = np.random.choice(list(trans_probs[n2].keys()), c_1[n2], list(trans_probs[n2].values()))
        walks += list(walks_2)
    ##count nodes reached    
    p_walks = collections.Counter(walks)
    ##filter nodes so we don't have self-loops
    sims = {n2: p_walks[n2] for n2 in p_walks if n2 != node}
    ##count self-loops
    if node in p_walks:
        self_loops += p_walks[node]
    ##normalize sims per pub
    sims = {x: sims[x]/ sum(sims.values()) for x in sims}
    return (node, sims, self_loops)
    
     



parser = argparse.ArgumentParser(description='Compute PURE-SIM.')
parser.add_argument('-data', action='store', type=str, help='JSON data with publications metadata', required=True)
parser.add_argument('-M', action='store', type=str, help='Metadata to read, separated by "_"', required=True)
parser.add_argument('-W', action='store', type=str, help='Weighting scheme to use. "P","p" or "pub" for publication normalization, otherwise metadata normalization is used', required=True)
parser.add_argument('-outfile', action='store', type=str, help='Output file to write similarities', required=True)
parser.add_argument('-N', action='store', type=int, help='Number of random walks to use', required=True)
parser.add_argument('-cpus', action='store', type=int, help='Number of cpus to use', required=True)


args = parser.parse_args()

   
tp = time.time()
        

star_type = "P"

attributes_to_read = args.M.split("_")

checkProblemAttributes(attributes_to_read, star_type)

if args.W[0].lower() == "p":
    metadata_normalization = False
else:
    metadata_normalization = True


global G
global trans_probs
global n_walks

n_walks = args.N

t1 = time.time()
G = readDict(args.data, attributes_to_read, star_type)
t1 = time.time() - t1
print ("Took %d sec to read the graph" % t1)

t1 = time.time()

removeUselessMetadata(G, star_type)
isolate_nodes = list()
for node in G:
    if node[0] == star_type: ##we want to normalize for metadata
        if len(G[node]) < 1:
            isolate_nodes.append(node)
for n in isolate_nodes:
    G.pop(n,None)
    
print ("Removed %d nodes because they are isolated" % int(len(isolate_nodes)))

print ("Number of nodes per type in the network:")
countTypes(G.keys())
   
if metadata_normalization:
    print ("Using the metadata weighting scheme")
    metadataNormalization(G, star_type)
else:
    print ("Using the publication weighting scheme")



mapping = idsToInt(G)


G2 = dict()
for n1 in G:
    G2[mapping[n1]] = dict()
    for n2 in G[n1]:
        G2[mapping[n1]][mapping[n2]] = G[n1][n2]
G = G2


t1 = time.time() - t1
print ("Took %d sec read data file" % int(t1))

pub_map = {mapping[i] : i for i in mapping if i[:2] == "P_"}



t1 = time.time()
trans_probs = estimateTransactionProbabilities(G, args.cpus)
t1 = time.time() - t1
print ("Took %d seconds to estimate transaction probabilities" % int(t1))



t1 = time.time()
    

sims = dict()
self_loops = 0
for node in pub_map:
    r = computeNodeWalks(node)
    sims[r[0]] = r[1]
    self_loops += r[2]

#sims, self_loops = computeRandomWalksParallel(pub_map, n_cpus)
print ("Took %d seconds to compute random walks" % int(time.time()-t1))


percent_self_loops = self_loops / (n_walks * len(pub_map))
print ("Random wals analyzer: %.6f self-loops rate" % percent_self_loops)


##write similarities to file
len_to_write = 10**6

f_out = open(args.outfile, "w")
counter = 0
t2 = time.time()
text = ""
for n1 in sims:
    for n2 in sims[n1]:
        text += ("%s %s %f\n" % (pub_map[n1], pub_map[n2], sims[n1][n2]))
        counter += 1
    if len(text) > len_to_write:
        f_out.write(text)
        text = ""
f_out.write(text)
f_out.close()
t2 = time.time() - t2
print ("%d sec to write %d sims to file %s" % (int(t2), counter, args.outfile))


 
tp= time.time() - tp
print ("process completed in %d seconds" % int(tp))



