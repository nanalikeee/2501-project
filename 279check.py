import ssl
import urllib.request
import json

ssl._create_default_https_context = ssl._create_unverified_context

# 第一步：获取 279X 的路线信息
print("正在获取 279X 路线信息...")
url = "https://data.etabus.gov.hk/v1/transport/kmb/route/"
with urllib.request.urlopen(url, timeout=10) as response:
    data = json.loads(response.read().decode('utf-8'))
    routes = data.get("data", [])

# 找到 279X
route_279x = None
for r in routes:
    if r.get("route") == "279X":
        route_279x = r
        print(f"找到 279X: bound={r.get('bound')}, service_type={r.get('service_type')}")
        break

if not route_279x:
    print("未找到 279X 路线")
    exit()

bound = route_279x.get("bound")
service_type = route_279x.get("service_type")

# 第二步：获取 279X 的站点列表（路线-站点关联）
print(f"\n正在获取 279X 的站点列表...")
url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-stop/279X/{bound}/{service_type}"
with urllib.request.urlopen(url, timeout=10) as response:
    data = json.loads(response.read().decode('utf-8'))
    stop_relations = data.get("data", [])

print(f"279X 共有 {len(stop_relations)} 个站点\n")

# 第三步：获取每个站点的详细信息（名称）
print("站点列表：")
print("-" * 60)

for rel in stop_relations:
    stop_id = rel.get("stop")
    seq = rel.get("seq")
    
    # 获取站点名称
    stop_url = f"https://data.etabus.gov.hk/v1/transport/kmb/stop/{stop_id}"
    try:
        with urllib.request.urlopen(stop_url, timeout=5) as resp:
            stop_data = json.loads(resp.read().decode('utf-8'))
            stop_info = stop_data.get("data", {})
            stop_name = stop_info.get("name_tc", "未知")
            print(f"seq {seq:3d}: {stop_name} -> {stop_id}")
    except:
        print(f"seq {seq:3d}: (无法获取名称) -> {stop_id}")