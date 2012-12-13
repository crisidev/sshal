#!/usr/bin/env python

#  SSH Utility Launcher (Aka sshal) 2012/12/13 15:36 bigo Exp $
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

# There are NOT validation check on configuration. don't break the law.

# Imports
import os
import shlex
import subprocess
import sys
import yaml
import dialog
from blessings import Terminal

# Define a terminal for pretty print
t = Terminal()

# utility function to write to console
def writer(message):
        sys.stdout.write(message)

# usage
def usage(prog_name):
    writer('Usage:\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal}'.format(t=t) + '\t\t\t\t- open dialog box with host selection\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal} hostname'.format(t=t) + '\t\t- connect to host via ssh\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal} hostlist'.format(t=t) + '\t\t- return the host list (usefull for zsh completion\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal} pull hostname src dst'.format(t=t) + '\t- copy file from hostname src into dst\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal} push hostname src dst'.format(t=t) + '\t- copy file from src to hostname dst\n')

# handler for dialog exit code if ESC or CANC are pressed
def handle_dialog_exit_code(d, code):
    # d is supposed to be a Dialog instance
    if code in (d.DIALOG_CANCEL, d.DIALOG_ESC):
        if code == d.DIALOG_CANCEL:
            msg = "You chose cancel in the last dialog box. Do you want to " \
                  "exit SSHAL?"
        else:
            msg = "You pressed ESC in the last dialog box. Do you want to " \
                  "exit SSHAL?"
        # "No" or "ESC" will bring the user back to the demo.
        # DIALOG_ERROR is propagated as an exception and caught in main().
        # So we only need to handle OK here.
        if d.yesno(msg) == d.DIALOG_OK:
            subprocess.call('clear', shell=True)
            sys.exit(0)
        return 0
    else:
        return 1

# using dialog's menu mode, get the user choice
def get_host_from_dialog(hosts, dialog_configuration):
    d = dialog.Dialog(dialog="dialog")
    d.add_persistent_args(["--backtitle", dialog_configuration['backtitle']])
    hostlist = []
    # for every host append a tuple to the list
    for host in hosts.keys():
        hostlist.append((host, hosts[host]['comment']))
    # make the dialogo and save response
    while 1:
        (code, tag) = d.menu(dialog_configuration['title'], width=60, choices=hostlist)
        if handle_dialog_exit_code(d, code):
            break
    # return user choice
    return tag

# check if host in configuration has parents
# a normal host (with public ip) is a frame of yaml:
# host1:
#     comment: "host1 comment"
#     user: root
#     host: host1.mydomain.ext
# this will result in ssh root@host1.mydomain.ext

# if you have to connect to a non public host you may have to use an other public host in his network
# the resulting yaml will be:
# host1:
#     comment: "host1 comment"
#     user: root
#     host: host1.mydomain.ext
#     parentuser: root
#     parenthost: parenthost1.mydomain.exit
# this will result in ssh root@parenthost1.mydomain.ext -t ssh root@host1.mydomain.ext
def host_has_parent(host_configuration):
    if 'parentuser' in host_configuration.keys() and 'parenthost' in host_configuration.keys():
        return True
    else:
        return False

# launch ssh session to a host chosen by dialog
def launch_ssh_dialog(configuration):
    host = get_host_from_dialog(configuration['hosts'], configuration['dialog'])
    if host_has_parent(configuration['hosts'][host]):
        subprocess.call('clear && ssh ' + configuration['hosts'][host]['parentuser'] + '@' + configuration['hosts'][host]['parenthost'] + ' -t ssh ' + configuration['hosts'][host]['user'] + '@' + configuration['hosts'][host]['host'], shell=True)
    else:
        subprocess.call('clear && ssh ' + configuration['hosts'][host]['user'] + '@' + configuration['hosts'][host]['host'], shell=True)

# launch ssh session to a host chosen by command line
def launch_ssh_host(configuration, host):
    if host in configuration['hosts'].keys():
        if host_has_parent(configuration['hosts'][host]):
            subprocess.call('clear && ssh ' + configuration['hosts'][host]['parentuser'] + '@' + configuration['hosts'][host]['parenthost'] + ' -t ssh ' + configuration['hosts'][host]['user'] + '@' + configuration['hosts'][host]['host'], shell=True)
        else:
            subprocess.call('clear && ssh ' + configuration['hosts'][host]['user'] + '@' + configuration['hosts'][host]['host'], shell=True)

# utility function used by zsh completion
def return_host_list(host_configuration):
    hostlist = str()
    for host in host_configuration.keys():
        hostlist = hostlist + ' ' + host
    return hostlist

# copy file to host
# TODO: implement
def push_file_to_host(args):
    pass

# copy file from host
# TODO: implement
def pull_file_from_host(args):
    pass

# exec single command
# TODO: implement
def exec_only_command(args):
    pass

# teh main function
def main():
    try:
        # configuration loading
        configurationfile = os.path.expanduser('~/.sshal.yaml')
        configuration = yaml.load(open(configurationfile))

        # main configuration parameters switch
        if len(sys.argv) == 1:
            launch_ssh_dialog(configuration)
        else:
            if sys.argv[1] == 'help' or sys.argv[1] == 'usage':
                usage(sys.argv[0])
            elif sys.argv[1] == 'hostlist':
                print return_host_list(configuration['hosts'])
            elif sys.argv[1] == 'pull':
                pull_file_from_host(sys.argv)
            elif sys.argv[1] == 'push':
                push_file_to_host(sys.argv)
            elif sys.argv[1] == 'cmd':
                exec_only_command(sys.argv)
            else:
                launch_ssh_host(configuration, sys.argv[1])
        sys.exit(0)
    except Exception, e:
        print e
        sys.exit(1)

if __name__ == "__main__":
        main()

