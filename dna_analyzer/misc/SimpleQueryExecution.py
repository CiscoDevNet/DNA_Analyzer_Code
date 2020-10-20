#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to collect and validate the data from DNAC Postgres

Usage: ./SimpleQueryExecution

Author: enataraj@cisco.com

"""
import os
from datetime import datetime

timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
log_file = "Postgres_Database_output_" + timestamp + ".log"

# Command to connect Database
command = "docker exec -it `docker ps | grep postgres_postgres | grep fusion | grep -oP '^\S+'` psql -U apic_em_user -d campus -P pager -c \"QUERY\""

# Add all your query part of this list
query_list = list()
query_list.append("select * from network device;")
query_list.append("select * from deviceinfo;")


# Postgres data collection
def collect_postgres_data_fn():
    outfile = open(log_file, "w+")
    output = []
    for query in query_list:
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
    collect_postgres_data_fn()
