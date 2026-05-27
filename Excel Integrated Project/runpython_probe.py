from pathlib import Path
import sys, time, json
out = Path(__file__).parent / 'outputs' / 'run_annotator_python_log.txt'
out.parent.mkdir(parents=True, exist_ok=True)
info = {
    'time': time.strftime('%Y-%m-%d %H:%M:%S'),
    'executable': sys.executable,
    'version': sys.version,
    'cwd': str(Path.cwd()),
    'sys_path': sys.path[:20]
}
with open(out, 'a', encoding='utf8') as f:
    f.write(json.dumps(info) + '\n')
