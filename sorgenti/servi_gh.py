"""Server di prova che imita GitHub Pages: gzip, Cache-Control max-age=600 su tutto, ETag con risposta 304.
Uso: python3 servi_gh.py <cartella> <porta>"""
import http.server, sys, os, gzip, hashlib, functools, email.utils

CACHE = {}


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        p = self.translate_path(self.path.split("?")[0])
        if os.path.isdir(p): p = os.path.join(p, "index.html")
        if not os.path.isfile(p): return self.send_error(404)
        st = os.stat(p)
        k = (p, st.st_mtime, st.st_size)
        if k not in CACHE:
            raw = open(p, "rb").read()
            CACHE[k] = (raw, gzip.compress(raw, 6), '"%s"' % hashlib.md5(raw).hexdigest()[:16])
        raw, gz, etag = CACHE[k]
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304); self.send_header("ETag", etag); self.send_header("Cache-Control", "max-age=600"); self.end_headers(); return
        ctype = self.guess_type(p)
        usa_gz = "gzip" in (self.headers.get("Accept-Encoding") or "") and not p.endswith((".webp", ".jpg", ".png"))
        body = gz if usa_gz else raw
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        if usa_gz: self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=600")
        self.send_header("ETag", etag)
        self.send_header("Last-Modified", email.utils.formatdate(st.st_mtime, usegmt=True))
        self.send_header("Vary", "Accept-Encoding")
        self.end_headers()
        self.wfile.write(body)


http.server.ThreadingHTTPServer(("", int(sys.argv[2])), functools.partial(H, directory=sys.argv[1])).serve_forever()
