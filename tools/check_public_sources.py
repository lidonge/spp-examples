#!/usr/bin/env python3
"""Check publication boundaries and local Markdown file targets without the private SDK."""
from pathlib import Path
import re
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parent.parent
errors=[]
ignored={'.git','target','__pycache__','.venv'}
files=[p for p in ROOT.rglob('*') if p.is_file() and not ignored.intersection(p.relative_to(ROOT).parts) and not p.is_relative_to(ROOT/'website/dist')]
for p in files:
 rel=p.relative_to(ROOT)
 if p.suffix.lower() in {'.cbl','.cob','.cpy','.pem','.key','.jks','.p12','.mv.db','.sqlite','.rdb','.jar','.class'}:
  errors.append(f'Excluded file type: {rel}')
 if p.name in {'.env','.git-credentials'}:
  errors.append(f'Local credential file: {rel}')
 if p.suffix in {'.md','.py','.sh','.json','.yml','.yaml','.properties','.xml','.spp','.app','.phy','.enum','.js','.html','.css'}:
  text=p.read_text()
  if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',text):
   errors.append(f'Private key material: {rel}')
  if re.search(r'gh[pousr]_[A-Za-z0-9]{30,}',text):
   errors.append(f'GitHub credential material: {rel}')
 if p.suffix=='.md':
  for href in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   parsed=urlsplit(href)
   if parsed.scheme or parsed.netloc or not parsed.path:continue
   path=unquote(parsed.path.split(' "',1)[0])
   if not (p.parent/path).resolve().exists():
    errors.append(f'{rel}: missing local link {href}')
for private in ['generator','lang','appframe','appframe-seata']:
 if (ROOT/private).exists():errors.append(f'Private toolchain directory included: {private}')
if 'All rights reserved' not in (ROOT/'book/COPYRIGHT.md').read_text():errors.append('Missing book reserved-rights notice')
if 'does not apply to `book/`' not in (ROOT/'LICENSE').read_text():errors.append('Missing code/book license boundary')
if errors:raise SystemExit('\n'.join(errors))
print(f'Checked {len(files)} public source files, Markdown targets and book/code license boundaries.')
