const assert=require("node:assert/strict");
const {pathToFileURL}=require("node:url");
const path=require("node:path");
const {chromium}=require(process.env.COAST_PLAYWRIGHT || "playwright-core");
const project=process.argv[2] || path.join(__dirname,"../tizen");
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.COAST_CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe", headless:true});
 const url=pathToFileURL(path.join(project,"index.html")).href;
 try {
  const plain=await browser.newPage();
  await plain.goto(url);
  await plain.getByRole("button",{name:"Library",exact:true}).click();
  assert.match(await plain.locator("#dock").textContent(),/unavailable/);
  assert.equal(await plain.locator("#dock .tile").count(),0);
  const page=await browser.newPage({viewport:{width:1920,height:1080}});
  const errors=[];
  page.on("pageerror",error=>errors.push(error.message));
  await page.addInitScript(()=>{
   window.fixtureApps=[{id:"coast",name:"Coast"},{id:"hide",name:"Hidden",show:false},
     {id:"a",name:"Cinema Library"},{id:"b",name:"Media Browser"},
     {id:"c",name:"Photo Library with a deliberately long application name"},
     {id:"d",name:"Audio Player"},{id:"e",name:"System Gallery"},{id:"f",name:"Watch Folder"}];
   window.launchLog=[];window.exitCount=0;
   window.tizen={application:{
     getCurrentApplication:()=>({appInfo:{id:"coast"},exit:()=>{window.exitCount++;}}),
     getAppsInfo:(ok,fail)=>window.failListing?fail():ok(window.fixtureApps),
     launch:(id,success,failure)=>{window.launchLog.push(id);if(id==="b")failure();else success();}
   }};
  });
  await page.goto(url);
  const button=(name)=>page.getByRole("button",{name,exact:true});
  const press=async(key)=>{if(key==="Enter")await page.waitForTimeout(145);await page.keyboard.press(key);};
  await press("ArrowRight");await press("Enter");
  assert.equal(await page.locator("#title").textContent(),"Library");
  assert.equal(await page.locator("#position").textContent(),"1 of 6");
  await press("ArrowRight");await press("Enter");
  await press("ArrowRight");await press("Enter");
  await page.waitForTimeout(200);await press("Escape");
  assert.equal(await page.locator(".focused").getAttribute("aria-label"),"Cinema Library");
  await button("Media Browser").click();await button("Pin to Home").click();
  await button("Move earlier").click();
  await button("Open app").click();
  assert.match(await page.locator("#status").textContent(),/Could not open Media Browser/);
  await page.waitForTimeout(200);await press("Escape");
  await button("Cinema Library").click();await button("Open app").click();
  assert.equal(await page.locator(".focused").getAttribute("aria-label"),"Cinema Library");
  assert.deepEqual(await page.evaluate(()=>window.launchLog),["b","a"]);
  await button("Settings").click();await button("Wallpaper on").click();
  assert.match(await page.locator("body").getAttribute("class"),/quiet/);
  await page.reload();
  assert.match(await page.locator("body").getAttribute("class"),/quiet/);
  assert.deepEqual(await page.locator("#dock .name").allTextContents(),["Media Browser","Cinema Library"]);
  await page.evaluate(()=>{window.fixtureApps=window.fixtureApps.filter(a=>a.id!=="b");document.dispatchEvent(new Event("visibilitychange"));});
  assert.deepEqual(await page.locator("#dock .name").allTextContents(),["Cinema Library"]);
  await button("Search").click();
  for (const letter of "CINEMA") await button(letter).click();
  await button("Results").click();
  assert.deepEqual(await page.locator("#dock .name").allTextContents(),["Cinema Library"]);
  await button("Settings").click();
  await page.evaluate(()=>{window.failListing=true;});
  await button("Refresh installed apps").click();
  assert.match(await page.locator("#status").textContent(),/Could not read/);
  await button("Reset preferences").click();
  await press("ArrowRight");await press("Enter");
  assert.doesNotMatch(await page.locator("body").getAttribute("class"),/quiet/);
  await page.evaluate(()=>{window.failListing=false;document.dispatchEvent(new Event("visibilitychange"));});
  await button("Library").click();
  await page.screenshot({path:process.env.COAST_SCREENSHOT || "coast-preview.png"});
  await page.waitForTimeout(200);await press("Escape");
  await page.waitForTimeout(200);await press("Escape");
  assert.equal(await page.evaluate(()=>window.exitCount),1);
  await page.evaluate(()=>localStorage.setItem("tv-os-coast.preferences.v1","not JSON"));
  await page.reload();
  assert.match(await page.locator("#dock").textContent(),/Open app library/);
  assert.deepEqual(errors,[]);
  console.log("PASS: desktop empty state, 1080p navigation, paging, launch failures, focus, favorites, reorder, reload, search, removed apps, refresh errors, reset, Back and corrupted storage.");
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
