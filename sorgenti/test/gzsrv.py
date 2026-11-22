import http.server,gzip,os,sys,re,functools
ROOT=sys.argv[1];PORT=int(sys.argv[2])
cache={}
class H(http.server.SimpleHTTPRequestHandler):
  def __init__(s,*a,**k):super().__init__(*a,directory=ROOT,**k)
  def log_message(s,*a):pass
  def do_GET(s):
    p=s.path.split('?')[0].split('#')[0]
    if p=='/':p='/index.html'
    fp=os.path.join(ROOT,p.lstrip('/'))
    if not os.path.isfile(fp):return super().do_GET()
    ext=fp.rsplit('.',1)[-1]
    ct={'html':'text/html; charset=utf-8','json':'application/json','js':'application/javascript','css':'text/css','webp':'image/webp','jpg':'image/jpeg','png':'image/png','svg':'image/svg+xml'}.get(ext,'application/octet-stream')
    m=os.path.getmtime(fp)
    data=open(fp,'rb').read()
    gz='gzip' in s.headers.get('Accept-Encoding','') and ext in('html','json','js','css','svg')
    if gz:
      k=(fp,m)
      if k not in cache:cache[k]=gzip.compress(data,6)
      data=cache[k]
    s.send_response(200);s.send_header('Content-Type',ct);s.send_header('Content-Length',str(len(data)))
    if gz:s.send_header('Content-Encoding','gzip')
    hashed=re.search(r'\.[0-9a-f]{10}\.',p)
    s.send_header('Cache-Control','max-age=31536000, immutable' if hashed else 'max-age=600')
    s.end_headers();s.wfile.write(data)
http.server.ThreadingHTTPServer(('',PORT),H).serve_forever()
