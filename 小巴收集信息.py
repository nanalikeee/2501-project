import ssl
import urllib.request
import json
import csv
import os
from datetime import datetime, timezone, timedelta

# ================== 配置区域 ==================
OUTPUT_CSV = "gmb_eta_data.csv"

STOPS_GMB10 = {
    "20014859": "10号-謝斐道, 近兆安廣場（始发站）",
    "20000009": "10号-薄扶林道, 寶翠園對面",
    "20014874": "10号-數碼港巴士總站（终点站）",
}
ROUTE_ID_GMB10 = 2006706

STOPS_GMB58 = {
    "20009733": "58号-堅尼地城站（始发站）",
    "20004594": "58号-沙灣徑, 麥理浩復康院外",
    "20000326": "58号-湖南街, 安泰大廈外（终点站）",
}
ROUTE_ID_GMB58 = 2002580

STOPS = {**STOPS_GMB10, **STOPS_GMB58}

ssl._create_default_https_context = ssl._create_unverified_context
# ============================================

def fetch_stop_eta(stop_id):
    url = f"https://data.etagmb.gov.hk/eta/stop/{stop_id}"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except Exception as e:
        print(f"  [错误] 站点 {stop_id} 请求失败: {e}")
        return []

def get_route_from_stop(stop_id):
    if stop_id in STOPS_GMB10:
        return "10"
    elif stop_id in STOPS_GMB58:
        return "58"
    return "未知"

def main():
    print("=" * 60)
    print("绿色小巴 ETA 数据采集程序")
    print("=" * 60)
    print(f"监控站点数: {len(STOPS)} 个")
    print(f"输出文件: {OUTPUT_CSV}")
    print("-" * 60)

    file_exists = os.path.isfile(OUTPUT_CSV)
    
    # 使用香港时区 UTC+8
    hong_kong_tz = timezone(timedelta(hours=8))
    current_time = datetime.now(hong_kong_tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] 开始采集...")
    
    rows_to_write = []
    
    for stop_id, stop_name in STOPS.items():
        route = get_route_from_stop(stop_id)
        eta_list = fetch_stop_eta(stop_id)
        
        if not eta_list:
            rows_to_write.append([current_time, route, stop_name, stop_id, "", "", "", "", "", ""])
            continue
        
        for item in eta_list:
            item_route = item.get("route", "")
            item_route_id = item.get("route_id", "")
            
            if route == "10" and (item_route == "10" or item_route_id == ROUTE_ID_GMB10):
                rows_to_write.append([
                    current_time, "10", stop_name, stop_id,
                    item.get("dir", ""), item.get("eta_seq", ""),
                    item.get("eta", ""), item.get("dest_tc", "") or item.get("dest", ""),
                    item.get("rmk_tc", "") or item.get("remark", ""),
                    item.get("data_timestamp", "")
                ])
                print(f"  ✅ {stop_name}: ETA = {item.get('eta', '暂无')}")
                
            elif route == "58" and (item_route == "58" or item_route_id == ROUTE_ID_GMB58):
                rows_to_write.append([
                    current_time, "58", stop_name, stop_id,
                    item.get("dir", ""), item.get("eta_seq", ""),
                    item.get("eta", ""), item.get("dest_tc", "") or item.get("dest", ""),
                    item.get("rmk_tc", "") or item.get("remark", ""),
                    item.get("data_timestamp", "")
                ])
                print(f"  ✅ {stop_name}: ETA = {item.get('eta', '暂无')}")
    
    if rows_to_write:
        with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["采集时间", "路线", "站点名", "站点ID", "方向", "班次序号", "预计到达时间(ETA)", "目的地", "备注", "数据生成时间"])
            writer.writerows(rows_to_write)
        print(f"  ✅ 成功写入 {len(rows_to_write)} 条记录")
    else:
        print(f"  ⚠️ 未获取到任何有效数据")

if __name__ == "__main__":
    main()
