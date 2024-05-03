from time import sleep
import network
import socket
import machine

ssid = 'Shivam1'
password = '12345678'
MAX_TRIES = 10
HOST = '192.168.37.62'

I2C_MODE = 0x01
UART_MODE = 0x02
DEV_ADDRESS = 0x22

DEVICE_VID = 0x3343
DEVICE_ADDRESS = 0x22

HPA = 0x01
KPA = 0x02
TEMP_C = 0x03
TEMP_F = 0x04


class DFRobotEnvironmentalSensor:
    def __init__(self, bus):
        self.i2c = machine.I2C(bus, scl=machine.Pin(27), sda=machine.Pin(26))

    def _detect_device_address(self):
        try:
            self.i2c.readfrom_mem(DEV_ADDRESS, 0x04, 2)
            return DEV_ADDRESS
        except OSError:
            return None

    def begin(self):
        return self._detect_device_address() == DEV_ADDRESS

    def get_temperature(self):
        data = int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x14, 2), 'big')
        # temp = (-45) + ((data * 175.00) / 1024.00 / 64.00)
        # if unit == TEMP_F:
        #     temp = temp * 1.8 + 32
        # return round(temp, 2)
        return data

    def get_humidity(self):
        data = int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x16, 2), 'big')
        # humidity = (data / 1024) * 100 / 64
        # return humidity
        return data

    def get_ultraviolet_intensity(self):
        version = int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x05, 2), 'big')
        if version == 0x1001:
            data = int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x10, 2), 'big')
            # ultraviolet = data / 1800
            return data
        else:
            data = int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x10, 2), 'big')
            # output_voltage = 3.0 * data / 1024
            # ultraviolet = (output_voltage - 0.99) * (15.0 - 0.0) / (2.9 - 0.99) + 0.0
            return data
        # return round(ultraviolet, 2)

    def get_luminous_intensity(self):
        data = int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x12, 2), 'big')
        # luminous = data * (1.0023 + data * (8.1488e-5 + data * (-9.3924e-9 + data * 6.0135e-13)))
        # return round(luminous, 2)
        return data

    def get_atmosphere_pressure(self):
        data = int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x18, 2), 'big')
        return data

    def get_elevation(self):
        data = int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x18, 2), 'big')
        # elevation = 44330 * (1.0 - pow(data / 1015.0, 0.1903))
        # return round(elevation, 2)
        return data


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    for i in range(1, MAX_TRIES + 1):
        wlan.connect(ssid, password)
        if wlan.isconnected():
            wlan_ip = wlan.ifconfig()[0]
            print(f'Connected on {wlan_ip}')
            return wlan_ip
        print(f'{i}/{MAX_TRIES} tries connecting to wifi')

        if i < MAX_TRIES:
            sleep(1)

    print('Failed to connect. Soft Resetting!')
    machine.soft_reset()


def open_tcp_socket(host):
    addr = socket.getaddrinfo(host, 12345)[0][-1]
    s = socket.socket()
    s.connect(addr)
    print('Socket opened')
    return s


if connect():
    sock = open_tcp_socket(HOST)

    sensor = DFRobotEnvironmentalSensor(1)  # I2C bus 0

    if sensor.begin():
        while True:
            sleep(1)
            temp = sensor.get_temperature()
            humidity = sensor.get_humidity()
            uv = sensor.get_ultraviolet_intensity()
            lumen = sensor.get_luminous_intensity()
            pressure = sensor.get_atmosphere_pressure()
            elevation = sensor.get_elevation()

            print(temp)
            print(humidity)
            print(uv)
            print(lumen)
            print(pressure)
            print(elevation)
            print()

            sock.write(temp.to_bytes(4, 'big'))
            sock.write(humidity.to_bytes(4, 'big'))
            sock.write(uv.to_bytes(4, 'big'))
            sock.write(lumen.to_bytes(4, 'big'))
            sock.write(pressure.to_bytes(4, 'big'))
            sock.write(elevation.to_bytes(4, 'big'))

    else:
        print("Failed to initialize sensor")
