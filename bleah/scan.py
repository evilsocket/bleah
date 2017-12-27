# This file is part of BLEAH.
#
# Copyleft 2017 Simone Margaritelli
# evilsocket@protonmail.com
# http://www.evilsocket.net
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 3 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
import time
import binascii

from terminaltables import SingleTable
from bluepy.btle import BTLEException, Scanner, ScanEntry, DefaultDelegate

import bleah.vendors as vendors
from bleah.swag import *

class SmarterScanner(Scanner):
    def __init__(self,mac=None,iface=0):
        Scanner.__init__(self,iface)
        self.mac = mac

    def _find_or_create( self, addr ):
        if addr in self.scanned:
            dev = self.scanned[addr]
        else:
            dev = ScanEntry(addr, self.iface)
            self.scanned[addr] = dev

        return dev

    def _decode_address( self, resp ):
        addr = binascii.b2a_hex(resp['addr'][0]).decode('utf-8')
        return ':'.join([addr[i:i+2] for i in range(0,12,2)])

    def process(self, timeout=10.0):
        if self._helper is None:
            raise BTLEException(BTLEException.INTERNAL_ERROR, "Helper not started (did you call start()?)")

        start = time.time()
        while True:
            if timeout:
                remain = start + timeout - time.time()
                if remain <= 0.0: 
                    break
            else:
                remain = None

            resp = self._waitResp(['scan', 'stat'], remain)
            if resp is None:
                break

            respType = resp['rsp'][0]

            if respType == 'stat':
                # if scan ended, restart it
                if resp['state'][0] == 'disc':
                    self._mgmtCmd("scan")

            elif respType == 'scan':
                # device found
                addr = self._decode_address(resp) 
                dev = self._find_or_create(addr)

                isNewData = dev._update(resp)

                if self.delegate is not None:
                    self.delegate.handleDiscovery(dev, (dev.updateCount <= 1), isNewData)

                if self.mac is not None and dev.addr == self.mac:
                    break

            else:
                raise BTLEException(BTLEException.INTERNAL_ERROR, "Unexpected response: " + respType)

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
        elif self.opts.mac is not None and dev.addr != self.opts.mac:
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
            [ 'Address Type', dev.addrType]
        ]

        for ( tag, desc, val ) in dev.getScanData():
            if desc == 'Flags':
                tdata.append([ 'Flags', self._parseFlags(val) ])

            # short local name or complete local name
            elif tag in [8, 9]:
                try:
                    tdata.append([ desc, yellow( val.decode('utf-8') ) ])
                except UnicodeEncodeError:
                    tdata.append([ desc, yellow( repr(val) ) ])
            else:
                tdata.append([ desc, repr(val) ])


        table = SingleTable(tdata, title)
        table.inner_heading_row_border = False

        print table.table + "\n"

def start_scan(args):
    vendors.load()
    scanner = SmarterScanner(args.mac,args.hci).withDelegate(ScanReceiver(args))

    if args.timeout == 0:
        print "@ Continuous scanning [%d dBm of sensitivity] ...\n" % args.sensitivity
    else:
        print "@ Scanning for %ds [%d dBm of sensitivity] ...\n" % ( args.timeout, args.sensitivity )

    return scanner.scan(args.timeout)

