#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module analyzes SPF log file and determines time it took for provision, detect the errors etc.

Usage: ./Radioactive_task_tracer.py --rca <rca_.tar.gz_file> --log <log_file> --taskid <instanceuuid of the task>

Author: parthiv Shah - parthivs@cisco.com (SDA Escalation Team)
        ilan nagalingam (SDA Escalation Team)

<log_file>: SPF Log file Location
<rca_.tar.gz_file>: RCA file location

"""

import argparse
import glob
import os
import pprint
import re
import tarfile
from datetime import datetime

sdaparsepattern = {
    "create": "Creating task:",
    "complete": "message ServiceCompletionMessage",
    "excp": "Exception executing function",
    "error_response": "Error Response:",
    "exception": "Exception",
    "submit_rfs": "Submitted child RFS workflow with Id=",
    "workflow_uuid": "The UUID of workflow is =>",
    "acquire_lock_time": "Time taken to acquire locks",
    "task_execution": "Received request for task execution:",
    "service_request": "ServiceModifyRequestMessageHandler :",
    "task_id": "task id:",
    "step_string": "Started executing spf.",
    "task_result_stauts": "Task Result Status:",
}


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

LOG_PATH= 'dna_analyzer_logs/dna_analyzer_logs/'
timestamp = datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S_UTC")
ispf_ser_log_file = LOG_PATH+"Spf-service-output_" + timestamp + ".log"
sm_log_file_name_template = '/docker_logs_k8s_spf-service-manager-service_spf-service-manager-service*.log'
dm_log_file_name_template = '/docker_logs_k8s_spf-device-manager-service_spf-device-manager-service*.log'
np_log_file_name_template = '/docker_logs_k8s_apic-em-network-programmer-service_apic-em-network-programmer-service*.log'


def read_subtask_logs_with_taskId(full_logs, subtask_id):
    subtask_logs = []
    startIndex = -1
    endIndex = -1
    if full_logs:
        for index, lines in enumerate(full_logs):
            if re.search(r'%s' % subtask_id, lines):
                if startIndex == -1:
                    startIndex = index
                subtask_logs.append(lines)
                endIndex = index

    return [subtask_logs, startIndex, endIndex]


def read_log_sub(full_logs, startIndex, endIndex):
    subtask_logs = []
    if full_logs:
        for index, lines in enumerate(full_logs):
            if index >= startIndex and index <= endIndex:
                subtask_logs.append(lines)

    return subtask_logs


count_func = 0
count_success = 0
count_failure = 0



def parse_log_fn(log_files, full_logs, dm_log_files, prov_task_id, is_dm_parse):
    output = []
    pp = pprint.PrettyPrinter(indent=4)
    if full_logs:
        for index, lines in enumerate(full_logs):
            if re.search(r'%s' % sdaparsepattern["service_request"], lines):
                next_line = full_logs[(index + 2) % len(full_logs)]
                if prov_task_id and re.search(r'%s' % prov_task_id, next_line):
                    # next_line = logs[(index + 4) % len(logs)]
                    output.append("REQUEST JSON:" + full_logs[(index + 4) % len(full_logs)])

    logs = read_logs(log_files, prov_task_id, is_dm_parse)
    if logs:
        for index, lines in enumerate(logs):
            if re.search(r'%s' % sdaparsepattern["create"], lines):
                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                global count_func
                global count_success
                global count_failure

                count_func += 1
                print("\n\t\t\tFound Task  " + str(count_func) + " from current SPF Log File" + "\n")
                output.append("\t\t\tPROVISIONING OPERATION STARTED for " + prov_task_id + " at " + start_time)

            if re.search(r'%s' % sdaparsepattern["submit_rfs"], lines):
                dm_logs = []
                for dm_logfile in dm_log_files:
                    with open("%s" % dm_logfile, "r") as file:
                        dm_lines = file.readlines()
                        for dm_line in dm_lines:
                            dm_logs.append(dm_line)
                dm_output = parse_log_fn(dm_log_files, dm_logs, dm_log_files, prov_task_id, True)
                for dm_item in dm_output:   
                    output.append(dm_item)

            if re.search(r'%s' % sdaparsepattern["step_string"], lines):
                stepStr = re.findall(r'spf.(\w+)', lines)[0]
                step_taskId = re.findall(r'taskId : ((?:\w+-)+\w+)', lines)[0]
                if stepStr:
                    output.append("\t\t\tInside step " + stepStr + "\t: task Id for this step:" + step_taskId)
                if step_taskId:
                    subtask_logs = read_subtask_logs_with_taskId(full_logs, step_taskId)
                    if (subtask_logs and subtask_logs[0]):
                        isFailed = False
                        task_result_str = 'Task Result Status:'
                        task_thread_error_str = 'ERROR | '
                        for lines in subtask_logs[0]:
                            if re.search(r'%s' % sdaparsepattern["task_result_stauts"], lines):
                                func = re.findall(r"%s" % sdaparsepattern["task_result_stauts"], lines)[0]
                                if func:
                                    task_result = re.findall(r'Task Result Status: (.*)', lines)[0]
                                    task_result_str += task_result
                                    if task_result and not task_result.startswith("SUCCESS"):
                                        isFailed = True
                                        task_thread_line = re.findall(r'(.*)Task Result Status:', lines)[0]
                                        if task_thread_line and task_thread_line.split('|'):
                                            task_thread_error_str += task_thread_line.split('|')[2]
                        if isFailed == True:
                            log_chunk = read_log_sub(full_logs, subtask_logs[1], subtask_logs[2])
                            # output.append(log_chunk)
                            if (log_chunk):
                                recordException = False
                                exception_stacktrace = []
                                for index, lines in enumerate(log_chunk):
                                    if re.search(r'%s' % sdaparsepattern["error_response"], lines):
                                        output.append(log_chunk[index])
                                        next_line = log_chunk[(index + 1) % len(log_chunk)]
                                        val = re.findall(r'%s' % sdaparsepattern["exception"], next_line)
                                        if val:
                                            recordException = True
                                            continue
                                    if re.search(r'%s' % task_thread_error_str, lines):
                                        error_log_chunk = re.findall(r"%s" % task_thread_error_str, lines)
                                        if error_log_chunk:
                                            output.append(log_chunk[index])
                                            next_line = log_chunk[(index + 1) % len(log_chunk)]
                                            val = re.findall(r'%s' % sdaparsepattern["exception"], next_line)
                                            if val:
                                                recordException = True
                                                continue
                                    if len(lines) > 0 and not lines[0].lstrip().isdigit() and recordException:
                                        exception_stacktrace.append(log_chunk[index])
                                    if len(lines) > 0 and lines[0].lstrip().isdigit() and recordException:
                                        recordException = False
                                        for stacktrace in exception_stacktrace:
                                            output.append(stacktrace)
                                        exception_stacktrace = []

            if re.search(r'%s' % sdaparsepattern["acquire_lock_time"], lines):
                func = re.findall(r"%s" % sdaparsepattern["acquire_lock_time"], lines)[0]
                in_time = re.findall(r'is (\d+) secs', lines)[0]
                if int(in_time) == 0:
                    output.append(
                        "\t\t\tTIME TAKEN TO ACQUIRE LOCK for " + prov_task_id + " is " + in_time + " seconds")
                else:
                    output.append(
                        color.RED + "\t\t\tTIME TAKEN TO ACQUIRE LOCK for " + prov_task_id + " is " + in_time + " seconds" + color.END)

            if re.search(r'%s' % sdaparsepattern["complete"], lines):
                func = re.findall(r"%s" % sdaparsepattern["complete"], lines)[0]
                if func:
                    find_failure_reason = re.findall(r'failureReason=(\w+)', lines)
                    if not find_failure_reason:
                        find_failure_reason = re.findall(r'failureReason==>\s(\w+)', lines)
                    if not find_failure_reason:
                        break
                    else:
                        in_time = find_failure_reason[0]
                        if not in_time:
                            break
                        else:
                            if in_time == "null":
                                start_time = re.findall(r"(\d+[-]\d+[-]\d+[ ]\d+[:]\d+[:]\d+)", lines)[0]
                                count_success += 1
                                output.append(
                                    color.BOLD + "\t\t\tPROVISIONING OPERATION STATUS CODE = SUCCESS" + " at " + start_time + color.END)

                            else:
                                if re.search(r'failureReason=(.*)errorCode', lines):
                                    msg = re.findall(r'failureReason=(.*)errorCode', lines)
                                    if msg:
                                        count_failure += 1
                                        output.append(
                                            color.RED + "\t\t\tPROVISIONING OPERATION STATUS FAILURE WITH FAILURE REASON " +
                                            msg[0] + color.END)
                                        output.append(color.RED + lines + color.END)

                else:
                    output.append(color.RED + "\t\t\tNO PROVISIONING OOPERATION COMPLETIION FOUND " + color.END)



        if not is_dm_parse:
            file = open(ispf_ser_log_file, "a+")
            for item in output:
                file.write("%s\n" % item)
                if (str(item).startswith("REQUEST JSON:")):
                    json_output = str(item)
                    json_start_index = json_output.find("[")
                    print("REQUEST JSON:")
                    pp.pprint(json_output[json_start_index:len(json_output) - 1])
                else:
                    print(item)
            file.close()
        else:
            return output



def read_logs(log_files, prov_task_id, is_dm_parse):
    logs = []
    for logfile in log_files:
        with open("%s" % logfile, "r") as file:
            lines = file.readlines()

            device_id = None
            if not is_dm_parse:
                for line in lines:
                    if not re.search(r'%s' % sdaparsepattern["create"], line) and \
                            re.search(r'\s%s\s' % prov_task_id, line):
                        # device_id = re.findall(r"deviceId: (\d+)", line)[0]
                        break


            for line in lines:
                if prov_task_id and re.search(r'%s' % prov_task_id, line):
                    logs.append(line)

                elif prov_task_id and re.search(r'%s' % sdaparsepattern["exception"], line):
                    logs.append(line)
    # print(logs)
    return logs


def parse_tasks_fn(sm_log_files, dm_log_files, taskid):
    sm_logs = []


    prov_task_ids = []
    if(taskid !=""):
        prov_task_ids.append(taskid)
    for sm_logfile in sm_log_files:
        with open("%s" % sm_logfile, "r") as file:
            lines = file.readlines()
            for line in lines:
                sm_logs.append(line)
                if taskid == "" and re.search(r'%s' % sdaparsepattern["create"], line):
                    val = re.findall(r'Creating task: (\w+[-]\w+[-]\w+[-]\w+[-]\w+)', line)[0]
                    if val not in prov_task_ids:
                        prov_task_ids.append(val)




    for prov_task_id in prov_task_ids:
        parse_log_fn(sm_log_files, sm_logs, dm_log_files, prov_task_id, False)
        print("*" * 175)

    print(color.GREEN + "\n\n\t\t\tTotal Processsed Task for this SPF service log file = " + str(count_func) +
          "\n\n")


def main_fn(params):
    """
    Start Method
    :param params:
    :return:
    """
    sm_log_files = []
    dm_log_files = []
    taskid = ""
    if params.taskid:
        taskid = params.taskid
    if params.rca:
        tar = tarfile.open('%s' % params.rca, 'r:gz')
        tar.extractall()
        base_name = os.path.basename(params.rca)
        folder_name = os.path.splitext(os.path.splitext(base_name)[0])[0]

        sm_log_path = 'data/rca/' + folder_name \
                   + sm_log_file_name_template
        dm_log_path = 'data/rca/' + folder_name \
                      + dm_log_file_name_template
        sm_log_files = glob.glob(sm_log_path)
        dm_log_files = glob.glob(dm_log_path)
        tar.close()
        parse_tasks_fn(sm_log_files, dm_log_files, taskid)

    elif params.logfolder:
        sm_log_path = params.logfolder + sm_log_file_name_template
        dm_log_path = params.logfolder + dm_log_file_name_template
        print(sm_log_path)
        print(dm_log_path)
        sm_log_files = glob.glob(sm_log_path)
        dm_log_files = glob.glob(dm_log_path)
        print(sm_log_files)
        print(dm_log_files)
        parse_tasks_fn(sm_log_files, dm_log_files, taskid)


    else:
        print('Pass the spf-service log file or RCA')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='Example usage: ./invoker.py --log apic-em-network-programmer-service.log ')
    parser.add_argument('--rca', help='give the RCA maglev-<cluster_ip>-rca... .tar.gz file')
    parser.add_argument('--logfolder', help='specify local folder path of log file')
    parser.add_argument('--taskid', help='specify the taskId')
    args = parser.parse_args()
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    main_fn(args)
