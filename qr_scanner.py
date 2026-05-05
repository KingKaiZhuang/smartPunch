import cv2
from datetime import datetime, timedelta
import os
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import time
from db import insert_check_in, update_check_out

# ---------- 顏色設定 ----------
if os.name == 'nt':
    os.system('color')

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'


# ---------- MP3 播放（使用 mpg123） ----------
SOUND_PATH = "/home/user/myproject~/mp3/"  # 你的音效資料夾路徑

def play_mp3(filename):
    full_path = os.path.join(SOUND_PATH, filename)
    try:
        os.system(f"mpg123 -q '{full_path}' &")  # -q 靜音模式, & 背景播放
    except Exception as e:
        print(f"{Colors.RED}⚠️ 無法播放 MP3 ({filename}): {e}{Colors.RESET}")


# ---------- 加密/解密 ----------
SECRET_PASSPHRASE = "MyVeryStrongSecretPassword"

def make_key(passphrase):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"fixed_salt_16b",
        iterations=390000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

FERNET = Fernet(make_key(SECRET_PASSPHRASE))

def decrypt_payload(payload: str):
    try:
        data = json.loads(payload)
        ct = data["ct"]
        return FERNET.decrypt(ct.encode()).decode()
    except Exception:
        return payload


# ---------- 工具 ----------
def split_after_colon(s: str):
    for c in (":", "："):
        if c in s:
            return s.split(c, 1)[1].strip()
    return ""

def parse_qr_text(data: str):
    lines = [ln.strip() for ln in data.replace("\r\n", "\n").split("\n") if ln.strip()]
    name = nid = ""

    for ln in lines:
        low = ln.lower()

        if ("姓名" in ln or low.startswith("name")) and (":" in ln or "：" in ln):
            name = split_after_colon(ln)

        elif (
            "身分證" in ln
            or "身份證" in ln
            or low.startswith(("id ", "id:", "idno", "id no", "id number"))
        ) and (":" in ln or "：" in ln):
            nid = split_after_colon(ln)

    if not (name or nid):
        if len(lines) > 0:
            name = lines[0]
        if len(lines) > 1:
            nid = lines[1]

    if not name:
        name = "未提供"
    if not nid:
        nid = "未提供"

    return {"name": name, "nid": nid}


# ---------- 相機 ----------
def open_camera_try():
    for idx in (0, 1, 2):
        cap = cv2.VideoCapture(idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        if cap.isOpened():
            return cap, idx

        cap.release()

    return None, None


# ---------- 主程式 ----------
def main():
    cap, cam_idx = open_camera_try()

    if cap is None:
        print(f"{Colors.RED}❌ 無法開啟 USB 攝影機{Colors.RESET}")
        return

    detector = cv2.QRCodeDetector()

    # 用來避免同一張 QR 一直被攝影機重複讀取
    last_seen = {}

    # 用來記錄目前上下班狀態
    clock_records = {}

    # 用來控制同一人重複打卡冷卻時間
    last_clock_time = {}

    # 前 10 秒讓使用者有時間把 QR 拿起來，不播放失敗音
    IGNORE_SECONDS = 10

    # 同一人 60 秒內不能重複打卡
    COOLDOWN_SECONDS = 60

    print(f"{Colors.GREEN}🎯 Raspberry Pi QR Code 打卡系統已啟動{Colors.RESET}")
    print(f"{Colors.CYAN}📱 第一次掃 → 上班打卡 | 第二次掃 → 下班打卡{Colors.RESET}")
    print(f"{Colors.YELLOW}📷 使用攝影機索引：{cam_idx}{Colors.RESET}")

    play_mp3("work.MP3")  # 系統啟動音效

    try:
        while True:
            ok, frame = cap.read()

            if not ok:
                continue

            retval, decoded_info, points, _ = detector.detectAndDecodeMulti(frame)

            if retval and points is not None:
                for data, pts in zip(decoded_info, points):
                    data = (data or "").strip()

                    if not data:
                        continue

                    now = datetime.now()

                    # ==================================================
                    # 同一張 QR 前 10 秒完全忽略
                    # 避免使用者還沒把 QR 拿走，就一直被攝影機掃到
                    # ==================================================
                    if data in last_seen:
                        qr_diff = (now - last_seen[data]).total_seconds()

                        if qr_diff < IGNORE_SECONDS:
                            continue

                    last_seen[data] = now

                    # ---------- 解密 QR ----------
                    decrypted = decrypt_payload(data)
                    info = parse_qr_text(decrypted)

                    nid = info["nid"]
                    name = info["name"]

                    # ---------- 必須有身分證字號 ----------
                    if nid == "未提供" or nid.strip() == "":
                        print(f"{Colors.RED}❌ 無效 QR（缺少身分證）{Colors.RESET}")
                        play_mp3("fail.MP3")
                        continue

                    # ==================================================
                    # 同一人冷卻判斷
                    #
                    # 0～10 秒：
                    #     完全忽略，不播放 fail.MP3
                    #
                    # 10～60 秒：
                    #     拒絕重複打卡，播放 fail.MP3
                    #
                    # 60 秒後：
                    #     允許重新打卡
                    # ==================================================
                    if nid in last_clock_time:
                        diff = (now - last_clock_time[nid]).total_seconds()

                        # 前 10 秒無聲忽略
                        if diff < IGNORE_SECONDS:
                            continue

                        # 第 10～60 秒播放失敗音
                        if diff < COOLDOWN_SECONDS:
                            remain = int(COOLDOWN_SECONDS - diff)
                            print(f"{Colors.YELLOW}⏳ {name} 請等待 {remain} 秒後再次打卡{Colors.RESET}")
                            play_mp3("fail.MP3")
                            continue

                    # ==================================================
                    # 走到這裡，代表允許打卡
                    # 注意：只有真正允許打卡時，才更新 last_clock_time
                    # ==================================================
                    last_clock_time[nid] = now

                    # ========== 打卡邏輯 ==========

                    # 第一次掃描，或上一輪已經下班，代表這次是上班打卡
                    if nid not in clock_records or "end" in clock_records[nid]:
                        clock_records[nid] = {
                            "name": name,
                            "start": now
                        }

                        insert_check_in(name, nid, now)

                        print(f"{Colors.GREEN}🌅 {name} 上班打卡成功{Colors.RESET}")
                        play_mp3("work.MP3")

                    # 已經有上班紀錄，但還沒有下班，代表這次是下班打卡
                    else:
                        start = clock_records[nid]["start"]
                        delta = now - start

                        # 先算出實際總共經過了多少分鐘
                        total_minutes = int(delta.total_seconds() // 60)

                        # 算出基礎的「小時」與「剩餘分鐘」
                        base_h = total_minutes // 60
                        rem_m = total_minutes % 60

                        # 工時計算進位邏輯
                        if rem_m <= 15:
                            out_h = base_h
                            out_m = 0

                        elif rem_m <= 30:
                            out_h = base_h
                            out_m = 30

                        else:
                            out_h = base_h + 1
                            out_m = 0

                        # 將計算並進位後的結果寫入資料庫
                        update_check_out(nid, now, out_h, out_m)

                        clock_records[nid]["end"] = now

                        print(
                            f"{Colors.YELLOW}🌙 {name} 下班打卡成功 | "
                            f"工時 {out_h} 小時 {out_m} 分{Colors.RESET}"
                        )
                        play_mp3("getoffwork.MP3")

                    # ==============================

    except KeyboardInterrupt:
        print("\n使用者手動中止")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"{Colors.PURPLE}🔚 程式結束{Colors.RESET}")


if __name__ == "__main__":
    main()