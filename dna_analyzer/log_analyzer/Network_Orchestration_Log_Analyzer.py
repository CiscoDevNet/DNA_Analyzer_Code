#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to analyze Network Orchestration Log

Usage: ./Network_Orchestration_Log_Analyzer.py --rca <rca_.tar.gz_file> --log <log_file>

Author: parthivs@cisco.com

"""

import argparse
import glob
import os
import re
import tarfile
from datetime import datetime

noparsepattern = {
    "no_start": "Received unclaimed notification for pnp device Device",
    "received_ztd": "Received Ztd Device Provisioned Message for",
    "general_config": "General and config entry created for",
    "NwOrchCreate_Allocated_SVI_address": "NwOrchCreate:Allocated SVI address",
    "added_device_inv": "Added device ",
    "first_time_collection": "Received FirstTimeCollectionMessage for device",
    "request_to_delete_PNP_device": "Received request to delete PNP device with",
    "Released_subnet_associated": "Released subnet associated to SN",
    "Removed_device_from_inventory": "Removed device",
    "stopping_network_orchestration": "NwOrchUpdate:Starting the process of stopping network orchestration for seedDeviceId"
}


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

LOG_PATH='./dna_analyzer_logs/'
timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
net_orc_log_file = LOG_PATH+"Network-orchestration-output_" + timestamp + ".log"



def read_ip_logs(sn_address, log_files, flag):
    logs = []
    for logfile in log_files:
        with open("%s" % logfile, "r") as file:
            lines = file.readlines()
            for line in lines:
                if sn_address and re.search(r'%s' % sn_address, line):
                    logs.append(line)

    parse_network_orchestration_fn(sn_address, logs, flag)


def parse_network_orchestration_log_fn(log_files):
    get_device_serial_number_fn(log_files)


def get_device_serial_number_fn(log_files):
    sn_of_device = []
    for logfile in log_files:
        with open("%s" % logfile, "r") as file:
            lines = file.readlines()
            for line in lines:
                if re.search(r'%s' % noparsepattern["no_start"], line):
                    val = re.findall(r'serialNumber=(\w+)', line)[0]
                    if val not in sn_of_device:
                        sn_of_device.append(val)

    for sn_address in sn_of_device:
        flag = True
        read_ip_logs(sn_address, log_files, flag)
        print("*" * 175)
    file.close()


def parse_network_orchestration_fn(sn_address, logs, flag):
    output = []
    if logs:
        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["no_start"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append("\t\t\tReceived unclaimed notification for " +
                              " for DEVICE SN: " + sn_address + " started at " + start_time + "\n")

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["received_ztd"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(color.GREEN + "\t\t\tReceived Ztd Device Provisioned Message for " +
                              " DEVICE SN: " + sn_address + " started at " + start_time + color.END + "\n")

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["added_device_inv"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(color.GREEN + "\t\t\tAdded device wiith " +
                              " DEVICE SN: " + sn_address + " to Inventory at " + start_time + color.END + "\n")

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["NwOrchCreate_Allocated_SVI_address"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(color.GREEN + "\t\t\tAdded device wiith " +
                              " DEVICE SN: " + sn_address + " to Inventory at " + start_time + color.END + "\n")

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["general_config"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(color.GREEN + "\t\t\tGeneral and config entry created for " +
                              " DEVICE SN: " + sn_address + " at " + start_time + color.END + "\n")

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["first_time_collection"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(color.GREEN + "\t\t\tReceived FirstTimeCollectionMessage for " +
                              " DEVICE SN: " + sn_address + " at " + start_time + color.END)

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["request_to_delete_PNP_device"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(color.RED + "\t\t\tReceived request to delete PNP device with " +
                              " DEVICE SN: " + sn_address + " at " + start_time + color.END)

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["Released_subnet_associated"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(color.RED + "\t\t\tReleased subnet associated to device with " +
                              " DEVICE SN: " + sn_address + " at " + start_time + color.END)

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["Removed_device_from_inventory"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(color.RED + "\t\t\tRemoved device with " +
                              " DEVICE SN: " + sn_address + " at " + start_time + color.END)

        for index, lines in enumerate(logs):
            if re.search(r'%s' % noparsepattern["stopping_network_orchestration"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                output.append(
                    color.GREEN + "\t\t\tStarting the process of stopping network orchestration for seedDeviceId " +
                    " DEVICE SN: " + sn_address + " at " + start_time + color.END)

    file = open(net_orc_log_file, "a+")
    for item in output:
        file.write("%s\n" % item)
        print(item)
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
                   + '/docker_logs_k8s_network-orchestration-service_network-orchestration-service*.log'

        log_files = glob.glob(log_path)
        tar.close()
        get_device_serial_number_fn(log_files)

    elif params.log:
        log_files = sorted(glob.glob(params.log))
        get_device_serial_number_fn(log_files)

    else:
        print('Pass the log file or RCA')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='Example usage: ./Network_Orchestration_Log_Analyzer.py --log network-orchestration-service.log ')
    parser.add_argument('--rca', help='give the RCA maglev-<cluster_ip>-rca... .tar.gz file')
    parser.add_argument('--log', help='specify location of log file')
    args = parser.parse_args()
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    start_fn(args)
