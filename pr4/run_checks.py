"""Reproduce PR4 checks. Run --setup once, then --group all (Python 3.11+, JDK 17+)."""

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
import venv
import zipfile

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / '.tools'
RESULTS = ROOT / 'results' / 'rerun'
BUILD = ROOT / 'build'
JAVA_TOOLS = {
    'checkstyle-10.21.4-all.jar':
        'https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.21.4/checkstyle-10.21.4-all.jar',
    'pmd-bin-6.55.0.zip':
        'https://github.com/pmd/pmd/releases/download/pmd_releases%2F6.55.0/pmd-bin-6.55.0.zip',
    'spotbugs-4.9.3.zip':
        'https://repo.maven.apache.org/maven2/com/github/spotbugs/spotbugs/4.9.3/spotbugs-4.9.3.zip',
}


def python_tool():
    return TOOLS / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def setup():
    TOOLS.mkdir(exist_ok=True)
    if not python_tool().exists():
        venv.create(TOOLS / 'venv', with_pip=True)
    subprocess.run([str(python_tool()), '-m', 'pip', 'install', '-r',
                    str(ROOT / 'requirements-tools.txt')], check=True)
    for name, url in JAVA_TOOLS.items():
        destination = TOOLS / name
        if not destination.exists():
            print(f'Downloading {url}', flush=True)
            temporary = destination.with_suffix(destination.suffix + '.part')
            with urllib.request.urlopen(url, timeout=120) as response:
                with temporary.open('wb') as stream:
                    shutil.copyfileobj(response, stream)
            temporary.replace(destination)
        if name.endswith('.zip'):
            with zipfile.ZipFile(destination) as archive:
                # Refuse archive entries outside the tool directory.
                for member in archive.infolist():
                    (TOOLS / member.filename).resolve().relative_to(TOOLS.resolve())
                archive.extractall(TOOLS)
    print('Setup complete. Run: python run_checks.py --group all --java-home <JDK directory>')


def java_executable(home, name):
    if home:
        path = Path(home) / 'bin' / (name + ('.exe' if os.name == 'nt' else ''))
        if not path.is_file():
            raise RuntimeError(f'JDK executable missing: {path}')
        return str(path)
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f'{name} not found. Set JAVA_HOME to JDK 17+ or use --java-home.')
    return path


def execute(name, command, allowed=(0,)):
    command = [str(value) for value in command]
    print(f'[{name}] {subprocess.list2cmdline(command)}', flush=True)
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1', NO_COLOR='1')
    result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, encoding='utf-8', errors='replace',
                            timeout=180)
    text = (f'COMMAND: {subprocess.list2cmdline(command)}\nEXIT: {result.returncode}\n\n'
            + result.stdout)
    (RESULTS / f'{name}.txt').write_text(text, encoding='utf-8')
    if result.returncode not in allowed:
        raise RuntimeError(f'{name} failed with exit {result.returncode}; see {RESULTS / (name + ".txt")}')
    return result.stdout, result.returncode


def python_checks(group, rows):
    interpreter = python_tool()
    if not interpreter.is_file():
        raise RuntimeError('Run python run_checks.py --setup first.')
    if group in ('all', 'static'):
        for version in ('baseline', 'static_faults'):
            target = f'python/{version}/library_manager.py'
            commands = {
                'pylint': [interpreter, '-m', 'pylint', '--output-format=text',
                           '--score=n', '--reports=n', '--persistent=n', target],
                'ruff': [interpreter, '-m', 'ruff', 'check', '--isolated', '--select',
                         'E,F,N,S,B', '--output-format', 'concise', target],
                'bandit': [interpreter, '-m', 'bandit', '-q', '-f', 'json', target],
            }
            for tool, command in commands.items():
                allowed = tuple(range(32)) if tool == 'pylint' else (0, 1)
                output, code = execute(f'python_{version}_{tool}', command, allowed)
                if tool == 'pylint':
                    if code & (1 | 32) or 'Traceback' in output:
                        raise RuntimeError('Pylint execution error')
                    count = len(re.findall(r':\d+:\d+: [A-Z]\d{4}:', output))
                elif tool == 'ruff':
                    count = len(re.findall(r':\d+:\d+: [A-Z]+\d+ ', output))
                else:
                    report = json.loads(output)
                    if report.get('errors'):
                        raise RuntimeError('Bandit could not analyze the source')
                    count = len(report['results'])
                rows.append(dict(language='Python', version=version, tool=tool, count=count))
    if group in ('all', 'dynamic'):
        for version, failures in (('baseline', 0), ('dynamic_faults', 3)):
            execute(f'python_{version}_dynamic', [interpreter, 'python/dynamic_check.py',
                    f'python/{version}', '--profile',
                    RESULTS / f'python_{version}.prof', '--expect-failures', failures])


def java_checks(group, home, rows):
    java = java_executable(home, 'java')
    javac = java_executable(home, 'javac')
    jfr = java_executable(home, 'jfr')
    execute('java_version', [java, '-version'])
    execute('javac_version', [javac, '-version'])
    versions = ('baseline', 'static_faults', 'dynamic_faults') if group == 'all' else (
        ('baseline', 'static_faults') if group == 'static' else ('baseline', 'dynamic_faults'))
    for version in versions:
        classes = BUILD / version
        classes.mkdir(parents=True, exist_ok=True)
        sources = [f'java/{version}/Converter.java']
        if version != 'static_faults':
            sources += ['java/Probe.java', 'java/RuntimeMonitor.java', 'java/MonitorProbe.java']
        execute(f'java_{version}_build', [javac, '--release', '17', '-encoding', 'UTF-8',
                                        '-d', classes, *sources])
    if group in ('all', 'static'):
        for version in ('baseline', 'static_faults'):
            target = f'java/{version}/Converter.java'
            checkstyle = TOOLS / 'checkstyle-10.21.4-all.jar'
            pmd = TOOLS / 'pmd-bin-6.55.0' / 'lib' / '*'
            spotbugs = TOOLS / 'spotbugs-4.9.3' / 'lib' / 'spotbugs.jar'
            output, _ = execute(f'java_{version}_checkstyle', [java, '-Dfile.encoding=UTF-8',
                '-jar', checkstyle, '-c', '/google_checks.xml', target], (0, 1))
            rows.append(dict(language='Java', version=version, tool='checkstyle',
                             count=len(re.findall(r'\[(?:WARN|ERROR)\]', output))))
            output, _ = execute(f'java_{version}_pmd', [java, '-Dfile.encoding=UTF-8', '-cp', pmd,
                'net.sourceforge.pmd.PMD', '-d', target, '-R',
                'category/java/bestpractices.xml,category/java/errorprone.xml',
                '-f', 'text', '--no-cache'], (0, 4))
            rows.append(dict(language='Java', version=version, tool='pmd',
                             count=len(re.findall(r'Converter\.java:\d+:', output))))
            output, _ = execute(f'java_{version}_spotbugs', [java, '-Dfile.encoding=UTF-8',
                '-jar', spotbugs, '-textui', '-effort:max', '-low', '-exitcode',
                BUILD / version / 'Converter.class'], (0, 1))
            rows.append(dict(language='Java', version=version, tool='spotbugs',
                             count=len(re.findall(r'^[HML] [A-Z] ', output, re.MULTILINE))))
    if group in ('all', 'dynamic'):
        for version, failures in (('baseline', 0), ('dynamic_faults', 3)):
            recording = RESULTS / f'java_{version}.jfr'
            execute(f'java_{version}_jmx', [java, '-cp', BUILD / version,
                    'RuntimeMonitor', recording, failures])
            summary, _ = execute(f'java_{version}_jfr', [jfr, 'summary', recording])
            if not re.search(r'pr4\.Workload\s+1\s', summary):
                raise RuntimeError('JFR recording is missing the measured workload event')
            execute(f'java_{version}_jfr_event', [jfr, 'print', '--events', 'pr4.Workload', recording])


def make_report(rows, manifest):
    """Render actual captured output as a local HTML report for review/screenshots."""
    style = '''body{margin:32px;font:18px Arial;color:#17212b;background:#fff}
    h1{font-size:28px}h2{font-size:22px}h3{font-size:19px}
    pre{font:15px/1.35 Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;
    background:#f4f6f8;padding:14px;border:1px solid #cbd2d9}a{color:#0757a6}
    table{border-collapse:collapse}td,th{border:1px solid #cbd2d9;padding:8px 16px}
    section{margin:24px 0 36px}.note{color:#505c68}'''
    def log(name):
        return (RESULTS / f'{name}.txt').read_text(encoding='utf-8')
    def body(name):
        return log(name).split('\n\n', 1)[1].strip().replace(str(ROOT) + os.sep, '')
    def block(title, content):
        return f'<h3>{html.escape(title)}</h3><pre>{html.escape(content)}</pre>'
    sections = {}
    sections['python_dynamic'] = ''.join(block(f'Python {v} — cProfile + tracemalloc',
        body(f'python_{v}_dynamic')) for v in ('baseline', 'dynamic_faults')
        if manifest['group'] in ('all', 'dynamic') and manifest['language'] in ('all', 'python')
        and (RESULTS / f'python_{v}_dynamic.txt').exists())
    sections['java_dynamic'] = ''
    for version in ('baseline', 'dynamic_faults'):
        if manifest['group'] not in ('all', 'dynamic') or manifest['language'] not in ('all', 'java'):
            continue
        if not (RESULTS / f'java_{version}_jmx.txt').exists():
            continue
        summary = body(f'java_{version}_jfr')
        # Relevant lines only; full jfr summary remains linked in the report.
        selected = '\n'.join(line for line in summary.splitlines()
                             if any(key in line for key in ('Version:', 'Chunks:', 'Duration:',
                                 'Event Type', 'pr4.Workload', 'jdk.ExecutionSample',
                                 'jdk.GarbageCollection', 'jdk.GCHeapSummary',
                                 'jdk.ThreadAllocationStatistics')))
        sections['java_dynamic'] += block(f'Java {version} — JMX + JFR',
            body(f'java_{version}_jmx') + '\n\nJFR summary (selected rows):\n' + selected
            + '\n\n' + body(f'java_{version}_jfr_event'))
    for language, tools in (('python', ('pylint', 'ruff', 'bandit')),
                            ('java', ('checkstyle', 'pmd', 'spotbugs'))):
        for version in ('baseline', 'static_faults'):
            content = ''
            for tool in tools:
                row = next((row for row in rows if row['language'].lower() == language
                            and row['version'] == version and row['tool'] == tool), None)
                if row is None:
                    continue
                name = f'{language}_{version}_{tool}'
                if not (RESULTS / f'{name}.txt').exists():
                    continue
                output = body(name)
                if tool == 'bandit':
                    data = json.loads(output)
                    output = '\n\n'.join(
                        f"{item['filename']}:{item['line_number']}: {item['test_id']} "
                        f"{item['test_name']} [{item['issue_severity']}]\n{item['issue_text']}"
                        for item in data['results']) or 'No issues found.'
                count = row['count']
                if tool == 'checkstyle':
                    lines = [line for line in output.splitlines() if re.search(r'\[(WARN|ERROR)\]', line)]
                    output = '\n'.join(lines[:5])
                    if len(lines) > 5:
                        output += f'\n\n[Excerpt: 5 of {len(lines)} diagnostics; full output in {name}.txt]'
                elif tool == 'pylint' and count > 6:
                    output = '\n'.join(output.splitlines()[:7])
                    output += f'\n\n[Excerpt: 6 of {count} diagnostics; full output in {name}.txt]'
                exit_code = log(name).splitlines()[1].split(':', 1)[1].strip()
                content += block(f'{tool} — messages: {count}; exit: {exit_code}', output)
            sections[f'{language}_{version}_static'] = content
    intro = (f'<p class="note">Captured run: {html.escape(manifest["started_utc"])} · '
             f'Python {platform.python_version()} · exact logs and raw profiles below.</p>')
    index = '<h1>PR4 — результаты повторного запуска</h1>' + intro
    if rows:
        index += '<table><tr><th>Language</th><th>Version</th><th>Analyzer</th><th>Messages</th></tr>'
        for row in rows:
            index += '<tr>' + ''.join(f'<td>{html.escape(str(row[k]))}</td>'
                         for k in ('language', 'version', 'tool', 'count')) + '</tr>'
        index += '</table>'
    for key, content in sections.items():
        if content:
            document = f'<!doctype html><meta charset="utf-8"><style>{style}</style>'
            document += f'<h1>{html.escape(key)}</h1>' + intro + content
            (RESULTS / f'{key}.html').write_text(document, encoding='utf-8')
            index += f'<p><a href="{key}.html">{html.escape(key)}</a></p>'
    index += '<h2>Полные протоколы и записи</h2>'
    for path in sorted(RESULTS.iterdir()):
        if path.suffix in ('.txt', '.jfr', '.prof', '.json'):
            index += f'<p><a href="{path.name}">{path.name}</a></p>'
    (RESULTS / 'index.html').write_text(
        f'<!doctype html><meta charset="utf-8"><style>{style}</style>{index}', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup', action='store_true')
    parser.add_argument('--group', choices=('all', 'static', 'dynamic'), default='all')
    parser.add_argument('--language', choices=('all', 'python', 'java'), default='all')
    parser.add_argument('--java-home', default=os.environ.get('JAVA_HOME'))
    args = parser.parse_args()
    if args.setup:
        setup()
        return
    RESULTS.mkdir(parents=True, exist_ok=True)
    manifest = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    python=sys.version, platform=platform.platform(), group=args.group,
                    language=args.language, tools={'pylint': '4.1.4', 'ruff': '0.17.6',
                    'bandit': '1.9.4', 'checkstyle': '10.21.4', 'pmd': '6.55.0',
                    'spotbugs': '4.9.3'})
    sources = [ROOT / 'run_checks.py', ROOT / 'requirements-tools.txt',
               *ROOT.glob('python/**/*.py'), *ROOT.glob('java/**/*.java')]
    manifest['source_sha256'] = {p.relative_to(ROOT).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}
    manifest['download_sha256'] = {name: hashlib.sha256((TOOLS / name).read_bytes()).hexdigest()
        for name in JAVA_TOOLS if (TOOLS / name).exists()}
    manifest['status'] = 'running'
    (RESULTS / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    rows = []
    if args.language in ('all', 'python'):
        execute('python_version', [python_tool(), '--version'])
        execute('python_packages', [python_tool(), '-m', 'pip', 'freeze'])
        python_checks(args.group, rows)
    if args.language in ('all', 'java'):
        java_checks(args.group, args.java_home, rows)
    manifest['static_counts'] = rows
    manifest['status'] = 'completed'
    (RESULTS / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    make_report(rows, manifest)
    print('All requested checks completed. Expected failures in faulty copies are preserved.')
    print(RESULTS / 'index.html')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        raise SystemExit(1)
