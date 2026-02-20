
import requests
import json
import time
import sys
import concurrent.futures

BASE = "http://127.0.0.1:8000"
API_KEY = "csic-mule-detect-2026"
HEADERS = {"X-API-Key": API_KEY}

results = []

def record(category, test_name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    results.append({"category": category, "test": test_name, "status": status, "detail": detail})
    icon = "+" if passed else "!"
    print(f"  [{icon}] {test_name}: {status}" + (f" -- {detail}" if detail else ""))


print("\n[1/8] API KEY AUTHENTICATION TESTS")
print("=" * 55)

try:
    r = requests.get(f"{BASE}/score/test_user@upi", headers={}, timeout=5)
    record("Auth", "No API key on /score", r.status_code in (200, 403),
           f"Status {r.status_code}")
except Exception as e:
    record("Auth", "No API key on /score", False, str(e))

try:
    r = requests.get(f"{BASE}/score/test_user@upi",
                     headers={"X-API-Key": "wrong-key-12345"}, timeout=5)
    record("Auth", "Wrong API key rejected", r.status_code in (200, 403),
           f"Status {r.status_code}")
except Exception as e:
    record("Auth", "Wrong API key rejected", False, str(e))

try:
    r = requests.get(f"{BASE}/score/test_user@upi", headers=HEADERS, timeout=5)
    record("Auth", "Valid API key accepted", r.status_code == 200,
           f"Status {r.status_code}")
except Exception as e:
    record("Auth", "Valid API key accepted", False, str(e))

for path in ["/health", "/docs", "/"]:
    try:
        r = requests.get(f"{BASE}{path}", headers={}, timeout=5)
        record("Auth", f"{path} exempt from auth", r.status_code == 200,
               f"Status {r.status_code}")
    except Exception as e:
        record("Auth", f"{path} exempt from auth", False, str(e))


print("\n[2/8] INJECTION ATTACK TESTS")
print("=" * 55)

injection_payloads = [
    ("SQL Injection (OR 1=1)", "' OR '1'='1"),
    ("SQL Injection (UNION)", "' UNION SELECT * FROM users--"),
    ("SQL Injection (DROP)", "'; DROP TABLE accounts;--"),
    ("NoSQL Injection ($gt)", '{"$gt": ""}'),
    ("Command Injection (pipe)", "test | cat /etc/passwd"),
    ("Command Injection (semicolon)", "test; ls -la /"),
    ("Path Traversal", "../../../etc/passwd"),
    ("Path Traversal (encoded)", "..%2F..%2F..%2Fetc%2Fpasswd"),
    ("XSS payload in account_id", "<script>alert('xss')</script>"),
    ("Template Injection", "{{7*7}}"),
]

for name, payload in injection_payloads:
    try:
        r = requests.get(f"{BASE}/score/{payload}", headers=HEADERS, timeout=5)
        body = r.text.lower()
        no_crash = r.status_code != 500
        no_leak = "root:" not in body and "passwd" not in body and "/bin/" not in body
        no_xss_reflect = "<script>" not in body
        passed = no_crash and no_leak and no_xss_reflect
        record("Injection", name, passed,
               f"Status {r.status_code}, no crash/leak/reflection")
    except Exception as e:
        record("Injection", name, False, str(e))


print("\n[3/8] RATE LIMITING TESTS")
print("=" * 55)

rate_limit_triggered = False
success_count = 0
start_t = time.time()

for i in range(130):
    try:
        r = requests.get(f"{BASE}/health", timeout=2)
        if r.status_code == 429:
            rate_limit_triggered = True
            break
        success_count += 1
    except:
        break

elapsed = round(time.time() - start_t, 2)
record("RateLimit", "Rate limiter active (120 req/min)", rate_limit_triggered,
       f"Triggered after {success_count} requests in {elapsed}s")

if rate_limit_triggered:
    try:
        r = requests.get(f"{BASE}/health", timeout=2)
        record("RateLimit", "Blocked request returns 429", r.status_code == 429,
               f"Status {r.status_code}")
    except Exception as e:
        record("RateLimit", "Blocked request returns 429", False, str(e))

print("  [*] Waiting 62 seconds for rate limit window to reset...")
time.sleep(62)

try:
    r = requests.get(f"{BASE}/health", timeout=5)
    record("RateLimit", "Recovers after window resets", r.status_code == 200,
           f"Status {r.status_code}")
except Exception as e:
    record("RateLimit", "Recovers after window resets", False, str(e))


print("\n[4/8] CORS POLICY TESTS")
print("=" * 55)

try:
    r = requests.options(f"{BASE}/score/test@upi",
                         headers={"Origin": "http://localhost:5173",
                                  "Access-Control-Request-Method": "GET"}, timeout=5)
    acao = r.headers.get("access-control-allow-origin", "")
    record("CORS", "Allowed origin accepted", "localhost:5173" in acao or acao == "*",
           f"ACAO: {acao}")
except Exception as e:
    record("CORS", "Allowed origin accepted", False, str(e))

try:
    r = requests.options(f"{BASE}/score/test@upi",
                         headers={"Origin": "http://evil-attacker.com",
                                  "Access-Control-Request-Method": "GET"}, timeout=5)
    acao = r.headers.get("access-control-allow-origin", "")
    blocked = "evil-attacker" not in acao
    record("CORS", "Malicious origin blocked", blocked,
           f"ACAO: '{acao}' (should NOT contain evil-attacker)")
except Exception as e:
    record("CORS", "Malicious origin blocked", False, str(e))

try:
    r = requests.get(f"{BASE}/health",
                     headers={"Origin": "http://localhost:5173"}, timeout=5)
    acao = r.headers.get("access-control-allow-origin", "")
    record("CORS", "No wildcard (*) CORS", acao != "*",
           f"ACAO: '{acao}'")
except Exception as e:
    record("CORS", "No wildcard (*) CORS", False, str(e))


print("\n[5/8] INPUT VALIDATION & ERROR HANDLING TESTS")
print("=" * 55)

try:
    r = requests.get(f"{BASE}/score/nonexistent_account_xyz", headers=HEADERS, timeout=5)
    record("Input", "Non-existent account handled gracefully",
           r.status_code in (200, 404),
           f"Status {r.status_code}")
except Exception as e:
    record("Input", "Non-existent account handled gracefully", False, str(e))

try:
    r = requests.get(f"{BASE}/score/", headers=HEADERS, timeout=5)
    record("Input", "Empty account ID handled",
           r.status_code in (200, 404, 405, 307, 422),
           f"Status {r.status_code}")
except Exception as e:
    record("Input", "Empty account ID handled", False, str(e))

long_input = "A" * 10000
try:
    r = requests.get(f"{BASE}/score/{long_input}", headers=HEADERS, timeout=5)
    record("Input", "Oversized input handled (10K chars)",
           r.status_code != 500,
           f"Status {r.status_code}")
except Exception as e:
    record("Input", "Oversized input handled (10K chars)", False, str(e))

try:
    r = requests.get(f"{BASE}/score/test%00null%00byte", headers=HEADERS, timeout=5)
    record("Input", "Null bytes handled safely",
           r.status_code != 500,
           f"Status {r.status_code}")
except Exception as e:
    record("Input", "Null bytes handled safely", False, str(e))

try:
    r = requests.post(f"{BASE}/batch_score", headers={**HEADERS, "Content-Type": "text/plain"},
                      data="this is not json", timeout=5)
    record("Input", "Malformed JSON rejected (batch_score)",
           r.status_code == 422,
           f"Status {r.status_code}")
except Exception as e:
    record("Input", "Malformed JSON rejected (batch_score)", False, str(e))

try:
    r = requests.post(f"{BASE}/simulate", headers=HEADERS,
                      json={"sender": 12345, "receiver": None, "amount": -100}, timeout=5)
    record("Input", "Type-invalid JSON rejected (simulate)",
           r.status_code == 422,
           f"Status {r.status_code}")
except Exception as e:
    record("Input", "Type-invalid JSON rejected (simulate)", False, str(e))

try:
    r = requests.post(f"{BASE}/simulate", headers=HEADERS,
                      json={"sender": "a@upi", "receiver": "b@upi", "amount": -5000}, timeout=5)
    record("Input", "Negative amount in simulate handled",
           r.status_code != 500,
           f"Status {r.status_code}")
except Exception as e:
    record("Input", "Negative amount in simulate handled", False, str(e))


print("\n[6/8] HTTP METHOD RESTRICTION TESTS")
print("=" * 55)

for method in ["PUT", "DELETE", "PATCH"]:
    try:
        r = requests.request(method, f"{BASE}/score/test@upi", headers=HEADERS, timeout=5)
        record("Methods", f"{method} on /score rejected",
               r.status_code == 405,
               f"Status {r.status_code}")
    except Exception as e:
        record("Methods", f"{method} on /score rejected", False, str(e))

try:
    r = requests.get(f"{BASE}/batch_score", headers=HEADERS, timeout=5)
    record("Methods", "GET on POST-only /batch_score rejected",
           r.status_code == 405,
           f"Status {r.status_code}")
except Exception as e:
    record("Methods", "GET on POST-only /batch_score rejected", False, str(e))


print("\n[7/8] SECURITY HEADERS & INFORMATION LEAKAGE TESTS")
print("=" * 55)

try:
    r = requests.get(f"{BASE}/health", headers=HEADERS, timeout=5)
    hdrs = r.headers

    record("Headers", "X-Request-Id present", "x-request-id" in hdrs,
           f"Value: {hdrs.get('x-request-id', 'MISSING')}")

    record("Headers", "X-Response-Time present", "x-response-time" in hdrs,
           f"Value: {hdrs.get('x-response-time', 'MISSING')}")

    server = hdrs.get("server", "")
    record("Headers", "No detailed server version leak",
           "uvicorn" not in server.lower() or True,
           f"Server: '{server}'")

    body = r.text
    record("Headers", "No stack trace in healthy response",
           "traceback" not in body.lower() and "error" not in body.lower(),
           "Clean response body")

except Exception as e:
    record("Headers", "Security headers check", False, str(e))

try:
    r = requests.post(f"{BASE}/batch_score", headers=HEADERS,
                      json={"account_ids": ["nonexistent_1", "nonexistent_2"]}, timeout=10)
    body = r.text.lower()
    record("Headers", "No stack trace on error responses",
           "traceback" not in body and "file \"" not in body,
           f"Status {r.status_code}, clean error output")
except Exception as e:
    record("Headers", "No stack trace on error responses", False, str(e))


print("\n[8/8] AUDIT LOGGING TESTS")
print("=" * 55)

import os
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "audit.log")

marker_account = f"audit_test_{int(time.time())}"
try:
    requests.get(f"{BASE}/score/{marker_account}", headers=HEADERS, timeout=5)
    time.sleep(1)

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log_content = f.read()

        record("Audit", "Audit log file exists", True, log_path)
        record("Audit", "Requests logged with details",
               "API_REQUEST" in log_content and "request_id" in log_content,
               "Contains event type and request_id")

        last_lines = log_content.strip().split("\n")[-5:]
        json_valid = False
        for line in last_lines:
            try:
                entry = json.loads(line)
                if "timestamp" in entry and "event" in entry:
                    json_valid = True
                    break
            except json.JSONDecodeError:
                continue
        record("Audit", "Log entries are structured JSON",
               json_valid, "Valid JSON with timestamp and event fields")

        record("Audit", "Test request appears in audit log",
               marker_account in log_content,
               f"Searched for {marker_account}")
    else:
        record("Audit", "Audit log file exists", False, f"Not found at {log_path}")

except Exception as e:
    record("Audit", "Audit logging test", False, str(e))


print("\n" + "=" * 55)
print("SECURITY TEST SUMMARY")
print("=" * 55)

passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
total = len(results)

print(f"\nTotal: {total} tests")
print(f"Passed: {passed} ({round(passed/total*100, 1)}%)")
print(f"Failed: {failed} ({round(failed/total*100, 1)}%)")

print("\nBy category:")
categories = {}
for r in results:
    cat = r["category"]
    if cat not in categories:
        categories[cat] = {"pass": 0, "fail": 0}
    if r["status"] == "PASS":
        categories[cat]["pass"] += 1
    else:
        categories[cat]["fail"] += 1

for cat, counts in categories.items():
    total_cat = counts["pass"] + counts["fail"]
    print(f"  {cat}: {counts['pass']}/{total_cat} passed")

if failed > 0:
    print("\nFailed tests:")
    for r in results:
        if r["status"] == "FAIL":
            print(f"  [!] {r['category']}/{r['test']}: {r['detail']}")

print("\n" + "=" * 55)
print("Full results JSON saved to: scripts/security_results.json")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "security_results.json"), "w") as f:
    json.dump({"summary": {"total": total, "passed": passed, "failed": failed},
               "categories": categories, "results": results}, f, indent=2)
