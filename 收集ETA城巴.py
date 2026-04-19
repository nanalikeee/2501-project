import urllib.request
import urllib.error
import json
import time
import csv
from datetime import datetime
import ssl

# 禁用 SSL 验证（解决可能的证书问题）
ssl._create_default_https_context = ssl._create_unverified_context

# ================== 配置区域 ==================
# 采集间隔（秒），5分钟 = 300秒
FETCH_INTERVAL = 300

# 输出文件名
OUTPUT_CSV = "ctb_eta_data.csv"

# 要采集的城巴站点（使用你提供的 stop_id）
# 格式: stop_id -> (路线号, 站点名称)
# 注意：城巴 API 返回的数据中，方向字段可能不是 O/I，需要根据实际情况调整
STATIONS = {
    "7959F14FBCC06B74": ("10", "堅尼地城"),      # 堅尼地城巴士總站
    "001262": ("10", "北角碼頭"),                # 北角碼頭巴士總站
    "001028": ("10", "中環街市"),                # 中環街市
    "001016": ("10", "中環港澳碼頭"),            # 中環 (港澳碼頭)
    "002103": ("619", "順利邨"),                 # 順利邨
    "001537": ("619", "紅磡海底隧道"),           # 紅磡海底隧道
    "001990": ("969", "天水圍市中心"),           # 天水圍市中心
    "002445": ("969", "銅鑼灣摩頓台"),           # 銅鑼灣 (摩頓台)
    "002266": ("969", "大欖隧道轉車站"),         # 大欖隧道轉車站
}

# ============================================

def fetch_ctb_stop_eta(stop_id):
    """获取城巴指定站点的实时ETA数据"""
    url = f"https://rt.data.gov.hk/v2/transport/citybus/eta/stop/{stop_id}"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except urllib.error.HTTPError as e:
        print(f"  HTTP错误 {e.code}: {url}")
        return []
    except Exception as e:
        print(f"  错误: {e}")
        return []

def main():
    print("=" * 60)
    print("城巴 ETA 数据采集程序")
    print("=" * 60)
    print(f"采集间隔: {FETCH_INTERVAL // 60} 分钟")
    print(f"监控站点数: {len(STATIONS)} 个")
    print(f"输出文件: {OUTPUT_CSV}")
    print("-" * 60)
    
    # 打印监控的站点列表
    print("监控站点列表：")
    for stop_id, (route, stop_name) in STATIONS.items():
        print(f"  {route} - {stop_name} -> {stop_id}")
    print("-" * 60)

    # 初始化CSV文件
    try:
        with open(OUTPUT_CSV, 'x', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["采集时间", "路线", "站点名", "站点ID", "方向", "班次序号", "预计到达时间(ETA)", "目的地", "数据生成时间"])
        print("已创建新的CSV文件\n")
    except FileExistsError:
        print("CSV文件已存在，将在末尾追加数据\n")

    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 开始采集...")
        
        rows_to_write = []
        
        for stop_id, (route, stop_name) in STATIONS.items():
            eta_list = fetch_ctb_stop_eta(stop_id)
            
            if not eta_list:
                rows_to_write.append([current_time, route, stop_name, stop_id, "", "", "", "", ""])
                continue
            
            for item in eta_list:
                # 只保留我们关心的路线
                if item.get("route") == route:
                    rows_to_write.append([
                        current_time,
                        route,
                        stop_name,
                        stop_id,
                        item.get("dir", ""),
                        item.get("eta_seq", ""),
                        item.get("eta", ""),
                        item.get("dest_tc", ""),
                        item.get("data_timestamp", "")
                    ])
        
        if rows_to_write:
            with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows_to_write)
            print(f"  ✅ 成功写入 {len(rows_to_write)} 条记录")
        else:
            print(f"  ⚠️ 未获取到任何有效数据")
        
        print(f"等待 {FETCH_INTERVAL // 60} 分钟后进行下一次采集...")
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已手动停止。数据已保存。")