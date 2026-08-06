# -*- coding: utf-8 -*-
# @File : file_section.py
# @Desc : 提供基于段落标记的安全文件读写，支持文件锁防并发
import re
from pathlib import Path
from filelock import FileLock


def write_section(filepath, section_name, content):
    """将 content 写入 filepath 中 section_name 对应的段落。
    - 段落已存在 → 只替换该段落，不影响其他段落
    - 段落不存在 → 追加到文件末尾
    """
    lock = FileLock(filepath + ".lock")
    with lock:
        p = Path(filepath)
        text = p.read_text(encoding="utf-8") if p.exists() else ""

        start_tag = f"# === {section_name}_START ==="
        end_tag = f"# === {section_name}_END ==="
        new_section = f"{start_tag}\n{content}\n{end_tag}"

        pattern = re.compile(
            rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL
        )

        if pattern.search(text):
            text = pattern.sub(new_section, text)
        else:
            text = (text.rstrip("\n") + "\n\n" + new_section) if text else new_section

        p.write_text(text, encoding="utf-8")


def read_section(filepath, section_name):
    """读取 filepath 中 section_name 段落的内容，不存在返回空字符串。"""
    lock = FileLock(filepath + ".lock")
    with lock:
        p = Path(filepath)
        if not p.exists():
            return ""
        text = p.read_text(encoding="utf-8")

        start_tag = f"# === {section_name}_START ==="
        end_tag = f"# === {section_name}_END ==="
        pattern = re.compile(
            rf"{re.escape(start_tag)}\n(.*?)\n{re.escape(end_tag)}", re.DOTALL
        )
        m = pattern.search(text)
        return m.group(1) if m else ""


def section_exists(filepath, section_name):
    """检查段落是否存在。"""
    return bool(read_section(filepath, section_name))