from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json,time,threading,secrets,os,socket,urllib.parse,math,struct,zlib,sys,subprocess,re
import qrcode
os.chdir(Path(__file__).resolve().parent)
D={d['id']:d for d in json.load(open('game-data.json'))}; L=json.load(open('speech.json')); lock=threading.RLock(); admin=os.environ.get("ADMIN_TOKEN") or secrets.token_urlsafe(18); players={}; phase='intro'; cue='intro'; endAt=0; line=0; session=secrets.token_hex(6); video=''; join_override=''; outro='assets/angela-outro.mp4'; audio=dict(volume=40,muted=False,paused=False,restart=0)
PORT=int(os.environ.get('PORT') or os.environ.get('CC_PORT') or (sys.argv[1] if len(sys.argv)>1 else 8000))
PUBLIC_URL=(os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('PUBLIC_URL') or '').rstrip('/')
if os.environ.get('RENDER') and not os.environ.get('ADMIN_TOKEN'):raise RuntimeError('Set ADMIN_TOKEN in Render Environment Variables')
def lan_ip():
 if sys.platform=='darwin':
  try:
   ip=subprocess.check_output(['ipconfig','getifaddr','en0'],text=True,stderr=subprocess.DEVNULL,timeout=2).strip()
   if ip:return ip
  except (OSError,subprocess.SubprocessError):pass
 ip='127.0.0.1'
 try:
  with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
   sock.connect(('8.8.8.8',80));ip=sock.getsockname()[0]
 except OSError:pass
 return ip
LAN_IP=lan_ip()
def player_url():
 return join_override or (PUBLIC_URL+'/' if PUBLIC_URL else f'http://{LAN_IP}:{PORT}/')
def now():return int(time.time()*1000)
def finish():
 global phase,cue,endAt
 if phase=='running':phase='finished';cue='end';endAt=min(endAt,now())
def rows():return sorted(players.values(),key=lambda p:(-p['netProfit'],p['playerId']))
def state():
 if phase=='running' and now()>=endAt:finish()
 r=rows(); top={}
 for p in r:
  for h in p['history']:
   if h['id'] not in top or h['money']>top[h['id']]['money']:top[h['id']]={**h,'playerId':p['playerId']}
 return dict(version='9',playerUrl=player_url(),phase=phase,cue=cue,endAt=endAt,now=now(),line=line,session=session,video=video,outro=outro,audio=audio.copy(),rows=[{k:v for k,v in p.items() if k not in ('requests','ledger')} for p in r],trending=sorted(top.values(),key=lambda h:-h['money']))
def public(p):return {k:v for k,v in p.items() if k!='requests'}
def elapsed():
 t=max(0,min(420,420-math.ceil((endAt-now())/1000)));return f'{t//60}:{t%60:02}'
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,fmt,*args):
  if '/api/state' not in str(args):super().log_message(fmt,*args)
 def send_head(self):
  path=self.translate_path(self.path)
  if path.lower().endswith('.mp4') and os.path.isfile(path):
   size=os.path.getsize(path);rg=self.headers.get('Range');start=0;end=size-1;status=200
   if rg:
    m=re.fullmatch(r'bytes=(\d*)-(\d*)',rg.strip())
    if not m:self.send_error(416);return None
    a,b=m.groups()
    if a:start=int(a);end=min(end,int(b)) if b else end
    elif b:start=max(0,size-int(b))
    if start>end or start>=size:self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return None
    status=206
   f=open(path,'rb');f.seek(start);self._remaining=end-start+1
   self.send_response(status);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(self._remaining))
   if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
   self.end_headers();return f
  self._remaining=None;return super().send_head()
 def copyfile(self,source,outputfile):
  if getattr(self,'_remaining',None) is None:return super().copyfile(source,outputfile)
  left=self._remaining
  while left:
   block=source.read(min(left,65536))
   if not block:break
   outputfile.write(block);left-=len(block)

 def end_headers(self):
  if self.path.startswith('/api/') or urllib.parse.urlsplit(self.path).path in ('/','/index.html','/director.html','/screen.html','/speech.json'):
   self.send_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
   self.send_header('Pragma','no-cache')
  super().end_headers()
 def reply(self,d,status=200):
  b=json.dumps(d,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urllib.parse.urlsplit(self.path)
  if u.path=='/healthz':
   self.reply({'ok':True})
  elif u.path=='/api/info':
   self.reply({'playerUrl':player_url(),'version':'9'})
  elif u.path=='/api/state':
   with lock:
    s=state();k=urllib.parse.parse_qs(u.query).get('key',[''])[0];payload=dict(state=s,player=public(players[k]) if k in players else None)
   self.reply(payload)
  elif u.path=='/api/qr':
   url=urllib.parse.parse_qs(u.query).get('url',[player_url()])[0] or player_url()
   try:
    qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4);qr.add_data(url);qr.make(fit=True);matrix=qr.get_matrix();scale=10;size=len(matrix)*scale
    raw=b''.join((b'\x00'+bytes(0 if cell else 255 for cell in row for _ in range(scale)))*scale for row in matrix)
    def chunk(t,d):return struct.pack('!I',len(d))+t+d+struct.pack('!I',zlib.crc32(t+d)&0xffffffff)
    v=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',size,size,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
    self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(v)));self.end_headers();self.wfile.write(v)
   except Exception as e:self.reply({'error':str(e)},400)
  else:super().do_GET()
 def do_POST(self):
  global phase,cue,endAt,line,session,video,join_override,outro,audio
  try:
   a=self.path.split('?')[0].split('/')[-1]; b=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))));
   with lock:
    state();k=b.get('key','');p=players.get(k)
    if a=='join':
     if not p:
      if phase=='finished':raise ValueError('Session finished')
      k=secrets.token_urlsafe(18);p=dict(playerId=f'{len(players)+1:03}',tokens=100,gross=0,spent=0,netProfit=0,used=0,purchases=0,history=[],ledger=[],requests=set());players[k]=p
     self.reply(dict(key=k,player=public(p),state=state()));return
    if a=='control':
     if b.get('admin')!=admin: self.reply({'error':'Invalid director key'},403);return
     cmd=b.get('cmd');
     if cmd=='reset':players.clear();phase='intro';cue='intro';endAt=0;line=0;session=secrets.token_hex(6)
     elif cmd=='outro':outro=str(b.get('video',''))
     elif cmd=='audio':
      if 'volume' in b:audio['volume']=max(0,min(100,int(b['volume'])))
      if 'muted' in b:audio['muted']=bool(b['muted'])
      if 'paused' in b:audio['paused']=bool(b['paused'])
      if b.get('restart'):audio['restart']+=1
     elif cmd=='video':video=str(b.get('video',''))
     elif cmd=='join_url':
      url=str(b.get('url','')).strip();u=urllib.parse.urlsplit(url)
      if u.scheme not in ('http','https') or not u.hostname or u.hostname in ('localhost','127.0.0.1'):raise ValueError('Use the LAN player URL, not localhost')
      join_override=url
     elif cmd=='start' and phase in ('intro','lobby'):phase='running';cue='ranking';endAt=now()+420000;audio['paused']=False;audio['restart']+=1
     elif cmd=='start' and phase=='running':cue='ranking'
     elif cmd=='start':raise ValueError('Session finished. Reset session before starting again.')
     elif cmd=='end':
      if phase!='running':raise ValueError('No active game to end')
      finish()
     elif cmd=='cue':
      c=b.get('cue');
      if c in ('intro','qr','lobby'):
       cue=c
       if phase in ('intro','lobby'):phase='lobby' if c!='intro' else 'intro'
      elif c in ('winner','speech','outro','archive','end') and phase=='finished':
       if c=='speech' and cue!='speech':line=0
       cue=c
      elif c=='black':cue=c
      elif c=='ranking' and phase=='running':cue=c
      else:raise ValueError('Cue unavailable in current phase: '+phase+' / '+str(c))
     elif cmd=='line' and phase=='finished' and cue=='speech':line=max(0,min(len(L)-1,int(b.get('line',0))))
     else:raise ValueError('Command unavailable: '+str(cmd))
     self.reply({'state':state()});return
    if not p:raise ValueError('Join first')
    if phase!='running':raise ValueError('Game is not running')
    req=b.get('requestId');
    if not req:raise ValueError('Missing request ID')
    if req in p['requests']:self.reply(dict(player=public(p),state=state()));return
    if a=='produce':
     id=b.get('id');m=b.get('model');d=D.get(id);seen={h['id'] for h in p['history']}
     if not d or m not in (10,20,30) or p['tokens']<m or (len(seen)<len(D) and id in seen):raise ValueError('Invalid recipe or insufficient tokens')
     base=math.floor(d['metrics']['views']/1000*{'TikTok':.03,'Instagram':.01,'Xiaohongshu':0}.get(d['platform'],0)+.5);money=math.floor(base*{10:1,20:1.05,30:1.08}[m]+.5);prev=rows().index(p)+1;p['tokens']-=m;p['used']+=m;p['gross']+=money;p['history'].insert(0,dict(id=id,model=m,money=money,previousRank=prev));p['ledger'].insert(0,dict(time=elapsed(),label=d['title'],amount=money))
    elif a=='topup':
     fee=math.floor(p['netProfit']*30+.5)/100;p['spent']=round(p['spent']+fee,2);p['tokens']+=100;p['purchases']+=1;p['ledger'].insert(0,dict(time=elapsed(),label='Buy 100 tokens',amount=-fee))
    else:raise ValueError('Unknown action')
    p['netProfit']=round(p['gross']-p['spent'],2);p['requests'].add(req);self.reply(dict(player=public(p),state=state()))
  except (ValueError,TypeError,KeyError) as e:self.reply({'error':str(e)},400)
if __name__=='__main__':
 try:httpd=ThreadingHTTPServer(('0.0.0.0',PORT),Handler)
 except OSError as e:
  print(f'Cannot bind port {PORT}: {e}. Stop the previous server (Ctrl+C) or run python3 server.py 8001.',flush=True);sys.exit(1)
 if PUBLIC_URL:print(f'CUTENESS CASINO V9 — READY\nPlayer URL: {player_url()}\nDirector: {PUBLIC_URL}/director.html?admin=<ADMIN_TOKEN>\nProjection: {PUBLIC_URL}/screen.html?v=9',flush=True)
 else:print(f'CUTENESS CASINO V9 — READY\nPlayer URL: {player_url()}\nDirector: http://localhost:{PORT}/director.html?admin={admin}&v=9\nProjection: http://localhost:{PORT}/screen.html?v=9',flush=True)
 if LAN_IP=='127.0.0.1':print('WARNING: no LAN address found. Connect Wi-Fi and restart, or set Player URL in Director.',flush=True)
 httpd.serve_forever()
