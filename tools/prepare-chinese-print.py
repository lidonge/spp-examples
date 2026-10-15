#!/usr/bin/env python3
"""Prepare the reserved-rights Chinese print manuscript; remove it before site deployment."""
from pathlib import Path
import json,re
import markdown
root=Path(__file__).resolve().parent.parent
book=root/'book'
entries=json.loads((book/'en/translation-map.json').read_text())['sections']
parts=[]
for p in [book/'README.md']+[book/item['source'] for item in entries]:
 text=p.read_text()
 # Printed source references point to the published repository, rather than a local preview server.
 def link(match):
  name,url=match[1],match[2]
  if '://' in url or url.startswith('#') or url.startswith('mailto:'):return match.group()
  file,sep,fragment=url.partition('#')
  target=(p.parent/file).resolve()
  if target.is_relative_to(root):
   url='https://github.com/lidonge/spp-examples/blob/main/'+target.relative_to(root).as_posix()+sep+fragment
   return f'[{name}]({url})'
  return name
 text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
 parts.append(text)
body=markdown.markdown('\n\n---\n\n'.join(parts),extensions=['tables','fenced_code','toc'])
out=root/'website/dist/pdf-zh/index.html';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>面向角色的服务架构</title><link rel="stylesheet" href="/book.css"><style>body{font-family:"Noto Serif CJK SC",serif}.book-article{max-width:none}h1,h2,h3{break-after:avoid}</style></head><body><article class="book-article">'+body+'</article></body></html>')
print('Prepared temporary Chinese print manuscript')
