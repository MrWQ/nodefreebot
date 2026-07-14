# -*- coding: utf-8 -*-
# @Time : 2023/4/19 18:06
# @Author : ordar
# @Project : nodefreebot
# @File : getnode.py
# @Python: 3.7.5
import requests
import re
from pathlib import Path

base_url = "https://nodefree.me/"
node_url = "https://node.nodefree.me/"
ua = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "referer": base_url,
}

# 每种订阅类型的配置：(索引, 主文件名, 最新路径记录文件)
SUB_TYPES = {
    "v2ray": {"index": 0, "dy_file": "v2ray.txt", "latest_file": "v2ray_lastest_file.txt"},
    "clash": {"index": 1, "dy_file": "clash.yml", "latest_file": "clash_lastest_file.yml"},
    "mihomo": {"index": 2, "dy_file": "mihomo.yml", "latest_file": "mihomo_lastest_file.yml"},
}


def get_latest_page():
    """获取最新节点发布页面"""
    ua["referer"] = node_url
    html = requests.get(base_url, headers=ua, timeout=5).content.decode()
    a = re.findall(rf"{base_url}p/\d+.html", html)
    return a[0] if a else None


def get_node_dy_url():
    """获取所有订阅链接"""
    latest_page_url = get_latest_page()
    print(latest_page_url)
    if not latest_page_url:
        exit(-1)
    req = requests.get(latest_page_url, headers=ua, timeout=5)
    html = req.content.decode()
    print(latest_page_url, req.status_code, html)
    return re.findall(rf"<p>({node_url}.*?)</p>", html)


def fetch_subscription(url):
    """从网络获取订阅内容"""
    return requests.get(url, headers=ua, timeout=5).content.decode()


def get_url_path(url):
    return url.replace(node_url, "")


def get_saved_latest_path(latest_file):
    try:
        with open(latest_file, "r", encoding="utf8") as f:
            return f.read()
    except:
        return False


def save_latest_path(latest_file, content):
    with open(latest_file, "w", encoding="utf8") as f:
        f.write(content)


def save_to_file(fpath, content):
    """写入文件，自动创建父目录"""
    filepath = Path(fpath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(fpath, "w", encoding="utf8") as f:
        f.write(content)


def main():
    dy_list = get_node_dy_url()

    # 检查是否所有类型都已更新
    all_up_to_date = True
    for name, cfg in SUB_TYPES.items():
        idx = cfg["index"]
        if idx >= len(dy_list):
            continue
        remote_path = get_url_path(dy_list[idx])
        if remote_path != get_saved_latest_path(cfg["latest_file"]):
            all_up_to_date = False
            break

    if all_up_to_date:
        exit(0)

    # 下载并保存所有订阅
    for name, cfg in SUB_TYPES.items():
        idx = cfg["index"]
        if idx >= len(dy_list):
            print(f"警告: dy_list 中缺少 {name} 的订阅链接 (index={idx})")
            continue
        dy_url = dy_list[idx]
        local_path = get_url_path(dy_url)

        content = fetch_subscription(dy_url)
        save_latest_path(cfg["latest_file"], local_path)  # 记录最新路径
        save_to_file(local_path, content)                  # 按日期路径保存
        save_to_file(cfg["dy_file"], content)              # 根目录保存最新内容


if __name__ == "__main__":
    main()