import subprocess
import sys
import re
import json

args = sys.argv


"""
Get commit hash list (following time flow)
"""

def get_all_hash():
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(args[1]), 'log', '--all', '--pretty=format:%H'],
            universal_newlines=True
            ).splitlines()
    return hash_list
hash_list = get_all_hash()

"""
Get commit message 
"""

def get_commit_message(commit_hash):
    commit_msg_list = subprocess.check_output(
            ['git', '-C', '{}'.format(args[1]), 'log', '--format=%B', '-n', '1', commit_hash],
            universal_newlines=True
            ).splitlines()
    return commit_msg_list


def get_param(commit_hash):
    temp = get_commit_message(commit_hash)[0].split()
    return temp[0] if len(temp) < 2 else temp[2]

def get_file(commit_hash):
    temp = get_commit_message(commit_hash)[0].split()
    return temp[-1]

"""
Get all logs
"""

def git_log(commit_hash, str):
    log = subprocess.check_output(
            ['git', '-C', '{}'.format(args[1]), 'log', str , '-n', '1', commit_hash],
            universal_newlines=True
            )
    return log[:-1]

"""
Make json file
"""

with open(args[1] + '/test.json', 'w') as f:
    f.write('')

keys = ['author_name', 'author_date', 'committer_name', 'committer_date', 'command', 'parameter', 'original_file']

for log in range(len(hash_list)):
    values = [git_log(hash_list[log], '--format=%an'), git_log(hash_list[log], '--format=%ad'),
          git_log(hash_list[log], '--format=%cn'), git_log(hash_list[log], '--format=%cd'),
          git_log(hash_list[log], '--format=%s'), get_param(hash_list[log]), get_file(hash_list[log])]
    d = dict(zip(keys, values))

    with open(args[1]+'/test.json', 'a') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

    print(d)




