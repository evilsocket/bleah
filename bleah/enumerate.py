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
import binascii
import os
import sys
import string
import struct
from terminaltables import SingleTable
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, AssignedNumbers, UUID

from bleah.scan import *
from bleah.swag import *

def assigned_numbers_add( uuid, name ):
    u = UUID(uuid,name)
    AssignedNumbers.idMap[u] = u

assigned_numbers_add( "d0611e78-bbb4-4591-a5f8-487910ae4366", 'Apple Continuity Service' )
assigned_numbers_add( "7905f431-b5ce-4e99-a40f-4b1e122d00d0", 'Apple Notification Center Service' )
assigned_numbers_add( "69d1d8f3-45e1-49a8-9821-9bbdfdaad9d9", 'Control Point' )
assigned_numbers_add( "9fbf120d-6301-42d9-8c58-25e699a21dbd", 'Notification Source' )
assigned_numbers_add( "22eac6e9-24d6-4bb5-be44-b36ace7c7bfb", 'Data Source' )
assigned_numbers_add( "89d3502b-0f36-433a-8ef4-c502ad55f8dc", 'Apple Media Service' )
assigned_numbers_add( "9b3c81d8-57b1-4a8a-b8df-0e56f7ca51c2", 'Remote Command' )
assigned_numbers_add( "2f7cabce-808d-411f-9a0c-bb92ba96c102", 'Entity Update' )
assigned_numbers_add( "c6b2f38c-23ab-46d8-a6ab-a3a870bbd5d7", 'Entity Attribute' )

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

# org.bluetooth.characteristic.gap.appearance
def deserialize_appearance( raw ):
    apps = {
        0: "Unknown",
        64: "Generic Phone",
        128: "Generic Computer",
        192: "Generic Watch",
        193: "Watch: Sports Watch",
        256: "Generic Clock",
        320: "Generic Display",
        384: "Generic Remote Control",
        448: "Generic Eye-glasses",
        512: "Generic Tag",
        576: "Generic Keyring",
        640: "Generic Media Player",
        704: "Generic Barcode Scanner",
        768: "Generic Thermometer",
        769: "Thermometer: Ear",
        832: "Generic Heart rate Sensor",
        833: "Heart Rate Sensor: Heart Rate Belt",
        896: "Generic Blood Pressure",
        897: "Blood Pressure: Arm",
        898: "Blood Pressure: Wrist",
        960: "Human Interface Device (HID)",
        961: "Keyboard",
        962: "Mouse",
        963: "Joystick",
        964: "Gamepad",
        965: "Digitizer Tablet",
        966: "Card Reader",
        967: "Digital Pen",
        968: "Barcode Scanner",
        1024: "Generic Glucose Meter",
        1088: "Generic: Running Walking Sensor",
        1089: "Running Walking Sensor: In-Shoe",
        1090: "Running Walking Sensor: On-Shoe",
        1091: "Running Walking Sensor: On-Hip",
        1152: "Generic: Cycling",
        1153: "Cycling: Cycling Computer",
        1154: "Cycling: Speed Sensor",
        1155: "Cycling: Cadence Sensor",
        1156: "Cycling: Power Sensor",
        1157: "Cycling: Speed and Cadence Sensor",
        1216: "Generic Control Device",
        1217: "Switch",
        1218: "Multi-switch",
        1219: "Button",
        1220: "Slider",
        1221: "Rotary",
        1222: "Touch-panel",
        1280: "Generic Network Device",
        1281: "Access Point",
        1344: "Generic Sensor",
        1345: "Motion Sensor",
        1346: "Air Quality Sensor",
        1347: "Temperature Sensor",
        1348: "Humidity Sensor",
        1349: "Leak Sensor",
        1350: "Smoke Sensor",
        1351: "Occupancy Sensor",
        1352: "Contact Sensor",
        1353: "Carbon Monoxide Sensor",
        1354: "Carbon Dioxide Sensor",
        1355: "Ambient Light Sensor",
        1356: "Energy Sensor",
        1357: "Color Light Sensor",
        1358: "Rain Sensor",
        1359: "Fire Sensor",
        1360: "Wind Sensor",
        1361: "Proximity Sensor",
        1362: "Multi-Sensor",
        1408: "Generic Light Fixtures",
        1409: "Wall Light",
        1410: "Ceiling Light",
        1411: "Floor Light",
        1412: "Cabinet Light",
        1413: "Desk Light",
        1414: "Troffer Light",
        1415: "Pendant Light",
        1416: "In-ground Light",
        1417: "Flood Light",
        1418: "Underwater Light",
        1419: "Bollard with Light",
        1420: "Pathway Light",
        1421: "Garden Light",
        1422: "Pole-top Light",
        1423: "Spotlight",
        1424: "Linear Light",
        1425: "Street Light",
        1426: "Shelves Light",
        1427: "High-bay / Low-bay Light",
        1428: "Emergency Exit Light",
        1472: "Generic Fan",
        1473: "Ceiling Fan",
        1474: "Axial Fan",
        1475: "Exhaust Fan",
        1476: "Pedestal Fan",
        1477: "Desk Fan",
        1478: "Wall Fan",
        1536: "Generic HVAC",
        1537: "Thermostat",
        1600: "Generic Air Conditioning",
        1664: "Generic Humidifier",
        1728: "Generic Heating",
        1729: "Radiator",
        1730: "Boiler",
        1731: "Heat Pump",
        1732: "Infrared Heater",
        1733: "Radiant Panel Heater",
        1734: "Fan Heater",
        1735: "Air Curtain",
        1792: "Generic Access Control",
        1793: "Access Door",
        1794: "Garage Door",
        1795: "Emergency Exit Door",
        1796: "Access Lock",
        1797: "Elevator",
        1798: "Window",
        1799: "Entrance Gate",
        1856: "Generic Motorized Device",
        1857: "Motorized Gate",
        1858: "Awning",
        1859: "Blinds or Shades",
        1860: "Curtains",
        1861: "Screen",
        1920: "Generic Power Device",
        1921: "Power Outlet",
        1922: "Power Strip",
        1923: "Plug",
        1924: "Power Supply",
        1925: "LED Driver",
        1926: "Fluorescent Lamp Gear",
        1927: "HID Lamp Gear",
        1984: "Generic Light Source",
        1985: "Incandescent Light Bulb",
        1986: "LED Bulb",
        1987: "HID Lamp",
        1988: "Fluorescent Lamp",
        1989: "LED Array",
        1990: "Multi-Color LED Array",
        3136: "Generic: Pulse Oximeter",
        3137: "Fingertip",
        3138: "Wrist Worn",
        3200: "Generic: Weight Scale",
        3264: "Generic",
        3265: "Powered Wheelchair",
        3266: "Mobility Scooter",
        3328: "Generic",
        5184: "Generic: Outdoor Sports Activity",
        5185: "Location Display Device",
        5186: "Location and Navigation Display Device",
        5187: "Location Pod",
        5188: "Location and Navigation Pod"
    }

    try:
        app = struct.unpack( 'h', raw )[0]
        s = green( apps[app] )
    except:
        s = repr(raw)

    return s

# org.bluetooth.characteristic.gap.peripheral_preferred_connection_parameters
def deserialize_connection_params( raw ):
    if len(raw) == 8:
        ( min_con_int, max_con_int, slave_lat, con_tim_mul ) = struct.unpack( 'hhhh', raw ) 
        s  = green('Connection Interval') + ": %d -> %d\n" % ( min_con_int, max_con_int )
        s += green('Slave Latency') + ": %d\n" % slave_lat
        s += green('Connection Supervision Timeout Multiplier') + ": %d" % con_tim_mul
    else:
        s = repr(raw)
    
    return s

# org.bluetooth.characteristic.pnp_id
def deserialize_pnp_id( raw ):
    try:
        ( vendor_id_src, vendor_id, prod_id, prod_ver ) = struct.unpack( '<Bhhh', raw )

        if vendor_id_src == 1:
            src = ' ( Bluetooth SIG assigned Company Identifier )'
        elif vendor_id_src == 2:
            src = ' ( USB Implementer’s Forum assigned Vendor ID value )'
        else:
            src = ''

        s  = green('Vendor ID') + ": 0x%04x%s\n" % ( vendor_id, src )
        s += green('Product ID') + ": 0x%04x\n" % prod_id
        s += green('Product Version') + ": 0x%04x\n" % prod_ver
        
    except:
        s = repr(raw)

    return s

# org.bluetooth.characteristic.gap.peripheral_privacy_flag
def deserialize_peripheral_privacy_flag( raw ):
    try:
        b = ord(raw[0])
        if b == 0x00:
            s = green('Privacy Disabled')
        else:
            s = red('Privacy Enabled')

    except:
        s = repr(raw)

    return s



def deserialize_char( char, props ):
    # INDICATE makes the read operation hang
    if 'READ' in props and 'INDICATE' not in props:
        try:
            raw = char.read()

            if char.uuid == AssignedNumbers.peripheral_preferred_connection_parameters:
                string = deserialize_connection_params(raw)

            elif char.uuid == AssignedNumbers.appearance:
                string = deserialize_appearance(raw)

            elif char.uuid == AssignedNumbers.pnp_id:
                string = deserialize_pnp_id(raw)

            elif char.uuid == AssignedNumbers.peripheral_privacy_flag:
                string = deserialize_peripheral_privacy_flag(raw)

            elif is_mostly_printable(raw):
                try:
                    string = yellow( repr( raw.decode('utf-8') ) )
                except:
                    string = yellow( repr( raw ) )

            else:
                string = repr(raw)

        except Exception as e:
            string = red( str(e) )
    else:
        string = ''

    return string


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
        for i, char in enumerate(chars):
            desc  = get_char_desc(char)
            props = char.propertiesToString().replace( 'WRITE', bold('WRITE') )
            hnd   = char.getHandle()
            value = deserialize_char( char, props )

            tdata.append([ "%04x" % hnd, desc, props, value ])

            """
            while args.handles:
                hnd += 1
                if hnd > s.hndEnd or (i < len(chars) - 1 and hnd >= chars[i + 1].getHandle() - 1):
                    break

                try:
                    val = dev.readCharacteristic(hnd)
                except Exception as e:
                    val = red( str(e) )
                    break

                tdata.append([ '%04x' % hnd, gray('    --'), gray('--'), binascii.b2a_hex(val).decode('utf-8') ])
            """

        tdata.append([ '', '', '', '' ])

    print "\n\n" + SingleTable(tdata).table
