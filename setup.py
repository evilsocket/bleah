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
from setuptools import setup, find_packages
import os

from bleah.version import VERSION

try:
  long_description = open( 'README.md', 'rt' ).read()
except:
  long_description = 'BLEAH - A BLE scanner for "smart" devices hacking.'

setup( name                 = 'bleah',
       version              = VERSION,
       description          = long_description,
       long_description     = long_description,
       author               = 'Simone Margaritelli',
       author_email         = 'evilsocket@protonmail.com',
       url                  = 'http://www.github.com/evilsocket/bleah',
       packages             = find_packages(), 
       include_package_data = True,
       package_data         = { 'bleah': ['./bleah/oui.dat'] },
       scripts              = [ 'bin/bleah' ],
       license              = 'GPL',
       zip_safe             = False,
       install_requires     = [ 'bluepy', 'terminaltables' ]
)
