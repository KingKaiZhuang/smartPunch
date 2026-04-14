import os
import subprocess

def xls_to_xlsx(in_xls_path: str, out_dir: str = None) -> str:
    """
    使用 LibreOffice headless 將 .xls 轉成 .xlsx
    回傳轉出的 .xlsx 完整路徑
    """
    if out_dir is None:
        out_dir = os.path.dirname(os.path.abspath(in_xls_path))

    cmd = [
        "libreoffice",
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to", "xlsx",
        in_xls_path,
        "--outdir", out_dir
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

    base = os.path.splitext(os.path.basename(in_xls_path))[0]
    out_xlsx_path = os.path.join(out_dir, base + ".xlsx")
    return out_xlsx_path
if __name__ == "__main__":
    in_path = "/home/user/Desktop/志工時數匯入.xls"
    out_path = xls_to_xlsx(in_path)
    print("Converted to:", out_path)
