#!/usr/bin/python

import sys
import os
import argparse
import re
import math
from xml.etree import ElementTree

# This program parses a GENI manifest file (which you can download from the
# GENI portal after reserving resources for a slice) and turns it into the
# format needed to provide input to the ping_all program

def main(argv):
   
    # Parse commandline args
    parser = argparse.ArgumentParser(description="Parse geni xml file to pull out ssh info for each reserved node")
    parser.add_argument('-f', '--filename', required=True,
                        help='Input file to read from')
    parser.add_argument('--extra-opts', required=False, help='Global ssh '\
                        'options to include for each entry in parsed file')
    args = parser.parse_args()

    if args.extra_opts is None:
        args.extra_opts = ''

    # Parse xml input
    root = ElementTree.parse(args.filename).getroot()
    for node_tag in root.findall('{http://www.geni.net/resources/rspec/3}node'):
        service_tag = node_tag.find('{http://www.geni.net/resources/rspec/3}services')
        login_tag = service_tag.find('{http://www.geni.net/resources/rspec/3}login')
        host_tag = node_tag.find('{http://www.geni.net/resources/rspec/3}host')
        if login_tag is None:
            print('WARNING: No login tag for {}'.format(node_tag.get('client_id')))
            continue
        hostname = login_tag.get('hostname')
        port = login_tag.get('port')
        user = login_tag.get('username')
        ip = host_tag.get('ipv4')
        print('{host} {ip} -l {user} -p {port} {extra_opts}'.format(
              host=hostname, ip=ip, user=user, port=port,
              extra_opts=args.extra_opts) )

    #with open(args.filename) as f:
    #    for line in f:


if __name__ == "__main__":
    main(sys.argv[1:])
