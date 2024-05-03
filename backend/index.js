const net = require('net');
const express = require('express');
const app = express();
const port = 3000;

// In-memory storage for sensor data
let sensorData = {
    temperature: 0,
    humidity: 0,
    ultraviolet: 0,
    luminous: 0,
    pressure: 0,
    elevation: 0
};

// TCP server to receive data
const tcpServer = net.createServer((socket) => {
    console.log('TCP client connected');

    socket.on('data', (data) => {
        // Assuming data is a sequence of 6 4-byte floats
        // Update in-memory storage
        sensorData = { temperature: data.readInt32BE(),
            humidity: data.readInt32BE(4),
            ultraviolet: data.readInt32BE(2*4),
            luminous: data.readInt32BE(3*4),
            pressure: data.readInt32BE(4*4),
            elevation: data.readInt32BE(5*4) };
        console.log('Received data:', sensorData);
    });

    socket.on('end', () => {
        console.log('TCP client disconnected');
    });
});

// HTTP server to serve data
app.get('/data', (req, res) => {
    res.json(sensorData);
});

// Start TCP server
tcpServer.listen(12345, () => {
    console.log('TCP server listening on port 12345');
});

// Start HTTP server
app.listen(port, () => {
    console.log(`HTTP server listening at http://localhost:${port}`);
});
