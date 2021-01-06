import subprocess
import sys
import json

args = sys.argv

"""
Get commit hash list (following time flow)
"""
def get_filename():#使ってない
    file_list = subprocess.check_output(
            ['git', '-C', '{}'.format(args[1]), 'ls-files'],
            universal_newlines=True
            ).splitlines()
    return file_list

def get_all_hash():
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(args[1]), 'log', '--all', '--pretty=format:%H'],
            universal_newlines=True
            ).splitlines()
    hash_list.reverse()
    return hash_list

"""
Get commit message 
"""

def get_commit_message(commit_hash):
    commit_msg_list = subprocess.check_output(
            ['git', '-C', '{}'.format(args[1]), 'log', '--format=%B', '-n', '1', commit_hash],
            universal_newlines=True
            ).split()
    return commit_msg_list

def count_metrics(commit_hash):
    num = 0
    temp = get_commit_message(commit_hash)
    for item in range(len(temp)):
        if 'metrics' == temp[item]:
            num = num + 1
    return num

def get_all(commit_hash, file_name):
    temp = get_commit_message(commit_hash)
    print(temp)
    print(temp.index(file_name))



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
    file_name = get_filename()
    hash_list = get_all_hash()
    ddd = {}
    metrics_value = None

    with open(args[1] + '/test.json', 'w') as f:
        f.write('')

    keys = ['author_name', 'author_date', 'committer_name', 'committer_date', 'command',
            'parameter', 'original_file', 'metrics', 'metrics_value']

    for commit_hash in hash_list:
        dd = {}
        count = count_metrics(commit_hash)##使ってない
        temp = get_commit_message(commit_hash)

        for file_num in file_name:
            param = None
            file = None
            metrics = None
            metrics_value = None

            index_num = [n for n, v in enumerate(temp) if v == 'change']
            print(index_num)
            for j in index_num:
                if len(temp[j:]) >= 10:
                    if temp[j + 1] == 'param' and temp[j + 9] == file_num:
                        print('---a----')
                        param = temp[j + 2]
                        file = temp[j + 7]
                        print(param)
                        print(file)
                        print('---end----')
                        break

            index_num = [n for n, v in enumerate(temp) if v == 'metrics']
            for j in index_num:
                if len(temp[j:]) >= 5:
                    if temp[j + 4] == file_num:
                        print('---b----')
                        metrics = temp[j + 1]
                        metrics_value = temp[j + 2]
                        print(metrics)
                        print(metrics_value)
                        print('---end----')
                        break

            if metrics_value is None:
                print('breakします')
                print(param)
                print(file)
                print(metrics)
                print(metrics_value)
                break
            else:
                values = [git_log(commit_hash, '--format=%an'), git_log(commit_hash, '--format=%ad'),
                          git_log(commit_hash, '--format=%cn'), git_log(commit_hash, '--format=%cd'),
                          git_log(commit_hash, '--format=%s'), param, file, metrics, metrics_value]

            d = {file_num: dict(zip(keys, values))}
            dd.update(d)

        ddd[commit_hash] = dd
        print(ddd)

    with open(args[1] + '/test.json', 'a') as f:
        json.dump(ddd, f, indent=2, ensure_ascii=False)

    print('git_cmd.py')