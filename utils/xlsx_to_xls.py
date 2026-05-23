import os
import subprocess
import sys

def xlsx_to_xls(in_xlsx_path: str, out_dir: str = None) -> str:
    """
    使用 LibreOffice headless 將 .xlsx 轉成 .xls
    回傳轉出的 .xls 完整路徑
    """
    in_xlsx_path = os.path.abspath(in_xlsx_path)
    if not os.path.exists(in_xlsx_path):
        raise FileNotFoundError(f"找不到輸入檔：{in_xlsx_path}")

    if out_dir is None:
        out_dir = os.path.dirname(in_xlsx_path)
    out_dir = os.path.abspath(out_dir)

    cmd = [
        "libreoffice",
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to", "xls",
        in_xlsx_path,
        "--outdir", out_dir
    ]

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"轉檔失敗\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")

    base = os.path.splitext(os.path.basename(in_xlsx_path))[0]
    out_xls_path = os.path.join(out_dir, base + ".xls")

    if not os.path.exists(out_xls_path):
        raise RuntimeError(f"指令執行後找不到輸出檔：{out_xls_path}\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")

    return out_xls_path


if __name__ == "__main__":
    # 用法：
    # python3 xlsx_to_xls.py input.xlsx [outdir]
    in_path = sys.argv[1] if len(sys.argv) > 1 else "out.xlsx"
    outdir = sys.argv[2] if len(sys.argv) > 2 else None

    out_path = xlsx_to_xls(in_path, outdir)
    print("✅ 轉檔成功")
    print("輸入：", os.path.abspath(in_path))
    print("輸出：", out_path)
