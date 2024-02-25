# Github Secrets

该工具分析给定的 Github 仓库，并搜索悬空或强制推送的提交，其中可能包含潜在的秘密或有趣的信息。

## 要求

- Python3
- [requests](https://pypi.org/project/requests/)

## 安装

```bash
git clone https://github.com/zgimszhd61/gitlab-secrets-simplify.git
```

## 用法

要获取基本选项和开关的列表，请使用：
```bash
python3 github_scanner.py -h
```

您可以完全不使用身份验证运行此脚本，但会受到较低的 Github API 速率限制，或者您可以导出生成的 [API 令牌](https://github.com/settings/tokens)。

这些令牌不需要任何特权，仅用于对 API 进行身份验证。对于此项目，需要一个细粒度的个人访问令牌，不需要任何其他权限。

要导出令牌，请使用：
```bash
export GITHUB_ACCOUNT_TOKEN=<your_secret_api_token>
```

要运行脚本并扫描一个仓库：
```bash
python3 github_scanner.py <username>/<repository>
```

## 资源

要使用令牌检查当前的 API 速率限制和使用情况：
```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer <your_secret_api_token>" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/rate_limit
```

不使用令牌：
```bash
curl -L -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/rate_limit
```

## 许可证

根据以下任一许可证授权

 * Apache 许可证，版本 2.0，([LICENSE-APACHE](LICENSE-APACHE) 或 <http://www.apache.org/licenses/LICENSE-2.0>)
 * MIT 许可证 ([LICENSE-MIT](LICENSE-MIT) 或 <http://opensource.org/licenses/MIT>)

根据您的选择。

### 贡献

除非您明确声明，否则您提交的任何贡献都是有意向地要纳入到作品中的，作品由您定义，遵循 Apache-2.0 许可证，将被双重许可，如上所述，没有附加的条款或条件。
