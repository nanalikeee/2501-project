from hk_bus_eta import HKEta
import csv
import time
from datetime import datetime

FETCH_INTERVAL = 300
OUTPUT_CSV = "ctb_bus_eta_data.csv"

ROUTES = {
    "10+1+Kennedy Town+North Point Ferry Pier": "CTB 10",
    "619+1+CENTRAL (MACAO FERRY)+SHUN LEE": "CTB 619",
    "969+1+Tin Shui Wai Town Centre+Causeway Bay (Moreton Terrace)": "CTB 969",
}

def main():
    print("=" * 60)
    print("城巴 ETA 数据采集程序 (采集所有数据)")
    print("=" * 60)
    
    hk_eta = HKEta()
    print("初始化成功\n")
    
    # 初始化 CSV
    try:
        with open(OUTPUT_CSV, 'x', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["采集时间", "路线ID", "路线名称", "方向", "站点名", "站点ID", "班次序号", "ETA", "目的地", "备注"])
        print("已创建 CSV 文件\n")
    except FileExistsError:
        print("CSV 文件已存在\n")
    
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 开始采集...")
        
        rows = []
        
        for route_id, name in ROUTES.items():
            try:
                etas = hk_eta.getEtas(route_id=route_id, seq=0, language="zh")
                print(f"  {route_id}: {len(etas)} 条")
                
                for eta in etas:
                    # 打印所有字段，看看有什么
                    print(f"    字段: {eta.keys()}")
                    rows.append([
                        current_time,
                        route_id,
                        name,
                        "去程",
                        eta.get("stopName", ""),
                        eta.get("stopId", ""),
                        eta.get("etaSeq", ""),
                        eta.get("eta", ""),
                        eta.get("dest", ""),
                        eta.get("remark", "")
                    ])
            except Exception as e:
                print(f"  {route_id}: 错误 {e}")
        
        if rows:
            with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            print(f"  写入 {len(rows)} 条")
        
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n停止")