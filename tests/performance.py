from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=b.new_page()
    page.goto('http://localhost:8765')
    print(page.evaluate('''async()=>{
      const {search}=await import('./engine.js'),{project}=await import('./analyzer.js')
      let frames=0,active=true;function frame(){if(active){frames++;requestAnimationFrame(frame)}}requestAnimationFrame(frame)
      const start=performance.now();await search('startpos',{ms:700,depth:18,hash:16,full:false});const engineMs=performance.now()-start;active=false
      const t=performance.now();for(let i=0;i<1000;i++)project({move:'e4',category:'BEST',loss:0},'Filósofo',i)
      const dialogueMs=(performance.now()-t)/1000
      const click=performance.now();document.querySelector('[aria-label=e2]').click();await new Promise(requestAnimationFrame)
      return {engineMs,framesPerSecond:frames*1000/engineMs,dialogueMs,clickToNextFrameMs:performance.now()-click,mainHeapBytes:performance.memory?.usedJSHeapSize}
    }'''))
    b.close()
