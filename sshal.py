#!/usr/bin/env python

import os
import shlex
import subprocess
import sys
import yaml
from blessings import Terminal
import dialog

t = Terminal()

def writer(message):
        sys.stdout.write(message)

def usage(prog_name):
    writer('Usage:\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal}'.format(t=t) + '\t\t\t\t- open dialog box with host selection\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal} hostname'.format(t=t) + '\t\t- connect to host via ssh\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal} hostlist'.format(t=t) + '\t\t- return the host list (usefull for zsh completion\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal} pull hostname src dst'.format(t=t) + '\t- copy file from hostname src into dst\n')
    writer('{t.yellow}\t* {t.cyan}'.format(t=t) + prog_name + ' {t.normal} push hostname src dst'.format(t=t) + '\t- copy file from src to hostname dst\n')

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
        return 1                        # code i

def get_host_from_dialog(d, hosts, title):
    hostlist = []
    for host in hosts.keys():
        hostlist.append((host, hosts[host]['comment']))
    while 1:
        (code, tag) = d.menu(title, width=60, choices=hostlist)
        if handle_dialog_exit_code(d, code):
            break
    return tag

def host_has_parent(host_configuration):
    if 'parentuser' in host_configuration.keys() and 'parenthost' in host_configuration.keys():
        return True
    else:
        return False

def launch_ssh_dialog(configuration):
    d = dialog.Dialog(dialog="dialog")
    d.add_persistent_args(["--backtitle", configuration['dialog']['backtitle']])
    host = get_host_from_dialog(d, configuration['hosts'], configuration['dialog']['title'])
    if host_has_parent(configuration['hosts'][host]):
        subprocess.call('clear && ssh ' + configuration['hosts'][host]['parentuser'] + '@' + configuration['hosts'][host]['parenthost'] + ' -t ssh ' + configuration['hosts'][host]['user'] + '@' + configuration['hosts'][host]['host'], shell=True)
    else:
        subprocess.call('clear && ssh ' + configuration['hosts'][host]['user'] + '@' + configuration['hosts'][host]['host'], shell=True)

def launch_ssh_host(configuration, host):
    if host in configuration['hosts'].keys():
        if host_has_parent(configuration['hosts'][host]):
            subprocess.call('clear && ssh ' + configuration['hosts'][host]['parentuser'] + '@' + configuration['hosts'][host]['parenthost'] + ' -t ssh ' + configuration['hosts'][host]['user'] + '@' + configuration['hosts'][host]['host'], shell=True)
        else:
            subprocess.call('clear && ssh ' + configuration['hosts'][host]['user'] + '@' + configuration['hosts'][host]['host'], shell=True)

def return_host_list(host_configuration):
    hostlist = str()
    for host in host_configuration.keys():
        hostlist = hostlist + ' ' + host
    return hostlist

def push_file_to_host(args):
    pass

def pull_file_to_host(args):
    pass

def exec_only_command(args):
    pass

def main():
    try:
        # Configuration loading
        configurationfile = os.path.expanduser('~/.sshal.yaml')
        configuration = yaml.load(open(configurationfile))

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
