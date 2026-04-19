import ssl
import urllib.request
import json
import time
import csv
from datetime import datetime

# ================== 配置区域 ==================
# 采集间隔（秒），5分钟 = 300秒
FETCH_INTERVAL = 300

# 输出文件名
OUTPUT_CSV = "bus_eta_data.csv"

# 要采集的站点（根据你整理的表格）
# 格式: stop_id -> (路线号, 方向, 站点名称)
STATIONS = {
    # 1A 路线 (方向 O: 尖沙咀 → 秀茂坪)
    "DCFF4041D0C0ACF8": ("1A", "O", "尖沙咀碼頭"),
    "F7CAA2D4FF9D61F7": ("1A", "O", "太子站"), 
    "A3ADFCDF8487ADB9": ("1A", "O", "中秀茂坪"),
    
    # 101X 路线 (方向 I: 觀塘 → 堅尼地城)
    "B7773ED8D2FC08E5": ("101", "I", "裕民坊"),          # ← 改为 101X
    "032C7D86DF9ED3AC": ("101", "I", "紅隧轉車站"),      # ← 改为 101X
    "002737": ("101", "I", "德輔道中"),        # ← 改为 101X
    
    # 279X 路线 (方向 O: 聯和墟 → 青衣)
    "E057FE733052DDD7": ("279X", "O", "聯和墟總站"),
    "3ECEF3B735084236": ("279X", "O", "大欖隧道轉車站"),
    "A2882A0EE6B8AF9B": ("279X", "O", "青衣站"),
}

# 解决 SSL 证书问题
ssl._create_default_https_context = ssl._create_unverified_context
# ============================================

def fetch_stop_eta(stop_id):
    """获取单个站点的实时ETA数据"""
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
    print(f"采集间隔: {FETCH_INTERVAL // 60} 分钟")
    print(f"监控站点数: {len(STATIONS)} 个")
    print(f"输出文件: {OUTPUT_CSV}")
    print("-" * 60)
    
    # 打印监控的站点列表
    print("监控站点列表：")
    for stop_id, (route, direction, stop_name) in STATIONS.items():
        print(f"  {route} {direction} - {stop_name} -> {stop_id}")
    print("-" * 60)

    # 初始化CSV文件（如果文件不存在，写入表头）
    try:
        with open(OUTPUT_CSV, 'x', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["采集时间", "路线", "方向", "站点名", "站点ID", "班次序号", "预计到达时间(ETA)", "数据生成时间"])
        print("已创建新的CSV文件\n")
    except FileExistsError:
        print("CSV文件已存在，将在末尾追加数据\n")

    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 开始采集...")
        
        rows_to_write = []
        
        for stop_id, (route, direction, stop_name) in STATIONS.items():
            eta_list = fetch_stop_eta(stop_id)
            
            if not eta_list:
                # 没有数据时记录一条空记录，便于排查
                rows_to_write.append([current_time, route, direction, stop_name, stop_id, "", "", ""])
                continue
            
            for item in eta_list:
                # 只保留我们关心的路线
                if item.get("route") == route:
                    rows_to_write.append([
                        current_time,
                        route,
                        direction,
                        stop_name,
                        stop_id,
                        item.get("eta_seq", ""),
                        item.get("eta", ""),
                        item.get("data_timestamp", "")
                    ])
        
        # 将本次采集的数据追加写入CSV文件
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