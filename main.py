import sys
import json
import git_cmd

args = sys.argv

"""
Make json file
"""
if __name__ == '__main__':
    file_name = git_cmd.get_filename()
    hash_list = git_cmd.get_all_hash()
    ddd = {}
    metrics_value = None

    with open(args[1] + '/test.json', 'w') as f:
        f.write('')

    keys = ['author_name', 'author_date', 'committer_name', 'committer_date', 'command',
            'parameter', 'original_file', 'metrics', 'metrics_value']

    for commit_hash in hash_list:
        dd = {}
        count = git_cmd.count_metrics(commit_hash)  ##使ってない
        temp = git_cmd.get_commit_message(commit_hash)

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
                        param = temp[j + 2]
                        file = temp[j + 7]
                        break

            index_num = [n for n, v in enumerate(temp) if v == 'metrics']
            for j in index_num:
                if len(temp[j:]) >= 5:
                    if temp[j + 4] == file_num:
                        metrics = temp[j + 1]
                        metrics_value = temp[j + 2]
                        break

            if metrics_value is None:
                break
            else:
                values = [git_cmd.git_log(commit_hash, '--format=%an'), git_cmd.git_log(commit_hash, '--format=%ad'),
                          git_cmd.git_log(commit_hash, '--format=%cn'), git_cmd.git_log(commit_hash, '--format=%cd'),
                          git_cmd.git_log(commit_hash, '--format=%s'), param, file, metrics, metrics_value]

            d = {file_num: dict(zip(keys, values))}
            dd.update(d)

        ddd[commit_hash] = dd
        print(ddd)

    with open(args[1] + '/test.json', 'a') as f:
        json.dump(ddd, f, indent=2, ensure_ascii=False)