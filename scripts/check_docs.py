"""检查正式2026题库的本地结构；不将HTTP连通性等同于事实核验。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter
from urllib.parse import unquote
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'sources/index.json').read_text(encoding='utf-8'))
errors = []
files = [p for p in ROOT.rglob('*.md')
         if not any(part.startswith('.') for part in p.relative_to(ROOT).parts)]
source_ids = [s['id'] for s in data['sources']]
question_ids = [q['id'] for q in data['questions']]


def check(condition, message):
    if not condition:
        errors.append(message)


def slugs(text):
    result = set(re.findall(r'<a id="([^"]+)"', text))
    for heading in re.findall(r'^#{1,6} (.+)$', text, re.M):
        heading = heading.lower().replace(' ', '-')
        result.add(''.join(c for c in heading
                           if c in '-_' or unicodedata.category(c)[0] in 'LN'))
    return result


check(len(source_ids) == len(set(source_ids)), 'duplicate source IDs')
check(len(question_ids) == len(set(question_ids)), 'duplicate question IDs')
urls = [s['url'].split('?')[0].rstrip('/') for s in data['sources']]
check(len(urls) == len(set(urls)), 'duplicate source URLs')
cutoff = datetime.fromisoformat(data['as_of']).replace(
    tzinfo=timezone(timedelta(hours=8))) + timedelta(days=1)
for source in data['sources']:
    try:
        stamp = datetime.fromisoformat(source['published'].replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone(timedelta(hours=8)))
        check(stamp.year == 2026 and stamp < cutoff,
              f"wrong publication year/date: {source['id']}")
    except ValueError:
        errors.append(f"bad publication timestamp: {source['id']}")
    for field in ('author', 'title', 'url', 'year_basis', 'platform'):
        check(bool(source.get(field)), f"missing {field}: {source['id']}")
    check('body' not in source and 'original' not in source,
          f"raw source content published: {source['id']}")

seen_sources = set()
docs = {}
for q in data['questions']:
    path = ROOT / q['file']
    if path not in docs:
        docs[path] = path.read_text(encoding='utf-8')
    text = docs[path]
    anchor = f'<a id="{q["id"].lower()}"></a>'
    check(text.count(anchor) == 1, f"question anchor: {q['id']}")
    if anchor not in text:
        continue
    body = text.split(anchor, 1)[1].split('<a id=', 1)[0]
    check(bool(q['sources']) and set(q['sources']) <= set(source_ids),
          f"invalid sources: {q['id']}")
    seen_sources.update(q['sources'])
    for sid in q['sources']:
        check(f'records.md#{sid.lower()}' in body, f"missing source link: {q['id']} {sid}")
    for label in ('参考答案', '怎么理解', '面试怎么讲', '追问与易错'):
        pattern = re.escape(f'**{label}**') + r'\s*\n\s*\n([^\n]+)'
        match = re.search(pattern, body)
        check(bool(match and len(match.group(1).strip()) >= 10),
              f"empty answer layer: {q['id']} {label}")
    detail = re.search(r'\*\*详细展开\*\*\s*(.*?)\*\*追问示范（练习口述）\*\*', body, re.S)
    check(bool(detail and len(detail.group(1).strip()) >= 180),
          f"detailed explanation missing/short: {q['id']}")
    check(body.count(f'<!-- detail:start {q["id"]} -->') == 1 and
          body.count(f'<!-- detail:end {q["id"]} -->') == 1,
          f"detail block missing/duplicate: {q['id']}")
    check('**技术依据 / 延伸核对：**' in body, f"missing technical reference: {q['id']}")
check(seen_sources == set(source_ids), 'unmapped source')

for path in files:
    text = path.read_text(encoding='utf-8')
    check('\ufffd' not in text, f'encoding replacement character: {path.name}')
    for dest in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        if re.match(r'^[a-zA-Z]+:', dest):
            continue
        rel, _, anchor = unquote(dest).partition('#')
        target = (path.parent / rel).resolve() if rel else path
        if not target.is_file():
            errors.append(f'local link missing: {path.relative_to(ROOT)} -> {dest}')
            continue
        if anchor and target.suffix == '.md':
            check(anchor in slugs(target.read_text(encoding='utf-8')),
                  f'anchor missing: {path.relative_to(ROOT)} -> {dest}')

for path, text in docs.items():
    rows = [q for q in data['questions'] if q['file'] == path.relative_to(ROOT).as_posix()]
    check(text.count('- [ ]') == len(rows), f'checklist count: {path.name}')
    check(len(re.findall(r'^## [A-Z]+-\d{3} ·', text, re.M)) == len(rows),
          f'question heading count: {path.name}')
readme = (ROOT / 'README.md').read_text(encoding='utf-8')
check(f"{len(source_ids)} 篇公开原帖，{len(question_ids)} 道分类题目" in readme,
      'README totals inconsistent')

report = dict(markdown_files=len(files), sources=len(source_ids), questions=len(question_ids),
              categories=len(docs), answer_layers=len(question_ids)*4,
              detailed_answers=len(question_ids),
              platforms=Counter(s['platform'] for s in data['sources']), errors=errors)
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
