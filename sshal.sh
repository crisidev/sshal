#!/bin/bash

#  SSH Utility Launcher (Aka sshal) 2011/08/31 11:50:12  bigo Exp $
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#  The original idea of function dsshsel was from
#  Matteo Sgalaberni (Ovus.it) <sgala@sgala.com>
#  and was called net_selektor. Many thanks to him! ;)
#
# The configuration of this script it's INLINE, below some specification
# Each lines must begin with "#> " and the other fields are:
# Name ; Host Description ; Command to execute for connect 
# Example:
# bau ; bau's home server ; ssh bigo@bau.bau.com
#
# There are NOT validation check on configuration. don't break the law.

FILECONF="$HOME/.sshal.conf"
if [ ! -e $FILECONF ]; then
    echo "No ~/.sshal.conf found"
    exit 1
fi

function dsshsel {

        BACKTITLE="ssh launcher"
        TITLE="trusted hosts"

        IFS=$'\n'
        for HOST in `grep "^#>" $FILECONF`; do
                IFS=';'
                set -- $HOST
                NAME=${1/"\#> "/}
                STRING=$STRING"\"$NAME\"  \"$2\" "
        done
        IFS=""

        TMPFILE=${TMPDIR:-/tmp}/sshal.$$
        touch $TMPFILE
		DIALOG="dialog --backtitle \"$BACKTITLE\" --title \"$TITLE\" --menu \"\n where do you want to ssh yourself? ;)\" 20 80 10 $STRING 2> $TMPFILE"
        eval $DIALOG

        CHOOSE=`cat $TMPFILE`
        rm $TMPFILE

        if [ -z $CHOOSE ]; then
                echo "here ;)"
                exit
        fi

        clear
        echo "choice: $CHOOSE"

        TMPCOMMAND=`cat $FILECONF |grep $CHOOSE`
        COMMAND=`echo ${TMPCOMMAND##*;}`
        echo -e "Executing command ... $COMMAND\n"
        eval $COMMAND
}

if [ "$1" = "" ]; then
		dsshsel
elif [ "$1" = "-a" ]; then
    IFS=$'\n'
    for HOST in `grep "^#>" $FILECONF`; do
        IFS=';'
        set -- $HOST
        NAME=`echo ${1/"\#> "/} | sed 's/\#\>//g'`
        STRING=$STRING$NAME
    done
    IFS=""
    echo $STRING
else
    CHOOSE=$1
    IFS=$'\n'
        for HOST in `grep "^#>" $FILECONF`; do
                CMD=$HOST
                IFS=';'
                set -- $HOST
                IFS=""
                NAME=`echo ${1/"\#> "/#} | awk '{print $2}'`
                if [ $NAME = $CHOOSE ]; then
                    TMPCOMMAND=`echo ${CMD}`
                fi
        done

    clear
	COMMAND=`echo ${TMPCOMMAND##*;}`
	echo -e "Executing command ... $COMMAND\n"
	eval $COMMAND

fi
