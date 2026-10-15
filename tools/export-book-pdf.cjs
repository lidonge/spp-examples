// Requires Playwright on NODE_PATH and a running website preview.
const {chromium}=require('playwright');
const path=require('node:path');
const fs=require('node:fs');
const root=path.resolve(__dirname,'..');
const base=process.env.SPP_BOOK_PREVIEW || 'http://127.0.0.1:18977';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.SPP_CHROME_BIN || '/usr/bin/google-chrome',args:['--no-sandbox']});
 try {
  const page=await browser.newPage();
  for(const [route,file] of [['/book/complete-manuscript/','Role-Oriented-Service-Architecture-en.pdf'],['/pdf-zh/','面向角色的服务架构-中文版.pdf']]){
   await page.goto(base+route,{waitUntil:'networkidle'});
   await page.evaluate(()=>{
    for(const a of document.querySelectorAll('a[href]')){
     const original=a.getAttribute('href');
     if(original.startsWith('#'))continue;
     const u=new URL(a.href);
     if(u.origin===location.origin)a.href='https://us.servpp.top'+u.pathname+u.search+u.hash;
    }
   });
   await page.emulateMedia({media:'print'});
   const destination=path.join(root,'book/exports',file);
   fs.mkdirSync(path.dirname(destination),{recursive:true});
   await page.pdf({path:destination,format:'A4',printBackground:true,displayHeaderFooter:true,
    margin:{top:'18mm',right:'16mm',bottom:'18mm',left:'16mm'},
    headerTemplate:'<div style="font-family:Arial,sans-serif;font-size:8px;color:#627568;width:100%;text-align:center">S++ · Role-Oriented Service Architecture · © 2026 · All rights reserved</div>',
    footerTemplate:'<div style="font-family:Arial,sans-serif;font-size:8px;color:#627568;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
   console.log('Exported',file);
  }
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
