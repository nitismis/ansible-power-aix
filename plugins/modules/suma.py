#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020- IBM, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
author:
- AIX Development Team (@pbfinley1911)
module: suma
short_description: Download/Install fixes, SP or TL from IBM Fix Central website.
description:
- Service Update Management Assistant (SUMA) sets up an automated interface to download fixes from
  the IBM Fix Central website to your systems.
- SUMA provides flexible, task-based options to periodically check the availability of specific new
  fixes, technology levels (TL) and service packs (SP). Therefore, system administrators do not have
  to manually retrieve maintenance updates.
version_added: '0.4.0'
requirements:
- AIX >= 7.1 TL3
- Python >= 3.6
- 'Privileged user with authorizations: B(aix.system.install)'
options:
  action:
    description:
    - Controls the SUMA action to be performed.
    - C(download) specifies to download and install the fixes.
    - C(preview) specifies to execute all the checks without downloading the fixes.
    - C(list) specifies to list all SUMA tasks.
    - C(edit) specifies to edit an exiting SUMA task.
    - C(run) specifies to run an exiting SUMA task.
    - C(unschedule) specifies to remove any scheduling information for the specified SUMA task.
    - C(delete) specifies to delete a SUMA task and remove any schedules for the specified SUMA task.
    - C(config) specifies to list global SUMA configuration settings.
    - C(default) specifies to list default SUMA tasks.
    type: str
    choices: [ download, preview, list, edit, run, unschedule, delete, config, default ]
    default: preview
  oslevel:
    description:
    - Specifies the Operating System level to update to;
    - C(Latest) specifies to update the target to the latest SP suma can update for the current TL.
    - C(xxxx-xx(-00-0000)) specifies to update the target to a specific TL.
    - C(xxxx-xx-xx-xxxx) or C(xxxx-xx-xx) specifies to update the target to a specific SP.
    - Required when I(action=download) or I(action=preview).
    type: str
    default: Latest
  download_dir:
    description:
    - Specifies the directory to download updates files into.
    - Can be used if I(action=download) or I(action=preview).
    type: path
    default: /usr/sys/inst.images
  download_only:
    description:
    - Specifies to perform the preview and download operation only. Do not install the updates.
    - Can be used if I(action=download) or I(action=preview).
    type: bool
    default: no
  last_sp:
    description:
    - Specifies to download the last SP of the TL specified in I(oslevel).
    - When I(last_sp=no), only the TL is downloaded and/or installed.
    - Can be used if I(action=download) or I(action=preview).
    type: bool
    default: no
  extend_fs:
    description:
    - Specifies to automatically extends the filesystem if extra space is needed.
    - When I(extend_fs=no) and additional space is required for the download, no download occurs.
    - When set, a filesystem could have increased while the task returns I(changed=False).
    - Can be used if I(action=download) or I(action=preview).
    type: bool
    default: yes
  task_id:
    description:
    - Specifies the SUMA task identification number.
    - Can be used if I(action=list) or I(action=edit) or I(action=delete) or I(action=run) or
      I(action=unschedule).
    - Required when I(action=edit) or I(action=delete) or I(action=run) or I(action=unschedule).
    type: str
  sched_time:
    description:
    - Specifies the schedule time for the task.
    - When an empty or space filled string is specified, it unschedules the task.
    - When not set, it saves the task for later scheduling.
    - Can be used if I(action=edit).
    type: str
  save_task:
    description:
    - Specifies to save the SUMA task allowing scheduling information to be added later.
    - Can be used if I(action=download) or I(action=preview).
    - If I(oslevel) is a TL and I(last_sp=yes) the task is saved with the last SP available at the
      time the task is saved.
    type: bool
    default: no
  description:
    description:
    - Specifies the display name for SUMA task. This is used when viewing existing SUMA tasks in
      SMIT for example.
    - If not set they will be labelled as 'I(action) request for oslevel I(oslevel)'.
    - Can be used for I(action=download) or I(action=preview).
    type: str
  metadata_dir:
    description:
    - Specifies the directory where metadata files are downloaded.
    - Can be used if I(action=download) or I(action=preview) when I(last_sp=yes) or I(oslevel) is
      not exact, for example I(oslevel=Latest).
    type: path
    default: /var/adm/ansible/metadata
notes:
  - The B(/var/adm/ras/suma.log) file on your system contains detailed results from running the SUMA
    command.
  - The B(/var/adm/ras/suma_dl.log) file on your system contains a list of files that have been
    downloaded.
  - When you configure SUMA in an AIX logical partition (LPAR) or as the NIM master, it establishes
    a connection to the fix distribution website and downloads the available service update. The fix
    distribution website is an IBM server with the domain name of esupport.ibm.com. If your
    configuration contains a firewall that blocks the connection to the fix distribution website,
    you must customize the firewall rules to allow SUMA to connect to the following IP addresses
    129.42.56.189, 129.42.60.189, 129.42.54.189. SUMA connects to one of these IP addresses based on
    your geography.
  - You can refer to the IBM documentation for additional information on the SUMA command and
    configuration settings at
    U(https://www.ibm.com/support/knowledgecenter/ssw_aix_72/s_commands/suma.html).
  - If you hit the known bug that prevents suma from running successfully, contact IBM AIX support
    and request and ifix for this problem (APAR IJ06197 SUMA MAY CAUSE A NULLPOINTEREXCEPTION) at
    U(http://www-01.ibm.com/support/docview.wss?uid=isg1IJ06197).
  - To get assistance for SUMA errors through AIX Support refer to
    U(https://www-01.ibm.com/support/docview.wss?uid=ibm10719985).
'''

EXAMPLES = r'''
- name: Check, download and install system updates for the current oslevel of the system
  suma:
    action: download
    oslevel: Latest
    download_dir: /usr/sys/inst.images

- name: Check and download required to update to SP 7.2.3.2
  suma:
    action: download
    oslevel: '7200-03-02'
    download_only: true
    download_dir: /tmp/dl_updt_7200-03-02
  when: ansible_distribution == 'AIX'

- name: Check, download and install to latest SP of TL 7.2.4
  suma:
    action: download
    oslevel: '7200-04'
    last_sp: true
    extend_fs: false

- name: Check, download and install to TL 7.2.3
  suma:
    action: download
    oslevel: '7200-03'
'''

RETURN = r'''
msg:
    description: The execution message.
    returned: always
    type: str
    sample: 'Suma preview completed successfully'
cmd:
    description: The command executed.
    returned: if a command was run.
    type: str
stdout:
    description: The standard output of the command.
    returned: always
    type: str
stderr:
    description: The standard error of the command.
    returned: always
    type: str
meta:
    description: Detailed information on the module execution.
    returned: always
    type: dict
    contains:
        messages:
            description: Details on errors/warnings/information
            returned: always
            type: list
            elements: str
            sample: "Parameter last_sp=yes is ignored when oslevel is a TL 7200-02-00"
    sample:
        "meta": {
            "messages": [
                "Parameter last_sp=yes is ignored when oslevel is a TL ",
                "Suma metadata: 7200-02-01-1732 is the latest SP of TL 7200-02",
                ...,
            ]
        }
'''


import os
import re
import glob
import shutil

from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type


module = None
results = None
suma_params = {}


def compute_rq_type(oslevel, last_sp):
    """
    Compute rq_type to use in a suma request based on provided oslevel.
    arguments:
        oslevel level of the OS
        last_sp boolean specifying if we should get the last SP
    return:
        Latest when oslevel is blank or latest (not case sensitive)
        SP     when oslevel is a TL (6 digits: xxxx-xx) and last_sp==True
        TL     when oslevel is xxxx-xx(-00-0000)
        SP     when oslevel is xxxx-xx-xx(-xxxx)
        ERROR  when oslevel is not recognized
    """

    if oslevel is None or not oslevel.strip() or oslevel == 'Latest':
        return 'Latest'
    if re.match(r"^([0-9]{4}-[0-9]{2})$", oslevel) and last_sp:
        return 'SP'
    if re.match(r"^([0-9]{4}-[0-9]{2})(|-00|-00-0000)$", oslevel):
        if last_sp:
            msg = f"Parameter last_sp={last_sp} is ignored when oslevel is a TL {oslevel}."
            module.log(msg)
            results['meta']['messages'].append(msg)
        return 'TL'
    if re.match(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})(|-[0-9]{4})$", oslevel):
        return 'SP'

    return 'ERROR'


def find_sp_version(file):
    """
    Open and parse the provided file to find higher SP version
    arguments:
        file    path of the file to parse
    return:
       sp_version   value found or None
    """
    sp_version = ""
    module.debug(f"opening file: {file}")
    with open(file, mode="r", encoding="utf-8") as myfile:
        for line in myfile:
            # module.debug("line: {0}".format(line.rstrip()))
            match_item = re.match(
                r"^<SP name=\"([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{4})\">$",
                line.rstrip())
            if match_item:
                version = match_item.group(1)
                debug_line = line.rstrip()
                module.debug(f"matched line: {debug_line}, version={version}")
                if sp_version == "" or version > sp_version:
                    sp_version = version
                break

    return sp_version


def compute_rq_name(rq_type, oslevel, last_sp):
    """
    Compute rq_name.
        if oslevel is a TL then return the SP extratced from it
        if oslevel is a complete SP (12 digits) then return RqName = oslevel
        if oslevel is an incomplete SP (8 digits) or equal Latest then execute
        a metadata suma request to find the complete SP level (12 digits).
    The return format depends on rq_type value,
        - for Latest: return None
        - for TL: return the TL value in the form xxxx-xx
        - for SP: return the SP value in the form xxxx-xx-xx-xxxx

    arguments:
        rq_type     type of request, can be Latest, SP or TL
        oslevel     requested oslevel
        last_sp     if set get the latest SP level for specified oslevel
    note:
        Exits with fail_json in case of error
    return:
       rq_name value
    """

    rq_name = ''
    if rq_type == 'Latest':
        return None

    if rq_type == 'TL':
        rq_name = re.match(r"^([0-9]{4}-[0-9]{2})(|-00|-00-0000)$",
                           oslevel).group(1)

    elif rq_type == 'SP' and re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{4}$", oslevel):
        rq_name = oslevel

    else:
        # oslevel has either a TL format (xxxx-xx) or a short SP format (xxxx-xx-xx)

        # Build the FilterML for metadata request from the oslevel
        metadata_filter_ml = oslevel[:7]
        if not metadata_filter_ml:
            msg = f"Cannot build minimum level filter based on the target OS level {oslevel}"
            module.log(msg)
            results['msg'] = msg
            module.fail_json(**results)

        if not os.path.exists(suma_params['metadata_dir']):
            os.makedirs(suma_params['metadata_dir'])

        DLTarget = suma_params['metadata_dir']
        DisplayName = suma_params['description']
        FilterDir = suma_params['metadata_dir']

        cmd = ['/usr/sbin/suma', '-x', '-a', 'Action=Metadata', '-a', 'RqType=Latest']
        cmd += ['-a', f'DLTarget={DLTarget}']
        cmd += ['-a', f'FilterML={metadata_filter_ml}']
        cmd += ['-a', f'DisplayName="{DisplayName}"']
        cmd += ['-a', f'FilterDir={FilterDir}']

        rc, stdout, stderr = module.run_command(cmd)
        if rc != 0:
            msg_cmd = ' '.join(cmd)
            msg = f"Suma metadata command '{msg_cmd}' failed with return code {rc}"
            module.log(msg + f", stderr: {stderr}, stdout:{stdout}".format(stderr, stdout))
            results['cmd'] = ' '.join(cmd)
            results['stdout'] = stdout
            results['stderr'] = stderr
            results['msg'] = msg
            module.fail_json(**results)
        debug_cmd = ' '.join(cmd)
        module.debug(f"SUMA command '{debug_cmd}' rc:{rc}, stdout:{stdout}")

        sp_version = ""
        if len(oslevel) == 10:
            # find latest SP build number for the SP
            file_name = suma_params['metadata_dir'] + "/installp/ppc/" + oslevel + ".xml"
            sp_version = find_sp_version(file_name)
        else:
            # find latest SP build number for the TL
            file_name = suma_params['metadata_dir'] + "/installp/ppc/" + "*.xml"
            files = glob.glob(file_name)
            module.debug(f"searching SP in files: {files}")
            for cur_file in files:
                version = find_sp_version(cur_file)
                if sp_version == "" or version > sp_version:
                    sp_version = version

        if sp_version is None or not sp_version.strip():
            msg = f"Cannot determine SP version for OS level {oslevel}: \
                'SP name' not found in metadata files {files}"
            module.log(msg)
            results['msg'] = msg
            module.fail_json(**results)

        shutil.rmtree(suma_params['metadata_dir'])

        rq_name = sp_version
        msg = f'Suma metadata: {rq_name} is the latest SP of {oslevel}'
        module.log(msg)
        results['meta']['messages'].append(msg)

    if not rq_name or not rq_name.strip():  # should never happen
        msg_oslevel = suma_params['oslevel']
        msg = f"OS level {msg_oslevel} does not match any fixes"
        msg += f"Last sp is {last_sp}"
        module.log(msg)
        results['msg'] = msg
        module.fail_json(**results)

    return rq_name


def suma_command(action):
    """
    Run a suma command.

    arguments:
        action   preview, download or install
    note:
        Exits with fail_json in case of error
    return:
       stdout  suma command output
    """

    rq_type = suma_params['RqType']
    DLTarget = suma_params['DLTarget']
    description = suma_params['description']
    FilterDir = suma_params['DLTarget']
    RqName = suma_params['RqName']
    cmd = ['/usr/sbin/suma', '-x', '-a', f'RqType={rq_type}']
    cmd += ['-a', f'Action={action}']
    cmd += ['-a', f'DLTarget={DLTarget}']
    cmd += ['-a', f'DisplayName={description}']
    cmd += ['-a', f'FilterDir={FilterDir}']

    if rq_type != 'Latest':
        cmd += ['-a', f'RqName={RqName}']

    if suma_params['extend_fs']:
        cmd += ['-a', 'Extend=y']
    else:
        cmd += ['-a', 'Extend=n']

    # save the task only if that's the last action
    if suma_params['action'].upper() == action.upper() and suma_params['save_task']:
        cmd += ['-w']

    info_cmd = ' '.join(cmd)
    module.debug(f"SUMA - Command:{info_cmd}")
    results['meta']['messages'].append(f"SUMA - Command: {info_cmd}")

    rc, stdout, stderr = module.run_command(cmd)
    results['cmd'] = ' '.join(cmd)
    results['stdout'] = stdout
    results['stderr'] = stderr
    if rc != 0:
        msg = f"Suma {action} command '{info_cmd}' failed with return code {rc}"
        module.log(msg + f", stderr: {stderr}, stdout:{stdout}")
        results['msg'] = msg
        module.fail_json(**results)

    return stdout


def suma_list():
    """
    List all SUMA tasks or the task associated with the given task ID

    note:
        Exits with fail_json in case of error
    """

    task = suma_params['task_id']
    if task is None or not task.strip():
        cmd = ['/usr/sbin/suma', '-L']
    else:
        cmd = ['/usr/sbin/suma', '-L', task]

    rc, stdout, stderr = module.run_command(cmd)

    results['cmd'] = ' '.join(cmd)
    results['stdout'] = stdout
    results['stderr'] = stderr

    if rc != 0:
        info_cmd = results['cmd']
        msg = f"Suma list command '{info_cmd}' failed with return code {rc}"
        module.log(msg + f", stderr: {stderr}, stdout:{stdout}")
        results['msg'] = msg
        module.fail_json(**results)


def check_time(val, mini, maxi):
    """
    Check a value is equal to '*' or is a numeric value in the
    [mini, maxi] range

    arguments:
        val     value to check
        mini    range minimal value
        mini    range maximal value
    """
    if val == '*':
        return True

    if val.isdigit() and mini <= int(val) and maxi >= int(val):
        return True

    return False


def suma_edit():
    """
    Edit a SUMA task associated with the given task ID

    Depending on the shed_time parameter value, the task wil be scheduled,
        unscheduled or saved

    note:
        Exits with fail_json in case of error
    """

    cmd = '/usr/sbin/suma'
    sched_time = suma_params['sched_time']
    if suma_params['sched_time'] is None:
        # save
        cmd += ' -w'

    elif not suma_params['sched_time'].strip():
        # unschedule
        cmd += ' -u'

    else:
        # schedule
        minute, hour, day, month, weekday = suma_params['sched_time'].split(' ')

        if check_time(minute, 0, 59) and check_time(hour, 0, 23) \
           and check_time(day, 1, 31) and check_time(month, 1, 12) \
           and check_time(weekday, 0, 6):

            cmd += f' -s "{sched_time}"'
        else:
            info_cmd = ' '.join(cmd)
            msg = f"Suma edit command '{info_cmd}' failed: Bad schedule time '{sched_time}'"
            module.log(msg)
            results['msg'] = msg
            module.fail_json(**results)

    task_id = suma_params['task_id']
    cmd += f' {task_id}'
    rc, stdout, stderr = module.run_command(cmd)

    results['cmd'] = cmd
    results['stdout'] = stdout
    results['stderr'] = stderr

    if rc != 0:
        msg = f"Suma edit command '{cmd}' failed with return code {rc}"
        module.log(msg + f", stderr: {stderr}, stdout:{stdout}")
        results['msg'] = msg
        module.fail_json(**results)


def suma_unschedule():
    """
    Unschedule a SUMA task associated with the given task ID

    note:
        Exits with fail_json in case of error
    """

    task_id = suma_params['task_id']
    cmd = f"/usr/sbin/suma -u {task_id}"
    rc, stdout, stderr = module.run_command(cmd)

    results['cmd'] = cmd
    results['stdout'] = stdout
    results['stderr'] = stderr

    if rc != 0:
        msg = f"Suma unschedule command '{cmd}' failed with return code {rc}"
        module.log(msg + f", stderr: {stderr}, stdout:{stdout}")
        results['msg'] = msg
        module.fail_json(**results)


def suma_delete():
    """
    Delete the SUMA task associated with the given task ID

    note:
        Exits with fail_json in case of error
    """

    task_id = suma_params['task_id']
    cmd = f"/usr/sbin/suma -d {task_id}"
    rc, stdout, stderr = module.run_command(cmd)

    results['cmd'] = cmd
    results['stdout'] = stdout
    results['stderr'] = stderr

    if rc != 0:
        msg = f"Suma delete command '{cmd}' failed with return code {rc}"
        module.log(msg + f", stderr: {stderr}, stdout:{stdout}")
        results['msg'] = msg
        module.fail_json(**results)


def suma_run():
    """
    Run the SUMA task associated with the given task ID

    note:
        Exits with fail_json in case of error
    """

    task_id = suma_params['task_id']
    cmd = f"/usr/sbin/suma -x {task_id}"
    rc, stdout, stderr = module.run_command(cmd)

    results['cmd'] = cmd
    results['stdout'] = stdout
    results['stderr'] = stderr

    if rc != 0:
        msg = f"Suma run command '{cmd}' failed with return code {rc}"
        module.log(msg + f", stderr: {stderr}, stdout:{stdout}")
        results['msg'] = msg
        module.fail_json(**results)


def suma_config():
    """
    List the SUMA global configuration settings

    note:
        Exits with fail_json in case of error
    """

    cmd = '/usr/sbin/suma -c'
    rc, stdout, stderr = module.run_command(cmd)

    results['cmd'] = cmd
    results['stdout'] = stdout
    results['stderr'] = stderr

    if rc != 0:
        msg = f"Suma config command '{cmd}' failed with return code {rc}"
        module.log(msg + f", stderr: {stderr}, stdout:{stdout}")
        results['msg'] = msg
        module.fail_json(**results)


def suma_default():
    """
    List default SUMA tasks

    note:
        Exits with fail_json in case of error
    """

    cmd = '/usr/sbin/suma -D'
    rc, stdout, stderr = module.run_command(cmd)

    results['cmd'] = cmd
    results['stdout'] = stdout
    results['stderr'] = stderr

    if rc != 0:
        msg = f"Suma list default command '{cmd}' failed with return code {rc}"
        module.log(msg + f", stderr: {stderr}, stdout:{stdout}")
        results['msg'] = msg
        module.fail_json(**results)


def suma_download():
    """
    Download / Install (or preview) action

    suma_params['action'] should be set to either 'preview' or 'download'.

    First compute all Suma request options. Then preform a Suma preview, parse
    output to check there is something to download, if so, do a suma download
    if needed (if action is Download). If suma download output mentions there
    is downloaded items, then use install_all_updates command to install them.

    note:
        Exits with fail_json in case of error
    """

    # Check oslevel format
    if not suma_params['oslevel'].strip() or suma_params['oslevel'].upper() == 'LATEST':
        suma_params['oslevel'] = 'Latest'
    else:
        if re.match(r"^[0-9]{4}(|-00|-00-00|-00-00-0000)$", suma_params['oslevel']):
            msg_oslevel = suma_params['oslevel']
            msg = f"Bad parameter: oslevel is '{msg_oslevel}', \
                specify a non 0 value for the Technical Level or the Service Pack"
            module.log(msg)
            results['msg'] = msg
            module.fail_json(**results)
        elif not re.match(r"^[0-9]{4}-[0-9]{2}(|-[0-9]{2}|-[0-9]{2}-[0-9]{4})$",
                          suma_params['oslevel']):
            msg_oslevel = suma_params['oslevel']
            msg = f"Bad parameter: oslevel is '{msg_oslevel}', \
                should repect the format: xxxx-xx or xxxx-xx-xx or xxxx-xx-xx-xxxx"
            module.log(msg)
            results['msg'] = msg
            module.fail_json(**results)

    # =========================================================================
    # compute SUMA request type based on oslevel property
    # =========================================================================
    rq_type = compute_rq_type(suma_params['oslevel'], suma_params['last_sp'])
    if rq_type == 'ERROR':
        msg_oslevel = suma_params['oslevel']
        msg = f"Bad parameter: oslevel is '{msg_oslevel}', parsing error"
        module.log(msg)
        results['msg'] = msg
        module.fail_json(**results)

    suma_params['RqType'] = rq_type
    module.debug(f"SUMA req Type: {rq_type}")

    # =========================================================================
    # compute SUMA request name based on metadata info
    # =========================================================================
    suma_params['RqName'] = compute_rq_name(rq_type, suma_params['oslevel'], suma_params['last_sp'])
    debug_rqname = suma_params['RqName']
    module.debug(f"Suma req Name: {debug_rqname}")

    # =========================================================================
    # compute suma dl target
    # =========================================================================
    if not suma_params['download_dir']:
        msg_action = suma_params['action']
        msg_download_dir = suma_params['download_dir']
        msg = f"Bad parameter: action is {msg_action} but download_dir is '{msg_download_dir}'"
        module.log(msg)
        results['msg'] = msg
        module.fail_json(**results)
    else:
        suma_params['DLTarget'] = suma_params['download_dir'].rstrip('/')

    log_DLTarget = suma_params['DLTarget']
    module.log(f"The download location will be: {log_DLTarget}.")
    if not os.path.exists(suma_params['DLTarget']):
        os.makedirs(suma_params['DLTarget'])

    # ========================================================================
    # SUMA command for preview
    # ========================================================================
    stdout = suma_command('Preview')
    module.debug(f"SUMA preview stdout:{stdout}")

    # parse output to see if there is something to download
    downloaded = 0
    failed = 0
    skipped = 0
    for line in stdout.rstrip().splitlines():
        line = line.rstrip()
        matched = re.match(r"^\s+(\d+)\s+downloaded$", line)
        if matched:
            downloaded = int(matched.group(1))
            continue
        matched = re.match(r"^\s+(\d+)\s+failed$", line)
        if matched:
            failed = int(matched.group(1))
            continue
        matched = re.match(r"^\s+(\d+)\s+skipped$", line)
        if matched:
            skipped = int(matched.group(1))

    msg = f"Preview summary : {downloaded} to download, {failed} failed, {skipped} skipped"
    module.log(msg)

    # If action is preview or nothing is available to download, we are done
    if suma_params['action'] == 'preview':
        results['meta']['messages'].append(msg)
        return
    if downloaded == 0 and skipped == 0:
        return
    # else continue
    results['meta']['messages'].extend(stdout.rstrip().splitlines())
    results['meta']['messages'].append(msg)

    # ================================================================
    # SUMA command for download
    # ================================================================
    if downloaded != 0:
        stdout = suma_command('Download')
        module.debug(f"SUMA dowload stdout:{stdout}")

        # parse output to see if something has been downloaded
        downloaded = 0
        failed = 0
        skipped = 0
        for line in stdout.rstrip().splitlines():
            line = line.rstrip()
            matched = re.match(r"^\s+(\d+)\s+downloaded$", line)
            if matched:
                downloaded = int(matched.group(1))
                continue
            matched = re.match(r"^\s+(\d+)\s+failed$", line)
            if matched:
                failed = int(matched.group(1))
                continue
            matched = re.match(r"^\s+(\d+)\s+skipped$", line)
            if matched:
                skipped = int(matched.group(1))

        msg = f"Download summary : {downloaded} downloaded, {failed} failed, {skipped} skipped"
        if downloaded == 0 and skipped == 0:
            # All expected download have failed
            module.log(msg)
            results['meta']['messages'].append(msg)
            return

        module.log(msg)
        results['meta']['messages'].extend(stdout.rstrip().splitlines())
        results['meta']['messages'].append(msg)

        if downloaded != 0:
            results['changed'] = True

    # ===========================================================
    # Install updates
    # ===========================================================
    if not suma_params['download_only']:
        cmd_DLTarget = suma_params['DLTarget']
        cmd = f"/usr/sbin/install_all_updates -Yd {cmd_DLTarget}"

        module.debug(f"SUMA command:{cmd}")
        results['meta']['messages'].append(msg)

        rc, stdout, stderr = module.run_command(cmd)

        results['cmd'] = cmd
        results['stdout'] = stdout
        results['stderr'] = stderr
        results['changed'] = True

        if rc != 0:
            msg = f"Suma install command '{cmd}' failed with return code {rc}."
            module.log(msg + f", stderr:{stderr}, stdout:{stdout}")
            results['msg'] = msg
            module.fail_json(**results)

        module.log(f"Suma install command output: {stdout}")


##############################################################################

def main():
    global module
    global results

    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=False,
                        choices=['download', 'preview', 'list', 'edit', 'run',
                                 'unschedule', 'delete', 'config', 'default'],
                        type='str', default='preview'),
            oslevel=dict(required=False, type='str', default='Latest'),
            last_sp=dict(required=False, type='bool', default=False),
            extend_fs=dict(required=False, type='bool', default=True),
            download_dir=dict(required=False, type='path', default='/usr/sys/inst.images'),
            download_only=dict(required=False, type='bool', default=False),
            save_task=dict(required=False, type='bool', default=False),
            task_id=dict(required=False, type='str'),
            sched_time=dict(required=False, type='str'),
            description=dict(required=False, type='str'),
            metadata_dir=dict(required=False, type='path', default='/var/adm/ansible/metadata'),
        ),
        required_if=[
            ['action', 'edit', ['task_id']],
            ['action', 'delete', ['task_id']],
            ['action', 'run', ['task_id']],
            ['action', 'download', ['oslevel']],
            ['action', 'preview', ['oslevel']],
            ['action', 'unschedule', ['task_id']],
        ],
        supports_check_mode=True
    )

    results = dict(
        changed=False,
        msg='',
        stdout='',
        stderr='',
        meta={'messages': []},
    )

    module.debug('*** START ***')
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    action = module.params['action']
    oslevel = module.params['oslevel']

    # switch action
    if action == 'list':
        suma_params['task_id'] = module.params['task_id']
        suma_list()

    elif action == 'edit':
        suma_params['task_id'] = module.params['task_id']
        suma_params['sched_time'] = module.params['sched_time']
        suma_edit()

    elif action == 'unschedule':
        suma_params['task_id'] = module.params['task_id']
        suma_unschedule()

    elif action == 'delete':
        suma_params['task_id'] = module.params['task_id']
        suma_delete()

    elif action == 'run':
        suma_params['task_id'] = module.params['task_id']
        suma_run()

    elif action == 'config':
        suma_config()

    elif action == 'default':
        suma_default()

    elif action == 'download' or action == 'preview':
        suma_params['oslevel'] = module.params['oslevel']
        suma_params['download_dir'] = module.params['download_dir']
        suma_params['metadata_dir'] = module.params['metadata_dir']
        suma_params['download_only'] = module.params['download_only']
        suma_params['save_task'] = module.params['save_task']
        suma_params['last_sp'] = module.params['last_sp']
        suma_params['extend_fs'] = module.params['extend_fs']
        if module.params['description']:
            suma_params['description'] = module.params['description']
        else:
            suma_params['description'] = f"{action} request for oslevel {oslevel}"

        suma_params['action'] = action
        suma_download()

    # Exit
    msg = f'Suma {action} completed successfully'
    module.log(msg)
    results['msg'] = msg
    module.exit_json(**results)


if __name__ == '__main__':
    main()
