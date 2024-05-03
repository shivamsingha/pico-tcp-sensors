const net = require('net');
const express = require('express');
const app = express();
const port = 3000;

// In-memory storage for sensor data
let sensorData = []

function getTemperature(data) {
    let temp = (-45) + ((data * 175.00) / 1024.00 / 64.00);

    return Math.round(temp * 100) / 100;
}

function getHumidity(data) {
    const humidity = (data / 1024) * 100 / 64;
    return humidity;
}

function getUltravioletIntensity(data, version) {
    let ultraviolet;

    if (version === 8704) {
        ultraviolet = data / 1800;
    } else {
        const outputVoltage = 3.0 * data / 1024;
        ultraviolet = (outputVoltage - 0.99) * (15.0 - 0.0) / (2.9 - 0.99) + 0.0;
    }

    return Math.round(ultraviolet * 100) / 100;
}

function getLuminousIntensity(data) {
    const luminous = data * (1.0023 + data * (8.1488e-5 + data * (-9.3924e-9 + data * 6.0135e-13)));
    return Math.round(luminous * 100) / 100;
}

function getAtmospherePressure(data) {
    return data/10;
}

function getElevation(data) {
    const elevation = 44330 * (1.0 - Math.pow(data / 1015.0, 0.1903));
    return Math.round(elevation * 100) / 100;
}

// TCP server to receive data
const tcpServer = net.createServer((socket) => {
    console.log('TCP client connected');

    socket.on('data', (data) => {
        uv_version = data.readInt32BE(2 * 4);
        sensorData = {
            temperature: getTemperature(data.readInt32BE()),
            humidity: getHumidity(data.readInt32BE(4)),
            ultraviolet: getUltravioletIntensity(data.readInt32BE(3 * 4), uv_version),
            luminous: getLuminousIntensity(data.readInt32BE(4 * 4)),
            pressure: getAtmospherePressure(data.readInt32BE(5 * 4)),
            elevation: getElevation(data.readInt32BE(6 * 4))
        };
        console.log(sensorData);
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
