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
import os

FILEPATH = os.path.realpath( os.path.join( os.path.dirname( os.path.realpath(__file__) ), 'oui.dat' ) )
VENDORS = {}

def load():
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
