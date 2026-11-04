"""统计目录内 SRT 时间轴行的数量；不转写音频，不判断字幕内容。"""

import argparse
import csv
from pathlib import Path
import re


TIMELINE = re.compile(r"^\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}(?:\s+.*)?$")


def main():
    parser = argparse.ArgumentParser(description="统计指定目录中小写 .srt 文件的字幕段数。")
    parser.add_argument("folder", type=Path, help="字幕所在目录（不递归子目录）")
    parser.add_argument("output", type=Path, help="CSV 输出路径")
    args = parser.parse_args()
    if not args.folder.is_dir():
        parser.error(f"输入目录不存在或不是目录：{args.folder}")

    files = sorted((p for p in args.folder.iterdir() if p.is_file() and p.suffix.lower() == ".srt"), key=lambda p: p.name)
    with args.output.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["file", "cues"])
        for path in files:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
            writer.writerow([path.name, sum(bool(TIMELINE.fullmatch(line.strip())) for line in lines)])
    print(f"已统计 {len(files)} 个字幕文件，结果保存至：{args.output}")


if __name__ == "__main__":
    main()
