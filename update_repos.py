import json
import os
import re
import urllib.request

USER = "harshit8629"
README = "README.md"
START, END = "<!--REPOS:START-->", "<!--REPOS:END-->"


def fetch_repos():
    repos, page = [], 1
    while True:
        url = f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner&sort=pushed"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get('GH_TOKEN', '')}",
            "User-Agent": "profile-readme-updater",
        })
        with urllib.request.urlopen(req) as resp:
            batch = json.load(resp)
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def clean(text):
    return (text or "").replace("|", "/").replace("\n", " ").strip()


def build_table(repos):
    repos = [r for r in repos if not r["fork"] and r["name"].lower() != USER.lower()]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)
    if not repos:
        return "_No public projects yet._"
    lines = [
        f"**{len(repos)} public projects**",
        "",
        "| Project | Description | Language | Stars | Updated |",
        "|:--|:--|:--|:--:|:--:|",
    ]
    for r in repos:
        lines.append(
            f"| [**{r['name']}**]({r['html_url']}) "
            f"| {clean(r['description']) or '-'} "
            f"| {r['language'] or '-'} "
            f"| {r['stargazers_count']} "
            f"| {r['pushed_at'][:10]} |"
        )
    return "\n".join(lines)


def main():
    table = build_table(fetch_repos())
    with open(README, encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    new_block = f"{START}\n{table}\n{END}"
    updated = pattern.sub(lambda _: new_block, content)
    if updated != content:
        with open(README, "w", encoding="utf-8") as f:
            f.write(updated)


if __name__ == "__main__":
    main()
