(function () {
    const url = new URL(window.location);

    function WSConnection() {
        let ws = null;
        let connectTimerId = 0;
        let sendTimerId = 0;

        function connect() {
            ws = new WebSocket("ws://" + url.hostname + ":" + url.port + "/ws/" + roomId);

            ws.onopen = function () {
                console.log("WS connected");
                clearTimeout(connectTimerId);
            }

            ws.onclose = function (event) {
                if (event.wasClean) {
                    console.log("WS closed clean");
                } else {
                    console.log("WS closed bad");
                    connectTimerId = setTimeout(connect, 1000);
                }
                console.log("WS code: " + event.code + " reason: " + event.reason);
            };

            ws.onmessage = function (event) {
                const data = JSON.parse(event.data);
                console.log("WS message: " + event.data);
                if (data.type === "room_update") {
                    roomApp.state = data.data;
                }
            };

            ws.onerror = function (error) {
                console.log("WS  error: " + error.message);
                if (ws.readyState != 1) {
                    connectTimerId = setTimeout(connect, 1000);
                }
            };
        }

        function send(msg) {
            if (ws.readyState === 1) {
                ws.send(msg);
                clearTimeout(sendTimerId);
            } else {
                sendTimerId = setTimeout(function () {
                    send(msg);
                }, 1000);
            }
        }

        if (!ws) {
            connect();
        }

        return {send}
    }

    const roomApp = new Vue({
        el: "#roomApp",
        data: {
            state: {
                id: "",
                participants: {},
                is_exposed: false,
                moderator: "",
            },
            isModerator: isModerator,
            ws: WSConnection()
        },
        methods: {
            renderResult: function (result) {
                if (result === true) {
                    return "X";
                } else if (result === false) {
                    return "-";
                } else {
                    return result;
                }
            },
            isExposed: result => (result !== true && result !== false),
            vote: function (points) {
                this.ws.send(JSON.stringify({
                    type: "vote",
                    data: {
                        points,
                    }
                }))
            },
            reset: function () {
                this.ws.send(JSON.stringify({
                    type: "reset",
                    data: {}
                }))
            },
            expose: function () {
                this.ws.send(JSON.stringify({
                    type: "expose",
                    data: {}
                }))
            }
        },
        computed: {
            isReady: function () {
                return Boolean(this.state.id)
            }
        }
    });

}());
