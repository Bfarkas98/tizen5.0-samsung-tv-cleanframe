/* Adapted from the MIT-licensed Free My TV startup service. */
var http = require('http');
var appId = '__CLEANFRAME_APP_ID__';
var pollTimer = null;
var earlyTimer = null;
var pending = false;
var power = null;
var wake = {};

function launch(early) {
  if (wake.accepted || wake.request || wake.confirmed) return;
  if (!early) wake.confirmed = true;
  var request = {};
  wake.request = request;

  function finish(accepted) {
    if (wake.request !== request) return;
    clearTimeout(request.timeout);
    wake.request = null;
    wake.accepted = accepted;
    if (early && !accepted && power === 'on') launch(false);
  }

  if (early) {
    request.timeout = setTimeout(function () { finish(false); }, 8000);
  }
  try {
    tizen.application.launch(appId, function () { finish(true); }, function () { finish(false); });
  } catch (error) {
    finish(false);
  }
}

function resetWake() {
  if (wake.request) clearTimeout(wake.request.timeout);
  wake = {};
}

function schedulePolls(interval) {
  if (pollTimer !== null) clearInterval(pollTimer);
  pollTimer = setInterval(poll, interval);
}

function observe(value) {
  var state = String(value).toLowerCase();
  if ((state !== 'on' && state !== 'standby') || state === power) return;
  power = state;
  clearTimeout(earlyTimer);
  earlyTimer = null;
  schedulePolls(state === 'on' ? 1000 : 250);
  if (state === 'on') launch(false);
  else resetWake();
}

function poll() {
  if (pending) return;
  pending = true;
  try {
    var request = http.get({host: '127.0.0.1', port: 8001, path: '/api/v2/'}, function (response) {
      var body = '';
      response.on('data', function (chunk) { body += chunk; });
      response.on('end', function () {
        pending = false;
        if (pollTimer === null) return;
        try { observe(JSON.parse(body).device.PowerState); } catch (error) {}
      });
    });
    request.on('error', function () { pending = false; });
    request.setTimeout(2000, function () { request.destroy(); });
  } catch (error) {
    pending = false;
  }
}

exports.onStart = function () {
  if (pollTimer !== null) return;
  power = null;
  schedulePolls(250);
  poll();
  if (power === null) {
    earlyTimer = setTimeout(function () {
      earlyTimer = null;
      if (power === null && pollTimer !== null) launch(true);
    }, 500);
  }
};
exports.onRequest = function () {};
exports.onExit = function () {
  if (pollTimer !== null) clearInterval(pollTimer);
  pollTimer = null;
  clearTimeout(earlyTimer);
  earlyTimer = null;
  resetWake();
};
