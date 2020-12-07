import subprocess
import sys
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

"""
Get commit message 
"""

def get_commit_message(commit_hash):
    commit_msg_list = subprocess.check_output(
            ['git', '-C', '{}'.format(args[1]), 'log', '--format=%B', '-n', '1', commit_hash],
            universal_newlines=True
            ).splitlines()
    return commit_msg_list

#コミットメッセージから変更されたパラメータを取り出す(change param height = 0.1 to height = 0.2 from ?.ipynb ---> height)
def get_param(commit_hash):
    temp = get_commit_message(commit_hash)[0].split()
    return '' if len(temp) < 2 else temp[2] #temp[2]だけだと、list index out of range だと怒られたので一応場合わけ

#コミットメッセージから変更もとのファイルを取り出す(change param height = 0.1 to height = 0.2 from ?.ipynb ---> ?.ipynb)
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

if __name__ == '__main__':
    hash_list = get_all_hash()
    value = []
    dd = {}

    with open(args[1] + '/test.json', 'w') as f:
        f.write('')

    keys = ['author_name', 'author_date', 'committer_name', 'committer_date', 'command', 'parameter', 'original_file']

    for commit_hash in hash_list:
        values = [git_log(commit_hash, '--format=%an'), git_log(commit_hash, '--format=%ad'),
                  git_log(commit_hash, '--format=%cn'), git_log(commit_hash, '--format=%cd'),
                  git_log(commit_hash, '--format=%s'), get_param(commit_hash), get_file(commit_hash)]
        d = dict(zip(keys, values))
        dd[commit_hash] = d

    with open(args[1] + '/test.json', 'a') as f:
        json.dump(dd, f, indent=2, ensure_ascii=False)

    print('git_cmd.py')