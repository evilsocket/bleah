#coding:utf8
import binascii
import os
import sys
import string
from terminaltables import SingleTable
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, AssignedNumbers

from bleah.scan import *
from bleah.swag import *

def is_mostly_printable(s):
    tot = len(s)
    if tot == 0:
        return False

    pr  = 0

    for c in s:
        if c in string.printable:
            pr += 1

    return ( pr / float(tot) ) >= 0.75

def get_svc_desc(s):
    uuid_name = s.uuid.getCommonName()
    if uuid_name and uuid_name != str(s.uuid):
        svc_line = bold( green( uuid_name ) ) + " ( %s )" % s.uuid
    else:
        svc_line = bold( str(s.uuid) ) 

    return svc_line

def get_char_desc(c):
    char_name = c.uuid.getCommonName()
    if char_name and char_name != str(c.uuid):
        char_line = '  ' + bold( green( char_name ) ) + " ( %s )" % c.uuid
    else:
        char_line = '  ' + str(c.uuid)
    
    return char_line

def enumerate_device_properties(dev,args):
    tdata = [
        [ "Handles", "Service > Characteristics", "Properties", "Data" ] 
    ]

    services = sorted(dev.services, key=lambda s: s.hndStart)
    for s in services:
        sys.stdout.write('.')
        sys.stdout.flush()

        if s.hndStart == s.hndEnd:
            continue

        tdata.append([ "%04x -> %04x" % ( s.hndStart, s.hndEnd ), get_svc_desc(s), "", "" ])

        chars = s.getCharacteristics()
        for i, c in enumerate(chars):
            props = c.propertiesToString()
            h     = c.getHandle()
            
            # INDICATE makes the read operation hang
            if 'READ' in props and 'INDICATE' not in props:
                try:
                    val = c.read()
                    if c.uuid == AssignedNumbers.device_name:
                        string = yellow( '\'' + val.decode('utf-8') + '\'' )
                    elif is_mostly_printable(val):
                        string = yellow( repr(val) )
                    else:
                        string = repr(val)

                except Exception as e:
                    string = red( str(e) )
            else:
                string = ''

            tdata.append([ "%04x" % h, get_char_desc(c), props, string ])

            while args.handles:
                h += 1
                if h > s.hndEnd or (i < len(chars) - 1 and h >= chars[i + 1].getHandle() - 1):
                    break

                try:
                    val = dev.readCharacteristic(h)
                except Exception as e:
                    val = red( str(e) )
                    break

                tdata.append([ '%04x' % h, gray('    --'), gray('--'), binascii.b2a_hex(val).decode('utf-8') ])

        tdata.append([ '', '', '', '' ])

    print "\n\n" + SingleTable(tdata).table

