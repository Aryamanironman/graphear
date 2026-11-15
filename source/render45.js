const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const FPS=30, DUR=42, OUT=path.join(__dirname,'out','frames45');
(async()=>{
  fs.mkdirSync(OUT,{recursive:true});
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  await p.goto('file:///C:/Users/asus/graphear/video45.html?render=1',{waitUntil:'load'});
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(250);
  if(process.argv[2]==='poster'){
    for(const t of [2.2,7.4,12,16.6,22.5,28.8,34.5,39.2]){
      await p.evaluate(tt=>window.seek(tt),t); await p.waitForTimeout(60);
      await p.screenshot({path:path.join(__dirname,'out',`poster45_${String(t).replace('.','_')}.png`)});
    }
    await b.close(); console.log('posters45 done'); return;
  }
  for(let i=0;i<FPS*DUR;i++){
    await p.evaluate(tt=>window.seek(tt),i/FPS);
    await p.screenshot({path:path.join(OUT,`f_${String(i).padStart(5,'0')}.jpg`),type:'jpeg',quality:92});
    if(i%200===0) console.log('frame',i);
  }
  await b.close(); console.log('rendered 1260');
})();
