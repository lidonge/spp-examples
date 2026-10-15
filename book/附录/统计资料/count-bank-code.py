from pathlib import Path
import re,json,collections,csv,argparse
parser=argparse.ArgumentParser(description='Count bank case COBOL sources and S++ code.')
parser.add_argument('cobol_root',type=Path,help='Directory containing original .cbl and .copy directories')
parser.add_argument('--output-dir',type=Path,default=Path('/tmp/bank-demo-code-count'))
args=parser.parse_args()
ROOT=args.cobol_root.resolve()
REPO=Path(__file__).resolve().parents[3]
OUT=args.output_dir
OUT.mkdir(parents=True,exist_ok=True)
if not ROOT.is_dir():parser.error('COBOL source directory does not exist')
text='\n'.join(p.read_text() for p in (REPO/'demos/bank-deposit/docs').glob('*.md'))+'\n'+(REPO/'book/references/cbod-gsa01102-deposit-analysis.md').read_text()
all_tokens=set(re.findall(r'\b[A-Z][A-Z0-9]{4,14}\b',text))
anchored=set(re.findall(r'\b([A-Z][A-Z0-9]{4,14})(?::\d|\.cbl\b)',text))
programs={p.stem:p for p in ROOT.rglob('*.cbl') if p.is_file()}
copybooks=collections.defaultdict(list)
for p in ROOT.rglob('*'):
 if p.is_file() and '.copy' in p.parent.name:
  copybooks[p.stem.upper()].append(p)
def active_lines(p):
 result=[]
 for l in p.read_bytes().splitlines():
  if len(l)>6 and l[6:7] in (b'*',b'/'):continue
  area=l[7:72] if len(l)>7 else b''
  area=area.split(b'*>',1)[0]
  if area.strip():result.append(area.decode('gb18030',errors='replace'))
 return result
def refs(p):
 # Recognize COPY directives at the start of active fixed-format source lines.
 return set(re.findall(r'^\s*COPY\s+[\"\']?([A-Z0-9_-]+)', '\n'.join(active_lines(p)),re.I|re.M))
def closure(ps):
 found=set();pending=list(ps);unresolved=set()
 while pending:
  p=pending.pop()
  for n in refs(p):
   candidates=copybooks.get(n.upper(),[])
   if len(candidates)!=1:
    unresolved.add((str(p.relative_to(ROOT)),n,len(candidates)));continue
   cp=candidates[0]
   if cp not in found:found.add(cp);pending.append(cp)
 return found,sorted(unresolved)
def stats(ps):
 return {'files':len(ps),'physical_lines':sum(len(p.read_bytes().splitlines()) for p in ps),'code_lines':sum(len(active_lines(p)) for p in ps)}
sets={label:{p for n,p in programs.items() if n in tokens} for label,tokens in [('anchored',anchored),('mentioned',all_tokens)]}
out={}
for label,ps in sets.items():
 direct=set();missing=[]
 for p in ps:
  for n in refs(p):
   cs=copybooks.get(n.upper(),[])
   if len(cs)==1:direct.add(cs[0])
   else:missing.append((str(p.relative_to(ROOT)),n,len(cs)))
 recursive,unresolved=closure(ps)
 out[label]={'programs':stats(ps),'direct_copybooks':stats(direct),'recursive_copybooks':stats(recursive),'unresolved':unresolved,'program_list':[str(p.relative_to(ROOT)) for p in sorted(ps)]}
 with (OUT/(label+'-files.csv')).open('w') as f:
  w=csv.writer(f,lineterminator="\n");w.writerow(['type','path','physical_lines','code_lines'])
  for typ,paths in [('program',ps),('copybook',recursive)]:
   for p in sorted(paths):w.writerow([typ,str(p.relative_to(ROOT)),len(p.read_bytes().splitlines()),len(active_lines(p))])
pattern=re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/')
def spp_code(t):
 def strip(m):
  s=m.group();return '\n'*s.count('\n') if s.startswith(('//','/*')) else s
 return sum(bool(l.strip()) for l in pattern.sub(strip,t).splitlines())
spp={}
for suffix in ['.spp','.enum','.app','.phy']:
 ps=list((REPO/'demos/bank-deposit/src/main/spp').rglob('*'+suffix))
 spp[suffix]={'files':len(ps),'physical_lines':sum(len(p.read_text().splitlines()) for p in ps),'code_lines':sum(spp_code(p.read_text()) for p in ps)}
out['spp']=spp
(OUT/'result.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
print(json.dumps(out,indent=2,ensure_ascii=False))
