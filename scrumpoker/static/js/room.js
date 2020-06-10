(function () {
    const url = (new URL(window.location));
    let socket = new WebSocket("ws://" + url.hostname + ":" + url.port + "/ws/" + roomId);

    const roomApp = new Vue({
        el: "#room",
        data: {
            state: {
                id: "",
                participants: {},
                is_exposed: false,
                moderator: "",
            }
        },
        methods: {
            renderResult: function (result) {
                if (result === true){
                    return "X";
                } else if (result === false) {
                    return "-";
                } else {
                    return result;
                }
            },
            isExposed: result => result === "true",
            vote: function (points) {
                socket.send(JSON.stringify({
                    type: "vote",
                    data: {
                        points,
                    }
                }))
            }
        }

    });


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
        const data = JSON.parse(event.data);
        console.log("WS message: " + event.data);
        if (data.type === "room_update") {
            roomApp.state = data.data;
        }
    };

    socket.onerror = function (error) {
        console.log("WS  error: " + error.message);
    };


}());