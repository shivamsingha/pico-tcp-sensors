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
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x14, 2), 'big')

    def get_humidity(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x16, 2), 'big')

    def get_ultraviolet_version(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x05, 2), 'big')

    def get_ultraviolet_intensity(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x10, 2), 'big')

    def get_luminous_intensity(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x12, 2), 'big')

    def get_atmosphere_pressure(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x18, 2), 'big')

    def get_elevation(self):
        return int.from_bytes(self.i2c.readfrom_mem(DEV_ADDRESS, 0x18, 2), 'big')


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

            data = [sensor.get_temperature(), sensor.get_humidity(), sensor.get_ultraviolet_version(),
                    sensor.get_ultraviolet_intensity(), sensor.get_luminous_intensity(),
                    sensor.get_atmosphere_pressure(), sensor.get_elevation()]

            print(data)
            for x in data:
                bytes_written = sock.write(x.to_bytes(4, 'big'))
                if bytes_written != 4:
                    print(f'Error: {bytes_written} bytes written, expected 4')
            print()

    else:
        print("Failed to initialize sensor")
