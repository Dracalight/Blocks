const cacheName='nexus-mittens-v1-02'
const files=['./','./index.html','./style.css','./game.js','./chess.js','./engine.js','./analyzer.js','./cat.svg','./manifest.json','./icon192.png','./icon512.png',...['js','wasm'].map(s=>'./engine/stockfish-19-lite-single.'+s)]
self.addEventListener('install',e=>e.waitUntil(caches.open(cacheName).then(c=>c.addAll(files))))
self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const k of await caches.keys())if(k.startsWith('nexus-mittens-')&&k!==cacheName)await caches.delete(k);await self.clients.claim()})()))
self.addEventListener('fetch',e=>{if(e.request.method==='GET'&&e.request.url.startsWith(self.registration.scope))e.respondWith(caches.open(cacheName).then(async c=>{const cached=await c.match(e.request);if(cached)return cached;const res=await fetch(e.request);if(res.ok&&/engine\/stockfish-19(-single)?\.(wasm|js)$/.test(e.request.url))await c.put(e.request,res.clone()).catch(()=>{});return res}))})
