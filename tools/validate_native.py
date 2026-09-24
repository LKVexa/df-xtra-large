"""Run the embedded VM/world tests in a disposable copy; requires Java and POSIX."""
from pathlib import Path
import os,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
PAYLOAD=next((ROOT/'vm').iterdir())
with tempfile.TemporaryDirectory(prefix='df-xlarge-native-') as temp:
    vm=Path(temp)/'payload'
    shutil.copytree(PAYLOAD,vm,ignore=shutil.ignore_patterns('.build','__pycache__'))
    for script in ('vm/tests/test_vm.py','vm/world/tests/test_world_runtime.py',
                   'vm/world/tests/test_blocked_gate_remediation.py','vm/world/tests/test_operational_reference.py'):
        result=subprocess.run([sys.executable,'-B',script],cwd=vm,capture_output=True,text=True,
                              encoding='utf-8',errors='replace',timeout=600,
                              env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        output=result.stdout+result.stderr
        print(script, result.returncode, flush=True)
        print('\n'.join(output.splitlines()[-8:]) if not result.returncode else output[-16000:],flush=True)
        if result.returncode:raise SystemExit(result.returncode)
print('QUORUM_NATIVE_REGRESSIONS_PASS')
