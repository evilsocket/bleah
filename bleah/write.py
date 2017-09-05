#coding:utf8
import sys
from bluepy.btle import Characteristic

from bleah.swag import *

def do_write_ops( dev, args ):
    char = None
    print "@ Searching for characteristic %s ..." % ( bold(args.uuid) ),
    sys.stdout.flush()

    for s in dev.services:
        if char is not None:
            break
        elif s.hndStart == s.hndEnd:
            continue
    
        for i, c in enumerate( s.getCharacteristics() ):
            if str(c.uuid) == args.uuid:
                char = c
                break

    if char is not None:
        if "WRITE" in char.propertiesToString():
            print green("found")
            print "@ Sending %d bytes ..." % len(args.data),
            sys.stdout.flush()

            try:
                char.write( args.data )
                print green('done')
            except Exception as e:
                print red( str(e) )

        else:
            print red('not writable')

    else:
        print red( bold("NOT FOUND") )
