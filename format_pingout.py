#!/usr/bin/python

import sys
import os
import argparse
import re
import math

# Match a line like: **** PING (1, 2) : host1.edu -> host2.net ****
# Group 1 (source_id) : 1
# Group 2 (dest_id)   : 2
# Group 3 (source_name) : host1.edu
# Group 4 (dest_name)   : host2.net
EDGE_PATTERN = re.compile(r'^\*\*\*\* PING \(([0-9]+), ([0-9]+)\) : (.*) -> (.*) \*\*\*\*')

# Match a line like: rtt min/avg/max/mdev = 7.147/7.360/7.472/0.119 ms
# Group 1 (min) : 7.147
# Group 2 (avg) : 7.360
# Group 3 (max) : 7.472
# Group 4 (mdev) : 0.119
RESULT_PATTERN = re.compile(r'^rtt min/avg/max/mdev = ([0-9]+\.[0-9]+)/([0-9]+\.[0-9]+)/([0-9]+\.[0-9]+)/([0-9]+\.[0-9]+) ms')

def main(argv):
   
    # Parse commandline args
    parser = argparse.ArgumentParser(description="Generate edges section of spines configuration file from ping output")
    parser.add_argument('-f', '--filename', required=True,
                        help="Input file to read from")
    args = parser.parse_args()

    # Read file and populate list of edges (and node names dict)
    node_names = {}
    edges = []
    active_edge = None
    with open(args.filename) as f:
        for line in f:
            edge_match = re.match(EDGE_PATTERN, line)
            result_match = re.match(RESULT_PATTERN, line)

            if edge_match != None:
                source_id = int(edge_match.group(1))
                dest_id = int(edge_match.group(2))
                source_name = edge_match.group(3)
                dest_name = edge_match.group(4)
                if source_id not in node_names:
                    node_names[source_id] = source_name
                if dest_id not in node_names:
                    node_names[dest_id] = dest_name
                active_edge = (source_id, dest_id)
            elif result_match != None:
                min_rtt = float(result_match.group(1))
                edges.append((active_edge[0], active_edge[1], min_rtt))
                #print "\t", active_edge[0], "->", active_edge[1], ":", min_rtt

    # go through list of edges populated above and build matrix of roundtrip times
    num_nodes = len(node_names)
    min_rtts = [[0 for i in range(num_nodes+1)] for j in range(num_nodes+1)]
    for e in edges: # (source_id, dest_id, rtt)
        source_id = e[0]
        dest_id = e[1]
        rtt = int(math.ceil(e[2]))

        existing_rtt = min_rtts[source_id][dest_id]
        # check whether there is a significant differnece between the two directions (shouldn't be)
        if existing_rtt != 0 and abs(rtt-existing_rtt) > 1:
            print("WARNING: rtt discrepancy: ({source}, {dest}) : {rtt} - {prev} = {diff}".format(
                    source=source_id, dest=dest_id, rtt=rtt, prev=existing_rtt,
                    diff=(rtt-existing_rtt)))
        # update rtt (if needed)
        if existing_rtt == 0 or rtt < existing_rtt:
            min_rtts[source_id][dest_id] = rtt
            min_rtts[dest_id][source_id] = rtt

    # print out final edge list
    for i in xrange(1,num_nodes+1): # for each source
        for j in xrange(1,num_nodes+1): # for each dest
            if i == j: # don't include edge from node to itself
                continue
            print("   {source:2d} {dest:2d} {rtt:4d} # {sname:s} {dname:s}".format(
                    source=i, dest=j, rtt=min_rtts[i][j], sname=node_names[i],
                    dname=node_names[j]))
        print("")

if __name__ == "__main__":
    main(sys.argv[1:])
