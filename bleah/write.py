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
import sys
from bluepy.btle import Characteristic

from bleah.swag import *

def do_write_ops( dev, args ):
    char = None
    lookingfor = "uuid(%s)" % (args.uuid)
    if args.handle:
        lookingfor="handle(%d)" % (args.handle)
    print "@ Searching for characteristic %s ..." % ( bold(lookingfor) ),
    sys.stdout.flush()

    for s in dev.services:
        if char is not None:
            break
        elif s.hndStart == s.hndEnd:
            continue
    
        for i, c in enumerate( s.getCharacteristics() ):
            if args.uuid:
                if str(c.uuid) == args.uuid:
                    char = c
                    break
            if args.handle:
                if c.getHandle() == args.handle:
                    char =c
                    break

    if char is not None:
        if "WRITE" in char.propertiesToString():
            print green("found")
            print "@ Sending %d bytes ..." % len(args.data),
            sys.stdout.flush()

            wwrflag=False

            if "NO RESPONSE" in char.propertiesToString():
                wwrflag=True

            try:
                char.write( args.data, wwrflag )
                print green('done')
            except Exception as e:
                print red( str(e) )

        else:
            print red('not writable')

    else:
        print red( bold("NOT FOUND") )
