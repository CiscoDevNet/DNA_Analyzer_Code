#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to collect debug bundle

Usage: ./DebugBundleCollector

Author: enataraj@cisco.com, rishipat@cisco.com

"""
import os
from datetime import datetime
import re

from database_analyzer import Database_Data_Collector as dbcollector

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


timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
DEBUG_PATH="./dna_analyzer_debug_bundle_"+ timestamp +"/"
all_sda_app_log_file = DEBUG_PATH+"All_SDA_Application_postgres_data_" + timestamp + ".log"
log_command = 'magctl service logs -r '
zipfile_name = re.sub('[./]',"",DEBUG_PATH)+".tar.gz"
lan_auto_log_file = DEBUG_PATH+"LAN_Automation_postgres_data_" + timestamp + ".log"
provision_log_file = DEBUG_PATH+"Provision_postgres_data_" + timestamp + ".log"
host_onb_log_file = DEBUG_PATH+"Host_onboarding_postgres_data_" + timestamp + ".log"
ipam_log_file = DEBUG_PATH+"IPAM_postgres_data_" + timestamp + ".log"
migration_log_file = DEBUG_PATH+"Migration_based_postgres_data_" + timestamp + ".log"
compliance_log_file = DEBUG_PATH+"compliance_checker_postgres_data_" + timestamp + ".log"
ise_log_file = DEBUG_PATH+"ise_based_postgres_data_" + timestamp + ".log"

def get_logs_service_list(service,listonly=False):
    service_list = os.popen("magctl appstack status |awk '/"+service+"/ {print $2}' |grep -v inmemory |grep -v job").readlines()
    logpath = DEBUG_PATH + service + '_'+timestamp+'.log'
    if len(service_list) == 0:
        print("Service "+service+" not found on cluster")
    else:
        if listonly != False:
            return(service_list)
        else:
            for service in service_list:
                os.popen("magctl service logs -r " + service.strip() + " >> " + logpath)

def debug_bundle_menu_fn():
    print(color.BOLD + color.DARKCYAN + "\t\t\t\t\t\t Collect Debug Bundle" + color.END)
    print(color.BOLD + color.BLUE + "\t\t "  + "Options" + color.END)
    print(color.PURPLE + "\t\t\t 1 -> LAN Automation " + color.END)
    print(color.PURPLE + "\t\t\t 2 -> Provision " + color.END)
    print(color.BLUE + "\t\t\t 3 -> Exit" + color.END)
    print("*" * 75)

    if not os.path.exists(DEBUG_PATH):
        os.makedirs(DEBUG_PATH)

    option = int(input(color.GREEN + "\n\t Enter the Option : " + color.END))
    if option >= 4:
        print(color.BOLD + color.RED + "\t\t\t Invalid Option" + color.END)
    elif option == 1:
        lan_debug_bundle_collection_fn()
    elif option == 2:
        provision_debug_bundle_collection_fn()

    os.popen('tar -czf '+zipfile_name+' '+DEBUG_PATH)
    print(color.GREEN + "\n\t Log Archive "+zipfile_name+" Created")

def lan_debug_bundle_collection_fn():
    print("*" * 75)
    print(color.BOLD + color.DARKCYAN + "\t\t\t\t\t\t LAN Automation Debug Bundle Data Collection " + color.END)
    print(color.PURPLE + "\n\t Collecting Database Content " + color.END)

    dbcollector.collect_lan_automation_data_fn(lan_auto_log_file)
    dbcollector.collect_ipam_data_fn(ipam_log_file)
    dbcollector.collect_migration_data_fn(migration_log_file)
    dbcollector.collect_sda_compliance_data_fn(compliance_log_file)

    print(color.PURPLE + "\n\t Collecting Log files " + color.END)

    get_logs_service_list('network-design-service')
    get_logs_service_list('connection-manager-service')
    get_logs_service_list('onboarding-service')
    get_logs_service_list('network-orchestration-service')

    common_collection_fn()

def provision_debug_bundle_collection_fn():
    print("*" * 75)
    print(color.BOLD + color.DARKCYAN + "\t\t\t\t\t\t Provision Debug Bundle Data Collection " + color.END)
    print(color.PURPLE + "\n\t Collecting Database Content " + color.END)

    dbcollector.collect_host_onboarding_data_fn(host_onb_log_file)
    dbcollector.collect_ipam_data_fn(ipam_log_file)
    dbcollector.collect_ise_data_fn(ise_log_file)
    dbcollector.collect_migration_data_fn(migration_log_file)
    dbcollector.collect_sda_compliance_data_fn(compliance_log_file)

    print(color.PURPLE + "\n\t Collecting Log files " + color.END)

    get_logs_service_list('spf-service-manager-service')
    get_logs_service_list('spf-device-manager-service')
    get_logs_service_list('orchestration-engine-service')
    get_logs_service_list('network-programmer-service')

    common_collection_fn()

def common_collection_fn():

    get_logs_service_list('inventory-manager-service')
    get_logs_service_list('ipam-service')


    print(color.PURPLE + "\n\t Collecting RabbitMQ Message Details " + color.END)
    rabbitmq_commands = [['magctl service exec ',' -c rabbitmq "rabbitmqctl list_unresponsive_queues"'],
    ['magctl service exec ',' -c rabbitmq "rabbitmqctl list_queues name state messages_ready messages_unacknowledged messages"']]
    logfile = DEBUG_PATH+'rabbitmq-message-details_'+timestamp+'.log'
    rabmq_instances = get_logs_service_list('rabbitmq',listonly=True)
    for instance in rabmq_instances:
        for command in rabbitmq_commands:
            command_redirect = instance.strip().join(command)
#            print(command_redirect)
            os.popen('echo "'+command_redirect+'"'+' >> '+logfile)
            os.popen(command_redirect+' >> '+logfile)

    print(color.PURPLE + "\n\t Collecting Appstack Status " + color.END)
    logfile = DEBUG_PATH + 'appstack-status_'+timestamp+'.log'
#    print('magctl appstack status > '+DEBUG_PATH+'magctl-appstack-status_'+timestamp+'.log')
    os.popen('magctl appstack status >> '+logfile)
