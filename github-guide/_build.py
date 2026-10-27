"""把 4 张截图 base64 内嵌进模板，生成单文件离线导览页。"""

import base64
import pathlib

d = pathlib.Path(__file__).parent
html = (d / "_template.html").read_text(encoding="utf-8")

for i, name in enumerate(
    ["01_repo_home.png", "02_commits.png", "03_actions.png", "04_run_failed.png"], 1
):
    raw = (d / name).read_bytes()
    b64 = base64.b64encode(raw).decode()
    html = html.replace(f"__IMG{i}__", f"data:image/png;base64,{b64}")
    print(f"嵌入 {name}: {len(raw)//1024} KB")

out = d / "GitHub页面导览.html"
out.write_text(html, encoding="utf-8")
print("生成:", out.name, f"{out.stat().st_size//1024} KB")
