import urllib.request
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

stop_id = "001227"
url = f"https://rt.data.gov.hk/v2/transport/citybus/eta/stop/{stop_id}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")