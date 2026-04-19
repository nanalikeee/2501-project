import ssl
import urllib.request
import json

ssl._create_default_https_context = ssl._create_unverified_context

def get_route_stops(route, direction="O", service_type="1"):
    """获取路线的站点列表"""
    url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{direction}/{service_type}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except Exception as e:
        print(f"获取 {route} 失败: {e}")
        return []

def get_stop_name(stop_id):
    """获取站点名称"""
    url = f"https://data.etabus.gov.hk/v1/transport/kmb/stop/{stop_id}"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            stop_info = data.get("data", {})
            return stop_info.get("name_tc", "未知")
    except:
        return "未知"

# 获取龙运路线的站点
routes = ["A31", "A41", "E33"]

for route in routes:
    print(f"\n{'='*50}")
    print(f"路线: {route}")
    print('='*50)
    
    stops = get_route_stops(route)
    if not stops:
        print(f"无法获取 {route} 的站点列表")
        continue
    
    print(f"共 {len(stops)} 个站点\n")
    
    for stop in stops[:15]:  # 打印前15个
        stop_id = stop.get("stop")
        seq = stop.get("seq")
        stop_name = get_stop_name(stop_id)
        print(f"  seq {seq:3d}: {stop_name} -> {stop_id}")