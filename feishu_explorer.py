#!/usr/bin/env python3
"""
飞书文件夹架构探索脚本
在本地运行: python3 feishu_explorer.py
"""

import urllib.request
import urllib.parse
import json

APP_ID = "cli_a9f7c6d8d6391cd9"
APP_SECRET = "QbIrxxOMWiA27C1ukgc4o27m8W4ePEcG"
ROOT_FOLDER_TOKEN = "IHycIfuZOZICQv9dQFazc8GBon2f"

BASE_URL = "https://open.feishu.cn"


def get_token():
    url = f"{BASE_URL}/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise Exception(f"获取 Token 失败: {result}")
    return result["tenant_access_token"]


def list_files(token, folder_token, page_token=None):
    params = {"folder_token": folder_token, "page_size": 200}
    if page_token:
        params["page_token"] = page_token
    url = f"{BASE_URL}/open-apis/drive/v1/files?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_all_files(token, folder_token):
    files = []
    page_token = None
    while True:
        result = list_files(token, folder_token, page_token)
        if result.get("code") != 0:
            print(f"  [错误] {result.get('msg')}")
            break
        data = result.get("data", {})
        files.extend(data.get("files", []))
        if not data.get("has_more"):
            break
        page_token = data.get("next_page_token")
    return files


def print_tree(token, folder_token, prefix="", name="根目录"):
    print(f"{prefix}{name}/")
    files = get_all_files(token, folder_token)
    for i, f in enumerate(files):
        is_last = (i == len(files) - 1)
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")
        ftype = f.get("type", "unknown")
        fname = f.get("name", "未知")
        ftoken = f.get("token", "")
        if ftype == "folder":
            print_tree(token, ftoken, child_prefix, fname)
        else:
            icon = {"doc": "📄", "sheet": "📊", "bitable": "🗃️", "file": "📎"}.get(ftype, "📄")
            print(f"{prefix}{connector}{icon} {fname} [{ftype}]")


def main():
    print("正在获取飞书 Token...")
    try:
        token = get_token()
        print("Token 获取成功！\n")
        print("=" * 60)
        print("ByteC 飞书文件夹架构")
        print("=" * 60)
        print_tree(token, ROOT_FOLDER_TOKEN)
        print("=" * 60)
        print("\n请将以上输出复制粘贴给 Claude。")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
