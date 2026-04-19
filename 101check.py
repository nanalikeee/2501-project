import ssl
import urllib.request
import json

ssl._create_default_https_context = ssl._create_unverified_context

route = "101"
bound = "O"  # 从 /route/ 接口获取的值

# 常见的 service_type 值
service_types_to_try = ["1", "2", "3", "4", "5"]

for service_type in service_types_to_try:
    url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{bound}/{service_type}"
    print(f"尝试 URL: {url}")
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            stops = data.get("data", [])
            if stops:
                print(f"✅ 成功！service_type = {service_type} 有效")
                print(f"   共找到 {len(stops)} 个站点")
                # 打印前5个站点作为验证
                for stop in stops[:5]:
                    print(f"   seq {stop.get('seq')}: stop_id = {stop.get('stop')}")
                break
            else:
                print(f"❌ service_type = {service_type} 返回空数据")
    except Exception as e:
        print(f"❌ service_type = {service_type} 失败: {e}")