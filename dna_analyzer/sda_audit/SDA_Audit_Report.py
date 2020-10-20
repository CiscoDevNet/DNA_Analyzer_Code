#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to collect and Generate SDA Audit data

Usage: ./SDA_Audit_Report

Author: enataraj@cisco.com

"""
import os
from datetime import datetime
import time
from report.ReportGenerator import generate_dna_analyzer_pdf_report


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
sda_audit_log_file = LOG_PATH+"SDA_Audit_postgres_data_" + timestamp + ".log"
sda_audit_report_file = REPORT_PATH+"DNAC_SDA_Audit_Report_"+timestamp+".pdf"

# Command to connect Database
query = ""
command = "docker exec -it `docker ps | grep postgres_postgres | grep fusion | grep -oP '^\S+'` psql -U apic_em_user -d campus -P pager -c \"QUERY\""
query_count=0

# SDA Audit Inventory related Query
sda_audit_query_inventory_tuple = list()
query_tuple=(("SDA-AUDIT-INV-1001"),("inv-device-count"),("Number of Devices in Inventory"),("select count(*) from networkdevice;"))
sda_audit_query_inventory_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-INV-1002"),("inv-switch-count"),("Number of Switches in Inventory"),("select count(*) from networkdevice where family='Switches and Hubs';"))
sda_audit_query_inventory_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-INV-1003"),("inv-wlc-count"),("Number of WLC in Inventory"),("select count(*) from networkdevice where family='Wireless Controller';"))
sda_audit_query_inventory_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-INV-1004"),("inv-pcf-count"),("Number of Devices in Partial Collection Failure"),("select count(*) from networkdevice where collectionstatus='Partial Collection Failure';"))
sda_audit_query_inventory_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-INV-1005"),("inv-sync-count"),("Number of Devices in Sync Progress"),("select count(*) from networkdevice where collectionstatus='In Progress';"))
sda_audit_query_inventory_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-INV-1006"),("inv-switchport-count"),("Number of Switch Port"),("select count(*) from deviceif where classname='SwitchPort';"))
sda_audit_query_inventory_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-INV-1007"),("inv-vlan-count"),("Number of Vlan Extended Interface"),("select count(*) from deviceif where classname='VLANInterfaceExtended' and portname!='Vlan1';"))
sda_audit_query_inventory_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-INV-1008"),("inv-vrf-external-count"),("Number of vrf interface to External router"),("select count(*) from deviceif where classname='VLANInterfaceExtended' and description='vrf interface to External router';"))
sda_audit_query_inventory_tuple.append(query_tuple)


# SDA Audit Network Design related Query
sda_audit_query_network_design_tuple = list()
query_tuple=(("SDA-AUDIT-ND-1001"),("nd-wlan-count"),("Number of WLAN Setting "),("select count(distinct key) from commonsetting where namespace='wlan' and type='wlan.setting';"))
sda_audit_query_network_design_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-ND-1002"),("nd-rf-profile-count"),("Number of RF Profile Setting "),("select count(distinct value) from commonsetting where namespace='wlan' and type='rfprofile.setting';"))
sda_audit_query_network_design_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-ND-1003"),("nd-ippool-generic-count"),("Number of Generic Pool "),("select count(*) from ippoolgroup where type='generic';"))
sda_audit_query_network_design_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-ND-1004"),("nd-ippool-lan-count"),("Number of LAN Pool "),("select count(*) from ippoolgroup where type='lan';"))
sda_audit_query_network_design_tuple.append(query_tuple)




# SDA Audit Provision related Query
sda_audit_query_provision_tuple = list()
query_tuple=(("SDA-AUDIT-PROV-1001"),("sda_devices"),("Device count per role per provisioned site \n Note : Role: S-N where N is MS=0, EN=1, BN=2, EndpointProxy=4, Subtended=5, TransitNode=10, TransitMS=16, Vedge=17"),("select count(*), resourcegroup.name, deviceinfo.roles from cnnctvtydmnhsdvcinfs  INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id INNER JOIN resourcegroup  ON deviceinfo.siteid = resourcegroup.instanceuuid group by resourcegroup.name, deviceinfo.roles;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1002"),("sda_fabric_border_series"),("Number of border nodes by platform series"),("select 'ALL' as sitename, series, count(*) from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id inner join networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid where roles similar to '(S-|%:)2(:%)?' group by series;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1003"),("sda_fabric_cp_series"),("Number of CP nodes by platform series"),("select 'ALL' as sitename, series, count(*) from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id inner join networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid where roles similar to '(S-|%:)1(:%)?' group by series;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1004"),("sda_fabric_edge_series"),("Number of edge nodes by platform series"),("select 'ALL' as sitename, series, count(*) from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id inner join networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid where roles similar to '(S-|%:)0(:%)?' group by series;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1005"),("sda_fabric_wlc_series"),("Number of wlc by platform series and software version"),("select 'ALL' as sitename, series, softwareversion, count(*) from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id inner join networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid where roles similar to '(S-|%:)4(:%)?' group by series, softwareversion;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-FAILED-1006"),("sda_fabric_prov_failed"),("Number of Devices Provision Failed"),("select count(distinct deviceid) from deviceconfigstatus where islatest=true and status IN ('Failed','Configuring','Rollback Success');"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1007"),("sda_connectivity_domains"),("Count of fabric domains \n Note : domain type [ 1= FABRIC_LAN, 4=FABRIC_SITE, 5=TRANSIT ]"),("select count(*), domaintype from connectivitydomain group by domaintype;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1008"),("sda_virtual_networks"),("Number of VNs created"),("select count(*) from virtualnetworkcontext;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1009"),("sda_fabric_ip_pools"),("Number of IP pools associated to fabric per site"),("select count(*), resourcegroup.name from segment INNER JOIN connectivitydomain ON segment.connectivitydomain_id = connectivitydomain.connectivitydomain_id INNER JOIN resourcegroup ON connectivitydomain.siteid = resourcegroup.instanceuuid group by resourcegroup.name;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1010"),("sda_multicast_rps"),("Number of Multicast RPs"),("select count(DISTINCT rpnetworkdeviceid) from mltcstinf_rpntwrkdvcid;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1011"),("sda_multicast_pools"),("Number of Multicast Pools"),("select count(*) from mltcstinf_ippoollist;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1012"),("sda_native_multicast"),("Number of Native Multicast"),("select count(*) from connectivitydomain where isnativemulticastenabled = 't';"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1013"),("sda_border_handoffs"),("Number of borders handoffs"),("select count(*) from externalconnectivitysettings;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1014"),("sda_l2handoff_borders"),("Number of borders doing L2 handoffs"),("select count(DISTINCT extconnectivitysettings_id) from l2handoff;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1015"),("sda_l3handoff_borders"),("Number of borders doing L3 handoffs"),("select count(DISTINCT extconnectivitysettings_id) from l3handoff;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1016"),("sda_handoff_pools"),("Number of pools being used for handoff"),("select count(*) from devicesettings where externalconnectivityippool IS NOT NULL;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1017"),("sda_l3handoff_vns"),("Number of VNs being L3 handed off"),("select count(DISTINCT virtualnetworkcontextid) from l3handoff INNER JOIN virtualnetwork ON l3handoff.virtualnetwork_id = virtualnetwork.virtualnetwork_id;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1018"),("sda_l2handoff_vns"),("Number of VNs being L2 handed off "),("select count(DISTINCT virtualnetworkcontextid) from l2handoff INNER JOIN virtualnetwork ON l2handoff.virtualnetwork_id = virtualnetwork.virtualnetwork_id;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-1019"),("sda_virtual_network_types"),("Number guest VNs "),("select count(*) from virtualnetworkcontext;"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-STRUCK-1020"),("device_struck_in_provision"),("Number of device struck or in progress provision "),("select count(*) from networkdevice where instanceuuid IN (select distinct(resourcename) from resourcelock);"))
sda_audit_query_provision_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-PROV-FAILED-1021"),("device_Failed_in_provision"),("Number of device Failed in provision "),("select count(distinct deviceid) from deviceconfigstatus where islatest=true and status IN ('Failed','Configuring','Rollback Success');"))
sda_audit_query_provision_tuple.append(query_tuple)




# SDA Audit LAN Automation related Query
sda_audit_query_lan_automation_tuple = list()
query_tuple=(("SDA-AUDIT-LAN-AUTO-1001"),("lan-auto-count"),("Number of LAN Automation Session"),("select count(*) from networkorchestration;"))
sda_audit_query_lan_automation_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-LAN-AUTO-1002"),("lan-auto-device-discovered"),("Number of Device Discovered via LAN Automation"),("select count(*) from nworchdiscovereddevice where state !=5;"))
sda_audit_query_lan_automation_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-LAN-AUTO-1003"),("lan-auto-device-discovered-deleted"),("Number of Device Discovered via LAN Automation and Deleted"),("select count(*) from nworchdiscovereddevice where state =5;"))
sda_audit_query_lan_automation_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-LAN-AUTO-1004"),("lan-auto-device-link_configured"),("Number of L3 Link Configured via LAN Auto"),("select count(*) from nworchlink where lwrintrfcinf_state !=3 and pprintrfcinf_state!=3;"))
sda_audit_query_lan_automation_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-LAN-AUTO-1005"),("lan_commonsetting_value_empty"),("Number of Commonsetting table value is empty for LAN Automation"),("select count (*)  from commonsetting where namespace='lan' and value IN ('',' ',null);"))
sda_audit_query_lan_automation_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-LAN-AUTO-1006"),("lan_discovered_site"),("Number of discovered site used LAN Automation"),("select count(distinct siteid) from networkorchestration;"))
sda_audit_query_lan_automation_tuple.append(query_tuple)
query_tuple=(("SDA-AUDIT-LAN-AUTO-1007"),("lan_discovered_site_deleted"),("Number of site deleted was used in LAN Automation"),("select count(*) from networkorchestration where siteid NOT IN (select instanceuuid from resourcegroup);"))
sda_audit_query_lan_automation_tuple.append(query_tuple)



report_data_tuple_list = list()
# DNAC Audit Report
def collect_dnac_audit_data_fn():
    outfile = open(sda_audit_log_file, "w+")
    output = []
    script_start_time=time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime())
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t SDA - Inventory " + color.END)
    output.append("\n\n\t\t\t SDA - Inventory  \n\n")
    report_data_tuple = (("SDA - Inventory"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in sda_audit_query_inventory_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t SDA - Network Design " + color.END)
    output.append("\n\n\t\t\t SDA - Network Design  \n\n")
    report_data_tuple = (("SDA - Network Design"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in sda_audit_query_network_design_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t SDA - Provision " + color.END)
    output.append("\n\n\t\t\t SDA - Provision \n\n")
    report_data_tuple = (("SDA - Provision"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in sda_audit_query_provision_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t SDA - LAN Automation " + color.END)
    output.append("\n\n\t\t\t SDA - LAN Automation \n\n")
    report_data_tuple = (("SDA - LAN Automation"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in sda_audit_query_lan_automation_tuple:
        (runid,name,description,query) = query_tuple
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)

    writeIntoFile(output, outfile)
    generate_dna_analyzer_pdf_report("Cisco DNAC - SDA Audit Report",sda_audit_report_file,script_start_time,report_data_tuple_list)



# Query execution
def execute(query, output):
    global query_count
    command_run = command.replace("QUERY", query)
    #print(query)
    output.append(command_run)
    output.append("\n" + query + "\n")
    cmdOutput = os.popen(command_run)
    result = cmdOutput.read()
    #print(result)
    output.append(result.strip())
    report_data_tuple = ((''),(''),(result.strip()))
    report_data_tuple_list.append(report_data_tuple)
    query_count+=1

# Write into File
def writeIntoFile(output, outfile):
    global query_count
    for item in output:
        outfile.write("%s\n" % item)
    print(color.BOLD  + "\n\t\t\t Number of table data collected : {} ".format(query_count)+ color.END)
    report_data_tuple = ((''),("    Number of table data collected : {} ".format(query_count)),())
    report_data_tuple_list.append(report_data_tuple)
    report_data_tuple = ((''),("    Thanks for using DNA Analyzer !!"),())
    report_data_tuple_list.append(report_data_tuple)




if __name__ == "__main__":
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    if not os.path.exists(REPORT_PATH):
        os.makedirs(REPORT_PATH)
    collect_dnac_audit_data_fn()
