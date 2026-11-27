"""Serve the game and an optional OpenAI-compatible text backend on loopback."""
import json, os, time, threading
from collections import deque
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from pathlib import Path

calls = deque()
lock = threading.Lock()
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(Path(__file__).parent/'app'),**kwargs)
    def do_POST(self):
        if self.path != '/api/projection' or self.headers.get('Origin') != 'http://127.0.0.1:8765' or self.headers.get('Host') != '127.0.0.1:8765':
            return self.send_error(403)
        try:
            size = int(self.headers.get('Content-Length',0))
            if not 0 < size <= 8192: return self.send_error(413)
            data = json.loads(self.rfile.read(size))
            with lock:
                now=time.monotonic()
                while calls and calls[0] < now-3600: calls.popleft()
                if len(calls)>=30: return self.send_error(429)
                calls.append(now)
            payload={'model':os.getenv('NEXUS_MODEL','qwen2.5:0.5b'),'max_tokens':80,'messages':[{'role':'system','content':'Escribe una frase breve en español para todas las edades sobre esta jugada real. Usa una metáfora. Evita insultos, datos personales y consejos sobre relaciones.'},{'role':'user','content':json.dumps(data,ensure_ascii=False)}]}
            headers={'Content-Type':'application/json'}
            if os.getenv('NEXUS_API_KEY'): headers['Authorization']='Bearer '+os.environ['NEXUS_API_KEY']
            req=Request(os.getenv('NEXUS_ENDPOINT','http://127.0.0.1:11434/v1/chat/completions'),data=json.dumps(payload).encode(),headers=headers)
            with urlopen(req,timeout=8) as res: phrase=json.load(res)['choices'][0]['message']['content'].strip()[:280]
            body=json.dumps({'phrase':phrase}).encode()
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.end_headers()
            self.wfile.write(body)
        except Exception: self.send_error(503)
if __name__=='__main__': ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
