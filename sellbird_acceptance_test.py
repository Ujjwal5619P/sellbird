"""Run the eight local Sellbird workflow smoke tests against the running dashboard.
Uses only Python stdlib and the dashboard's local token. No emails are sent.
"""
import json, sys, urllib.request, urllib.error
from pathlib import Path

BASE = 'http://127.0.0.1:5555'
TOKEN_FILE = Path('data/dashboard-token')
if not TOKEN_FILE.exists():
    raise SystemExit('ERROR: data/dashboard-token not found. Run from the Sellbird repository root.')
token = TOKEN_FILE.read_text(encoding='utf-8').strip()
if not token:
    raise SystemExit('ERROR: dashboard token file is empty.')

def request(path, method='GET', payload=None):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=360) as response:
            raw = response.read().decode('utf-8')
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode('utf-8', 'replace')
        try: body = json.loads(raw)
        except Exception: body = {'error': raw[:500]}
        return exc.code, body
    except Exception as exc:
        return 0, {'error': str(exc)}

status, products = request('/api/products')
if status != 200 or not isinstance(products, list) or not products:
    raise SystemExit(f'ERROR: cannot load products (HTTP {status}): {products}')
product = next((p for p in products if p.get('is_active', p.get('enabled', True))), products[0])
pid = product['id']
status, docs = request('/api/research/documents?product_id=' + pid)
if status != 200:
    raise SystemExit(f'ERROR: cannot load research library (HTTP {status}): {docs}')
if not docs:
    raise SystemExit('ERROR: no research documents found for selected product; save downloaded research first.')

cases = [
 ('business_profile', {'product_id': pid, 'company_information': 'Sellbird is a local AI sales workspace. This is a test business profile.'}),
 ('icp', {'product_id': pid, 'company_information': 'Use the product description and existing customer context only.'}),
 ('prospect_research', {'product_id': pid, 'input': {'research_note': 'Use saved local research only.'}}),
 ('buying_signals', {'product_id': pid, 'company_information': 'The prospect requested a demo next month and asked about deployment security.'}),
 ('problem_statement', {'product_id': pid, 'company_information': 'The prospect struggles to verify manipulated media before publishing.'}),
 ('personalized_email', {'product_id': pid, 'company_information': 'Prospect role: Security Lead. Evidence: asked about detecting synthetic audio. Draft only; do not send.'}),
 ('prospect_score', {'product_id': pid, 'company_information': 'Industry: financial services. Role: Security Lead. Need: verify synthetic audio and deepfake media. Timing: evaluating this quarter.'}),
 ('reply_classification', {'product_id': pid, 'conversation_sample': 'Thanks, this looks relevant. Please send available times for a short demo.'}),
]
print('Product:', product.get('name', pid))
print('Saved research documents:', len(docs))
print('\nLOCAL WORKFLOW ACCEPTANCE TEST')
passed = failed = 0
for name, data in cases:
    code, result = request('/api/local/workflows/' + name, 'POST', data)
    ok = code == 200 and isinstance(result, dict) and result.get('success') is True
    print(('PASS' if ok else 'FAIL'), name, '| HTTP', code,
          '| provider:', result.get('provider', '-'),
          '| model:', result.get('model', '-'))
    if not ok:
        print('   ', result.get('error', result))
        failed += 1
    else:
        passed += 1
print(f'\nRESULT: {passed}/8 passed; {failed}/8 failed')
print('No email delivery was invoked.')
sys.exit(0 if failed == 0 else 1)
