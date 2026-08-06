# -*- coding: utf-8 -*-
# @Project : nodefreebot
# @File : clashnode_crawler.py
# @Desc  : 从 clashnode GitHub README 提取订阅链接，下载到日期文件夹并记录路径
import requests
import re
import time
from pathlib import Path
from file_section import read_section, write_section

README_URL = "https://raw.githubusercontent.com/clashnode/clashnode.github.io/refs/heads/main/README.md"
URL_PREFIX = "https://clashnode.github.io/"

REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_INTERVAL = 5

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
}

SUB_TYPES = {
    "clash": {
        "pattern": re.compile(r"https://clashnode\.github\.io/uploads/\d{4}/\d{2}/\d+-\d{8}\.yaml"),
        "latest_file": "clash_lastest_file.yml",
    },
    "v2ray": {
        "pattern": re.compile(r"https://clashnode\.github\.io/uploads/\d{4}/\d{2}/\d+-\d{8}\.txt"),
        "latest_file": "v2ray_lastest_file.txt",
    },
    "singbox": {
        "pattern": re.compile(r"https://clashnode\.github\.io/uploads/\d{4}/\d{2}/\d{8}\.json"),
        "latest_file": "singbox_lastest_file.json",
    },
}


def fetch_readme(url):
    """获取 README 文本内容"""
    for i in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=UA, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"获取 README 失败 (第{i + 1}次): {e}")
            if i < MAX_RETRIES - 1:
                time.sleep(RETRY_INTERVAL)
    return None


def extract_links(content, pattern):
    """正则提取匹配的链接列表"""
    return pattern.findall(content)


def download_content(url):
    """下载单个订阅文件内容"""
    for i in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=UA, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"下载失败 (第{i + 1}次) {url}: {e}")
            if i < MAX_RETRIES - 1:
                time.sleep(RETRY_INTERVAL)
    return None


def get_url_path(url):
    """从 URL 提取本地路径，如 2026/08/0-20260805.yaml"""
    path = url.replace(URL_PREFIX, "")
    # uploads/2026/08/0-20260805.yaml -> 2026/08/0-20260805.yaml
    if path.startswith("uploads/"):
        path = path[len("uploads/"):]
    return path


def save_to_file(fpath, content):
    """写入文件，自动创建父目录"""
    filepath = Path(fpath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(fpath, "w", encoding="utf8") as f:
        f.write(content)


def read_latest_paths(latest_file):
    """读取已记录的最新文件路径列表（每行一个）"""
    text = read_section(latest_file, "clashnode")
    return [line.strip() for line in text.splitlines() if line.strip()]


def write_latest_paths(latest_file, paths):
    """替换写入所有最新文件路径（每行一个，去重）"""
    recorded = set(read_latest_paths(latest_file))
    for p in paths:
        recorded.add(p)
    write_section(latest_file, "clashnode", "\n".join(sorted(recorded)))


def any_updated(links):
    """检查是否有新链接不在已记录的路径中"""
    for sub_type, cfg in SUB_TYPES.items():
        new_paths = [get_url_path(url) for url in links.get(sub_type, [])]
        if not new_paths:
            continue
        recorded = set(read_latest_paths(cfg["latest_file"]))
        if any(p not in recorded for p in new_paths):
            return True
    return False


def main():
    # 1. 获取 README
    readme = fetch_readme(README_URL)
    if not readme:
        print("无法获取 README，退出")
        exit(-1)

    # 2. 按类型提取链接
    links = {
        sub_type: extract_links(readme, cfg["pattern"])
        for sub_type, cfg in SUB_TYPES.items()
    }

    total = sum(len(v) for v in links.values())
    print(f"共提取到 {total} 个订阅链接: " + ", ".join(f"{k}={len(v)}" for k, v in links.items()))

    # 3. 检查是否有更新
    if not any_updated(links):
        print("无新链接，跳过下载")
        exit(0)

    # 4. 下载并保存
    for sub_type, cfg in SUB_TYPES.items():
        type_links = links[sub_type]
        if not type_links:
            print(f"未找到 {sub_type} 链接")
            continue

        local_paths = []
        for url in type_links:
            local_path = get_url_path(url)
            content = download_content(url)
            if content is None:
                print(f"跳过下载失败的链接: {url}")
                continue
            save_to_file(local_path, content)
            local_paths.append(local_path)
            print(f"已保存: {local_path}")

        # 追加写入最新路径记录
        if local_paths:
            write_latest_paths(cfg["latest_file"], local_paths)
            print(f"{sub_type}: 已记录 {len(local_paths)} 个路径到 {cfg['latest_file']}")


if __name__ == "__main__":
    main()