# geni-tools
Tools for working with GENI to do measurements and create overlay topologies

The basic tools allow generating a configuration file with pairwise latencies
between each pair of nodes in a GENI manifest. For example, you can run
```
python parse_geni_manifest.py -f manifest.xml > geni_nodes.txt
```
This will parse the GENI manifest file to generate a list of nodes with their
login info. Then, you can use that list of nodes as input to the ping_all.sh
script. The ping_all.sh script will ssh into each GENI node and run a ping test
to each other node, and report the results.

```
./ping_all.sh -f geni_nodes.txt
```

The output from the ping_all.sh script can then be processed using
format_pingout.py. This program will parse the ping results and generate an
output file listing the minimum observed pairwise latency for each pair of
nodes. The example below assumes the output from ping_all.sh was saved in a
file pingoutput.txt.

```
python format_pingout.py -f pingoutput.txt
```
