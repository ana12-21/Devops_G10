import hashlib
import json
from pathlib import Path

root = Path('work')
summary = {}
logs = (root / 'services.log').read_text()
for name in ['e14-sample-01', 'e14-real-01', 'e14-recovery-01']:
    folder = root / name
    result = json.loads((folder / 'result.json').read_text())
    assert result['status'] == 'SUCCEEDED'
    assert [s['name'] for s in result['stages']] == ['draft', 'full-check', 'incremental-check', 'repair', 'recheck']
    for stage in result['stages']:
        value = json.loads((folder / stage['artifact']['uri']).read_text())
        assert value['job_id'] == result['job_id'] and value['trace_id'] == result['trace_id']
        assert value['status'] == 'SUCCEEDED'
    for item in result['artifacts']:
        data = (folder / item['uri']).read_bytes()
        assert len(data) == item['bytes']
        assert hashlib.sha256(data).hexdigest() == item['sha256']
    report = folder / 'incremental/incremental-check.json'
    response = json.loads((folder / 'incremental-response.json').read_text())
    assert hashlib.sha256(report.read_bytes()).hexdigest() == response['sha256']
    assert json.loads((folder / 'repair-response.json').read_text())['validation']['accepted']
    assert json.loads((folder / 'recheck.json').read_text())['data']['remaining_missing'] == 0
    for role in ['buildchecker', 'echecker', 'draft', 'mdfixer']:
        assert any(result['job_id'] in line and '"role": "' + role + '"' in line and 'elapsed_ms' in line for line in logs.splitlines())
    summary[name] = {'status': 'PASS', 'job_id': result['job_id'], 'trace_id': result['trace_id'], 'artifacts_verified': len(result['artifacts'])}
bad = json.loads((root / 'e14-timeout-01/result.json').read_text())
assert bad['status'] == 'FAILED' and 'TIMEOUT' in bad['error']
assert bad['job_id'] != summary['e14-recovery-01']['job_id']
assert bad['trace_id'] != summary['e14-recovery-01']['trace_id']
assert (root / 'timeout-processes.txt').stat().st_size == 0
summary['timeout'] = {'status': 'EXPECTED_FAILURE', 'job_id': bad['job_id'], 'matching_build_clients_at_check': 0}
(root / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
