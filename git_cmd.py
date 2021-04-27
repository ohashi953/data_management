import subprocess
import sys
import json
import datetime
import os

args = sys.argv
repo = "/Users/yukinaohashi/Desktop/cifar_project" #手動
"""
Get commit hash list (following time flow)
"""


def get_filename(repo):
    file_list = subprocess.check_output(
        ['git', '-C', '{}'.format(repo), 'ls-files'],
        universal_newlines=True
    ).splitlines()
    return file_list


def get_all_hash(repo):
    hash_list = subprocess.check_output(
        ['git', '-C', '{}'.format(repo), 'log', '--all', '--pretty=format:%H'],
        universal_newlines=True
    ).splitlines()
    hash_list.reverse()
    return hash_list


"""
Get commit message 
"""


def get_commit_message(commit_hash, repo):
    commit_msg_list = subprocess.check_output(
        ['git', '-C', '{}'.format(repo), 'log', '--format=%B', '-n', '1', commit_hash],
        universal_newlines=True
    )
    return commit_msg_list

"""
Get all logs
"""


def git_log(commit_hash, str, repo):
    log = subprocess.check_output(
        ['git', '-C', '{}'.format(repo), 'log', str, '-n', '1', commit_hash],
        universal_newlines=True
    )
    return log[:-1]


def git_clone():
    log = subprocess.check_output(
        ['git', 'clone', args[1]],
        universal_newlines=True
    )


if __name__ == '__main__':
    # jsonファイル作成
    file_name = get_filename(repo)
    hash_list = get_all_hash(repo)
    ddd = {}
    metrics_value = None

    with open(os.getcwd() + '/commit_log.json', 'w') as f:
        f.write('')

    keys = ['File_name', 'author_name', 'author_date', 'committer_name', 'committer_date', 'command',
            'parameter', 'parameter_change', 'original_file', 'metrics', 'metrics_value']

    for commit_hash in hash_list:
        dd = {}
        temp = get_commit_message(commit_hash, repo).split()

        for file_num in file_name:
            param = []
            change = []
            file = []
            metrics = []
            metrics_value = []

            index_num = [n for n, v in enumerate(temp) if v == 'change']
            for j in index_num:
                if len(temp[j:]) >= 10:
                    if temp[j + 1] == 'param' and (temp[j + 7] == file_num or temp[j + 9] == file_num):
                        param.append(temp[j + 2])
                        if temp[j + 4] == "to":
                            change.append(' '.join(temp[j+3:j+6]))
                        if temp[j + 6] != 'from': break
                        file.append(temp[j + 7])

            index_num = [n for n, v in enumerate(temp) if v == 'metrics']
            for j in index_num:
                if len(temp[j:]) >= 5:
                    if temp[j + 4] == file_num:
                        metrics.append(temp[j + 1])
                        metrics_value.append(temp[j + 2])

            if not metrics_value:
                continue
            else:
                values = [file_num, git_log(commit_hash, '--format=%an', repo), str(
                    datetime.datetime.strptime(git_log(commit_hash, '--format=%ad', repo), '%a %b %d %H:%M:%S %Y %z')),
                          git_log(commit_hash, '--format=%cn', repo), str(
                        datetime.datetime.strptime(git_log(commit_hash, '--format=%cd', repo), '%a %b %d %H:%M:%S %Y %z')),
                          get_commit_message(commit_hash, repo), param, change, file, metrics, metrics_value]
            d = {file_num: dict(zip(keys, values))}
            dd.update(d)

        ddd[commit_hash] = dd

    with open(os.getcwd() + '/commit_log.json', 'a') as f:
        json.dump(ddd, f, indent=2, ensure_ascii=False)

    print('git_cmd.py')
