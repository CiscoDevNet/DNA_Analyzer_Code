#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
About the Tool
==============
    The DNA Analyzer is command line tool to perform a variety of RCA / Log Analyzer,
Various application related data collection from postgres database table,
Finding inconsistent data existence from various application related postgres table and
Search Known defect based on Log Analyzer result.

Authors
========
Framework Concept and code - Elumalai Natarajan (enataraj@cisco.com)
Inventory Log Analyzer - Goutham Bodduluri (gboddulu@cisco.com)
Log Analyzer - Ilan Nagalingam/Parthiv/Elumalai (inagalin@cisco.com,parthivs@cisco.com,enataraj@cisco.com)
Database data Collection , Compliance, Audit and Telemetry - Elumalai Natarajan (enataraj@cisco.com)
Defect Search - Parthiv Shah (parthivs@cisco.com)

Feedback
=========
Share any feedback at log-analyzer-feedback@cisco.com

Usage
=====
 ./DNA_Analyzer

"""

import argparse
import glob
import os
import tarfile
from datetime import datetime

from log_analyzer.Inventory_log_analyzer import get_ip_address
from log_analyzer.Network_Orchestration_Log_Analyzer import parse_network_orchestration_log_fn
from log_analyzer.Onboarding_Log_Analyzer import parse_onboarding_log_fn
from log_analyzer.Spf_Service_Log_Analyzer import parse_spf_service_log_fn

# Version Number - enatataj - Update every release.
version ='1.0.1'  # TODO FIXME

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
REPORT_PATH='./dna_analyzer_reports/'

def log_analyzer_menu():
    print(color.BOLD + color.DARKCYAN + "\t\t\t\t\t\t DNA Log Analyzer" + color.END)
    print(color.BOLD + color.BLUE + "\t\t "  + "Options" + color.END)
    print(color.PURPLE + "\t\t\t 1 -> Inventory Service " + color.END)
    print(color.PURPLE + "\t\t\t 2 -> Spf Service Manager " + color.END)
    print(color.PURPLE + "\t\t\t 3 -> Network Orchestration " + color.END)
    print(color.PURPLE + "\t\t\t 4 -> Onboarding Service " + color.END)
    print(color.BLUE + "\t\t\t 5 -> Previous Menu" + color.END)
    print(color.BLUE + "\t\t\t 6 -> Exit" + color.END)

    print("*" * 75)
    option = int(input(color.GREEN + "\n\t Enter the Option : " + color.END))
    if option >= 7:
        print(color.BOLD + color.RED + "\t\t\t Invalid Option" + color.END)
    elif option == 5:
        main_menu()
    elif option == 6:
        print(color.BOLD + color.GREEN + "\t\t\t Thanks for using the Script !" + color.END)
    else:
        print(color.BOLD + color.BLUE + "\t\t\t\t " + "Options" + color.END)
        print(color.PURPLE + "\t\t\t\t\t 1 -> Analysis of Existing Log File " + color.END)
        print(color.PURPLE + "\t\t\t\t\t 2 -> Analyze Live Log " + color.END)
        print(color.BLUE + "\t\t\t\t\t 3 -> Exit " + color.END)

        logOption = int(input(color.GREEN + "\n\t Enter the Log Option : " + color.END))
        log_files = list()

        if logOption >= 4:
            print(color.BOLD + color.RED + "\t\t\t Invalid Option" + color.END)
        if(logOption== 3) :
            return None
        elif logOption == 2:
            timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
            command_run=""
            filepath=""
            command='magctl service logs -r'
            if option == 1:
                filepath = LOG_PATH+'apic-em-inventory-manager-service_' +timestamp +'.log'
                command_run = "for svc in $(magctl appstack status fusion |awk '/inventory-manager-service/ {print $1}');do magctl service logs -r $svc >> "+filepath+";done"
            elif option == 2:
                filepath = LOG_PATH+'spf-service-manager-service_' +timestamp +'.log'
                command_run = command + ' spf-service-manager-service > ' + filepath
            elif option == 3:
                filepath = LOG_PATH+'network-orchestration-service_' +timestamp +'.log'
                command_run = command + ' network-orchestration-service > ' +filepath
            elif option == 4:
                filepath = LOG_PATH+'onboarding-service_' +timestamp +'.log'
                command_run = command + ' onboarding-service > ' +filepath
            print(command_run)
            os.popen(command_run)
            if not os.path.exists(filepath):
                print(color.BOLD + color.RED + "\n\t\t\t Log file ( " + filepath + " ) is not exist !" + color.END)
            log_files = glob.glob(filepath)
        elif logOption == 1 :
            try:
                filepath = raw_input(color.PURPLE + "\n\t Enter RCA or Log Location : " + color.END)
            except:
                filepath = input(color.PURPLE + "\n\t Enter RCA or Log Location : " + color.END)

            if os.path.exists(filepath):
                if filepath.endswith('.gz'):
                    tar = tarfile.open('%s' % filepath, 'r:gz')
                    tar.extractall()
                    base_name = os.path.basename(filepath)
                    folder_name = os.path.splitext(os.path.splitext(base_name)[0])[0]
                    if option == 1:
                        log_path = 'data/rca/' + folder_name \
                                   + '/docker_logs_k8s_apic-em-inventory-manager-service*.log'
                    if option == 2:
                        log_path = 'data/rca/' + folder_name \
                                   + '/docker_logs_k8s_spf-service-manager-service_spf-service-manager-service*.log'
                    elif option == 3:
                        log_path = 'data/rca/' + folder_name \
                                   + '/docker_logs_k8s_network-orchestration-service*.log'
                    elif option == 4:
                        log_path = 'data/rca/' + folder_name \
                                   + '/docker_logs_k8s_onboarding-service*.log'
                    log_files = glob.glob(log_path)
                    tar.close()
                elif filepath.endswith('.log'):
                    log_files = glob.glob(filepath)
                else:
                    print(
                        color.BOLD + color.RED + "\n\t\t\t Given RCA or Log file ( " + filepath + " ) is Invalid !" + color.END)
            else:
                print(
                    color.BOLD + color.RED + "\n\t\t\t Given RCA or Log file ( " + filepath + " ) is not exist !" + color.END)

        if option == 1:
            if len(log_files) != 0:
                print(color.GREEN + "\n\t\t Calling inventory-service Log parsing  ... " + color.END)
                get_ip_address(args, log_files)
            else:
                print(color.RED + "\n\t\t\t Log file is not exist in the given RCA  ... " + color.END)

        if option == 2:
            if len(log_files) != 0:
                print(color.GREEN + "\n\t\t\t Calling spf-service Log parsing  ... " + color.END)
                parse_spf_service_log_fn(log_files)
            else:
                print(color.RED + "\n\t\t\t Log file is not exist in the given RCA  ... " + color.END)

        if option == 3:
            if len(log_files) != 0:
                print(color.GREEN + "\n\t\t\t Calling Network Orchestration Log parsing  ... " + color.END)
                parse_network_orchestration_log_fn(log_files)
            else:
                print(color.RED + "\n\t\t\t Log file is not exist in the given RCA  ... " + color.END)
        if option == 4:
            if len(log_files) != 0:
                print(color.GREEN + "\n\t\t\t Calling Onboarding Log parsing  ... " + color.END)
                parse_onboarding_log_fn(log_files)
            else:
                print(color.RED + "\n\t\t\t Log file is not exist in the given RCA  ... " + color.END)

def introduction():

    print(color.DARKCYAN+"*" * 77)
    print("*" * 77)
    print("*****"+" "* 67+"*****");
    print("*****"+" " * 10+"Welcome to the Cisco DNA Center Analyzer Tool"+" "* 12+"*****")
    print("*****"+" " * 25+"Version {}".format(version)+" "* 29+"*****")
    print("*****"+" "* 67+"*****");
    print("*" * 77)
    print("*" * 77+color.END)

    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    if not os.path.exists(REPORT_PATH):
        os.makedirs(REPORT_PATH)
    main_menu()
    print(color.BOLD+color.DARKCYAN )
    print("*" * 102)
    print("*****"+" "* 92+"*****");
    print("*****"+" " * 30+"Thanks for using DNA Analyzer !! "+" "* 29+"*****")
    print("*****"+" " * 2+"Logs and Reports are available at dna_analyzer_logs and dna_analyzer_reports directory.".format(version)+" "* 3+"*****")
    print("*****"+" "* 92+"*****");
    print("*" * 102+color.END)



def main_menu():
    print("\n")
    print(color.BOLD + color.DARKCYAN + "\t\t\t\t\t\t Cisco DNAC Data Analyzer" + color.END)
    print(color.BOLD + color.BLUE + "\t\t "  + "Options" + color.END)
    print(color.PURPLE + "\t\t\t 1 -> Log Analyzer " + color.END)
    print(color.PURPLE + "\t\t\t 2 -> Database Data Collection " + color.END)
    print(color.PURPLE + "\t\t\t 3 -> Database Compliance checker " + color.END)
    print(color.PURPLE + "\t\t\t 4 -> SDA Telemetry " + color.END)
    print(color.PURPLE + "\t\t\t 5 -> DNAC SDA Audit Report " + color.END)
    print(color.PURPLE + "\t\t\t 6 -> Search Known Cisco External Defect / Issues " + color.END)
    print(color.BLUE + "\t\t\t 7 -> Exit " + color.END)
    print(color.DARKCYAN+"\n\n\t For Feedback/Support Reachout : log-analyzer-feedback@cisco.com"+ color.END+"\n")
    print("*" * 75)
    option = int(input(color.GREEN + "\n\t Enter the Option : " + color.END))
    if option == 1:
        log_analyzer_menu()
    elif option == 2:
        from database_analyzer.Database_Data_Collector import database_data_collection_fn
        value = database_data_collection_fn()
        if value=="pre_menu":
            main_menu()
    elif option == 3:
        from sda_compliance.SDA_Compliance_Checker import collect_dnac_compliance_data_fn
        collect_dnac_compliance_data_fn()
    elif option == 4:
        from sda_telemetry.SDA_Telemetry import collect_sda_telemetry_data_fn
        collect_sda_telemetry_data_fn()
    elif option == 5:
        from sda_audit.SDA_Audit_Report import collect_dnac_audit_data_fn
        collect_dnac_audit_data_fn()
    elif option == 6:
        from search.Cisco_Defect_search import defect_search_menu_fn
        defect_search_menu_fn()
    elif option == 7:
        print(color.BOLD + color.GREEN + "\t\t\t Thanks for using the script !" + color.END)
    else:
        print(color.BOLD + color.RED + "\t\t\t Invalid Option" + color.END)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--rca', help=argparse.SUPPRESS)
    parser.add_argument('--log', help=argparse.SUPPRESS)
    parser.add_argument('--ip', help=argparse.SUPPRESS)
    parser.add_argument('--time', help=argparse.SUPPRESS)
    parser.add_argument('--iprange', nargs=2, help=argparse.SUPPRESS)

    args = parser.parse_args()
    introduction()
