#coding:utf8
from terminaltables import SingleTable
from bluepy.btle import Scanner, DefaultDelegate

import bleah.vendors as vendors
from bleah.swag import *

class ScanReceiver(DefaultDelegate):
    def __init__(self, opts):
        DefaultDelegate.__init__(self)
        self.opts = opts

    def _isBitSet( self, byteval, idx ):
        return ((byteval&(1<<idx))!=0);

    # http://www.argenox.com/a-ble-advertising-primer/
    def _parseFlags( self, flags ):
        bits  = []
        flags = int( flags, 16 )

        if self._isBitSet( flags, 0 ):
            bits.append( 'LE Limited Discoverable' )

        if self._isBitSet( flags, 1 ):
            bits.append( 'LE General Discoverable' )

        if self._isBitSet( flags, 2 ):
            bits.append( 'BR/EDR' )

        if self._isBitSet( flags, 3 ):
            bits.append( 'LE + BR/EDR Controller Mode' )

        if self._isBitSet( flags, 4 ):
            bits.append( 'LE + BR/EDR Host Mode' )

        return ', '.join(bits)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if not isNewDev:
            return 
        elif self.opts.bssid != '' and dev.addr != self.opts.bssid:
            return 
        elif dev.rssi < self.opts.sensitivity:
            return

        vendor = vendors.find(dev.addr)
        vlabel = yellow( vendor + ' ' ) if vendor is not None else '?'
        clabel = green( u'\u2713' ) if dev.connectable else red( u'\u2715' )
        dlabel = "(no data) " if not dev.scanData else ""
        title  = " %s (%s dBm) %s" % ( bold(dev.addr), dev.rssi, dlabel )
        tdata  = [
            [ 'Vendor', vlabel ],
            [ 'Allows Connections', clabel ],
        ]

        for ( sdid, desc, val ) in dev.getScanData():
            if desc == 'Flags':
                tdata.append([ 'Flags', self._parseFlags(val) ])
            elif sdid in [8, 9]:
                tdata.append([ desc, yellow(val) ])
            else:
                tdata.append([ desc, repr(val) ])


        table = SingleTable(tdata, title)
        table.inner_heading_row_border = False

        print table.table + "\n"

def start_scan(args):
    vendors.load()
    scanner = Scanner(args.hci).withDelegate(ScanReceiver(args))

    if args.timeout == 0:
        print "@ Continuous scanning [%d dBm of sensitivity] ...\n" % args.sensitivity
    else:
        print "@ Scanning for %ds [%d dBm of sensitivity] ...\n" % ( args.timeout, args.sensitivity )

    return scanner.scan(args.timeout)

