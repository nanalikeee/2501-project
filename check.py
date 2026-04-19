import ssl
import urllib.request
import json

ssl._create_default_https_context = ssl._create_unverified_context

route = "101"
direction = "I"  # 入城方向（觀塘 → 堅尼地城）

# 测试服务类型 1 和 2
for service_type in ["1", "2"]:
    url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{direction}/{service_type}"
    print(f"\n尝试 URL: {url}")
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            stops = data.get("data", [])
            if stops:
                print(f"✅ 成功！service_type = {service_type}")
                print(f"   共找到 {len(stops)} 个站点")
                # 打印前10个站点
                for stop in stops[:10]:
                    print(f"   seq {stop.get('seq')}: stop_id = {stop.get('stop')}")
                break
            else:
                print(f"❌ service_type = {service_type} 返回空数据")
    except Exception as e:
        print(f"❌ service_type = {service_type} 失败: {e}")