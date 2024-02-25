import requests, logging, os, argparse

############################# 配置 #############################
# 可以在这里创建：https://gitlab.com/-/user_settings/personal_access_tokens
# 个人访问令牌需要 `read_api` 范围
gitlab_access_token = os.getenv('GITLAB_ACCOUNT_TOKEN')
# 例如 https://gitlab.com 用于公共实例
gitlab_instance_url = os.getenv('GITLAB_INSTANCE_URL', default="https://gitlab.com")
############################# 配置 #############################


# 打印提交的函数
def commit_print(project:str, repository:str , commits: set[str]):
    for commit in commits:
        print(f"{gitlab_instance_url}/{project}/{repository}/-/commit/{commit}")

# 根据项目和仓库名称获取仓库ID
def get_repository_id_from_name(project:str, repository:str) -> int:
    url = f"{gitlab_instance_url}/api/v4/projects/{project}%2f{repository}?simple=true"
    data = requests.get(url, headers=request_headers)
    datajson = data.json()
    id = datajson['id']
    logging.info(f"获取到 {project}/{repository} 的ID为 {id}")
    return id

# 获取所有提交
def get_all_commits(repo_id:int) -> set[str]:
    url = f"{gitlab_instance_url}/api/v4/projects/{repo_id}/events?action=pushed"
    data = requests.get(url, headers=request_headers)
    datajson = data.json()
    commits = set()
    for event in datajson:
        if event.get("push_data") and event.get("push_data").get("commit_from"):
            commits.add(event.get("push_data").get("commit_from"))
        if event.get("push_data") and event.get("push_data").get("commit_to"):
            commits.add(event.get("push_data").get("commit_to"))
    logging.info(f"获取到总共 {len(commits)} 个提交")
    return commits
            
# 获取所有官方提交
def get_all_official_commits(repo_id:int) -> set[str]:
    url = f"{gitlab_instance_url}/api/v4/projects/{repo_id}/repository/commits?all=true" # 不能工作，即使可以直接获取，也不显示悬挂提交
    data = requests.get(url, headers=request_headers)
    datajson = data.json()
    commits = set()
    for commit in datajson:
        if commit.get("id"):
            commits.add(commit.get("id"))
    logging.info(f"获取到 {len(commits)} 个官方提交")
    return commits

# 查找悬挂提交
def find_dangling_commits(project, repository):
    repo_id = get_repository_id_from_name(project, repository)
    official_commits = get_all_official_commits(repo_id)
    all_commits = get_all_commits(repo_id)
    dangling_commits = all_commits - official_commits

    if dangling_commits:
        print("\n发现以下悬挂提交，这些提交出现在事件日志中，但不再存在于历史记录中：")
        commit_print(project, repository ,dangling_commits)
    else:
        print("\n未发现悬挂提交")

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description='Github 删除的秘密扫描器')
    parser.add_argument('project',help='必须指定项目')
    parser.add_argument('repository',help='必须扫描的仓库')
    parser.add_argument('-v', '--verbose', action='store_true',help='使脚本更详细输出。')
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.ERROR)
    request_headers = {}

    if gitlab_access_token:
        request_headers["Authorization"] = "Bearer " + gitlab_access_token
        logging.info("使用提供的API令牌！")
    try:
        find_dangling_commits(args.project, args.repository)
    except Exception as e:
        logging.exception(e)

