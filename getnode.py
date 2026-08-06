# -*- coding: utf-8 -*-
# @Time : 2023/4/19 18:06
# @Author : ordar
# @Project : nodefreebot
# @File : getnode.py
# @Python: 3.7.5
import requests
import re
from pathlib import Path
from file_section import read_section, write_section

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

cover_image_file = "cover.jpg"
cover_lastest_file = "cover_lastest_file.txt"
COVER_IMG_PATTERN = re.compile(r'<img[^>]+src="(https?://nodefree\.me/wp-content/uploads/[^"]+480x300\.jpg)"')


def get_latest_page():
    """获取最新节点发布页面"""
    ua["referer"] = node_url
    html = requests.get(base_url, headers=ua, timeout=5).content.decode()
    a = re.findall(rf"{base_url}p/\d+.html", html)
    return a[0] if a else None


def get_homepage_html():
    """获取首页 HTML"""
    ua["referer"] = node_url
    return requests.get(base_url, headers=ua, timeout=5).content.decode()


def get_cover_images(html):
    """从首页 HTML 中提取所有封面图片 URL"""
    return COVER_IMG_PATTERN.findall(html)


def get_cover_url_path(img_url):
    """从封面图 URL 中提取日期路径，如 wp-content/uploads/2023/01/14-480x300.jpg"""
    return img_url.replace(base_url, "")


def save_cover_image(img_url):
    """下载并保存封面图片到日期路径和根目录"""
    resp = requests.get(img_url, headers=ua, timeout=10)
    resp.raise_for_status()
    # 按日期路径保存
    local_path = get_cover_url_path(img_url)
    filepath = Path(local_path)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(resp.content)
    # 根目录保存最新封面
    with open(cover_image_file, "wb") as f:
        f.write(resp.content)


def get_node_dy_url():
    """获取所有订阅链接"""
    latest_page_url = get_latest_page()
    print(latest_page_url)
    if not latest_page_url:
        exit(-1)
    req = requests.get(latest_page_url, headers=ua, timeout=5)
    html = req.content.decode()
    # print(latest_page_url, req.status_code, html)
    return re.findall(rf"<p>({node_url}.*?)</p>", html)


def fetch_subscription(url):
    """从网络获取订阅内容"""
    return requests.get(url, headers=ua, timeout=5).content.decode()


def get_url_path(url):
    return url.replace(node_url, "")


def get_saved_latest_path(latest_file):
    return read_section(latest_file, "getnode").strip() or False


def save_latest_path(latest_file, content):
    write_section(latest_file, "getnode", content)


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

    # 保存最新封面图片
    try:
        html = get_homepage_html()
        images = get_cover_images(html)
        if images:
            img_url = images[0]
            cover_path = get_cover_url_path(img_url)
            if cover_path != get_saved_latest_path(cover_lastest_file):
                print(f"找到 {len(images)} 张封面图，保存最新: {img_url}")
                save_cover_image(img_url)
                save_latest_path(cover_lastest_file, cover_path)
            else:
                print("封面图片未更新")
        else:
            print("未找到封面图片")
    except Exception as e:
        print(f"获取封面图片失败: {e}")


if __name__ == "__main__":
    main()