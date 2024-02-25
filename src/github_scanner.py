import requests, logging, os, argparse

# 配置区域
# 在此处创建个人访问令牌：https://github.com/settings/tokens
# 个人访问令牌，不需要额外权限
github_account_token = os.getenv('GITHUB_ACCOUNT_TOKEN')

# 定义函数：从列表中找出不在另一个列表中的元素
def elements_not_in_list(search_from, search_in):
    return [x for x in search_from if x not in search_in]

# 定义函数：从列表中找出也在另一个列表中的元素
def elements_in_list(search_from, search_in):
    return [x for x in search_from if x in search_in]

# 定义函数：打印提交的URL
def commit_print(repo, commits):
    for commit in commits:
        print(f"https://github.com/{repo}/commit/{commit}")

# 定义函数：从给定的起始提交SHA1开始，拉取尽可能多的提交历史
def pull_commits(repo, start_commit, already_known_commits):
    initial_count = len(already_known_commits)
    stop = False
    start = start_commit
    while not stop:
        url = f"https://api.github.com:443/repos/{repo}/commits?per_page=100&sha={start}"
        data = requests.get(url, headers=request_headers)
        json_data = data.json()
        if len(json_data) == 1 and json_data[0]['sha'] in already_known_commits:
            stop = True
        else:
            for commit in json_data:
                if commit['sha'] in already_known_commits:
                    stop = True
                else:
                    already_known_commits.add(commit['sha'])
        start = json_data[-1]['sha']
    logging.info(f"Pulled {len(already_known_commits) - initial_count} commits")

# 定义函数：迭代所有公开可用的分支，并查询每个分支的所有提交
def pull_all_commits_from_all_branches(repo):
    commits = set()
    url = f"https://api.github.com:443/repos/{repo}/branches"
    data = requests.get(url, headers=request_headers)
    for branch in data.json():
        logging.info(f"Pulling all commits for branch {branch['name']}")
        pull_commits(repo, branch['commit']['sha'],commits)
    logging.info(f"Pulled {len(commits)} from all branches")
    return commits

# 定义函数：从事件API端点获取所有没有提交的推送事件，这些推送事件只覆盖了当前的头部
def pull_all_force_pushed_commits_from_events(repo):
    commits = set()
    url = f"https://api.github.com:443/repos/{repo}/events"
    data = requests.get(url, headers=request_headers)
    for event in data.json():
        if event["type"] == "PushEvent":
            if len(event["payload"]["commits"]) == 0:
                commits.add(event["payload"]["before"])
    logging.info(f"Pulled {len(commits)} force-pushed commits from events")
    return commits

# 定义函数：从事件API端点获取所有推送的提交
def pull_all_commits_from_events(repo):
    commits = set()
    url = f"https://api.github.com:443/repos/{repo}/events"
    data = requests.get(url, headers=request_headers)
    for event in data.json():
        if event["type"] == "PushEvent":
            for commit in event["payload"]["commits"]:
                commits.add(commit['sha'])
    logging.info(f"Pulled {len(commits)} commits from events")
    return commits

# 定义函数：寻找悬空提交
def find_dangling_commits(repo):
    historic_commits = pull_all_commits_from_all_branches(repo)
    force_pushed_commits = pull_all_force_pushed_commits_from_events(repo)
    event_commits = pull_all_commits_from_events(repo)
    missing_history_commits = elements_not_in_list(event_commits, historic_commits)
    probably_force_pushed_commits = elements_in_list(missing_history_commits, force_pushed_commits)
    if probably_force_pushed_commits:
        print("\nFound these commits, which were probably force pushed and are not in the history anymore:")
        commit_print(repo, probably_force_pushed_commits)

    dangling_commits = elements_not_in_list(missing_history_commits, probably_force_pushed_commits)
    if dangling_commits:
        print("\nFound these dangling commits, which were in the eventlog and are not in the history anymore:")
        commit_print(repo, dangling_commits)
    if not probably_force_pushed_commits and not dangling_commits:
        print("\nFound no dangling commits")

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description='Github Deleted Secrets Scanner')
    parser.add_argument('repository', help='Required repository to scan (format: username/repository)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Make the script more verbose.')
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.ERROR)
    request_headers = {}
    if github_account_token:
        request_headers["Authorization"] = "Bearer " + github_account_token
        logging.info("Using the supplied API Token!")
    try:
        find_dangling_commits(args.repository)
    except Exception as e:
        data = requests.get("https://api.github.com/rate_limit", headers=request_headers)
        json_data = data.json()
        if int(json_data["rate"]["remaining"]) == 0:
            logging.error("You have reached your Github API limits. If you run this script without an API Token, you have to wait for an hour, before you can scan again or you provide an API token!")
        else:
            logging.exception(e)

