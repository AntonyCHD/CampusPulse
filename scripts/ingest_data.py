"""数据导入脚本示例"""

import json
from datetime import datetime
from pathlib import Path


def ingest_jsonl(input_path: str, output_path: str):
    """导入 JSONL 文件并标准化"""
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"错误: 文件 {input_path} 不存在")
        return

    output_file.parent.mkdir(parents=True, exist_ok=True)

    success_count = 0
    error_count = 0

    with open(input_file, "r", encoding="utf-8") as infile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:
        for line_no, line in enumerate(infile, start=1):
            try:
                event = json.loads(line.strip())

                # 验证必填字段
                required_fields = ["event_id", "post", "comments"]
                for field in required_fields:
                    if field not in event:
                        raise ValueError(f"缺少必填字段: {field}")

                # 标准化输出
                outfile.write(json.dumps(event, ensure_ascii=False) + "\n")
                success_count += 1

            except Exception as e:
                print(f"行 {line_no} 解析错误: {e}")
                error_count += 1

    print(f"导入完成: 成功 {success_count} 条，失败 {error_count} 条")


if __name__ == "__main__":
    # 示例用法
    ingest_jsonl(
        "data/raw/campus_wall_sample.jsonl",
        "data/processed/events.jsonl",
    )
