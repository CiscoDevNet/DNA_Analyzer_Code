# -*- coding: utf-8 -*-
"""
This module provides a mechanism to collect and Generate report for Telemetry Data

Usage: ./SDA_Telemetry

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
sda_telemetry_log_file = LOG_PATH+"SDA_Telemetry_data_" + timestamp + ".log"
sda_telemetry_report_file = REPORT_PATH+"DNAC_SDA_Telemetry_Report_"+timestamp+".pdf"


# Command to connect Database
query = ""
command = "docker exec -it `docker ps | grep postgres_postgres | grep fusion | grep -oP '^\S+'` psql -U apic_em_user -d campus -P pager -c \"QUERY\""
query_count=0


# SDA Telemetry Data
sda_telemetry_query_tuple=list()
query_tuple = (("SDA-TEL-1001"),("sda_connectivity_domains"),("Count of fabric domains \n Note : domain type [ 1= FABRIC_LAN, 4=FABRIC_SITE, 5=TRANSIT ] "),("select count(*), domaintype from connectivitydomain group by domaintype;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1002"),("sda_devices"),("Device count per role per provisioned site \n Note : Role: S-N where N is MS=0, EN=1, BN=2, EndpointProxy=4, Subtended=5, TransitNode=10, TransitMS=16, Vedge=17"),("select count(*), resourcegroup.name, deviceinfo.roles from cnnctvtydmnhsdvcinfs  INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id INNER JOIN resourcegroup  ON deviceinfo.siteid = resourcegroup.instanceuuid group by resourcegroup.name, deviceinfo.roles;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1003"),("sda_virtual_networks"),("Number of VNs created"),("select count(*) from virtualnetworkcontext;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1004"),("sda_fabric_ip_pools"),("Number of IP pools associated to fabric per site"),("select count(*), resourcegroup.name from segment INNER JOIN connectivitydomain ON segment.connectivitydomain_id = connectivitydomain.connectivitydomain_id INNER JOIN resourcegroup ON connectivitydomain.siteid = resourcegroup.instanceuuid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1005"),("sda_fabric_connected_hosts"),("Number of hosts connected to fabric edges per provisioned site"),("select count(*), resourcegroup.name, host.hosttype from host INNER JOIN deviceinfo ON host.connectednetworkdeviceid = deviceinfo.networkdeviceid  INNER JOIN resourcegroup ON deviceinfo.siteid = resourcegroup.instanceuuid INNER JOIN cnnctvtydmnhsdvcinfs ON deviceinfo.deviceinfo_id = cnnctvtydmnhsdvcinfs.deviceinfo_id group by host.hosttype, resourcegroup.name UNION ALL select count(*), 'unknown' as name, 'wireless' as hosttype from fabricclient;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1006"),("sda_base_provisioned_devices"),("Count of all base provisioned devices per site"),("select count(*), resourcegroup.name from deviceinfo INNER JOIN resourcegroup ON deviceinfo.siteid = resourcegroup.instanceuuid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1007"),("sda_base_provisioned_device_versions"),("Software version for all base provisioned devices per site"),("select count(*), softwareversion, resourcegroup.name from deviceinfo INNER JOIN networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid INNER JOIN resourcegroup ON deviceinfo.siteid = resourcegroup.instanceuuid group by softwareversion, resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1008"),("sda_fabric_device_versions"),("Software version for all devices in fabric per provisioned site"),("select count(*), softwareversion, resourcegroup.name from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id INNER JOIN networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid INNER JOIN resourcegroup ON deviceinfo.siteid = resourcegroup.instanceuuid group by softwareversion, resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1009"),("sda_network_orch"),("Number of times LAN automation has been run per site"),("select resourcegroup.name, case count(*) when 0 then 'false' else 'true' end from networkorchestration INNER JOIN resourcegroup ON networkorchestration.siteid = resourcegroup.instanceuuid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1010"),("sda_global_auth_mode"),("Global auth mode per site"),("select rg.name as sitename, sp.name as globalauth from connectivitydomain as cd INNER JOIN resourcegroup as rg ON cd.siteid = rg.instanceuuid INNER JOIN siteprofile as sp ON  cd.authenticationprofileid = sp.siteprofileuuid;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1011"),("sda_port_assignment_pooltype"),("Static Vs. Dynamic Port Assignment \n Count of the number of ports that are statically assigned with \n  a) data pools, b) voice pools (per provisioned site)"),("select resourcegroup.name as sitename, case traffictype when 0 then 'Data' when 1 then 'Voice' else 'Unknown' end as traffictype, count(*) from dvcintrfcinfshssgmnts INNER JOIN segment ON dvcintrfcinfshssgmnts.segment_id = segment.segment_id INNER JOIN deviceinterfaceinfo ON dvcintrfcinfshssgmnts.deviceinterfaceinfo_id = deviceinterfaceinfo.id INNER JOIN deviceinfo ON deviceinterfaceinfo.deviceinfo_id = deviceinfo.deviceinfo_id INNER JOIN resourcegroup ON deviceinfo.siteid = resourcegroup.instanceuuid group by traffictype, resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1012"),("sda_port_assignment_sgt"),("Static Vs. Dynamic Port Assignment \n Count of the number of ports that are statically assigned with \n scalable groups (per provisioned site)"),("select resourcegroup.name as sitename, count(*) from deviceinterfaceinfo INNER JOIN deviceinfo ON deviceinterfaceinfo.deviceinfo_id = deviceinfo.deviceinfo_id AND scalablegroupid is not NULL INNER JOIN resourcegroup ON deviceinfo.siteid = resourcegroup.instanceuuid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1013"),("sda_port_assignment_connected_device"),("Static Vs. Dynamic Port Assignment \n Count of the number of ports that are statically assigned with \n type of device (per provisioned site)"),("select resourcegroup.name as sitename, case connecteddevicetype when 0 then 'UserDevice' when 1 then 'AP' when 2 then 'ExtendedNode' when 3 then 'Server' else 'Unknown' end as connecteddevicetype, count(*) from deviceinterfaceinfo INNER JOIN deviceinfo ON deviceinterfaceinfo.deviceinfo_id = deviceinfo.deviceinfo_id INNER JOIN resourcegroup ON deviceinfo.siteid = resourcegroup.instanceuuid group by connecteddevicetype, resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1014"),("sda_multicast_rps"),("Number of multicast RPs"),("select 'ALL' as sitename, count(DISTINCT rpnetworkdeviceid) from mltcstinf_rpntwrkdvcid;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1015"),("sda_multicast_pools"),("Number of multicast Pools"),("select count(*) from mltcstinf_ippoollist;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1016"),("sda_native_multicast"),("Number of sites with Native multicast"),("select count(*) from connectivitydomain where isnativemulticastenabled = 't';"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1017"),("sda_border_handoffs"),("Number of border handoffs"),("select 'ALL' as sitename, count(*) from externalconnectivitysettings;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1018"),("sda_border_l3handoff_transit_types"),("Type of handoff for each border."),("select resourcegroup.name as fabricsite, case tcd.transittype when 0 then 'SDA' when 1 then 'IP' when 2 then 'SDWAN' else 'Unknown' end as transittype, count(*) from deviceinfohastransitnetworks INNER JOIN connectivitydomain tcd ON deviceinfohastransitnetworks.transitnetworks_id = tcd.connectivitydomain_id INNER JOIN cnnctvtydmnhsdvcinfs ON deviceinfohastransitnetworks.deviceinfo_id = cnnctvtydmnhsdvcinfs.deviceinfo_id INNER JOIN connectivitydomain cd ON cnnctvtydmnhsdvcinfs.connectivitydomain_id = cd.connectivitydomain_id INNER JOIN resourcegroup ON resourcegroup.instanceuuid = cd.siteid group by tcd.transittype, resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1019"),("sda_l2handoff_borders"),("Number of borders doing L2 handoffs"),("select count(DISTINCT extconnectivitysettings_id) from l2handoff;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1020"),("sda_l3handoff_borders"),("Number of borders doing L3 handoffs"),("select count(DISTINCT extconnectivitysettings_id) from l3handoff;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1021"),("sda_handoff_pools"),("Number of pools being used for handoff"),("select count(*) from devicesettings where externalconnectivityippool IS NOT NULL;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1022"),("sda_l3handoff_vns"),("Number of VNs being L3 handed off "),("select count(DISTINCT virtualnetworkcontextid) from l3handoff INNER JOIN virtualnetwork ON l3handoff.virtualnetwork_id = virtualnetwork.virtualnetwork_id;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1023"),("sda_l2handoff_vns"),("Number VNs being L2 handed off "),("select count(DISTINCT virtualnetworkcontextid) from l2handoff INNER JOIN virtualnetwork ON l2handoff.virtualnetwork_id = virtualnetwork.virtualnetwork_id;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1024"),("sda_guest_devices"),("Number of guest devices "),("select 'ALL' as sitename, count(*) from fabricoverride;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1025"),("sda_virtual_network_types"),("Number of guest VNs "),("select count(*) from virtualnetworkcontext;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1026"),("sda_data_pools"),("Number of data pools "),("select resourcegroup.name as fabricsite, count(*) from segment INNER JOIN connectivitydomain ON segment.connectivitydomain_id = connectivitydomain.connectivitydomain_id AND traffictype = 0 INNER JOIN resourcegroup ON resourcegroup.instanceuuid = connectivitydomain.siteid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1027"),("sda_voice_pools"),("Number of voice pools "),("select resourcegroup.name as fabricsite, count(*) from segment INNER JOIN connectivitydomain ON segment.connectivitydomain_id = connectivitydomain.connectivitydomain_id AND traffictype = 1 INNER JOIN resourcegroup ON resourcegroup.instanceuuid = connectivitydomain.siteid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1028"),("sda_critical_pools"),("Number of critical pools "),("select resourcegroup.name as fabricsite, count(*) from segment INNER JOIN connectivitydomain ON segment.connectivitydomain_id = connectivitydomain.connectivitydomain_id AND iscriticalpool = 't' INNER JOIN resourcegroup ON resourcegroup.instanceuuid = connectivitydomain.siteid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1029"),("sda_l2_flooding_pools"),("Number of pools with L2 flooding"),("select resourcegroup.name as fabricsite, count(*) from segment INNER JOIN connectivitydomain ON segment.connectivitydomain_id = connectivitydomain.connectivitydomain_id AND isselectivefloodingenabled = 't' INNER JOIN resourcegroup ON resourcegroup.instanceuuid = connectivitydomain.siteid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1030"),("sda_scalable_group_pools"),("Number of pools with scalable groups"),("select resourcegroup.name as fabricsite, count(*) from segment INNER JOIN connectivitydomain ON segment.connectivitydomain_id = connectivitydomain.connectivitydomain_id AND scalablegroupid IS NOT NULL INNER JOIN resourcegroup ON resourcegroup.instanceuuid = connectivitydomain.siteid group by resourcegroup.name;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1031"),("sda_fabric_edge_series"),("Number of edge nodes by platform series"),("select 'ALL' as sitename, series, count(*) from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id inner join networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid where roles similar to '(S-|%:)0(:%)?' group by series;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1032"),("sda_fabric_border_series"),("Number of border nodes by platform series"),("select 'ALL' as sitename, series, count(*) from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id inner join networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid where roles similar to '(S-|%:)2(:%)?' group by series;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1033"),("sda_fabric_cp_series"),("Number of CP nodes by platform series"),("select 'ALL' as sitename, series, count(*) from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id inner join networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid where roles similar to '(S-|%:)1(:%)?' group by series;"))
sda_telemetry_query_tuple.append(query_tuple)
query_tuple = (("SDA-TEL-1034"),("sda_fabric_wlc_series"),("Number of wlc by platform series and software version"),("select 'ALL' as sitename, series, softwareversion, count(*) from cnnctvtydmnhsdvcinfs INNER JOIN deviceinfo ON cnnctvtydmnhsdvcinfs.deviceinfo_id = deviceinfo.deviceinfo_id inner join networkdevice ON networkdevice.instanceuuid = deviceinfo.networkdeviceid where roles similar to '(S-|%:)4(:%)?' group by series, softwareversion;"))
sda_telemetry_query_tuple.append(query_tuple)

report_data_tuple_list = list()
# SDA Telemetry Data
def collect_sda_telemetry_data_fn():
    script_start_time=time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime())
    outfile = open(sda_telemetry_log_file, "w+")
    output = []
    script_start_time=time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime())
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t SDA Telemetry Data" + color.END)
    output.append("\n\n\t\t\t SDA Telemetry Data \n\n")
    report_data_tuple = (("SDA Telemetry Data"),(''),(''))
    report_data_tuple_list.append(report_data_tuple)
    for query_tuple in sda_telemetry_query_tuple:
        (runid,name,description,query) = query_tuple
        #print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        print("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        output.append("\n\t RunID : "+runid+"\n\t Name : "+name+"\n\t Description : "+description+"\n")
        report_data_tuple = ((''),(description),())
        report_data_tuple_list.append(report_data_tuple)
        execute(query, output)
    writeIntoFile(output, outfile)
    generate_dna_analyzer_pdf_report("Cisco DNAC - SDA Telemetry Report",sda_telemetry_report_file,script_start_time,report_data_tuple_list)


# Query execution
def execute(query, output):
    global query_count
    command_run = command.replace("QUERY", query)
    #print(query)
    output.append(command_run)
    output.append("\n" + query + "\n")
    try:
        cmdOutput = os.popen(command_run)
        result = cmdOutput.read()
    except:
        print(color.RED+"Unable to run the command ... "+color.END)
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
    collect_sda_telemetry_data_fn()

