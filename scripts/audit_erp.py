from pathlib import Path
from zipfile import ZipFile
import argparse
import io
import json
import re
import subprocess


parser = argparse.ArgumentParser(description='Проверка размеров исходников и состава разделов ERP')
parser.add_argument('--repo', required=True)
parser.add_argument('--ref', default='origin/main')
parser.add_argument('--output', required=True)
args = parser.parse_args()


def git(*parts):
  return subprocess.check_output(['git', '-C', args.repo, *parts])


sha = git('rev-parse', args.ref).decode().strip()
archive = ZipFile(io.BytesIO(git('archive', '--format=zip', args.ref, 'frontend/src', 'backend/src', 'boards-sync/src', 'version.json')))
files = archive.namelist()
test_pattern = re.compile(r'(?:^|/)(?:__tests__|__mocks__)/|\.(?:test|spec)\.[jt]sx?$')
code = [f for f in files if f.endswith(('.ts', '.tsx', '.js', '.jsx')) and not test_pattern.search(f) and not f.endswith('.d.ts') and '/generated/' not in f and '/mocks/' not in f]
tests = [f for f in files if re.search(r'\.(?:test|spec)\.[jt]sx?$', f)]
parts = {}
for folder in ['frontend/src', 'backend/src', 'boards-sync/src']:
  group = [f for f in code if f.startswith(folder + '/')]
  parts[folder] = {'files': len(group), 'nonblank_lines': sum(sum(bool(line.strip()) for line in archive.read(f).decode('utf-8-sig').splitlines()) for f in group)}
nav = archive.read('frontend/src/constants/headerNav.ts').decode('utf-8-sig')
items = re.findall(r"\{\s*id:\s*'([^']+)'\s*,\s*label:\s*'([^']+)'\s*,\s*path:\s*'([^']+)'", nav)
data = {'commit': sha, 'version': json.loads(archive.read('version.json')), 'source_files': len(code), 'nonblank_source_lines': sum(p['nonblank_lines'] for p in parts.values()), 'test_files': len(tests), 'parts': parts, 'navigation': [{'id': i, 'label': label, 'path': path} for i, label, path in items], 'agent_route_groups': [f for f in code if f.startswith('backend/src/routes/agent') and f.endswith('Routes.ts')]}
Path(args.output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({key: data[key] for key in ['commit', 'version', 'source_files', 'nonblank_source_lines', 'test_files']}, ensure_ascii=False))
