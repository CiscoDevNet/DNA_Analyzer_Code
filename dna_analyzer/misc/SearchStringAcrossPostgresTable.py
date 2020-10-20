#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a mechanism to collect and validate the data from DNAC Postgres

Usage: ./SearchStringAcrossPostgresTable

Author: enataraj@cisco.com

"""
import os
from datetime import datetime



class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

LOG_PATH='./dna_analyzer_logs/'
timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
log_file = LOG_PATH+"Search_Postgres__output_" + timestamp + ".log"

# Command to connect Database
command = "docker exec -it `docker ps | grep postgres_postgres | grep fusion | grep -oP '^\S+'` psql -U apic_em_user -d campus -P pager -c \"QUERY\""

# Query
CREATE_VIEW = """CREATE OR REPLACE FUNCTION search_whole_db(_like_pattern text) RETURNS TABLE(_tbl regclass, _ctid tid) AS $func$
BEGIN
   FOR _tbl IN
      SELECT c.oid::regclass FROM pg_class c JOIN pg_namespace n ON n.oid = relnamespace WHERE c.relkind = 'r' AND n.nspname !~ '^(pg_|information_schema)' ORDER BY n.nspname, c.relname
   LOOP
      RETURN QUERY EXECUTE format('SELECT $1, ctid FROM %s t WHERE t::text ~~ %L', _tbl, '%' || _like_pattern || '%')
      USING _tbl;
   END LOOP;
END
$func$  LANGUAGE plpgsql;"""

query = "SELECT * FROM search_whole_db('SEARCH_STRING');"


# Search String from postgres tables
def search_string_postgres_tables():
    searchString = input(color.PURPLE + "\n\t Enter Search pattern : " + color.END)
    if searchString and searchString.strip():
        outfile = open(log_file, "w+")
        output = []
        execute(query.replace("SEARCH_STRING",searchString), output)
        writeIntoFile(output, outfile)
    else:
        search_string_postgres_tables();


# create function for search string
def create_postgres_function():
    command_run = command.replace("QUERY", CREATE_VIEW)
    print(CREATE_VIEW)
    cmdOutput = os.popen(command_run)
    result = cmdOutput.read()
    print(result)



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
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    create_postgres_function()
    search_string_postgres_tables()
