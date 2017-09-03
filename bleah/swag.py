#coding:utf8
import os
from bleah.version import VERSION

def effect(s,c,close=True):
    if os.getenv('c', '1') == 0:
        return s
    else:
        return "\033[%dm%s%s" % ( c, s, "\33[0m" if close else "" )

def red(s,close=True):
    return effect( s, 31, close )

def green(s,close=True):
    return effect( s, 32, close )

def yellow(s,close=True):
    return effect( s, 33, close )

def blue(s,close=True):
    return effect( s, 34, close )

def gray(s,close=True):
    return effect( s, 90, close )

def bold(s,close=True):
    return effect( s, 1, close )

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


