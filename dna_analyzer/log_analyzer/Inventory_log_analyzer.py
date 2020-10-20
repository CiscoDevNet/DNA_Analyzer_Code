#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to display features stats for a particular device

Usage: ./invoker.py --rca <rca_.tar.gz_file> --log <log_file> --ip <ip_address> --time <time_in_ms>
    --iprange <start_ip> <end_ip>
Author: gboddulu@cisco.com
<log_file>: Log file Location
<ip_address>:  IP Address of the device
<rca_.tar.gz_file>: RCA file location
<time_in_ms>: Time in ms. Shows features which took more time than this.
"""

import argparse
import glob
import os
import re
import socket
import struct
import tarfile
from datetime import datetime

inventory = {
    "start": "Continuing InventoryCollectorEngineXdeImpl.call",
    "end": "Done with collection",
    "complete": "Completed executing function",
    "error": "Exception executing function",
    "exception": "Exception Stack:",
    "previous": "Previous collection status",
    "post_collection": "addPostCollectionAuditLogs",
    "interim_status": "Interim status after execution of devicePackage"
}

LOG_PATH='./dna_analyzer_logs/'

def print_feature(feature_name, status, time, *argv):
    """
    Print the Features
    :param feature_name:
    :param status:
    :param time:
    :param argv:
    :return:
    """
    if len(argv) == 0:
        return ": " + feature_name + " " * (75 - len(feature_name)) + ": " + status + " : " + time + "ms"
    elif len(argv) == 1:
        return ": " + feature_name + " " * (75 - len(feature_name)) + ": " + status + " : " + time + "ms" \
               + " " * (6 - len(time)) + ": " + argv[0]
    elif len(argv) == 2:
        return ": " + feature_name + " " * (75 - len(feature_name)) + ": " + status + " : " + time + "ms" \
               + " " * (6 - len(time)) + ": " + argv[0] + " " + argv[1]


def find_ips(start, end):
    ipstruct = struct.Struct('>I')
    start, = ipstruct.unpack(socket.inet_aton(start))
    end, = ipstruct.unpack(socket.inet_aton(end))
    return [socket.inet_ntoa(ipstruct.pack(i)) for i in range(start, end + 1)]


def inventory_fn(params, ip_address, logs, flag):
    """
    Inventory Function
    :param params:
    :param ip_address:
    :param logs:
    :param flag:
    :return:
    """
    output = []
    if logs:
        for index, lines in enumerate(logs):
            if re.search(r'%s' % inventory["previous"], lines):
                if flag:
                    output = []
                status = re.findall(r'%s (\w*)' % inventory["previous"], lines)[0]
                output.append("=" * 160)
                output.append("\t\t\tPREVIOUS COLLECTION STATUS: " + status)

            if re.search(r'%s' % inventory["start"], lines):
                split = lines.split()
                output.append("\t\t\tINVENTORY COLLECTION STARTED at " + split[0] + " " + split[1] +
                              " for DEVICE IP: " + ip_address + "\n")

            if re.search(r'%s' % inventory["complete"], lines):
                func = re.findall(r"%s.*\[(.*?)\]" % inventory["complete"], lines)[0]
                in_time = re.findall(r"in time (\d+)", lines)[0]
                if params.time:
                    if int(in_time) >= int(params.time):
                        output.append(print_feature(func, "SUCCESS", in_time))
                else:
                    if int(in_time) >= 1000:
                        output.append(print_feature(func, "SUCCESS", in_time))

            if re.search(r'%s' % inventory["error"], lines):
                func = re.findall(r"%s.*\[(.*?)\]" % inventory["error"], lines)[0]
                in_time = re.findall(r"in time (\d+)", lines)[0]
                next_line = logs[(index + 1) % len(logs)]
                val = re.findall(r'%s (.*)' % inventory["exception"], next_line)
                if val:
                    value = val[0].split(" ", 1)[0]
                    if re.search(r'<message>(.*)</message>', val[0]):
                        msg = re.findall(r'<message>(.*)</message>', val[0])
                        output.append(print_feature(func, "FAILURE", in_time, value, msg[0]))
                    elif re.search(r'<message>(.*)', val[0]):
                        msg = re.findall(r'<message>(.*)', val[0])
                        output.append(print_feature(func, "FAILURE", in_time, value, msg[0]))
                    else:
                        output.append(print_feature(func, "FAILURE", in_time, val[0]))

                else:
                    output.append(print_feature(func, "FAILURE", in_time))

            if re.search(r'%s' % inventory["interim_status"], lines):
                val = re.findall(r'%s (\w*)' % inventory["interim_status"], lines)[0]
                output.append('\n\t\t\t' + inventory["interim_status"] + ": " + val)

            if re.search(r'%s' % inventory["end"], lines):
                split = lines.split()
                val = re.findall(r'%s\. (.*)deviceId' % inventory["end"], lines)[0]
                output.append("\t\t\tDONE WITH COLLECTION at " + split[0] + " " + split[1]
                              + " for DEVICE IP: " + ip_address)
                output.append("\t\t\t" + val.upper() + "for DEVICE IP: " + ip_address)

            if re.search(r'%s' % inventory["post_collection"], lines):
                current_status = re.findall(r'<general code="(\w*)"/>', lines)[0]
                # failed_features = re.findall(r'<failed_features names="(.*)" code', lines)[0]
                output.append("\t\t\tCollection status " + "for device ip: " + ip_address + " is " + current_status)
                # output.append("\t\t\tFAILED FEATURES = " + failed_features)
                # top_cause = re.findall(r'<topCause code=(.*)/>', lines)[0]
                # output.append("\t\t\tTopCause = " + top_cause)
                output.append("=" * 160)
    else:
        output.append("INVENTORY COLLECTION of Device IP: " + ip_address + " is NOT AVAILABLE!!")

    file = open(inv_log_file, "a+")
    for item in output:
        file.write("%s\n" % item)
        print(item)
    file.close()

def read_ip_logs(params, ip_address, log_files, flag):
    """
    To get the logs for that particular ip_address
    :param params:
    :param ip_address:
    :param log_files:
    :param flag:
    :return:
    """
    logs = []
    for logfile in log_files:
        with open("%s" % logfile, "r") as file:
            lines = file.readlines()
            device_id = None
            for line in lines:
                if not device_id and re.search(r'%s' % inventory["start"], line) and \
                        re.search(r'\s%s\s' % ip_address, line):
                    device_id = re.findall(r"deviceId: (\d+)", line)[0]
                    break

            for line in lines:
                if device_id and re.search(r'%s' % device_id, line):
                    logs.append(line)

                elif device_id and re.search(r'%s' % inventory["exception"], line):
                    logs.append(line)
    inventory_fn(params, ip_address, logs, flag)


timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
inv_log_file = LOG_PATH+"Inventory-output_" + timestamp + ".log"




def get_ip_address(params, log_files):
    """
    To get the ip_address of all devices
    :param params:
    :param log_files:
    :return:
    """
    ip_of_device = []
    for logfile in log_files:
        with open("%s" % logfile, "r") as file:
            lines = file.readlines()
            for line in lines:
                if re.search(r'%s' % inventory["start"], line):
                    val = re.findall(r'ManagementIP: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)[0]
                    if val not in ip_of_device:
                        ip_of_device.append(val)
    for ip_address in ip_of_device:
        flag = True
        read_ip_logs(params, ip_address, log_files, flag)
        print("*" * 175)
    file.close()


def start_fn(params):
    """
    Start Method
    :param params:
    :return:
    """
    log_files = []
    if params.rca:
        tar = tarfile.open('%s' % params.rca, 'r:gz')
        tar.extractall()
        base_name = os.path.basename(params.rca)
        folder_name = os.path.splitext(os.path.splitext(base_name)[0])[0]

        log_path = 'data/rca/' + folder_name \
                   + '/docker_logs_k8s_apic-em-inventory-manager-service*.log'

        log_files = glob.glob(log_path)
        tar.close()

    elif params.log:
        log_files = sorted(glob.glob(params.log))

    if params.ip:
        ip_address = params.ip
        flag = False
        read_ip_logs(params, ip_address, log_files, flag)

    elif params.iprange:
        flag = True
        ip1 = params.iprange[0]
        ip2 = params.iprange[1]
        print("All IP in Range: " + str(find_ips(ip1, ip2)))
        for ip in find_ips(ip1, ip2):
            read_ip_logs(params, ip, log_files, flag)

    else:
        get_ip_address(params, log_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='Example usage: ./invoker.py --log inventory.log --ip 1.1.1.1')
    parser.add_argument('--rca', help='give the RCA maglev-<cluster_ip>-rca... .tar.gz file')
    parser.add_argument('--log', help='specify location of log file')
    parser.add_argument('--ip', help='specify the ip address of device. Default gives output of all devices')
    parser.add_argument('--time', help='specify time in ms. Default is 1000ms')
    parser.add_argument('--iprange', nargs=2, help='specify the range of ip')

    args = parser.parse_args()
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    start_fn(args)
