import ssl
import urllib.request
import json
import csv
import os
from datetime import datetime

# ================== 配置区域 ==================
OUTPUT_CSV = "bus_eta_data.csv"

STATIONS = {
    "DCFF4041D0C0ACF8": ("1A", "O", "尖沙咀碼頭"),
    "F7CAA2D4FF9D61F7": ("1A", "O", "太子站"), 
    "A3ADFCDF8487ADB9": ("1A", "O", "中秀茂坪"),
    "B7773ED8D2FC08E5": ("101", "I", "裕民坊"),
    "032C7D86DF9ED3AC": ("101", "I", "紅隧轉車站"),
    "002737": ("101", "I", "德輔道中"),    
    "E057FE733052DDD7": ("279X", "O", "聯和墟總站"),
    "3ECEF3B735084236": ("279X", "O", "大欖隧道轉車站"),
    "A2882A0EE6B8AF9B": ("279X", "O", "青衣站"),
}

ssl._create_default_https_context = ssl._create_unverified_context
# ============================================

def fetch_stop_eta(stop_id):
    url = f"https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/{stop_id}"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except Exception as e:
        print(f"  [错误] 站点 {stop_id} 请求失败: {e}")
        return []

def main():
    print("=" * 60)
    print("香港巴士ETA数据采集程序")
    print("=" * 60)
    print(f"监控站点数: {len(STATIONS)} 个")
    print(f"输出文件: {OUTPUT_CSV}")
    print("-" * 60)

    file_exists = os.path.isfile(OUTPUT_CSV)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] 开始采集...")
    
    rows_to_write = []
    
    for stop_id, (route, direction, stop_name) in STATIONS.items():
        eta_list = fetch_stop_eta(stop_id)
        
        if not eta_list:
            rows_to_write.append([current_time, route, direction, stop_name, stop_id, "", "", ""])
            continue
        
        for item in eta_list:
            if item.get("route") == route:
                rows_to_write.append([
                    current_time, route, direction, stop_name, stop_id,
                    item.get("eta_seq", ""), item.get("eta", ""), item.get("data_timestamp", "")
                ])
    
    if rows_to_write:
        with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["采集时间", "路线", "方向", "站点名", "站点ID", "班次序号", "预计到达时间(ETA)", "数据生成时间"])
            writer.writerows(rows_to_write)
        print(f"  ✅ 成功写入 {len(rows_to_write)} 条记录")
    else:
        print(f"  ⚠️ 未获取到任何有效数据")

if __name__ == "__main__":
    main()