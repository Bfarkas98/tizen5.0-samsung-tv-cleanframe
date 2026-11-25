(function () {
  "use strict";
  var sdk = window.tizen && window.tizen.application;
  window.coastPlatform = {
    device: !!sdk || /SMART-TV|Tizen/i.test(navigator.userAgent),
    supported: !!sdk,
    list: function (success, failure) {
      if (!sdk) { failure(); return; }
      try {
        var own = sdk.getCurrentApplication().appInfo.id;
        sdk.getAppsInfo(function (apps) {
          var seen = Object.create(null);
          success(apps.filter(function (app) {
            if (!app || typeof app.id !== "string" || !app.id || app.id === own ||
                typeof app.name !== "string" || !app.name.trim() || app.show === false || seen[app.id]) return false;
            seen[app.id] = true;
            return true;
          }).map(function (app) {
            return {id:app.id, name:app.name.trim(), icon:typeof app.iconPath === "string" ? app.iconPath : ""};
          }).sort(function (a,b) { return a.name.localeCompare(b.name); }));
        }, failure);
      } catch (error) { failure(error); }
    },
    launch: function (id, success, failure) {
      if (!sdk) { failure(); return; }
      try { sdk.launch(id, success, failure); } catch (error) { failure(error); }
    },
    exit: function () {
      if (!sdk) return false;
      try { sdk.getCurrentApplication().exit(); return true; } catch (error) { return false; }
    }
  };
}());
