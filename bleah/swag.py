#coding:utf8
import os
from bleah.version import VERSION

def effect(s,c):
    if os.getenv('c', '1') == 0:
        return s
    else:
        return "\033[%dm%s\33[0m" % ( c, s )

def red(s):
    return effect( s, 31 )

def green(s):
    return effect( s, 32 )

def yellow(s):
    return effect( s, 33 )

def blue(s):
    return effect( s, 34 )

def gray(s):
    return effect( s, 90 )

def bold(s):
    return effect( s, 1 )

def print_sexy_banner():
    banner = u"""
          .                                                      .
        .n                   .                 .                  n.
  .   .dP                  dP                   9b                 9b.    .
 4    qXb         .       dX    BLEAH v%s     Xb       .        dXp     t
dX.    9Xb      .dXb    __                         __    dXb.     dXP     .Xb
9XXb._       _.dXXXXb dXXXXbo.                 .odXXXXb dXXXXb._       _.dXXP
 9XXXXXXXXXXXXXXXXXXXVXXXXXXXXOo.           .oOXXXXXXXXVXXXXXXXXXXXXXXXXXXXP
  `9XXXXXXXXXXXXXXXXXXXXX'~   ~`OOO8b   d8OOO'~   ~`XXXXXXXXXXXXXXXXXXXXXP'
    `9XXXXXXXXXXXP' `9XX'    *     `98v8P'     *    `XXP' `9XXXXXXXXXXXP'
        ~~~~~~~       9X.          .db|db.          .XP       ~~~~~~~
                        )b.  .dbo.dP'`v'`9b.odb.  .dX(
                      ,dXXXXXXXXXXXb     dXXXXXXXXXXXb.
                     dXXXXXXXXXXXP'   .   `9XXXXXXXXXXXb
                    dXXXXXXXXXXXXb   d|b   dXXXXXXXXXXXXb
                    9XXb'   `XXXXXb.dX|Xb.dXXXXX'   `dXXP
                     `'      9XXXXXX(   )XXXXXXP      `'
                              XXXX X.`v'.X XXXX
                              XP^X'`b   d'`X^XX
                              X. 9  `   '  P )X
                              `b  `       '  d'
                               `             '"""

    print bold( blue( banner % VERSION ) )
    print "                " + blue("Made with ") + red(u"\u2764") + blue(" by Simone 'evilsocket' Margaritelli") 
    print "\n\n"


