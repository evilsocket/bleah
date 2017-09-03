#coding:utf8
import os

FILEPATH = os.path.realpath( os.path.join( os.path.dirname( os.path.realpath(__file__) ), 'oui.dat' ) )
VENDORS = {}

def load():
    # print "@ Preloading vendors ..."
    with open( FILEPATH, 'rt' ) as fp:
        for line in fp:
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            
            oui, name = line.split(' ', 1)
            VENDORS[oui] = name

def find(addr):
    addr = ''.join( addr.upper().split(':')[:3] )
    if addr in VENDORS:
        return VENDORS[addr]
    return None
