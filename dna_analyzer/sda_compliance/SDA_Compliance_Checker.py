#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to collect and validate the data from DNAC Postgres

Usage: ./SDA_Compliance_Checker.py

Author: enataraj@cisco.com

"""
import os
from datetime import datetime
from report.ReportGenerator import generate_dna_analyzer_pdf_report
import time

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
timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
dnac_compliance_log_file = LOG_PATH+"SDA_Compliance_data_" + timestamp + ".log"
sda_compliance_report_file = REPORT_PATH+"DNAC_SDA_Compliance_Report_"+timestamp+".pdf"

# Command to connect Database
query = ""
command = "docker exec -it `docker ps | grep postgres_postgres | grep fusion | grep -oP '^\S+'` psql -U apic_em_user -d campus -P pager -c \"QUERY\""
report_command = "docker exec -it `docker ps | grep postgres_postgres | grep fusion | grep -oP '^\S+'` psql -U apic_em_user -d campus -t -P pager -c \"QUERY\""
query_count=0

# Provision Compliance related Query
provision_compliance_query_tuple = list()
# Network device stale
query_tuple=(("PROV-INC-1001"),("Network_device_inconsistent"),("Device Deleted from Inventory and exist in Fabric"),"select {} from deviceinfo where networkdeviceid NOT IN (select instanceuuid from networkdevice);")
provision_compliance_query_tuple.append(query_tuple)
# Device Interface stale
query_tuple=(("PROV-INC-1002"),("device_interface_inconsistent"),("Device Interface details not exist in deviceif but interfaceinfo holds the data"),("select {} from deviceinterfaceinfo where interfaceid NOT IN (select instanceuuid from deviceif);"))
provision_compliance_query_tuple.append(query_tuple)
# IP Pool deleted But Segment is exist
# sda_sg_segment_consistency_check Number of inconsistent Segments where scalablegroupid is not valid
query_tuple=(("PROV-INC-1003"),("sda_sg_segment_consistency_check"),("Number of inconsistent Segments where scalablegroupid is not valid"),("select {} from segment where scalablegroupid !='' and scalablegroupid not in (select instanceuuid from customerfacingservice where classname='scalablegroup');"))
provision_compliance_query_tuple.append(query_tuple)
# sda_ipam_segment_consistency_check Number of inconsistent Segments where ippoolid is not valid
query_tuple=(("PROV-INC-1004"),("sda_ipam_segment_consistency_check"),("Number of inconsistent Segments where ippoolid is not valid"),("select {} from segment where ippoolid not in (select instanceuuid from ippoolgroup);"))
provision_compliance_query_tuple.append(query_tuple)
# sda_ipam_l3handoff_consistency_check Number of inconsistent DeviceSettings where externalconnectivityippool is not valid
query_tuple=(("PROV-INC-1006"),("sda_ipam_l3handoff_consistency_check"),("Number of inconsistent DeviceSettings where externalconnectivityippool is not valid"),("select {} from devicesettings where externalconnectivityippool not in (select instanceuuid from ippoolgroup);"))
provision_compliance_query_tuple.append(query_tuple)
#sda_protocolendpoint_dii_consistency_check Number of inconsistent DeviceInterfaceInfos where interfaceid is not valid
query_tuple=(("PROV-INC-1007"),("sda_protocolendpoint_dii_consistency_check"),("Number of inconsistent DeviceInterfaceInfos where interfaceid is not valid"),("select {} from deviceinterfaceinfo where interfaceid not in (select instanceuuid from protocolendpoint where classname='SwitchPort');"))
provision_compliance_query_tuple.append(query_tuple)
#sda_reachabilitysession_consistency_check  Number of inconsistent ReachabilitySessions where sourcedeviceid is not valid
query_tuple=(("PROV-INC-1008"),("sda_reachabilitysession_consistency_check"),("Number of inconsistent ReachabilitySessions where sourcedeviceid is not valid"),("select {} from reachabilitysession where sourcedeviceid not in (select instanceuuid from networkdevice);"))
provision_compliance_query_tuple.append(query_tuple)
# Segment stale
query_tuple=(("PROV-INC-1009"),("interface_segment"),("Segment exist but deviceif deleted"),("select {} from dvcintrfcinfshssgmnts where deviceinterfaceinfo_id in (select id from deviceinterfaceinfo where interfaceid NOT IN (select instanceuuid from deviceif));"))
provision_compliance_query_tuple.append(query_tuple)
# Entry is part of deviceinfo not in devicesettings
query_tuple=(("PROV-INC-1010"),("deviceinfo_devicesetting"),("Entry is part of deviceinfo not in devicesettings"),("select {} from devicesettings where id NOT IN (select devicesettings_id from deviceinfo);"))
provision_compliance_query_tuple.append(query_tuple)
# Site stale based on Connectivitydomain
query_tuple=(("PROV-INC-1011"),("site_deleted_connectivity_domain"),("Site Deleted but entry exist in Connectivity Domain"),("select {} from resourcegroup where instanceuuid NOT IN (select siteid from connectivitydomain);"))
provision_compliance_query_tuple.append(query_tuple)
# Site got deleted and entry is there in Connectivity Domain and Virtual Network
query_tuple=(("PROV-INC-1012"),("site_deleted_vn_conn_dmn"),("Site got deleted and entry is there in Connectivity Domain and Virtual Network"),("select {} from resourcegroup,connectivitydomain where resourcegroup.instanceuuid NOT IN (select siteid from connectivitydomain);"))
provision_compliance_query_tuple.append(query_tuple)
# Connectivity Domain List not where site id is missing.
query_tuple=(("PROV-INC-1013"),("connectivity_domain_site_deleted"),("Connectivity Domain has Entry But Site deleted"),("select {} from connectivitydomain where connectivitydomain_id IN (select DISTINCT connectivitydomain.connectivitydomain_id from resourcegroup,connectivitydomain where resourcegroup.instanceuuid NOT IN (select siteid from connectivitydomain));"))
provision_compliance_query_tuple.append(query_tuple)
# Customerfacingservice for Device stale
query_tuple=(("PROV-INC-1014"),("cfs_device_inconsistent"),("Customerfacingservice for exist but Device deleted"),("select {} from customerfacingservice where ID IN (select deviceinfo_id from deviceinfo where networkdeviceid  NOT IN (select instanceuuid from networkdevice));"))
provision_compliance_query_tuple.append(query_tuple)
# Customerfacingservice for Device stale
query_tuple=(("PROV-INC-1015"),("cfs_device_inconsistent"),("Customerfacingservice for exist but Device deleted"),("select {} from customerfacingservice where deviceinfo_id IN (select deviceinfo_id from deviceinfo where networkdeviceid  NOT IN (select instanceuuid from networkdevice));"))
provision_compliance_query_tuple.append(query_tuple)
# Customerfacingservice for connectivity domain entry where site id missing
query_tuple=(("PROV-INC-1016"),("cfs_connectivity_domain_site_deleted"),("Customerfacingservice for connectivity domain entry where site id missing"),("select {} from customerfacingservice where id IN (select DISTINCT connectivitydomain.connectivitydomain_id from resourcegroup,connectivitydomain where resourcegroup.instanceuuid NOT IN (select siteid from connectivitydomain));"))
provision_compliance_query_tuple.append(query_tuple)
# Customerfacingservice for virtualnetwork entry where site id missing
query_tuple=(("PROV-INC-1017"),("cfs_vn_site_deleted"),("Customerfacingservice for virtualnetwork entry where site id missing"),("select {} from customerfacingservice where connectivitydomain_id IN (select DISTINCT connectivitydomain.connectivitydomain_id from resourcegroup,connectivitydomain where resourcegroup.instanceuuid NOT IN (select siteid from connectivitydomain));"))
provision_compliance_query_tuple.append(query_tuple)
# Virtual network entry where sitid missing
query_tuple=(("PROV-INC-1018"),("Virtual_Network_site_deleted"),("Virtual network entry where sitid missing"),("select {} from virtualnetwork where virtualnetwork_id IN (select id from customerfacingservice where connectivitydomain_id IN (select DISTINCT connectivitydomain.connectivitydomain_id from resourcegroup,connectivitydomain where resourcegroup.instanceuuid  NOT IN (select siteid from connectivitydomain)));"))
provision_compliance_query_tuple.append(query_tuple)
# Device entry part of Rechability session and not in Inventory
query_tuple=(("PROV-INC-1019"),("Rechability_Session_inconsistent"),("Device entry part of Rechability session and not in Inventory"),("select {} from reachabilitysession where sourcedeviceid not IN (select instanceuuid from networkdevice);"))
provision_compliance_query_tuple.append(query_tuple)
# Device struck in provision
query_tuple=(("PROV-INC-1020"),("device_struck_provision"),("Devices are struck in Provision or Inprogress"),("select {} from networkdevice where instanceuuid IN (select distinct(resourcename) from resourcelock);"))
provision_compliance_query_tuple.append(query_tuple)
# Device Failed in provision
query_tuple=(("PROV-INC-FAILED-1021"),("device_provision_failed"),("Devices are Failed in Provision "),("select {} from networkdevice where instanceuuid IN (select distinct deviceid from deviceconfigstatus where islatest=true and status IN ('Failed','Configuring','Rollback Success'));"))
provision_compliance_query_tuple.append(query_tuple)
# Device Failed in provision
query_tuple=(("PROV-INC-MULTICAST-1022"),("device_multicast_duplicate"),("Multicast duplicate entry CSCvv89025 "),("select contextValue , count(*) from ippoolcontext where contextkey='networkDeviceIdcom.cisco.ef.lan.rfs.util.ConnectivityDomainIpam$Feature' group by contextvalue having count(*) > 1;"))
provision_compliance_query_tuple.append(query_tuple)


# Host onboarding compliance Query
host_onbd_compliance_query_tuple = list()
query_tuple=(("PROV-HOST-INC-1001"),("cfs_segment_inconsistent"),("Segment has entry But Customerfacingservice entry deleted"),("select {} from segment where segment_id not in (select id from customerfacingservice where classname='Segment');"))
host_onbd_compliance_query_tuple.append(query_tuple)
query_tuple=(("PROV-HOST-INC-1002"),("cfs_vn_inconsistent"),("Vitrual Network has entry but customerfacingservice entry delete"),("select {} from virtualnetwork where virtualnetwork_id NOT IN (select id from customerfacingservice where classname='VirtualNetwork');"))
host_onbd_compliance_query_tuple.append(query_tuple)
# Site got deleted and entry is there in Connectivity Domain and Virtual Network
query_tuple=(("PROV-HOST-INC-1003"),("site_deleted_vn_cd"),("Site Deleted entry present in Connectivity Domain and Virtual Network"),("select {} from resourcegroup,connectivitydomain where resourcegroup.instanceuuid NOT IN (select siteid from connectivitydomain);"))
host_onbd_compliance_query_tuple.append(query_tuple)
# Connectivity Domain List not where site id is missing.
query_tuple=(("PROV-HOST-INC-1004"),("cd_siteid_missed"),("Connectivity Domain Entry with site id missed"),("select {} from connectivitydomain where connectivitydomain_id IN (select DISTINCT connectivitydomain.connectivitydomain_id from resourcegroup,connectivitydomain where resourcegroup.instanceuuid NOT IN (select siteid from connectivitydomain));"))
host_onbd_compliance_query_tuple.append(query_tuple)
# Customerfacingservice for connectivity domain entry where site id missing
query_tuple=(("PROV-HOST-INC-1005"),("site_deleted_cfs_cd"),("Site Deleted reference exist in customerfacingservice Connectivity Domain"),("select {} from customerfacingservice where id IN (select DISTINCT connectivitydomain.connectivitydomain_id from resourcegroup,connectivitydomain where resourcegroup.instanceuuid NOT IN (select siteid from connectivitydomain));"))
host_onbd_compliance_query_tuple.append(query_tuple)
# Customerfacingservice for virtualnetwork entry where site id missing
query_tuple=(("PROV-HOST-INC-1006"),("site_deleted_cfs_vn"),("Site Deleted reference exist in customerfacingservice Virtual Network"),("select {} from customerfacingservice where connectivitydomain_id IN (select DISTINCT connectivitydomain.connectivitydomain_id from resourcegroup,connectivitydomain where resourcegroup.instanceuuid NOT IN (select siteid from connectivitydomain));"))
host_onbd_compliance_query_tuple.append(query_tuple)
# Virtual network entry where sitid missing
query_tuple=(("PROV-HOST-INC-1007"),("virtual_network_site_deleted"),("Site Deleted but reference exist in Virtual Network"),("select {} from virtualnetwork where virtualnetwork_id IN (select id from customerfacingservice where connectivitydomain_id IN (select DISTINCT connectivitydomain.connectivitydomain_id from resourcegroup,connectivitydomain where resourcegroup.instanceuuid  NOT IN (select siteid from connectivitydomain)));"))
host_onbd_compliance_query_tuple.append(query_tuple)

# LAN Automation Compliance Query
lan_automation_compliance_query_tuple = list()
query_tuple=(("LAN-INC-1001"),("lan_automated_deleted_device"),("Devices Deleted after LAN Automation"),("select {} from nworchdiscovereddevice where state=5;"))
lan_automation_compliance_query_tuple.append(query_tuple)
query_tuple=(("LAN-INC-1002"),("lan_discovered_site_deleted"),("Discovered site Deleted After LAN Automation"),("select {} from networkorchestration where siteid NOT IN(select instanceuuid from resourcegroup);"))
lan_automation_compliance_query_tuple.append(query_tuple)
query_tuple=(("LAN-INC-1003"),("lan_commonsetting_deleted"),("Networkorchestration entry exist But commonsetting entry deleted"),("select {} from networkorchestration where commonsettinginstanceuuid NOT IN(select instanceuuid from commonsetting where namespace='lan');"))
lan_automation_compliance_query_tuple.append(query_tuple)
query_tuple=(("LAN-INC-1004"),("lan_discovered_site_deleted"),("Discovered site Deleted After LAN Automation (CSCvv94215)"),("select {} from networkorchestration where siteid NOT IN(select instanceuuid from resourcegroup) ;"))
lan_automation_compliance_query_tuple.append(query_tuple)
query_tuple=(("LAN-INC-1005"),("lan_commonsetting_value_empty"),("Commonsetting table value is empty for LAN Automation"),("select {} from commonsetting where namespace='lan' and value IN ('',' ',null);"))
lan_automation_compliance_query_tuple.append(query_tuple)
query_tuple=(("LAN-INC-1006"),("lan_commonsetting_multiple_enabled"),("Commonsetting table last enabled entry not exist in network orchestration.(CSCvw03683) If result 0."),("select {} from networkorchestration where commonsettinginstanceuuid IN (select instanceuuid from commonsetting where id IN (select max(id) from commonsetting where namespace='lan' and value like '%enabled%'));"))
lan_automation_compliance_query_tuple.append(query_tuple)


# IPAM Related Compliance Query
ipam_compliance_query_tuple = list()
query_tuple=(("IPAM-INC-1001"),("ipaddressreservedrange_inconsitent"),("IPAddresspoolinfo entry deleted but IPAddressreservedrange contains stale referene"),("select {} from ipaddressreservedrange where ipaddresspoolinfo_id  NOT IN (select id from ipaddresspoolinfo);"))
ipam_compliance_query_tuple.append(query_tuple)
query_tuple=(("IPAM-INC-1002"),("segment_ippool_inconsistent"),("IPPoolgroup entry deleted but reference exist in segment"),("select {} from segment where ippoolid not in(select instanceuuid from ippoolgroup);"))
ipam_compliance_query_tuple.append(query_tuple)


# Migration related Compliance Query
migration_compliance_query_tuple = list()
query_tuple=(("MIGR-INC-1001"),("migration_inconsistent"),("Migration Status more than one Commonresourceversion"),("SELECT {} FROM commonresourceversion as c1 where c1.runningversion=1 and c1.name IN (SELECT name FROM CommonResourceVersion as c2 GROUP BY c2.name HAVING COUNT(c2.name)>1);"))
migration_compliance_query_tuple.append(query_tuple)
query_tuple=(("MIGR-INC-1002"),("migration_inconsistent"),("Migration Status Migration type 3" ),("SELECT {} FROM migrationstatus WHERE connectivitydomain_id is NULL AND deviceinfo_id IS NOT NULL AND migrationtype=3;"))
migration_compliance_query_tuple.append(query_tuple)
query_tuple=(("MIGR-INC-1003"),("migration_inconsistent_cd"),("Connectivity Domain Migration Inconsistent"),("SELECT {} FROM MigrationStatus WHERE migrationstate='f' AND (connectivitydomain_id,migrationtype) IN (SELECT connectivitydomain_id,migrationtype FROM MigrationStatus GROUP BY connectivitydomain_id,migrationtype HAVING COUNT(*)>1);"))
migration_compliance_query_tuple.append(query_tuple)


report_data_tuple_list = list()
# Database Complaince Checker
def collect_dnac_compliance_data_fn(log_file):
    script_start_time=time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime())
    global outfile
    if log_file is "":
        outfile = open(dnac_compliance_log_file, "a+")
    else:
        outfile = open(log_file, "a+")
    output = []
    script_start_time=time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime())
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t Provision Related Compliance Data" + color.END)
    output.append("\n\n\t\t\t Provision Related Compliance Data \n\n")
    report_data_tuple = (("Provision Related Compliance Data"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in provision_compliance_query_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)
        #execute_report(query,description)

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t Hostonboarding Related Compliance Data" + color.END)
    output.append("\n\n\t\t\t Hostonboarding Related Compliance Data \n\n")
    report_data_tuple = (("Hostonboarding Related Compliance Data"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in host_onbd_compliance_query_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)
        #execute_report(query,description)

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t LAN Automation Related Compliance Data \n" + color.END)
    output.append("\n\n\t\t\t LAN Automation Related Compliance Data \n\n")
    report_data_tuple = (("LAN Automation Related Compliance Data"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in lan_automation_compliance_query_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)
        #execute_report(query,description)

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t IPAM Related Compliance Data \n" + color.END)
    output.append("\n\n\t\t\t IPAM Related Compliance Data \n\n")
    report_data_tuple = (("IPAM Related Compliance Data"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in ipam_compliance_query_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)
        #execute_report(query,description)

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t Migration Compliance Data" + color.END)
    output.append('\n\t\t\t Migration Compliance Data ')
    report_data_tuple = (("Migration Compliance Data"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in migration_compliance_query_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),(''))
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)
        #execute_report(query,description)

    writeIntoFile(output, outfile)
    report_data_tuple = ((''),("    Number of table data collected : {} ".format(query_count)),())
    report_data_tuple_list.append(report_data_tuple)
    report_data_tuple = ((''),("    Thanks for using DNA Analyzer !!"),())
    report_data_tuple_list.append(report_data_tuple)
    generate_dna_analyzer_pdf_report("SDA Compliance Summary Report",sda_compliance_report_file,report_data_tuple_list)


# Query execution
def execute(query, output):
    global query_count
    command_run = command.replace("QUERY", query.format("*"))
    #print(query)
    output.append(command_run+"\n")
    cmdOutput = os.popen(command_run)
    result = cmdOutput.read()
    #print(result)
    output.append(result.strip())

    # Below code is for Report Generation
    command_run = command.replace("QUERY", query.format("count(*)"))
    cmdOutput = os.popen(command_run)
    result = cmdOutput.read()
    #print(query.format("count(*)"))
    #print(result.strip())
    report_data_tuple = ((''),(''),(result.strip()))
    report_data_tuple_list.append(report_data_tuple)
    query_count+=1


# Write into File
def writeIntoFile(output, outfile):
    global query_count
    for item in output:
        outfile.write("%s\n" % item)
    print(color.BOLD  + "\n\t\t\t Number of table data collected : {} ".format(query_count)+ color.END)



if __name__ == "__main__":
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    if not os.path.exists(REPORT_PATH):
        os.makedirs(REPORT_PATH)
    collect_dnac_compliance_data_fn("")

