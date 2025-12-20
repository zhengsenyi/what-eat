import re
import os

# 输入/输出文件路径
IN_SQL = r"c:\Users\Administrator\Desktop\what-eat\python\foods_2000.sql"            # 原始 sql
OUT_SQL = r"c:\Users\Administrator\Desktop\what-eat\python\foods_2000_dedup.sql"    # 去重后的 sql

def main():
    seen = set()
    kept_lines = 0
    removed_lines = 0

    with open(IN_SQL, "r", encoding="utf-8") as fin, \
         open(OUT_SQL, "w", encoding="utf-8") as fout:

        for line in fin:
            stripped = line.strip()
            if not stripped or not stripped.startswith("INSERT INTO"):
                # 非 INSERT 行原样写出
                fout.write(line)
                continue

            # 抓出所有 'xxx' 字段： name, category, description, image_url, ...
            text_fields = re.findall(r"'([^']*)'", line)
            if len(text_fields) < 3:
                # 格式异常的行，防止误删，直接保留
                fout.write(line)
                kept_lines += 1
                continue

            name = text_fields[0]
            category = text_fields[1]
            description = text_fields[2]

            key = (name, category, description)

            if key in seen:
                # 这一组 (name, category, description) 已经出现过，视为重复，跳过
                removed_lines += 1
                continue

            # 第一次出现，保留
            seen.add(key)
            fout.write(line)
            kept_lines += 1

    print(f"去重完成：保留 {kept_lines} 行，删除 {removed_lines} 行重复。")
    print(f"输出文件：{OUT_SQL}")

if __name__ == "__main__":
    main()
