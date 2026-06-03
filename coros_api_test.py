"""Test COROS Training Hub API with correct auth and parameters."""
import json
import requests

# Auth data (char codes)
tc = [49,80,73,75,84,50,51,77,74,69,70,73,73,74,77,66,82,52,86,56,48,84,48,87,74,73,70,52,48,55,89,85]
uc = [52,53,49,56,55,50,48,56,49,52,50,48,55,54,51,49,51,55]

token = ''.join(chr(c) for c in tc)
user_id = ''.join(chr(c) for c in uc)

print(f"Token: {token[:4]}...{token[-4:]} ({len(token)} chars)")
print(f"UserId: {user_id}")

# Headers matching the page's working calls exactly
headers = {
    'Accept': 'application/json, text/plain, */*',
    'accessToken': token,
    'YFHeader': json.dumps({"userId": user_id}),
    'Origin': 'https://t.coros.com',
    'Referer': 'https://t.coros.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
}

# Cookies
cookies = {
    'CPL-coros-token': token,
    'CPL-coros-region': '2',
}

# Test 1: Working endpoint (teamlist)
print("\n--- Test 1: teamlist (known working) ---")
resp = requests.get('https://teamcnapi.coros.com/team/user/teamlist', headers=headers, cookies=cookies, timeout=15)
data = resp.json()
print(f"Result: {data['result']} ({data.get('message','')})")

# Test 2: Schedule query with CORRECT params
print("\n--- Test 2: schedule/query (correct params) ---")
resp = requests.get('https://teamcnapi.coros.com/training/schedule/query',
    params={'startDate': '20260518', 'endDate': '20260524', 'supportRestExercise': 'true'},
    headers=headers, cookies=cookies, timeout=15)
data = resp.json()
print(f"Result: {data['result']} ({data.get('message','')}) bodyLen={len(resp.text)}")

# Test 3: Try without Origin/Referer
print("\n--- Test 3: without Origin/Referer ---")
h2 = {k:v for k,v in headers.items() if k not in ('Origin', 'Referer')}
resp = requests.get('https://teamcnapi.coros.com/training/schedule/query',
    params={'startDate': '20260518', 'endDate': '20260524', 'supportRestExercise': 'true'},
    headers=h2, cookies=cookies, timeout=15)
data = resp.json()
print(f"Result: {data['result']} ({data.get('message','')}) bodyLen={len(resp.text)}")

# Test 4: Try POST instead of GET
print("\n--- Test 4: POST method ---")
resp = requests.post('https://teamcnapi.coros.com/training/schedule/query',
    json={'startDate': '20260518', 'endDate': '20260524', 'supportRestExercise': True},
    headers=headers, cookies=cookies, timeout=15)
data = resp.json()
print(f"Result: {data['result']} ({data.get('message','')}) bodyLen={len(resp.text)}")

# Test 5: Try with session (automatic cookie handling)
print("\n--- Test 5: with requests.Session ---")
sess = requests.Session()
sess.cookies.update(cookies)
sess.headers.update(headers)
resp = sess.get('https://teamcnapi.coros.com/training/schedule/query',
    params={'startDate': '20260518', 'endDate': '20260524', 'supportRestExercise': 'true'},
    timeout=15)
data = resp.json()
print(f"Result: {data['result']} ({data.get('message','')}) bodyLen={len(resp.text)}")
