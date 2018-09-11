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
import sys
import json

from terminaltables import SingleTable
from bluepy.btle import BTLEException, Scanner, ScanEntry, DefaultDelegate

import bleah.vendors as vendors
from bleah.swag import *
from bleah.enumerate import *

class SmarterScanner(Scanner):
    def __init__(self,mac=None,iface=0, args=None):
        Scanner.__init__(self,iface)
        self.mac = mac
        self.enumerations = {}    # Enumerated device characteristics
        self.sr = ScanReceiver(args)
        self.withDelegate(self.sr)

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

    def enumerateDeviceProperties(self, dev, args):
        """Enumerate the properties of a specific device

        @dev: a connected Peripheral class
        @args: Command line arguments
        """

        ens = enumerate_device_properties( dev, args )
        display_enumerated_device_properties(ens)
        self.enumerations[dev.addr.lower()] = ens

    def storeJson(self, filename):
        """ store scan results as json file

        @filename: name of the json file to write
        """

        def deflt(foo):
            print("Broken string " + str(foo))
            return "???"


        data = self.sr.devdata.copy()

        for akey in data.keys():
            if akey in self.enumerations:
                data[akey]["enumerations"] = self.enumerations[akey]

        with open(filename, "wt") as fh:
            json.dump(data, fh, default = deflt, indent=4)


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
        self.devdata = {}

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
            bits.append( 'BR/EDR Not Supported' )

        if self._isBitSet( flags, 3 ):
            bits.append( 'LE + BR/EDR Controller Mode' )

        if self._isBitSet( flags, 4 ):
            bits.append( 'LE + BR/EDR Host Mode' )

        return bits

    def getDevices(self):
        """ Returns all found device-addresses
        """

        return self.devdata.keys()

    def printShortTable(self, addr):
        """ Print the short overview table for the given device

        @addr: mac addr of the device to print
        """

        vendor = self.devdata[addr]["vendor"]
        vlabel = yellow( vendor + ' ' ) if vendor is not None else '?'
        clabel = green( u'\u2713' ) if self.devdata[addr]["connectable"] else red( u'\u2715' )
        dlabel = "(no data) " if not self.devdata[addr]["scanData"] else ""
        title  = " %s (%s dBm) %s" % ( bold(addr), self.devdata[addr]["rssi"], dlabel )

        tdata  = [
            [ 'Vendor', vlabel ],
            [ 'Allows Connections', clabel ],
            [ 'Address Type', self.devdata[addr]["addrType"]]
        ]

        for desc in self.devdata[addr]["descs"]:
            tdata.append([ desc, self.devdata[addr][desc] ])
        if "Short Local Name" in self.devdata[addr].keys():
            tdata.append([ "Short Local Name", yellow( self.devdata[addr]["Short Local Name"] ) ])
        if "Complete Local Name" in self.devdata[addr].keys():
            tdata.append([ "Complete Local Name", yellow( self.devdata[addr]["Complete Local Name"] ) ])

        tdata.append([ 'Flags', ', '.join(self.devdata[addr].get("flags",[])) ])

        table = SingleTable(tdata, title)
        table.inner_heading_row_border = False

        print(table.table + "\n")

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if not isNewDev:
            return
        elif self.opts.mac is not None and dev.addr != self.opts.mac:
            return
        elif dev.rssi < self.opts.sensitivity:
            return

        if not dev.addr in self.devdata:
            self.devdata[dev.addr] = {}

        self.devdata[dev.addr]["vendor"] = vendors.find(dev.addr)
        self.devdata[dev.addr]["connectable"] = dev.connectable
        self.devdata[dev.addr]["scanData"] =  dev.getScanData()
        self.devdata[dev.addr]["addr"] = dev.addr
        self.devdata[dev.addr]["rssi"] = dev.rssi
        self.devdata[dev.addr]["addrType"] = dev.addrType


        self.devdata[dev.addr]["descs"] = []
        for ( tag, desc, val ) in dev.getScanData():
            if desc == 'Flags':
                self.devdata[dev.addr]["flags"] = self._parseFlags(val)

            # short local name or complete local name
            elif tag in [8, 9]:
                try:
                    self.devdata[dev.addr][desc] = val.decode('utf-8')
                except UnicodeEncodeError:
                    self.devdata[dev.addr][desc] = repr(val)
            else:
                self.devdata[dev.addr][desc] = repr(val)
                self.devdata[dev.addr]["descs"].append(desc)

        self.printShortTable(dev.addr)





class Bleah():

    def __init__(self, args):
        """ Bleah main scanner class

        @args: argparse arguments to configure the scanner
        """

        self.args = args
        self.scanner = None

        self.start_scan()

        if args.enumerate or args.uuid is not None or args.handle is not None:
            for d in self.devices:
                if self.skip_device(d):
                    continue

                warn = ""
                if not d.connectable:
                    warn = yellow("(forcing connection, this could take a while) ")

                print("@ Connecting to %s %s..." % ( bold( d.addr ), warn )),
                sys.stdout.flush()

                try:
                    dev = Peripheral(d,d.addrType)
                    if args.mtu:
                      dev.setMTU(args.mtu)

                    print(green('connected.'))

                    if args.uuid or args.handle:
                        print()
                        do_write_ops( dev, args )
                        print()

                    if args.enumerate:
                        print("@ Enumerating all the things "),
                        self.scanner.enumerateDeviceProperties(dev, args)

                    dev.disconnect()
                    print()
                except Exception as e:
                    print("\n! %s" % red( str(e) ))
                    # just in case
                    try:
                        dev.disconnect()
                    except:
                        pass
            if args.json_log:
                self.scanner.storeJson(args.json_log)

    def skip_device(self, dev ):
        """ Checks if a device should be skipped for detailed scanning """

	if self.args.mac is not None and dev.addr != self.args.mac:
            return True
        elif not dev.connectable and self.args.force is False:
                return True
        else:
            return False


    def start_scan(self):
        """ Start the scan for new devices """

        vendors.load()

        self.scanner = SmarterScanner(self.args.mac,self.args.hci, self.args)

        if self.args.timeout == 0:
            print("@ Continuous scanning [%d dBm of sensitivity] ...\n" % self.args.sensitivity)
        else:
            print("@ Scanning for %ds [%d dBm of sensitivity] ...\n" % ( self.args.timeout, self.args.sensitivity ))

        self.devices = self.scanner.scan(self.args.timeout)
