#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module will search the provide pattern from into cisco defect tracking system and list matched defects.

Usage: .

Author: parthiv Shah - parthivs@cisco.com (SDA Escalation Team)
Author: Elumalai Natarajan - enataraj@cisco.com (SDA Escalation Team)

If you use any part of the script or concept of the script, please provide credit to original Author.


"""

import argparse
import json
from datetime import datetime
import os

import requests
import requests.auth


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
defect_log_file = LOG_PATH+"Defect_list_" + timestamp + ".log"


def get_token():
    CLIENT_ID = "ummafwzqyeju3ujqu5m82ngc"
    CLIENT_SECRET = "<REVOKED_GITGUARDIAN_618373>"
    TOKEN_URL = "https://cloudsso.cisco.com/as/token.oauth2"
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "client_credentials"}
    response = requests.post(TOKEN_URL, auth=client_auth, data=post_data)
    token_json = response.json()["access_token"]
    return token_json


def search_defects(pattern):
    token = get_token()
    headers = {'Authorization': 'Bearer ' + token, 'Content-type': 'application/json', 'Accept': 'application/json',
               'Vary': 'Accept'}
    DDTS_OUTPUT = requests.get('https://api.cisco.com/bug/v2.0/bugs/keyword/' + pattern, headers=headers)
    DDTS_OUTPUT_JSON = json.loads(DDTS_OUTPUT.text)
    output = json.dumps(DDTS_OUTPUT_JSON, indent=4)
    #print(output)
    bugs = DDTS_OUTPUT_JSON.get('bugs')
    print("\n\n\t Defect Details  ")
    print("\t ************** \n")
    for bug in bugs:
        print("\t Product : "+bug.get("product"))
        print("\t Severity : "+bug.get("severity"))
        print("\t Defect ID : "+bug.get("bug_id"))
        print("\t HeadLine : "+bug.get("headline"))
        print("\t Known Releases : "+bug.get("known_affected_releases"))
        print("\t Fixed Releases : "+bug.get("known_fixed_releases")+"\n\n")

    outfile = open(defect_log_file, "w+")
    writeIntoFile(output, outfile)



# Write into File
def writeIntoFile(output, outfile):
        outfile.write("%s\n" % output)


def defect_search_menu_fn():
    print(color.BOLD + color.DARKCYAN + "\n\n\t\t\t\t\t\t Search Known Issues" + color.END)
    searchString=''
    try:
        searchString = raw_input(color.GREEN + "\n\t Enter Search String (exit): " + color.END)
    except:
        searchString = input(color.GREEN + "\n\t Enter Search String : " + color.END)
    searchString=searchString.strip()
    if(searchString!=''):
        search_defects(searchString)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='Example usage: ./Cisco_Defect_search.py --pattern NCSP10025: Provisioning failed')
    parser.add_argument('--pattern',
                        help='Specify error message in double quotes like - "WLC fabric provisioning fails with NCSP10025"')
    args = parser.parse_args()
    searchString = args.pattern
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    if searchString and searchString.strip():
        search_defects(searchString)
    else:
        print(color.BOLD + color.RED + 'Provide the error message which needs to search Cisco Defects' + color.END)
