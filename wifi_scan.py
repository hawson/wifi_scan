#!/usr/bin/python

import os
import sys
import re
import subprocess
import logging as log

LOG_LEVEL=1000

log.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s', level=LOG_LEVEL) 




def file_or_pipe():

    if (sys.argv is None):
        return False

    try:
        f = open(sys.argv[1])
        f.close()

    except:
        return False

    return True

def get_file_output(iwlist_file):

    lines = tuple(open(iwlist_file))
    output = []
    for l in lines:
        output.append(l)

    return output


def get_pipe_output(cmd=['/usr/bin/iwlist','sc']):

    text = subprocess.run(cmd,universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.split("\n")

    return text

def find_networks(output):
    networks={}
    temp_network = {}
    regex = {}

    regex['essid']   = re.compile('ESSID:"(.*)"')
    regex['enc']     = re.compile('Encryption key:(.*)')
    #regex['quality'] = re.compile('Quality=([^ ]*)')
    regex['signal']  = re.compile('level=(-\d+)')
    regex['freq']    = re.compile('Frequency:(\d\.\d+)')
    regex['channel'] = re.compile('Channel:(\d+)')

    for line in output:

        #log.debug("Checking line: " + line)

        for RE in regex:
            match = regex[RE].search(line)
            #log.debug("..against %s" % RE)

            if match:
                temp_network[RE] = match.group(1)
                #print("%s <-- %s" %( RE, str(match.group(1))))
                break

        if 'essid' in temp_network:
            log.debug('Found network: ' + str(temp_network))
            networks[temp_network['essid']] = temp_network
            temp_network={}


    return networks

def get_max_widths(networks):

    widths = {}
    
    for network in networks:

        log.debug('Network='+network)
        log.debug('Network='+str(networks[network]))

        for field in networks[network]:

            value=networks[network][field]

            log.debug('Field='+field+' '+value)

            length = len(value)
            if field not in widths:
                widths[field] = length
            else:
                widths[field] = max(length, widths[field])

    return widths

                

def print_header(widths):
    
    #field_order = [ 'essid', 'enc', 'signal', 'quality', 'freq', 'channel']
    print("Enc  dB Freq   Ch ESSID               ")
    print("--- --- ----- --- --------------------")
    return

def report(networks):

    field_widths = get_max_widths(networks)
    print_header(field_widths)

    net_keys = sorted(networks.keys(), key=lambda x: (networks[x]['signal'], networks[x]['enc'],networks[x]['essid']))
    for net_key in net_keys:
        network = networks[net_key];
        print("{enc:>3s} {signal:3s} {freq:5s} {channel:>3s} {essid:20s}".format(**network))
        #print("{essid:>20s} {enc:>3s} {signal:3s} {freq:5.3s} {channel:3s}".format(**network))



if __name__ == '__main__':

    if file_or_pipe():
        log.debug(" reading from file")
        output = get_file_output(sys.argv[1])
    else:
        log.debug("reading from pipe")
        output = get_pipe_output()
        
    networks = find_networks(output)

    log.debug("All networks: " + str(networks))

    report(networks)


