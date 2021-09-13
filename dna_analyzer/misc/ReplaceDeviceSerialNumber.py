#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to update old device serialnumber with new device part of Manual RMA DNAC Postgres

Usage: ./ReplaceDeviceSerialNumber

Author: enataraj@cisco.com

"""
import os
from datetime import datetime

timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
log_file = "Postgres_Database_output_serialnumber_" + timestamp + ".log"

# Command to connect Database
command = "docker exec -it `docker ps | grep postgres_postgres | grep fusion | grep -oP '^\S+'` psql -U apic_em_user -d campus -P pager -c \"QUERY\""

# Add all your query part of this list
query_list = list()
query_list.append("select * from equipment where serialnumber='OLD_SERIAL_NUMBER';")
query_list.append("select * from serialnumberipaddressmapping where serialnumber='OLD_SERIAL_NUMBER';")
query_list.append("update equipment set serialnumber='NEW_SERIAL_NUMBER' where serialnumber='OLD_SERIAL_NUMBER';")
query_list.append("update serialnumberipaddressmapping set serialnumber='NEW_SERIAL_NUMBER' where serialnumber='OLD_SERIAL_NUMBER';")
query_list.append("select * from equipment where serialnumber='NEW_SERIAL_NUMBER';")
query_list.append("select * from serialnumberipaddressmapping where serialnumber='NEW_SERIAL_NUMBER';")



# Postgres data collection
def replace_device_serialnumber_fn():
    outfile = open(log_file, "w+")
    output = []
    print("\n\t Utility to Update OldSerialNumber to NewSerialNumber in Postgres \n")
    output.append("\n\t Utility to Update OldSerialNumber to NewSerialNumber in Postgres \n")
    try:
        oldSerialNumber = raw_input( "\n\t Enter the Old serial number : " )
    except:
        oldSerialNumber = input("\n\t Enter the Old serial number : ")
    try:
        newSerialNumber = raw_input( "\n\t Enter the New serial number : ")
    except:
        newSerialNumber = input("\n\t Enter the New serial number : ")


    output.append("Old SerialNumber : "+oldSerialNumber)
    output.append("New SerialNumber : "+newSerialNumber)
    output.append('\n\t\t\t Data Collection based on Device ')
    for query in query_list:
        query = query.replace("OLD_SERIAL_NUMBER", oldSerialNumber)
        query = query.replace("NEW_SERIAL_NUMBER", newSerialNumber)
        execute(query, output)
    writeIntoFile(output, outfile)


# Query execution
def execute(query, output):
    command_run = command.replace("QUERY", query)
    print(query)
    output.append(command_run)
    output.append("\n" + query + "\n")
    cmdOutput = os.popen(command_run)
    result = cmdOutput.read()
    print(result)
    output.append(result.strip())


# Write into File
def writeIntoFile(output, outfile):
    for item in output:
        outfile.write("%s\n" % item)


if __name__ == "__main__":
    replace_device_serialnumber_fn()
