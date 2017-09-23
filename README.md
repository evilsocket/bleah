# BLEAH 

A BLE scanner for "smart" devices hacking based on the `bluepy` library, dead easy to use because retarded devices should be dead easy to hack.

## How to Install

Install [bluepy following the instructions](https://github.com/IanHarvey/bluepy), then:

    cd bleah
    python setup.py build
    sudp python setup.py install

## Usage

From the `-h` help menu:

    usage: bleah [-h] [-i HCI] [-t TIMEOUT] [-s SENSITIVITY] [-b MAC] [-f] [-e]
                 [--handles] [-u UUID] [-d DATA] [-r DATAFILE]

    optional arguments:
      -h, --help            show this help message and exit
      -i HCI, --hci HCI     HCI device index.
      -t TIMEOUT, --timeout TIMEOUT
                            Scan delay, 0 for continuous scanning.
      -s SENSITIVITY, --sensitivity SENSITIVITY
                            dBm threshold.
      -b MAC, --mac MAC     Filter by device address.
      -f, --force           Try to connect even if the device doesn't allow to.
      -e, --enumerate       Connect to available devices and perform services
                            enumeration.
      --handles             Try to read every handle. WARNING: For some
                            devices this might cause the read operation to hang
                            ¯\_(ツ)_/¯
      -u UUID, --uuid UUID  Write data to this characteristic UUID (requires --mac
                            and --data).
      -d DATA, --data DATA  Data to be written.
      -r DATAFILE, --datafile DATAFILE
                            Read data to be written from this file.

**Examples**

Keep scanning for BTLE devices:

    sudo bleah -t0

Connect to a specific device and enumerate all the things:

    sudo bleah -b "aa:bb:cc:dd:ee:ff" -e

Write the bytes `hello world` to a specific characteristic of the device:

    sudo bleah -b "aa:bb:cc:dd:ee:ff" -u "c7d25540-31dd-11e2-81c1-0800200c9a66" -d "hello world"

## License

`bleah` is released under the GPL 3.0 license and it's copyleft of Simone 'evilsocket' Margaritelli
