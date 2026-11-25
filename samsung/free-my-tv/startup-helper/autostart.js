/* Samsung TV Web Service: one launch on boot and on each observed standby -> on transition.
 * It runs only in an opt-in build signed with a device-bound Partner certificate. */
var http = require('http');
var WAKE_POLL_MS = 250;
var ON_POLL_MS = 1000;
var EARLY_LAUNCH_DELAY_MS = 500;
var EARLY_LAUNCH_TIMEOUT_MS = 8000;
var APP_ID = 'FreeMyTVio.FreeMyTV';
var CONTEXT_CHECK_MS = 1000;
var CONTEXT_WINDOW_MS = 45000;
var timer = null;
var earlyTimer = null;
var pending = false;
var power = null;
var wake = {};
var serviceStartedAt = null;
var events = [];
var timingPort = null;
var timingListener = null;

function record(label) {
  events.push({ at: Date.now(), label: label });
  if (events.length > 8) events.shift();
}

function registerTimingPort() {
  try {
    timingPort = tizen.messageport.requestTrustedLocalMessagePort('StartupTiming');
    timingListener = timingPort.addMessagePortListener(function (items, sender) {
      if (!sender || sender.appId !== 'FMyTVBoot1.Helper') return;
      sender.sendMessage([{ key: 'timing', value: JSON.stringify({
        serviceStartedAt: serviceStartedAt,
        events: events
      }) }], timingPort);
    });
  } catch (error) {} // The startup service can run even if timing is unavailable.
}

function watchAppContext() {
  if (wake.contextWatch) return;
  var watchedWake = wake;
  var startedAt = Date.now();
  var gotList = false;
  var watch = {};
  wake.contextWatch = watch;

  function check() {
    if (wake !== watchedWake || watch.stopped) return;
    try {
      tizen.application.getAppsContext(function (contexts) {
        watch.pending = false;
        if (wake !== watchedWake || watch.stopped) return;
        if (contexts.some(function (context) { return context.appId === APP_ID; })) {
          record('Tizen listed Free My TV as running');
          stop();
        } else if (!gotList) {
          gotList = true;
          record('First app list did not contain Free My TV');
        }
      }, function (error) {
        watch.pending = false;
        if (wake !== watchedWake || watch.stopped) return;
        record('Could not read running apps (' + error.name + ')');
        stop();
      });
    } catch (error) {
      record('Could not read running apps (' + error.name + ')');
      stop();
    }
  }

  function stop() {
    clearTimeout(watch.timer);
    watch.stopped = true;
  }

  function tick() {
    if (wake !== watchedWake || watch.stopped) return;
    if (Date.now() - startedAt >= CONTEXT_WINDOW_MS) {
      record('Running context was not seen within 45 seconds');
      stop();
      return;
    }
    watch.timer = setTimeout(tick, CONTEXT_CHECK_MS);
    if (watch.pending) return;
    watch.pending = true;
    check();
  }

  watch.timer = setTimeout(tick, 0);
}

function launch(early) {
  if (wake.accepted || wake.request || wake.confirmed) return;
  if (!early) wake.confirmed = true;
  var request = {};
  wake.request = request;

  function finish(accepted, label) {
    if (wake.request !== request) return;
    clearTimeout(request.timeout);
    wake.request = null;
    wake.accepted = accepted;
    record(label);
    if (early && !accepted && power === 'on') launch(false);
  }

  record(early ? 'Early launch requested' : 'Launch requested after power confirmation');
  if (early) {
    request.timeout = setTimeout(function () {
      finish(false, 'Early launch received no reply');
    }, EARLY_LAUNCH_TIMEOUT_MS);
  }
  try {
    tizen.application.launch(APP_ID, function () {
      finish(true, 'Tizen accepted the request');
    }, function (error) {
      finish(false, 'Tizen declined the request (' + error.name + ')');
    });
  } catch (error) {
    finish(false, 'Launch request failed (' + error.name + ')');
  }
  watchAppContext();
}

function resetWake() {
  clearTimeout(earlyTimer);
  earlyTimer = null;
  if (wake.request) clearTimeout(wake.request.timeout);
  if (wake.contextWatch) clearTimeout(wake.contextWatch.timer);
  wake = {};
}

function observe(value) {
  var state = String(value).toLowerCase();
  if (state !== 'on' && state !== 'standby') return;
  var before = power;
  power = state;
  if (state === before) return;
  record(state === 'on' ? 'TV reported on' : 'TV reported standby');
  schedulePolls(state === 'on' ? ON_POLL_MS : WAKE_POLL_MS);
  if (state === 'standby') {
    resetWake();
  } else {
    clearTimeout(earlyTimer);
    earlyTimer = null;
    launch(false);
  }
}

function schedulePolls(interval) {
  if (timer !== null) clearInterval(timer);
  timer = setInterval(poll, interval);
}

function poll() {
  if (pending) return;
  pending = true;
  var req;
  try {
    req = http.get({host: '127.0.0.1', port: 8001, path: '/api/v2/'}, function (res) {
      var body = '';
      res.on('data', function (chunk) { body += chunk; });
      res.on('end', function () {
        pending = false;
        if (timer === null) return;
        try { observe(JSON.parse(body).device.PowerState); } catch (e) {}
      });
    });
    req.on('error', function () { pending = false; });
    req.setTimeout(2000, function () { req.destroy(); });
  } catch (e) { pending = false; }
}

exports.onStart = function () {
  if (timer !== null) return;
  power = null;
  serviceStartedAt = Date.now();
  events = [];
  schedulePolls(WAKE_POLL_MS);
  poll();
  if (power === null) {
    earlyTimer = setTimeout(function () {
      earlyTimer = null;
      if (power === null && timer !== null) launch(true);
    }, EARLY_LAUNCH_DELAY_MS);
  }
  registerTimingPort();
};
exports.onRequest = function () {};
exports.onExit = function () {
  if (timer !== null) clearInterval(timer);
  timer = null;
  resetWake();
  if (timingListener !== null) {
    try { timingPort.removeMessagePortListener(timingListener); } catch (error) {}
  }
  timingPort = null;
  timingListener = null;
};
