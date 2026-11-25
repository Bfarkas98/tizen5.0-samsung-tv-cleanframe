(function () {
  "use strict";
  var key = "tv-os-coast.preferences.v1";
  var defaults = {version:1, favorites:[], wallpaper:true, lastId:""};
  function normalize(value) {
    if (!value || value.version !== 1) return {version:1, favorites:[], wallpaper:true, lastId:""};
    var seen = Object.create(null);
    var ids = Array.isArray(value.favorites) ? value.favorites.filter(function (id) {
      if (typeof id !== "string" || !id || seen[id]) return false;
      seen[id] = true;
      return true;
    }).slice(0,100) : [];
    return {version:1, favorites:ids, wallpaper:value.wallpaper !== false,
            lastId:typeof value.lastId === "string" ? value.lastId : defaults.lastId};
  }
  window.coastPreferences = {
    read: function () {
      try { return normalize(JSON.parse(localStorage.getItem(key))); }
      catch (error) { return normalize(null); }
    },
    save: function (value) {
      try { localStorage.setItem(key, JSON.stringify(normalize(value))); return true; }
      catch (error) { return false; }
    },
    clear: function () { return normalize(null); }
  };
}());
