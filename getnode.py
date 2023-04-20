# -*- coding: utf-8 -*-
# @Time : 2023/4/19 18:06
# @Author : ordar
# @Project : nodefreebot
# @File : getnode.py
# @Python: 3.7.5
import requests
import re

ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
      "referer": "https://nodefree.org/"
      }

v2ray_dy_file = "v2ray.txt"
clash_dy_file = "clash.yml"


def get_latest_page():
    """
    获取最新节点发布页面
    :return:
    """
    html = requests.get("https://nodefree.org/", headers=ua, timeout=5).content.decode()
    # print(html)
    latest_page_url = None
    a = re.findall(r"https://nodefree.org/p/\d+.html", html)
    if a:
        latest_page_url = a[0]
    return latest_page_url


def get_node_dy_url():
    """
    获取v2ray和clash订阅链接
    :return:
    """
    latest_page_url = get_latest_page()
    print(latest_page_url)
    if latest_page_url:
        html = requests.get(latest_page_url, headers=ua, timeout=5).content.decode()
        dy_list = re.findall(r"<p>(https://nodefree.org/dy/.*?)</p>", html)
        return dy_list
    else:
        exit(-1)


def get_local_v2ray_dy():
    with open(v2ray_dy_file, "r", encoding='utf8') as f:
        return f.read()

def get_local_clash_dy():
    with open(clash_dy_file, "r", encoding='utf8') as f:
        return f.read()

def get_network_v2ray_dy(v2ray_dy_url):
    file_content = requests.get(v2ray_dy_url, headers=ua, timeout=5).content.decode()
    return file_content

def get_network_clash_dy(clash_dy_url):
    file_content = requests.get(clash_dy_url, headers=ua, timeout=5).content.decode()
    return file_content

def v2ray_dy_to_file(file_content):
    with open(v2ray_dy_file, 'w', encoding='utf8') as f:
        f.write(file_content)

def clash_dy_to_file(file_content):
    with open(clash_dy_file, 'w', encoding='utf8') as f:
        f.write(file_content)


def main():
    dy_list = get_node_dy_url()
    v2ray_dy_url = dy_list[0]
    clash_dy_url = dy_list[1]
    local_v2ray_dy = get_local_v2ray_dy()
    local_clash_dy = get_local_clash_dy()
    network_v2ray_dy = get_network_v2ray_dy(v2ray_dy_url)
    network_clash_dy = get_network_clash_dy(clash_dy_url)
    if local_clash_dy == network_clash_dy and local_v2ray_dy == network_v2ray_dy:
        exit(-2)
    else:
        v2ray_dy_to_file(network_v2ray_dy)
        clash_dy_to_file(network_clash_dy)


if __name__ == '__main__':
    main()