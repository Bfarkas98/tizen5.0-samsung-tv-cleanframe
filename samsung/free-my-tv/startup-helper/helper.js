var launch = document.getElementById('launch');
var statusText = document.getElementById('status');
var timingText = document.getElementById('timing');

function timingLine(timestamp, label) {
    var date = new Date(timestamp);
    var milliseconds = ('00' + date.getMilliseconds()).slice(-3);
    return date.toTimeString().slice(0, 8) + '.' + milliseconds + '  ' + label;
}

function readTiming() {
    var reply, listener, waiting;
    function finish(text) {
        clearTimeout(waiting);
        if (reply && listener !== undefined) reply.removeMessagePortListener(listener);
        timingText.textContent = text;
    }
    try {
        reply = tizen.messageport.requestTrustedLocalMessagePort('StartupTimingReply');
        listener = reply.addMessagePortListener(function (items, sender) {
            if (!sender || sender.appId !== 'FMyTVBoot1.Autostart') return;
            var item = items.filter(function (value) { return value.key === 'timing'; })[0];
            if (!item) return;
            var report = JSON.parse(item.value);
            var lines = [timingLine(report.serviceStartedAt, 'Startup service began')];
            report.events.slice(-6).forEach(function (event) {
                lines.push(timingLine(event.at, event.label));
            });
            finish(lines.join('\n'));
        });
        waiting = setTimeout(function () { finish('The startup service did not reply.'); }, 2000);
        var service = tizen.messageport.requestTrustedRemoteMessagePort('FMyTVBoot1.Autostart', 'StartupTiming');
        service.sendMessage([{ key: 'request', value: 'timing' }], reply);
    } catch (error) {
        finish('Startup timing unavailable (' + error.name + ').');
    }
}

readTiming();

launch.addEventListener('click', function () {
    statusText.textContent = 'Opening Free My TV…';
    try {
        tizen.application.launch('FreeMyTVio.FreeMyTV', function () {
            statusText.textContent = 'Tizen accepted the launch request.';
        }, function (error) {
            statusText.textContent = 'Tizen declined the launch: ' + error.name;
        });
    } catch (error) {
        statusText.textContent = 'The launch request failed: ' + error.name;
    }
});

document.addEventListener('keydown', function (event) {
    if (event.keyCode === 10009) {
        tizen.application.getCurrentApplication().exit();
    }
});
