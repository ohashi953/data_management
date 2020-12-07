import sys
import json
import git_cmd

args = sys.argv

"""
Make json file
"""
if __name__ == '__main__':
    hash_list = git_cmd.get_all_hash()
    value = []
    dd = {}

    with open(args[1] + '/test.json', 'w') as f:
        f.write('')

    keys = ['author_name', 'author_date', 'committer_name', 'committer_date', 'command', 'parameter', 'original_file']

    for commit_hash in hash_list:
        values = [git_cmd.git_log(commit_hash, '--format=%an'), git_cmd.git_log(commit_hash, '--format=%ad'),
                  git_cmd.git_log(commit_hash, '--format=%cn'), git_cmd.git_log(commit_hash, '--format=%cd'),
                  git_cmd.git_log(commit_hash, '--format=%s'), git_cmd.get_param(commit_hash), git_cmd.get_file(commit_hash)]
        d = dict(zip(keys, values))
        dd[commit_hash] = d

    with open(args[1] + '/test.json', 'a') as f:
        json.dump(dd, f, indent=2, ensure_ascii=False)




