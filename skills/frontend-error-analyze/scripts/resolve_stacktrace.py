#!/usr/bin/env python3
"""Source Map 堆栈还原。

用法:
    python resolve_stacktrace.py --sourcemap ./dist/main.abc123.js.map --line 1 --column 23456
    python resolve_stacktrace.py --sourcemap-dir ./dist --stacktrace-file ./event.json
    python resolve_stacktrace.py --sourcemap-dir ./dist --stacktrace-file ./event.json --app-only
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ResolvedFrame:
    """还原后的堆栈帧。"""
    original_file: str = ""
    original_line: int = 0
    original_column: int = 0
    original_name: str = ""
    generated_file: str = ""
    generated_line: int = 0
    generated_column: int = 0
    in_app: bool = True


def parse_vlq(segment: str) -> list:
    """解析 VLQ 编码段（简化实现）。"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    values = []
    shift = 0
    value = 0
    for char in segment:
        idx = chars.index(char)
        continuation = idx & 0x20
        digit = idx & 0x1F
        value += digit << shift
        if continuation:
            shift += 5
        else:
            sign = -1 if (value & 1) else 1
            value = (value >> 1) * sign
            values.append(value)
            value = 0
            shift = 0
    return values


def load_source_map(map_path: Path) -> dict:
    """加载 Source Map JSON 文件。"""
    if not map_path.exists():
        print(f"错误: Source Map 文件不存在: {map_path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(map_path.read_text(encoding="utf-8"))


def find_sourcemap_for_file(sourcemap_dir: Path, filename: str) -> Path:
    """根据文件名查找对应的 Source Map 文件。"""
    base = Path(filename)

    # 尝试精确匹配
    candidates = list(sourcemap_dir.glob(f"**/{base.name}.map"))
    if candidates:
        return candidates[0]

    # 尝试去掉 hash 后匹配
    name_no_hash = re.sub(r'\.[a-f0-9]{6,}\.', '.', base.name)
    candidates = list(sourcemap_dir.glob(f"**/{name_no_hash}.map"))
    if candidates:
        return candidates[0]

    candidates = list(sourcemap_dir.glob(f"**/{name_no_hash}.*.map"))
    if candidates:
        return candidates[0]

    return None


def resolve_position_simple(source_map_data: dict, line: int, column: int) -> ResolvedFrame:
    """纯 Python 的简化还原（基于 VLQ 解析）。"""
    sources = source_map_data.get("sources", [])
    names = source_map_data.get("names", [])
    mappings_str = source_map_data.get("mappings", "")

    lines = mappings_str.split(";")
    if line > len(lines) or line < 1:
        return ResolvedFrame(generated_line=line, generated_column=column)

    target_line = lines[line - 1] if line <= len(lines) else lines[0]
    segments = target_line.split(",")

    gen_col = 0
    src_idx = 0
    src_line = 0
    src_col = 0
    name_idx = 0

    best_match = None
    best_gen_col = -1

    for segment in segments:
        if not segment.strip():
            continue
        values = parse_vlq(segment)
        if len(values) >= 1:
            gen_col += values[0]
        if len(values) >= 2:
            src_idx += values[1]
        if len(values) >= 3:
            src_line += values[2]
        if len(values) >= 4:
            src_col += values[3]
        if len(values) >= 5:
            name_idx += values[4]

        if gen_col <= column and gen_col > best_gen_col:
            best_gen_col = gen_col
            source_file = sources[src_idx] if src_idx < len(sources) else "(unknown)"
            name = names[name_idx] if name_idx < len(names) else ""
            best_match = ResolvedFrame(
                original_file=source_file,
                original_line=src_line + 1,
                original_column=src_col,
                original_name=name,
                generated_file=source_map_data.get("file", ""),
                generated_line=line,
                generated_column=column,
            )

    if best_match:
        best_match.generated_column = column
        return best_match

    return ResolvedFrame(generated_line=line, generated_column=column)


def resolve_single_frame(source_map_data: dict, line: int, column: int) -> ResolvedFrame:
    """还原单个堆栈帧。"""
    return resolve_position_simple(source_map_data, line, column)


def resolve_stacktrace(sourcemap_dir: Path, frames: list, app_only: bool = False) -> list:
    """批量还原堆栈跟踪。"""
    resolved = []
    sourcemap_cache: dict = {}

    for frame in frames:
        filename = frame.get("filename", frame.get("absPath", ""))
        lineno = frame.get("lineno", frame.get("line", 1))
        colno = frame.get("colno", frame.get("column", 0))
        in_app = frame.get("inApp", True)
        func = frame.get("function", frame.get("name", ""))

        if app_only and not in_app:
            continue

        sm_data = None
        map_path = find_sourcemap_for_file(sourcemap_dir, filename)
        if map_path and str(map_path) not in sourcemap_cache:
            sourcemap_cache[str(map_path)] = load_source_map(map_path)
        if map_path:
            sm_data = sourcemap_cache[str(map_path)]

        resolved_frame = {
            "original_file": filename,
            "original_line": lineno,
            "original_column": colno,
            "function": func,
            "in_app": in_app,
            "resolved": False,
        }

        if sm_data:
            result = resolve_single_frame(sm_data, lineno, colno)
            if result.original_file:
                resolved_frame["original_file"] = result.original_file
                resolved_frame["original_line"] = result.original_line
                resolved_frame["original_column"] = result.original_column
                resolved_frame["original_name"] = result.original_name
                resolved_frame["resolved"] = True

        resolved.append(resolved_frame)

    return resolved


def format_resolved_stack(frames: list, title: str = "") -> str:
    """格式化还原后的堆栈。"""
    lines = []
    if title:
        lines.append(title)

    for frame in frames:
        file_loc = f"{frame['original_file']}:{frame['original_line']}:{frame['original_column']}"
        func = frame.get("original_name") or frame.get("function") or "(匿名)"
        marker = "→" if frame.get("in_app") else " "
        lines.append(f"  {marker} at {func} ({file_loc})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Source Map 堆栈还原")
    parser.add_argument("--sourcemap", type=Path, help="单个 Source Map 文件路径")
    parser.add_argument("--sourcemap-dir", type=Path, help="Source Map 文件目录")
    parser.add_argument("--line", type=int, help="行号（压缩代码）")
    parser.add_argument("--column", type=int, help="列号（压缩代码）")
    parser.add_argument("--stacktrace-file", type=Path, help="堆栈 JSON 文件路径")
    parser.add_argument("--stacktrace", type=str, help="堆栈 JSON 字符串")
    parser.add_argument("--app-only", action="store_true", help="只输出应用代码帧")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="输出格式")
    parser.add_argument("--output", "-o", type=Path, help="输出文件路径")
    args = parser.parse_args()

    if args.sourcemap and args.line is not None and args.column is not None:
        sm_data = load_source_map(args.sourcemap)
        result = resolve_single_frame(sm_data, args.line, args.column)
        output_data = asdict(result)
        if args.format == "text":
            formatted = f"{result.original_file}:{result.original_line}:{result.original_column}"
            if result.original_name:
                formatted = f"{result.original_name} ({formatted})"
            output_text = formatted
        else:
            output_text = json.dumps(output_data, indent=2, ensure_ascii=False)

    elif args.sourcemap_dir and (args.stacktrace_file or args.stacktrace):
        if args.stacktrace_file:
            raw = json.loads(args.stacktrace_file.read_text(encoding="utf-8"))
        else:
            raw = json.loads(args.stacktrace)

        frames = raw
        if isinstance(raw, dict):
            entries = raw.get("entries", [])
            for entry in entries:
                if entry.get("type") == "exception":
                    frames = entry.get("data", {}).get("values", [{}])[0].get("stacktrace", {}).get("frames", [])
                    break
            else:
                frames = raw.get("frames", raw.get("stacktrace", []))

        resolved_frames = resolve_stacktrace(args.sourcemap_dir, frames, args.app_only)
        title = ""
        if isinstance(raw, dict):
            title = raw.get("title", "")

        if args.format == "text":
            output_text = format_resolved_stack(resolved_frames, title)
        else:
            output_data = {"total": len(resolved_frames),
                           "resolved": sum(1 for f in resolved_frames if f.get("resolved")),
                           "frames": resolved_frames}
            output_text = json.dumps(output_data, indent=2, ensure_ascii=False)
    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
        print(f"已写入 {args.output}")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
