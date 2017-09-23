# MrSz6
# 2017-09-20
# ParamikoExample.py
# Description: SSH to a list of endpoints and perform different management actions
# usage python paramikoExample.py -u MYUSERNAME -p MYPASSWORD -f HOST_LIST_FILE -m clearlogs||reboot -e y


# import required modules
import logging
import sys
import paramiko
import time
import argparse
import socket

# Configure basic logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


REMOTE_USERNAME = None  # Usename for remote system
REMOTE_PASSWORD = None  # Password of remote system
FILE_LIST = None  # file
COMMAND = None  # Command that will be sent
LABEL = None   # Generic label for command that will be added to logging
METHOD = None  # GLOBAL variable for setting the method
ELEVATE = False  # GLOBAL variable for inicating commands need to be run with SUDO


# Function: send_command
# Purpose: Take a hostname, user, pass and issues a  command
# Input: hostname, username, password. username and password are optional, if not supplied globals are used
# Output: boolean success/failure
def send_command_sudo(host, command, label, elevate, username=REMOTE_USERNAME, password=REMOTE_PASSWORD):
    logging.info('f: send_command beginning {} sequence for {}'.format(label, host))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, username=username, password=password)
    except :
        logging.info('f: send_command Connecting to {} failed'.format(host))
        logging.debug(e)
        return False

    logging.debug(command)

    try:

        shell = ssh.invoke_shell()
        shell.send(command)
        time.sleep(5)
        receive_buffer = shell.recv(1024)
        logging.debug(receive_buffer)

        if elevate:
            shell.send(password + "\n")
            time.sleep(5)
            receive_buffer += shell.recv(2048)
            logging.debug(receive_buffer)

        ssh.close()
    except socket.error as e:
        logging.debug(e)
        ssh.close()
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script takes a username password and list file containing IPs"
                                                 "for systems that you want to reboot")
    parser.add_argument('u', help='username')
    parser.add_argument('p', help='password')
    parser.add_argument('f', help='filepath to list containing IP addresses')
    parser.add_argument('m', help='select method: clearlogs, reboot')
    parser.add_argument('e', help='elevate priv i.e. sudo y/n')

    args = parser.parse_args()

    if args.u:
        REMOTE_USERNAME = args.u
    if args.p:
        REMOTE_PASSWORD = args.p
    if args.f:
        FILE_LIST = args.f
    if args.m:
        METHOD = args.m
    if args.e == 'y':
        ELEVATE = True

    with open(FILE_LIST, 'r') as file:
        hosts = file.read().splitlines()

    if METHOD == 'clearlogs':
        COMMAND = "sudo rm -f /var/log/*.gz \n"
        LABEL = 'clear syslogs'

    elif METHOD == 'reboot':
        COMMAND = "sudo shutdown -r 1\n"
        LABEL = 'reboot hosts'

    for host in hosts:
        status = send_command_sudo(host, COMMAND, LABEL, ELEVATE, REMOTE_USERNAME, REMOTE_PASSWORD)
        if status:
            logging.info('{} was {}.'.format(host,LABEL))
        else:
            logging.info('{} was NOT {}.'.format(host,LABEL))

    sys.exit()
