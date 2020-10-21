#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to collect and validate the data from DNAC Postgres

Usage: ./Database_Data_Collector

Author: enataraj@cisco.com

"""
import os
from datetime import datetime


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
lan_auto_log_file = LOG_PATH+"LAN_Automation_postgres_data_" + timestamp + ".log"
provision_log_file = LOG_PATH+"Provision_postgres_data_" + timestamp + ".log"
host_onb_log_file = LOG_PATH+"Host_onboarding_postgres_data_" + timestamp + ".log"
device_log_file = LOG_PATH+"Device_based_postgres_data_" + timestamp + ".log"
ipam_log_file = LOG_PATH+"IPAM_postgres_data_" + timestamp + ".log"
migration_log_file = LOG_PATH+"Migration_based_postgres_data_" + timestamp + ".log"
ise_log_file = LOG_PATH+"ISE_postgres_data_" + timestamp + ".log"
ssid_log_file = LOG_PATH+"SSID_Prov_postgres_data_" + timestamp + ".log"
ap_log_file = LOG_PATH+"AP_Prov_postgres_data_" + timestamp + ".log"



# Command to connect Database
query = ""
command = "docker exec -it `docker ps | grep postgres_postgres | grep fusion | grep -oP '^\S+'` psql -U apic_em_user -d campus -P pager -c \"QUERY\""
query_count=0

# Lan Automation releated Query
lan_automation_query_tuple_list = list()
lan_automation_query_tuple = (("DB_LAN_1001"),("Devices in Inventory"),("select id,instanceuuid,hostname,managementipaddress,collectionstatus,serialnumber,inventorystatusdetail,errorcode,errordescription,platformid,series from networkdevice order by id asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1002"),("Commonsetting entries"),("select id,instanceuuid,version,lastupdateddatetime,groupuuid,value from commonsetting where namespace='lan' order by id asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1003"),("Networkorchestration entries"),("select id,instanceuuid,commonsettinginstanceuuid,creationtime,siteid,primaryseeddevice,action,status from networkorchestration order by creationtime asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1003"),("Networkorchestration entries"),("select id,instanceuuid,creationtime,siteid,primaryseeddevice,action,status from networkorchestration order by creationtime asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1004"),("Networkorch discovered device"),("select * from nworchdiscovereddevice,hdscvrddvc5_drssinuslst3 where nworchdiscovereddevice.id=hdscvrddvc5_drssinuslst3.instanceid order by id asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1005"),("Network orch device and network orch ip info"),("select * from nworchdevice,nworchipinfo, nworchdevicehasnworchipinfo where nworchdevice.id=nworchdevicehasnworchipinfo.nworchdevice_id and nworchdevicehasnworchipinfo.nworchipinfo_id=nworchipinfo.id;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1006"),("IP Address Pool Info"),("select id,instanceuuid,ippoolname,totalreserved,ippoolcidr,apicappname,parentuuid,createtime from ipaddresspoolinfo order by id ASC;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1007"),("IP Address Reserved"),("select id,instanceuuid,ipaddress,apicappname,subnetinfo,lastupdatetime,ipaddresspoolinfo_id from ipaddressreservedrange order by id ASC;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1008"),("Network orchestration Log"),("select id,loglevel,nworchid,timestamp,logentry,deviceid from networkOrchestrationLog order by id ASC;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1009"),("LAN Automatione discovered device"),("select id,name,serialnumber,pnpdevice,inventorydevice,state,networkorchestration_id,lastactivitytime from nworchdiscovereddevice order by id asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1010"),("LAN Automation device link details"),("select * from nworchlink order by id ASC;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1011"),("Networkorch device full"),("select * from nworchdevice order by id asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1012"),("Networkorch ip info"),("select * from nworchipinfo order by id asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1013"),("Network Decice and Network Orch IP Info"),("select * from nworchdevicehasnworchipinfo;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1014"),("Networkorch device details"),("select * from nworchdevicedata order by id asc;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1015"),("Networkorch inventory deviceinfo"),("select id,deviceid,deviceuuid,ntwrkorchstrtnglbldt_id from nworchinventorydeviceinfo order by id ASC;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1016"),("Site IP Pool reservation"),("select id,instanceuuid,siteid,resourceid,resourceowner from siteresourcemap order by id ASC;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)
lan_automation_query_tuple = (("DB_LAN_1017"),("Discovered site details"),("select id,instanceuuid,name,groupnamehierarchy,parentgroup_id from resourcegroup where instanceuuid in (select siteid from networkorchestration) order by id ASC;"))
lan_automation_query_tuple_list.append(lan_automation_query_tuple)

# Provision related Query
provision_query_tuple_list = list()
provision_query_tuple= (("DB_PROV_1001"),("Inventory Device details "),("select id,instanceuuid,hostname,managementipaddress,collectionstatus,serialnumber,inventorystatusdetail,errorcode,errordescription,platformid,series from networkdevice where instanceuuid IN (select networkdeviceid from deviceinfo) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1002"),("Provisioned device (DeviceInfo) cfs"),("select id,instanceuuid,name,createtime,provisioningstate from customerfacingservice where classname='DeviceInfo' order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1003"),("Provisioned device (DeviceInfo) details"),("select deviceinfo_id,networkdeviceid,siteid,devicesettings_id,networkwidesettings_id,dvcintrfcinfcntnr_id,profileid from deviceinfo order by deviceinfo_id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1004"),("Provisioned device NetworkDevice details"),("select id,instanceuuid,hostname,managementipaddress,collectionstatus,serialnumber,inventorystatusdetail,errorcode,errordescription from networkdevice where instanceuuid in (select networkdeviceid from deviceinfo) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1005"),("Provisioned device site details"),("select id,instanceuuid,name,groupnamehierarchy,parentgroup_id from resourcegroup where instanceuuid in (select siteid from deviceinfo) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1006"),("Provisioned device setting"),("select id,instanceuuid,externalconnectivityippool,nodetype,internaldomainprotocolnumber,connectedto from devicesettings where id in (select devicesettings_id from deviceinfo) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1007"),("Networkwide setting details "),("select * from networkwidesettings where id in (select networkwidesettings_id from deviceinfo) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1008"),("Connectivity domain cfs"),("select id,instanceuuid,name,createtime,provisioningstate from customerfacingservice where classname='ConnectivityDomain' order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1009"),("Connectivity domain details"),("select connectivitydomain_id,authenticationprofileid,siteid,authenticationprofile_id from connectivitydomain order by connectivitydomain_id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1010"),("Connectivity domain cfs filtered"),("select id,instanceuuid,name,createtime,provisioningstate,classname from customerfacingservice where id in (select connectivitydomain_id from connectivitydomain) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1011"),("Site details for Connectivity domain"),("select id,instanceuuid,name,groupnamehierarchy,parentgroup_id from resourcegroup where instanceuuid in (select siteid from connectivitydomain) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1012"),("ScalableGroup cfs"),("select id,instanceuuid,name,createtime,provisioningstate,deviceinfo_id,segment_id from customerfacingservice where classname='ScalableGroup' order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1013"),("Sclalable Group details"),("select scalablegroup_id,scalablegroupexternalhandle,parentscalablegroup_id,identitysource_id from scalablegroup where scalablegroup_id IN (select id from customerfacingservice where classname='ScalableGroup');"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1014"),("Scalable Group cfs filtered"),("select id,instanceuuid,name,createtime,provisioningstate,deviceinfo_id,segment_id from customerfacingservice  where instanceuuid IN (select scalablegroupid from segment) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
# Relationship between connectivity domain and virtual network
provision_query_tuple= (("DB_PROV_1015"),("Connectivity domain and Virtual Network releation"),("select id,instanceuuid,name,createtime,provisioningstate,classname from customerfacingservice where connectivitydomain_id in (select connectivitydomain_id from connectivitydomain) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1016"),("Authentication Profile for connectivitydomain"),("select id,instanceuuid,name,profileuuid,priority,preauthacl_id from authenticationprofile where connectivitydomain_id in (select connectivitydomain_id from connectivitydomain) order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1017"),("L3Handoff details"),("select * from l3handoff order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1018"),("External Connectivity Settings"),("select * from externalconnectivitysettings order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1019"),("Device information in detail"),("select * from managednetworkdevicebrief order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1020"),("L2Handoff details"),("select * from l2handoff order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1021"),("Resource Service Pool"),("select id,instanceuuid,resourceallocations,name,owner,authentityid from resourceservicepool order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1022"),("Resource service resource"),("select id,instanceuuid,resource_,parentuuid,authentityid from resourceserviceresource order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1023"),("Resource Service context"),("select id,instanceuuid,contextkey,contextvalue,resourceservicepool_id,authentityid from resourceservicecontext order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1024"),("Aggregated Device configstatus"),("select * from deviceconfigstatusaggregate order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1025"),("Deviceconfig status"),("select id,instanceuuid,servicetype,deviceid,namespace,status,cfsversion,error_message,workflowid,taskid from deviceconfigstatus where islatest=true order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
#provision_query_tuple= (("DB_PROV_1026"),("Serializedsnapshot details"),("select id,instanceuuid,namespace,version,createtime from serializedsnapshot order by id ASC;"))
#provision_query_tuple_list.append(provision_query_tuple)


# Wireless provision query
provision_query_tuple= (("DB_PROV_1026"),("APWirelessconfiguration cfs"),("select id,instanceuuid,name,createtime,provisioningstate,deviceinfo_id,segment_id from customerfacingservice where classname='APWirelessConfiguration' order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1027"),("APWirelessconfiguration detail"),("select * from apwirelessconfiguration;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1028"),("APWirelessconfiguration filtered cfs"),("select id,instanceuuid,name,createtime,provisioningstate,deviceinfo_id,segment_id,classname from customerfacingservice where id IN (select apwirelessconfiguration_id from apwirelessconfiguration);"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1029"),("WLAN cfs"),("select id,instanceuuid,name,createtime,provisioningstate,deviceinfo_id,segment_id from customerfacingservice where classname='Wlan' order by id ASC;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1030"),("WLAN details"),("select wlan_id,ssid,profilename,networkdeviceid,siteid,wlanid,wirelessauth_id from wlan;"))
provision_query_tuple_list.append(provision_query_tuple)
provision_query_tuple= (("DB_PROV_1031"),("WLAN filtered cfs"),("select id,instanceuuid,name,createtime,provisioningstate,deviceinfo_id,segment_id,classname from customerfacingservice where id IN (select wlan_id from wlan);"))
provision_query_tuple_list.append(provision_query_tuple)

# Host onboarding related Query
host_onbd_query_tuple_list = list()
host_onbd_query_tuple = (("DB_PROV_HOST_1001"),("Network Device detail for Provisioned device"),("select id,instanceuuid,hostname,managementipaddress,collectionstatus,serialnumber,inventorystatusdetail,errorcode,errordescription,platformid,series from networkdevice where instanceuuid IN (select networkdeviceid from deviceinfo) order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1002"),("Device Info detail"),("select deviceinfo_id,networkdeviceid,siteid,devicesettings_id,networkwidesettings_id,dvcintrfcinfcntnr_id,profileid from deviceinfo order by deviceinfo_id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1003"),("Network Device detail"),("select id,instanceuuid,hostname,managementipaddress,collectionstatus,serialnumber,inventorystatusdetail,errorcode,errordescription,platformid,series from networkdevice order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
# Segment related data
host_onbd_query_tuple = (("DB_PROV_HOST_1004"),("CFS for Segment"),("select id,instanceuuid,name,createtime,provisioningstate from customerfacingservice where classname='Segment' order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1005"),("Segment detail"),("select segment_id,ippoolid,l2instance,vlanid,connectivitydomain_id from segment;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1006"),("CFS for Segment filtered"),("select id,instanceuuid,name,createtime,provisioningstate from customerfacingservice where id in (select segment_id from segment) order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
# Virtual Network related data
host_onbd_query_tuple = (("DB_PROV_HOST_1007"),("CFS for Virtual Network "),("select id,instanceuuid,name,createtime,provisioningstate from customerfacingservice where classname='VirtualNetwork' order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1008"),("Virtual Network"),("select virtualnetwork_id,virtualnetworkcontextid,l3instance from virtualnetwork"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1009"),("CFS for Virtual Network filtered"),("select id,instanceuuid,name,createtime,provisioningstate from customerfacingservice where id in (select virtualnetwork_id from virtualnetwork) order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
# ip pool data
host_onbd_query_tuple = (("DB_PROV_HOST_1010"),("IP Address pool info for Segment"),("select id,instanceuuid,ippoolname,totalreserved,ippoolcidr,parentuuid,ippoolgroup_id from ipaddresspoolinfo where instanceuuid in (select ippoolid from segmentinfo where segment_id in (select segment_id from segment));"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
# Connectivity Domain Data
host_onbd_query_tuple = (("DB_PROV_HOST_1011"),("CFS Connectivity domain"),("select id,instanceuuid,name,createtime,provisioningstate,classname from customerfacingservice where connectivitydomain_id in (select connectivitydomain_id from connectivitydomain);"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1012"),("Connectivity domain for CFS detial"),("select id,instanceuuid,name,profileuuid,priority,preauthacl_id from authenticationprofile where connectivitydomain_id in (select connectivitydomain_id from connectivitydomain) order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1013"),("CFS for Connectivitydomain"),("select id,instanceuuid,name,createtime,provisioningstate from customerfacingservice where classname='ConnectivityDomain' order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1014"),("Connectivity domain"),("select connectivitydomain_id,authenticationprofileid,siteid,authenticationprofile_id from connectivitydomain;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1015"),("CFS for Connectivity domain"),("select id,instanceuuid,name,createtime,provisioningstate,classname from customerfacingservice where id in (select connectivitydomain_id from connectivitydomain);"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1016"),("Resource service pool"),("select id,instanceuuid,resourceallocations,name,owner,authentityid from resourceservicepool order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1017"),("Resource service service"),("select id,instanceuuid,resource_,parentuuid,authentityid from resourceserviceresource order by id ASC"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)
host_onbd_query_tuple = (("DB_PROV_HOST_1018"),("Resource Service context"),("select id,instanceuuid,contextkey,contextvalue,resourceservicepool_id,authentityid from resourceservicecontext order by id ASC;"))
host_onbd_query_tuple_list.append(host_onbd_query_tuple)

# Device based data Collection Query
device_based_query_tuple_list = list()
device_based_query_tuple=(("DB_PROV_DEV_1001"),("Network Device"),("select id,instanceuuid,hostname,managementipaddress,collectionstatus,serialnumber,inventorystatusdetail,errorcode,errordescription,platformid,series from networkdevice where managementipaddress='DEVICE_IP';"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1002"),("MNE Brief for Device"),("select * from managednetworkdevicebrief where managementipaddress='DEVICE_IP';"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1003"),("MEI for Device"),("select * from managedelementinterface where managementaddress='DEVICE_IP';"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1004"),("Device Info for Device"),("select deviceinfo_id,networkdeviceid,siteid,devicesettings_id,networkwidesettings_id,dvcintrfcinfcntnr_id,profileid from deviceinfo where networkdeviceid IN (select instanceuuid from networkdevice where managementipaddress='DEVICE_IP');"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1005"),("CFS Device Info for device"),("select id,instanceuuid,name,createtime,provisioningstate from customerfacingservice where id IN (select deviceinfo_id from deviceinfo where networkdeviceid IN (select instanceuuid from networkdevice where managementipaddress='DEVICE_IP'));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1006"),("CFS Segment Info for device"),("select id,instanceuuid,name,createtime,provisioningstate,deviceinfo_id,segment_id from customerfacingservice where deviceinfo_id IN (select deviceinfo_id from deviceinfo where networkdeviceid IN (select instanceuuid from networkdevice where managementipaddress='DEVICE_IP'));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1007"),("Device Setting for Device"),("select id,instanceuuid,externalconnectivityippool from devicesettings where id in (select devicesettings_id from deviceinfo where networkdeviceid IN (select instanceuuid from networkdevice where managementipaddress='DEVICE_IP'));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1008"),("CFS Connectivity domain for Device"),("select * from customerfacingservice where classname ='ConnectivityDomain' and instanceuuid in(select namespace from customerfacingservice where classname ='DeviceInfo' and id in(select deviceinfo_id from deviceinfo where networkdeviceid in(select instanceuuid from networkdevice where managementipaddress = 'DEVICE_IP')));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1009"),("CFS Virtual Network for Device"),("select * from customerfacingservice where classname ilike 'virtualnetwork' and namespace in (select instanceuuid from customerfacingservice where classname ='ConnectivityDomain' and instanceuuid in(select namespace from customerfacingservice where classname ='DeviceInfo' and id in(select deviceinfo_id from deviceinfo where networkdeviceid in(select instanceuuid from networkdevice where managementipaddress = 'DEVICE_IP'))));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1010"),("CFS Segment for Device"),("select * from customerfacingservice where classname ilike 'segment' and namespace in (select instanceuuid from customerfacingservice where classname ='ConnectivityDomain' and instanceuuid in(select namespace from customerfacingservice where classname ='DeviceInfo' and id in(select deviceinfo_id from deviceinfo where networkdeviceid in(select instanceuuid from networkdevice where managementipaddress = 'DEVICE_IP'))));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1011"),("Connectivity domain for Device"),("select * from ConnectivityDomain where connectivitydomain_id IN (select id from customerfacingservice where classname ='ConnectivityDomain' and instanceuuid in(select namespace from customerfacingservice where classname ='DeviceInfo' and id in(select deviceinfo_id from deviceinfo where networkdeviceid in(select instanceuuid from networkdevice where managementipaddress = 'DEVICE_IP'))));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1012"),("Virtual Network Detail for Device"),("select * from VirtualNetwork where virtualnetwork_id IN (select id from customerfacingservice where classname ilike 'virtualnetwork' and namespace in (select instanceuuid from customerfacingservice where classname ='ConnectivityDomain' and instanceuuid in(select namespace from customerfacingservice where classname ='DeviceInfo' and id in(select deviceinfo_id from deviceinfo where networkdeviceid in(select instanceuuid from networkdevice where managementipaddress = 'DEVICE_IP')))));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1013"),("Segment details for Device"),("select * from segment where segment_id IN (select id from customerfacingservice where classname ilike 'segment' and namespace in (select instanceuuid from customerfacingservice where classname ='ConnectivityDomain' and instanceuuid in(select namespace from customerfacingservice where classname ='DeviceInfo' and id in(select deviceinfo_id from deviceinfo where networkdeviceid in(select instanceuuid from networkdevice where managementipaddress = 'DEVICE_IP')))));"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1014"),("Device Config status for Device"),("select id,instanceuuid,servicetype,deviceid,namespace,cfsversion,status,error_detail from deviceconfigstatus where islatest=true and deviceid in (select instanceuuid from networkdevice where managementipaddress='DEVICE_IP');"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1015"),("Device Config status detail for device"),("select * from deviceconfigstatusdetail where deviceid in (select instanceuuid from networkdevice where managementipaddress='DEVICE_IP');"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1016"),("Device Config status Aggregation for Device"),("select * from deviceconfigstatusaggregate where deviceid in (select instanceuuid from networkdevice where managementipaddress='DEVICE_IP');"))
device_based_query_tuple_list.append(device_based_query_tuple)
device_based_query_tuple=(("DB_PROV_DEV_1017"),("Device InterfaceInfo for Device"),("select * from deviceinterfaceinfo where deviceinfo_id IN (select deviceinfo_id from deviceinfo where networkdeviceid IN (select instanceuuid from networkdevice where managementipaddress='DEVICE_IP'));"))
device_based_query_tuple_list.append(device_based_query_tuple)


# IPAM Related Query
ipam_query_tuple_list = list()
ipam_query_tuple = (("DB_IPAM_1001"),("IP Address Pool Info"),("select id,instanceuuid,ippoolname,totalreserved,ippoolcidr,apicappname,usedpercentage,parentuuid,createtime,lastupdatetime,ippoolgroup_id,tenantintsegment,tenantlongsegment from ipaddresspoolinfo order by id ASC;"))
ipam_query_tuple_list.append(ipam_query_tuple)
ipam_query_tuple = (("DB_IPAM_1002"),("IP Address Reservation"),("select id,instanceuuid,ipaddress,apicappname,featurename,subnetinfo,lastupdatetime,ipaddresspoolinfo_id,tenantintsegment,tenantlongsegment from ipaddressreservedrange order by id ASC;"))
ipam_query_tuple_list.append(ipam_query_tuple)
ipam_query_tuple = (("DB_IPAM_1003"),("IP Pool Group"),("select id,instanceuuid,name,owner,type from ippoolgroup order by id ASC;"))
ipam_query_tuple_list.append(ipam_query_tuple)
ipam_query_tuple = (("DB_IPAM_1004"),("IP Pool Context"),("select id,instanceuuid,owner,contextkey,contextvalue,ipaddressreservedrange_id,ipaddresspoolinfo_id,tenantintsegment,tenantlongsegment from ippoolcontext;"))
ipam_query_tuple_list.append(ipam_query_tuple)
ipam_query_tuple = (("DB_IPAM_1005"),("Site Resource and IP Pool Detail"),("select id,instanceuuid,siteid,resourceid,resourceowner,resourcetype,tenantintsegment,tenantlongsegment from siteresourcemap order by id ASC;"))
ipam_query_tuple_list.append(ipam_query_tuple)
ipam_query_tuple = (("DB_IPAM_1006"),("Site Detail for IP Pool Reservation"),("select id,instanceuuid,name,groupnamehierarchy,parentgroup_id,tenantintsegment,tenantlongsegment from resourcegroup where instanceuuid IN (select DISTINCT siteid from siteresourcemap);"))
ipam_query_tuple_list.append(ipam_query_tuple)
ipam_query_tuple = (("DB_IPAM_1007"),("Commonsetting Detail for IP Pool"),("select id,instanceuuid,version,lastupdateddatetime,groupuuid,type,key,value from commonsetting where  key ilike 'ip.pool%' order by id asc;"))
ipam_query_tuple_list.append(ipam_query_tuple)
ipam_query_tuple = (("DB_IPAM_1008"),("External IPAM Detail"),("select id,displayname,servername,serverurl,username,password,description,state,provider,configviewname from ipamconfiguration;"))
ipam_query_tuple_list.append(ipam_query_tuple)
ipam_query_tuple = (("DB_IPAM_1009"),("IP Address Reserved from IP Addresspoolinfo"),("select id,instanceuuid,ipaddress,apicappname,featurename,subnetinfo,lastupdatetime,ipaddresspoolinfo_id from ipaddressreservedrange where ipaddresspoolinfo_id IN (select id from ipaddresspoolinfo);"))
ipam_query_tuple_list.append(ipam_query_tuple)


# Migration Related Query
migration_query_tuple_list = list()
migration_query_tuple = (("DB_MIGR_1001"),("Migration status "),("select * from  migrationstatus;"))
migration_query_tuple_list.append(migration_query_tuple)
migration_query_tuple = (("DB_MIGR_1002"),("Migration Report"),("select * from  migrationreport;"))
migration_query_tuple_list.append(migration_query_tuple)
migration_query_tuple = (("DB_MIGR_1003"),("Migration"),("select * from  migration;"))
migration_query_tuple_list.append(migration_query_tuple)
migration_query_tuple = (("DB_MIGR_1004"),("Commonresourceversion details"),("select * from  commonresourceversion;"))
migration_query_tuple_list.append(migration_query_tuple)

# ISE Query List
ise_query_tuple_list = list()
ise_query_tuple = (("DB_ISE_1001"),("AAA Server Setting"),("select * from aaaserversetting"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1002"),("Identity Source detail"),("select * from identitysource;"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1003"),("ISE Trust Certificate"),("select id,instanceuuid,serialnumber,issuer,ciscoise_id from isetrustcertificate;"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1004"),("AAA Network Setting"),("select * from aaanesettings;"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1005"),("AAA Account Setting"),("select * from aaaaccountingsettings;"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1006"),("AAA Authendication Setting"),("select * from aaaauthenticationsettings;"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1007"),("AAA Authorization Setting"),("select * from aaaauthorizationsettings;"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1008"),("AAA Server Protocol Group"),("select * from aaaserverprotocolgroup;"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1009"),("Scalable Group Details"),("select * from scalablegroup;"))
ise_query_tuple_list.append(ise_query_tuple)
ise_query_tuple = (("DB_ISE_1010"),("Commonsetting detail for AAA"),("select * from commonsetting where type='aaa.setting';"))
ise_query_tuple_list.append(ise_query_tuple)

# AP Provisioning Data Collection
ap_prov_query_tuple_list=list()
ap_prov_query_tuple = (("DB_AP_1001"),("WLAN details for SSID"),("select * from wlan where ssid='SSID_NAME';"))
ap_prov_query_tuple_list.append(ap_prov_query_tuple)
ap_prov_query_tuple = (("DB_AP_1002"),("Wirelessauth details for SSID"),("select * from wirelessauth where id in (select wirelessauth_id from wlan where ssid='SSID_NAME');"))
ap_prov_query_tuple_list.append(ap_prov_query_tuple)
ap_prov_query_tuple = (("DB_AP_1003"),("WLAN CFS details"),("select * from customerfacingservice where id in (select wlan_id from wlan where ssid='SSID_NAME');"))
ap_prov_query_tuple_list.append(ap_prov_query_tuple)
ap_prov_query_tuple = (("DB_AP_1004"),("WLAN Profilename for SSID"),("select profilename from wlan where ssid='SSID_NAME';"))
ap_prov_query_tuple_list.append(ap_prov_query_tuple)
ap_prov_query_tuple = (("DB_AP_1005"),("WLAN Policy Profile details"),("select id,wlanpolicyname, wlanpolicydescription,wlanpolicystatus,wlanpolicycentralauthmode,wlanpolicysessiontimeout,wlanpolicyassoccentral,wlanpolicycentralswitchmode,wlanqospolicyperssidinput,wlanqospolicyperssidoutput,wlanpolicyblacklisttimeout,wlanpolicyuseridletimeout, wlanpolicyaaaoverride,wlanfabricpolicyname from wlanpolicyprofile where wlanpolicyname in (select profilename from wlan where ssid='SSID_NAME');"))
ap_prov_query_tuple_list.append(ap_prov_query_tuple)
ap_prov_query_tuple = (("DB_AP_1006"),("WLAN Adavanged Config"),("select  * from wlanconfigadvanced;"))
ap_prov_query_tuple_list.append(ap_prov_query_tuple)

# SSID Provisioning Data Collection
ssid_prov_query_tuple_list=list()
ssid_prov_query_tuple = (("DB_SSID_1001"),("WLC Inventory detail"),("select * from networkdevice where managementipaddress='WLC_ADDRESS';"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1002"),("WLC Provisioned detail"),("select * from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS');"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1003"),("Device interface container"),("select * from deviceinterfaceinfocontainer;"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1004"),("Device setting CFS AAA"),("select * from dsttngscfs6_aaa where networkwidesettingscfs_id in (select networkwidesettings_id from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1005"),("Device setting CFS CMX"),("select * from dsttngscfs6_cmx where networkwidesettingscfs_id in (select networkwidesettings_id from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1006"),("Device setting CFS DNS"),("select * from dsttngscfs6_dns where networkwidesettingscfs_id in (select networkwidesettings_id from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1007"),("Device setting CFS NTP"),("select * from dsttngscfs6_ntp where networkwidesettingscfs_id in (select networkwidesettings_id from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1008"),("Device setting CFS DHCP"),("select * from dsttngscfs6_dhcp where networkwidesettingscfs_id in (select networkwidesettings_id from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1009"),("Device setting CFS LDAP"),("select * from dsttngscfs6_ldap where networkwidesettingscfs_id in (select networkwidesettings_id from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1010"),("Device setting CFS SNMP"),("select * from dsttngscfs6_snmp where networkwidesettingscfs_id in (select networkwidesettings_id from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1011"),("Device setting CFS SYSLOG"),("select * from dsttngscfs6_syslogs where networkwidesettingscfs_id in (select networkwidesettings_id from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1012"),("Site Details for WLC"),("select * from resourcegroup where instanceuuid in (select siteid from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1013"),("Site Rule for WLC"),("select * from resourcegroupscoperule where resourcegroup_id in (Select id  from resourcegroup where instanceuuid in (select siteid from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS')));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1014"),("Site Device Link"),("select * from rsrcgrp_ddtnlinf where resourcegroup_id in (Select id  from resourcegroup where instanceuuid in (select siteid from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS')));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1015"),("Site Member details"),("select * from resourcegroupmember where resourcegroup_id in (Select id  from resourcegroup where instanceuuid in (select siteid from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS')));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)
ssid_prov_query_tuple = (("DB_SSID_1016"),("Site profile details"),("Select * from siteprofilesite where siteuuid in (select siteid from deviceinfo where networkdeviceid in (select instanceuuid from networkdevice where managementipaddress='WLC_ADDRESS'));"))
ssid_prov_query_tuple_list.append(ssid_prov_query_tuple)

# LAN Automation Data Collection
def collect_lan_automation_data_fn():
    outfile = open(lan_auto_log_file, "w+")
    output = []
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t LAN Automation Related Data Collection \n" + color.END)
    output.append("\n\t\t\t LAN Automation Related Data Collection\n\n")
    for lan_automation_query_tuple in lan_automation_query_tuple_list:
        (runid,name,query) = lan_automation_query_tuple
        execute(runid,name,query, output)
    writeIntoFile(output, outfile)


# Provision related data collection
def collect_provision_data_fn():
    outfile = open(provision_log_file, "w+")
    output = []
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t Provision Related Data Collection" + color.END)
    output.append("\n\t\t\t Provision Related Data Collection \n\n")
    for provision_query_tuple in provision_query_tuple_list:
        (runid,name,query) = provision_query_tuple
        execute(runid,name,query, output)
    writeIntoFile(output, outfile)



# Hostonboarding related data collection
def collect_host_onboarding_data_fn():
    outfile = open(host_onb_log_file, "w+")
    output = []
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t Provision Related Data Collection" + color.END)
    output.append("\n\t\t\t Provision Related Data Collection \n\n")
    for provision_query_tuple in provision_query_tuple_list:
        (runid,name,query) = provision_query_tuple
        execute(runid,name,query, output)

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t Host Onborading Related Data Collection" + color.END)
    output.append("\n\t\t\t Host Onborading Related Data Collection \n\n")
    for query_tuple in host_onbd_query_tuple_list:
        (runid,name,query) = query_tuple
        execute(runid,name,query, output)
    writeIntoFile(output, outfile)



# Device based data collection
def collect_device_based_data_fn():
    outfile = open(device_log_file, "w+")
    output = []
    try:
        deviceip = raw_input(color.GREEN + "\n\t Enter the Device IP Address : " + color.END)
    except:
        deviceip = input(color.GREEN + "\n\t Enter the Device IP Address : " + color.END)
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t Data Collection based on Device" + color.END)
    output.append('\n\t\t\t Data Collection based on Device ')
    output.append("\n\t\t\t Device IP Address :" + deviceip + "\n")

    for query_tuple in device_based_query_tuple_list:
        (runid,name,query) = query_tuple
        execute(runid,name,query.replace("DEVICE_IP", deviceip), output)
    writeIntoFile(output, outfile)

# IPAM Related Data Collection
def collect_ipam_data_fn():
    outfile = open(ipam_log_file, "w+")
    output = []
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t IPAM Related Data Collection \n" + color.END)
    output.append("\n\t\t\t IPAM Related Data Collection\n\n")
    for query_tuple in ipam_query_tuple_list:
        (runid,name,query) = query_tuple
        execute(runid,name,query, output)
    writeIntoFile(output, outfile)


# Migration Data Collection
def collect_migration_data_fn():
    outfile = open(migration_log_file, "w+")
    output = []
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t Migration Data Collection" + color.END)
    output.append('\n\t\t\t Migration Data Collection ')
    for query_tuple in migration_query_tuple_list:
        (runid,name,query) = query_tuple
        execute(runid,name,query, output)
    writeIntoFile(output, outfile)


# ISE Data Collection
def collect_ise_data_fn():
    outfile = open(ise_log_file, "w+")
    output = []

    print(color.BOLD + color.DARKCYAN + "\n\t\t\t ISE Integration Related Data Collection \n" + color.END)
    output.append("\n\t\t\t ISE Integration  Related Data Collection\n\n")
    for query_tuple in ise_query_tuple_list:
        (runid,name,query) = query_tuple
        execute(runid,name,query, output)
    writeIntoFile(output, outfile)



# SSID based data collection
def collect_ssid_prov_data_fn():
    outfile = open(ssid_log_file, "w+")
    output = []
    try:
        deviceip = raw_input(color.GREEN + "\n\t Enter the WLC IP Address : " + color.END)
    except:
        deviceip = input(color.GREEN + "\n\t Enter the WLC IP Address : " + color.END)
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t SSID Provisioning Data Collection" + color.END)
    output.append('\n\t\t\t SSID Provisioning Data Collection ')
    output.append("\n\t\t\t WLC IP Address :" + deviceip + "\n")
    for query_tuple in ssid_prov_query_tuple_list:
        (runid,name,query) = query_tuple
        execute(runid,name,query.replace("WLC_ADDRESS", deviceip), output)
    writeIntoFile(output, outfile)

# AP based data collection
def collect_ap_prov_data_fn():
    outfile = open(ap_log_file, "w+")
    output = []
    try:
        ssid_name = raw_input(color.GREEN + "\n\t Enter the SSID NAME : " + color.END)
    except:
        ssid_name = input(color.GREEN + "\n\t Enter the SSID NAME : " + color.END)
    print(color.BOLD + color.DARKCYAN + "\n\t\t\t AP Provisioning Data Collection" + color.END)
    output.append('\n\t\t\t AP Provisioning Data Collection ')
    output.append("\n\t\t\t SSID Name :" + ssid_name + "\n")
    for query_tuple in ap_prov_query_tuple_list:
        (runid,name,query) = query_tuple
        execute(runid,name,query.replace("SSID_NAME", ssid_name), output)
    writeIntoFile(output, outfile)


# Query execution
def execute(runid,name,query, output):
    global query_count
    print("\n\t RunID "+runid+"\n\t Name : "+name)
    output.append("\n\t RunID "+runid+"\n\t Name : "+name)
    command_run = command.replace("QUERY", query)
    #print(query)
    output.append(command_run)
    output.append("\n" + query + "\n")
    cmdOutput = os.popen(command_run)
    result = cmdOutput.read()
    #print(result)
    output.append(result.strip())
    query_count+=1


# Write into File
def writeIntoFile(output, outfile):
    global query_count
    for item in output:
        outfile.write("%s\n" % item)
    print(color.BOLD  + "\n\t\t\t Number of table data collected : {} ".format(query_count)+ color.END)


def database_data_collection_fn():
    print("*" * 75)
    print(color.BOLD + color.DARKCYAN + "\t\t\t\t\t\t Database Data Collection " + color.END)
    print(color.BOLD + color.BLUE + "\t\t " + "Options" + color.END)
    print(color.PURPLE + "\t\t\t 1 -> LAN Automation " + color.END)
    print(color.PURPLE + "\t\t\t 2 -> Device Provision " + color.END)
    print(color.PURPLE + "\t\t\t 3 -> Host Onboarding " + color.END)
    print(color.PURPLE + "\t\t\t 4 -> Device based Data Collection " + color.END)
    print(color.PURPLE + "\t\t\t 5 -> IPAM  " + color.END)
    print(color.PURPLE + "\t\t\t 6 -> ISE  " + color.END)
    print(color.PURPLE + "\t\t\t 7 -> Migration " + color.END)
    print(color.PURPLE + "\t\t\t 8 -> SSID Provisioning " + color.END)
    print(color.PURPLE + "\t\t\t 9 -> AP Provisioning " + color.END)
    print(color.BLUE + "\t\t\t 10 -> Previous Menu" + color.END)
    print(color.BLUE + "\t\t\t 11 -> Exit" + color.END)
    print("*" * 75)
    option = int(input(color.GREEN + "\n\t Enter the Option : " + color.END))
    if option == 1:
        collect_lan_automation_data_fn()
    elif option == 2:
        collect_provision_data_fn()
    elif option == 3:
        collect_host_onboarding_data_fn()
    elif option == 4:
        collect_device_based_data_fn()
    elif option == 5:
        collect_ipam_data_fn()
    elif option == 6:
        collect_ise_data_fn()
    elif option == 7:
        collect_migration_data_fn()
    elif option == 8:
        collect_ssid_prov_data_fn()
    elif option == 9:
        collect_ap_prov_data_fn()
    elif option == 10:
        return "pre_menu"
    elif option == 11:
        print(color.BOLD + color.GREEN + "\t\t " + "Thanks for using the script !" + color.END)
    else:
        print(color.BOLD + color.RED + "\t\t " + "Invalid Data Collection option" + color.END)


if __name__ == "__main__":
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    database_data_collection_fn()
