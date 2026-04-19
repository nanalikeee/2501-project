from hk_bus_eta import HKEta

hk_eta = HKEta()

# 测试三条路线
routes = [
    "10+1+Kennedy Town+North Point Ferry Pier",
    "619+1+CENTRAL (MACAO FERRY)+SHUN LEE",
    "969+1+Tin Shui Wai Town Centre+Causeway Bay (Moreton Terrace)"
]

for route_id in routes:
    print(f"\n{'='*50}")
    print(f"路线: {route_id}")
    print('='*50)
    try:
        etas = hk_eta.getEtas(route_id=route_id, seq=0, language="zh")
        print(f"共获取 {len(etas)} 条记录\n")
        for eta in etas:
            print(f"  站点: {eta.get('stopName')}")
            print(f"  站点ID: {eta.get('stopId')}")
            print(f"  ETA: {eta.get('eta')}")
            print(f"  目的地: {eta.get('dest')}")
            print(f"  班次序号: {eta.get('etaSeq')}")
            print("-" * 40)
    except Exception as e:
        print(f"错误: {e}")