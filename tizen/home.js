(function () {
  "use strict";
  var platform = window.coastPlatform;
  var store = window.coastPreferences;
  var prefs = store.read();
  var sections = ["Home","Library","Search","Settings"];
  var apps = [], section = 0, zone = "nav", selected = 0, nav = 0, key = 0;
  var query = "", actionApp = null, origin = null, confirm = false, pending = false;
  var listState = "loading", generation = 0, lastBack = 0, lastOk = 0;
  var keys = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".split("").concat(["Space","Delete","Clear","Results"]);
  var nodes = {};
  ["nav","clock","title","description","query","keyboard","shelf-title","position","dock","hint","status"].forEach(function (id) {
    nodes[id] = document.getElementById(id);
  });

  function status(message) { nodes.status.textContent = message; }
  function save() { if (!store.save(prefs)) status("Could not save changes on this device."); }
  function clock() {
    var now = new Date();
    nodes.clock.textContent = ("0"+now.getHours()).slice(-2)+":"+("0"+now.getMinutes()).slice(-2);
  }
  function find(id) {
    for (var i=0; i<apps.length; i++) if (apps[i].id === id) return apps[i];
    return null;
  }
  function option(name, run, icon) { return {name:name, run:run, symbol:icon || "settings"}; }
  function rows() {
    if (confirm) return [option("Cancel", back), option("Reset", function () {
      prefs = store.clear(); save(); back(); status("Launcher preferences reset.");
    })];
    if (actionApp) {
      var entry = find(actionApp);
      if (!entry) return [option("Back to apps", back)];
      var index = prefs.favorites.indexOf(entry.id);
      var options = [option("Open app", function () { launch(entry); }, "open"),
        option(index === -1 ? "Pin to Home" : "Remove from Home", function () {
          if (index < 0) {
            if (prefs.favorites.length >= 100) { status("The favorites list is full."); return; }
            prefs.favorites.push(entry.id);
          } else prefs.favorites.splice(index,1);
          save();
        }, "pin")];
      var visible = prefs.favorites.filter(function(id){return !!find(id);});
      var visibleIndex = visible.indexOf(entry.id);
      function move(other) {
        var target = prefs.favorites.indexOf(visible[other]);
        prefs.favorites[index] = prefs.favorites[target];
        prefs.favorites[target] = entry.id;
        save();
      }
      if (visibleIndex > 0) options.push(option("Move earlier",function () { move(visibleIndex-1); },"left"));
      if (visibleIndex >= 0 && visibleIndex+1 < visible.length) options.push(option("Move later",function () { move(visibleIndex+1); },"right"));
      return options;
    }
    if (section === 3) return [
      option("Wallpaper "+(prefs.wallpaper ? "on" : "off"),function(){prefs.wallpaper=!prefs.wallpaper;save();}),
      option("Refresh installed apps",function(){refresh(true);},"refresh"),
      option("Reset preferences",function(){confirm=true;selected=0;},"reset")];
    if (section === 1) return apps;
    if (section === 2) {
      var needle = query.trim().toLowerCase();
      return needle ? apps.filter(function (item) { return item.name.toLowerCase().indexOf(needle) >= 0; }) : [];
    }
    var pinned = prefs.favorites.map(find).filter(Boolean);
    if (pinned.length) return pinned;
    return [option("Open app library", function () { go(1,"items"); }, "library")];
  }

  function makeButton(parent, name, active, style, run) {
    var button = document.createElement("button");
    button.type = "button";
    button.tabIndex = -1;
    button.className = style + (active ? " focused" : "");
    button.setAttribute("aria-label",name);
    button.onclick = function () { run(); render(); };
    parent.appendChild(button);
    return button;
  }

  function render() {
    var list = rows();
    if (zone==="items"&&!list.length&&section!==2)zone="nav";
    selected = Math.max(0,Math.min(selected,list.length-1));
    document.body.classList.toggle("quiet",!prefs.wallpaper);
    document.body.classList.toggle("search",section === 2 && !actionApp && !confirm);
    nodes.nav.textContent = "";
    sections.forEach(function (name,i) {
      var current = i === section;
      var button = makeButton(nodes.nav,name,zone==="nav"&&i===nav, current ? "active" : "",function(){if(!confirm&&!actionApp&&!pending)go(i);});
      button.textContent = name;
      if (current) button.setAttribute("aria-current","page");
    });
    var info = ["Pin your installed apps here for quick access.","Open an app or add it to Favorites.",
                "Search the apps the TV makes available to Coast.","Appearance, catalog refresh, and launcher preferences."];
    nodes.title.textContent = confirm ? "Reset preferences?" : actionApp ? ((find(actionApp)||{}).name || "App unavailable") : sections[section];
    nodes.description.textContent = confirm ? "This clears Coast favorites and appearance preferences." :
      actionApp ? "Installed Samsung app" : info[section];
    var search = section===2&&!actionApp&&!confirm;
    nodes.query.hidden = !search;
    nodes.keyboard.hidden = !search;
    nodes.keyboard.textContent = "";
    if (search) {
      nodes.query.textContent = query ? "Search: "+query : "Enter an app name";
      keys.forEach(function (letter,i) {
        var button=makeButton(nodes.keyboard,letter,zone==="keys"&&i===key,"key",function(){key=i;activateKey();});
        button.textContent=letter;
      });
    }
    nodes["shelf-title"].textContent = confirm || actionApp || section===3 ? "Actions" :
      section===0 ? "Favorites" : section===2 ? "Results" : "Installed apps";
    nodes.position.textContent = list.length > 5 ? (selected+1)+" of "+list.length : "";
    nodes.dock.textContent="";
    var start=Math.floor(selected/5)*5;
    list.slice(start,start+5).forEach(function (item,offset) {
      var i=start+offset;
      var button=makeButton(nodes.dock,item.name,zone==="items"&&i===selected,"tile",function(){
        zone="items"; selected=i; choose(item);
      });
      var mark=document.createElement("span");
      mark.className="mark";
      mark.setAttribute("aria-hidden","true");
      mark.textContent=item.id ? item.name.charAt(0).toUpperCase() :
        ({open:">",pin:"+",left:"<",right:">",refresh:"+",settings:"=",reset:"x",library:"#"}[item.symbol] || "=");
      if (item.icon && /^(file:\/\/|\/opt\/|\/usr\/)/.test(item.icon)) {
        var image=document.createElement("img");
        image.alt="";
        image.onload=function(){mark.textContent="";mark.appendChild(image);};
        image.src=item.icon.charAt(0)==="/" ? "file://"+item.icon : item.icon;
      }
      var name=document.createElement("span");
      name.className="name"; name.textContent=item.name;
      var badge=document.createElement("span");
      badge.className="badge"; badge.textContent=item.id ? "Installed app" : "";
      button.appendChild(mark);button.appendChild(name);button.appendChild(badge);
    });
    if (!list.length) nodes.dock.textContent=section===2 && !query.trim() ? "Type to find an installed app." :
      listState==="loading" ? "Reading installed apps..." :
      listState==="error" ? "App list unavailable. Refresh from Settings." :
      section===2 ? "No matching installed apps." : "The TV returned no visible apps.";
    nodes.hint.textContent = platform.device ? "Arrows  Move    OK  Select    Back  Return" :
      "Desktop preview    Arrows  Move    Enter  Select    Esc  Back";
    var focused=document.querySelector(".focused");
    if (focused && !document.hidden) focused.focus();
  }

  function go(index, focus) {
    section=index;nav=index;zone=focus || (index===2 ? "keys" : "nav");
    selected=0;key=0;actionApp=null;confirm=false;origin=null;status("");
    if (section===1 && prefs.lastId) {
      apps.some(function(app,i){if(app.id!==prefs.lastId)return false;selected=i;return true;});
    }
  }

  function choose(item) {
    if (!item || pending) return;
    if (!item.id) { item.run(); return; }
    origin={selected:selected,id:item.id,zone:zone};
    actionApp=item.id; selected=0; zone="items";status("");
  }

  function launch(item) {
    if (pending || !find(item.id)) return;
    pending=true;
    status("Opening "+item.name+"...");
    var settled=false;
    var timer=setTimeout(function(){if(finish())status("Launch did not respond. Try again.");},5000);
    function finish() {
      if (settled) return false;
      settled=true; pending=false; clearTimeout(timer); return true;
    }
    platform.launch(item.id,function(){
      if (!finish()) return;
      prefs.lastId=item.id;
      status("");
      save();
      back();
      render();
    },function(){
      if (!finish()) return;
      status("Could not open "+item.name+". Refresh the app list if it was removed.");
    });
  }

  function refresh(showStatus) {
    var token=++generation;
    var previous=rows()[selected];
    var timer=setTimeout(function(){failed();},5000);
    function failed() {
      if(token!==generation)return;
      generation++; clearTimeout(timer); listState="error";
      status(platform.supported ? "Could not read installed apps." : "Samsung app discovery is unavailable on this runtime.");
      render();
    }
    if (!apps.length) listState="loading";
    if (showStatus) status("Refreshing installed apps...");
    render();
    platform.list(function(items){
      if(token!==generation)return;
      generation++; clearTimeout(timer);listState="ready";apps=items;
      if (actionApp && !find(actionApp)) { back(); status("That app is no longer available."); }
      else status(showStatus ? "App library refreshed." : "");
      if (previous && previous.id && !actionApp) {
        rows().some(function(item,i){if(item.id!==previous.id)return false;selected=i;return true;});
      }
      render();
    },failed);
  }

  function back() {
    if (pending) return;
    if (confirm) { confirm=false; selected=0; return; }
    if (actionApp) {
      actionApp=null;
      selected=origin ? origin.selected : 0;
      zone=origin ? origin.zone : "items";
      origin=null;
      return;
    }
    if(section!==0){go(0);return;}
    if(!platform.exit())status("Close the preview window to exit.");
  }

  function activateKey() {
    var value=keys[key];
    if(value==="Results"){if(rows().length){zone="items";selected=0;}return;}
    if(value==="Delete")query=query.slice(0,-1);
    else if(value==="Clear")query="";
    else if(query.length<70)query+=value==="Space"?" ":value;
    selected=0;
  }

  document.addEventListener("keydown",function(event){
    var code=event.keyCode, direction=code>=37&&code<=40;
    if(direction||code===13||code===10009)document.body.classList.add("remote");
    if(code===10009||code===27||code===8){
      event.preventDefault();
      if(event.repeat||Date.now()-lastBack<180)return;
      lastBack=Date.now();back();
    } else if(code===13){
      event.preventDefault();
      if(event.repeat||Date.now()-lastOk<130)return;
      lastOk=Date.now();
      if(zone==="nav")go(nav,nav===2?"keys":"items");
      else if(zone==="keys")activateKey();
      else choose(rows()[selected]);
    } else if(direction){
      event.preventDefault();
      var search=section===2&&!actionApp&&!confirm;
      var items=rows();
      if(zone==="nav"){
        if(code===37||code===39)nav=(nav+sections.length+(code===37?-1:1))%sections.length;
        if(code===40)zone=search?"keys":items.length?"items":"nav";
      } else if(zone==="keys"){
        if(code===38&&key<10)zone="nav";
        else if(code===40&&key>=30&&items.length)zone="items";
        else key=Math.max(0,Math.min(keys.length-1,key+({37:-1,38:-10,39:1,40:10}[code])));
      } else if(code===38&&!actionApp&&!confirm){
        zone=search?"keys":"nav";
      } else if(code===37||code===39){
        if(items.length)selected=(selected+items.length+(code===37?-1:1))%items.length;
      }
    } else if(section===2&&zone==="keys"&&!platform.device&&/^[a-z0-9 ]$/i.test(event.key||"")&&query.length<70){
      query+=event.key;selected=0;
    } else return;
    render();
  });
  document.addEventListener("pointermove",function(){if(!platform.device)document.body.classList.remove("remote");});
  document.addEventListener("visibilitychange",function(){if(!document.hidden){clock();refresh(false);}});
  if(platform.device)document.body.classList.add("remote");
  clock();setInterval(clock,15000);refresh(false);
}());
