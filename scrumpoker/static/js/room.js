(function () {
    const url = (new URL(window.location));
    let socket = new WebSocket("ws://" + url.hostname + ":" + url.port + "/ws/" + roomId);

    socket.onopen = function () {
        console.log("WS connected");
    }

    socket.onclose = function (event) {
        if (event.wasClean) {
            console.log("WS closed clean");
        } else {
            console.log("WS closed bad");
        }
        console.log("WS code: " + event.code + " reason: " + event.reason);
    };

    socket.onmessage = function (event) {
        console.log("WS message: " + event.data);
        document.getElementById("content").innerHTML = event.data;
    };

    socket.onerror = function (error) {
        console.log("WS  error: " + error.message);
    };


}());