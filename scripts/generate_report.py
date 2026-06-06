#!/usr/bin/env python3
"""Generate HTML report for skill optimization results."""


def generate_html(output: dict, auto_refresh: bool = False, skill_name: str = "") -> str:
    """Generate HTML report from optimization results."""
    history = output.get("history", [])
    best_description = output.get("best_description", "")
    original_description = output.get("original_description", "")

    refresh_tag = '<meta http-equiv="refresh" content="5">' if auto_refresh else ""

    rows = ""
    for h in history:
        iter_num = h.get("iteration", "?")
        train_score = f"{h.get('train_passed', 0)}/{h.get('train_total', 0)}"
        test_score = f"{h.get('test_passed', 0)}/{h.get('test_total', 0)}" if h.get("test_passed") is not None else "N/A"
        desc = h.get("description", "")[:100] + "..." if len(h.get("description", "")) > 100 else h.get("description", "")
        rows += f"<tr><td>{iter_num}</td><td>{train_score}</td><td>{test_score}</td><td>{desc}</td></tr>"

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Skill Optimization Report: {skill_name}</title>
    {refresh_tag}
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 1000px; margin: 20px auto; padding: 20px; }}
        h1, h2 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        tr:nth-child(even) {{ background-color: #fafafa; }}
        .best {{ background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .original {{ background-color: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        code {{ background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>Skill Optimization Report: {skill_name}</h1>

    <div class="best">
        <h2>Best Description</h2>
        <p><strong>Score:</strong> {output.get('best_score', 'N/A')}</p>
        <p><code>{best_description}</code></p>
    </div>

    <div class="original">
        <h2>Original Description</h2>
        <p><code>{original_description}</code></p>
    </div>

    <h2>Iteration History</h2>
    <table>
        <tr>
            <th>Iteration</th>
            <th>Train Score</th>
            <th>Test Score</th>
            <th>Description</th>
        </tr>
        {rows}
    </table>

    <p><strong>Exit Reason:</strong> {output.get('exit_reason', 'unknown')}</p>
    <p><strong>Iterations Run:</strong> {output.get('iterations_run', 0)}</p>
</body>
</html>"""