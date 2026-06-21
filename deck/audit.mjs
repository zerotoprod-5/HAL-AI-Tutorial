import puppeteer from 'puppeteer-core';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const REPO='/Users/work/HAL-AI-Tutorial';
const decks=['01-text-i','02-text-ii','03-speech-i','04-speech-ii'];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

const browser=await puppeteer.launch({executablePath:CHROME,headless:'new',
  args:['--no-sandbox','--window-size=1600,900','--force-device-scale-factor=1']});

const report={};
for(const d of decks){
  const url=`file://${REPO}/deck/${d}.html`;
  const page=await browser.newPage();
  await page.setViewport({width:1600,height:900});
  const errors=[];
  page.on('console',m=>{const t=m.text(); if(m.type()==='error'&&!/histogram|GPU stall|SharedImage/i.test(t))errors.push(t);});
  page.on('pageerror',e=>errors.push('PAGEERROR: '+e.message));
  await page.goto(url,{waitUntil:'load'}); await sleep(300);
  const count=await page.$$eval('.slide',e=>e.length);
  const bugs=[];

  // index of the currently-shown slide (the engine reveals the hash slide)
  const current=()=>page.evaluate(()=>{
    const ss=[...document.querySelectorAll('.slide')];
    let best=-1,area=0;
    ss.forEach((s,i)=>{const r=s.getBoundingClientRect(); const cs=getComputedStyle(s);
      const vis=cs.display!=='none'&&parseFloat(cs.opacity||'1')>0.5;
      const a=vis?Math.max(0,Math.min(r.right,innerWidth)-Math.max(r.left,0))*Math.max(0,Math.min(r.bottom,innerHeight)-Math.max(r.top,0)):0;
      if(a>area){area=a;best=i;}});
    return best;
  });

  for(let n=1;n<=count;n++){
    await page.goto(url+'#'+n,{waitUntil:'load'}); await sleep(220);
    const i=n-1;
    // blank-slide check + widget inventory (scoped to the shown slide)
    const meta=await page.evaluate((idx)=>{
      const s=document.querySelectorAll('.slide')[idx]; if(!s)return{blank:true,widgets:[]};
      const txt=(s.innerText||'').replace(/\s+/g,' ').trim();
      const widgets=[...s.querySelectorAll('[data-widget]')].map(w=>w.getAttribute('data-widget'));
      return {blank:txt.length<4&&widgets.length===0, txt:txt.slice(0,46), widgets};
    },i);
    if(meta.blank) bugs.push(`s${n}: BLANK slide (no text & no widget)`);

    // interaction tests, scoped to the shown slide
    const slideH=(await page.$$('.slide'))[i];
    if(!slideH) continue;

    // helper: click a control, assert (a) no slide-nav happened, (b) widget DOM mutated
    async function testControl(sel,label,{type,assertSel,mutate=true}={}){
      const h=await slideH.$(sel); if(!h) return;
      const box=await h.boundingBox(); if(!box){bugs.push(`s${n}: ${label} present but not visible/clickable`);return;}
      const before=await page.evaluate(el=>el.closest('[data-widget]').outerHTML.length,h);
      const slideBefore=await current();
      try{
        if(type==='type'){ await h.click(); await h.type('hairline crack near turbine',{delay:8}); }
        else { await h.click(); }
      }catch(e){ bugs.push(`s${n}: ${label} click threw: ${e.message}`); return; }
      await sleep(240);
      const slideAfter=await current();
      if(slideAfter!==slideBefore) bugs.push(`s${n}: clicking ${label} NAVIGATED the slide (${slideBefore}->${slideAfter})`);
      const after=await page.evaluate(el=>el.closest('[data-widget]')?.outerHTML.length||0,h);
      let revealed=true;
      if(assertSel){ revealed=await page.evaluate((el,s)=>!!el.closest('[data-widget]').querySelector(s),h,assertSel); }
      if(mutate && after===before && !assertSel) bugs.push(`s${n}: clicking ${label} had NO effect (widget DOM unchanged)`);
      if(assertSel && !revealed) bugs.push(`s${n}: ${label} did not reveal expected (${assertSel}) after click`);
    }

    for(const w of meta.widgets){
      if(w==='spectroPlay'){
        // only the reveal ones have a .spectro; cold-open (no img) just plays
        const hasImg=await page.evaluate(el=>!!el.querySelector('.spectro'), slideH);
        await testControl('.sp .play','spectroPlay ▶', hasImg?{assertSel:'.spectro.on'}:{mutate:false});
      } else if(w==='predictReveal'){
        await testControl('.pr .opt','predictReveal card');
      } else if(w==='thresholdConfusion'){
        const r=await slideH.$('.tc input[type=range]');
        if(r){ const sb=await current(); await page.evaluate(el=>{el.value=el.max||1;el.dispatchEvent(new Event('input',{bubbles:true}));},r); await sleep(150);
               const after=await page.evaluate(el=>el.closest('[data-widget]').innerText,r); /* just ensure no error */ }
        else await testControl('.tc canvas','thresholdConfusion');
      } else if(w==='drawBoundary'){
        const c=await slideH.$('.db canvas');
        if(c){ const b=await c.boundingBox(); try{await page.mouse.click(b.x+b.width*0.3,b.y+b.height*0.4); await page.mouse.click(b.x+b.width*0.7,b.y+b.height*0.6);}catch(e){} }
        await testControl('.db .showm, .db .btn','drawBoundary show-model');
      } else if(w==='liveTokenizer'){
        await testControl('.lt input, .lt textarea','liveTokenizer input',{type:'type',assertSel:'.feat'});
      } else if(w==='cmatrix'){
        /* fragment-driven (presenter advances) — no click control to test here */
      }
    }
  }
  report[d]={count,jsErrors:[...new Set(errors)].slice(0,8),bugs};
  await page.close();
}
await browser.close();
console.log(JSON.stringify(report,null,2));
