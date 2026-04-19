import ssl
import urllib.request
import json

ssl._create_default_https_context = ssl._create_unverified_context

def fetch_stop_list():
    url = "https://data.etabus.gov.hk/v1/transport/kmb/stop"
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        return data.get("data", [])

# 获取所有站点
all_stops = fetch_stop_list()
print(f"共获取 {len(all_stops)} 个站点")

# 创建名称到ID的映射
name_to_id = {}
for stop in all_stops:
    name = stop.get("name_tc", "")
    stop_id = stop.get("stop", "")
    if name and stop_id:
        name_to_id[name] = stop_id

# 你要搜索的站点名称（使用API中的实际名称）
target_stops = {
    "1A": {
        "direction": "O",
        "stop_names": ["尖沙咀碼頭,海港城 (YT901)", "旺角站 (MK621)", "中秀茂坪 (KT975)"]
    },
    "101": {
        "direction": "I",
        "stop_names": ["裕民坊 (KT557)", "紅磡海底隧道", "堅尼地城"]
    },
    "279X": {
        "direction": "O",
        "stop_names": ["聯和墟", "大欖隧道", "青衣站"]
    }
}

print("\n筛选结果：")
for route, info in target_stops.items():
    print(f"\n路线 {route} (方向: {info['direction']}):")
    for stop_name in info["stop_names"]:
        if stop_name in name_to_id:
            print(f"  ✓ {stop_name} -> {name_to_id[stop_name]}")
        else:
            # 尝试模糊搜索
            found = False
            for name, sid in name_to_id.items():
                if stop_name.replace("(", "").replace(")", "") in name:
                    print(f"  ✓ {stop_name} -> {sid} (匹配到: {name})")
                    found = True
                    break
            if not found:
                print(f"  ✗ 未找到: {stop_name}")