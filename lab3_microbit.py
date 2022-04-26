print("IoT Gateway")
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
plt.style.use('fivethirtyeight')

ports = serial.tools.list_ports.comports()
for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
#
BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

#TODO: Add your token and your comport
#Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "5ROY8XpEiwZCHRpLeVmg"
bbc_port = "/dev/ttyACM0"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)
y_temp, y_light =[0],[0]

def processData(data):
    try:
        #print(data)
        data = data.replace("!1:", "")
        data = data.replace("#", "")
        splitData = data.split(":")
        data_dict = {splitData[0]:splitData[1]}
        print(data_dict)
        client.publish('v1/devices/me/telemetry', json.dumps(data_dict), 1)
        if splitData[0] == "TEMP":
            y_temp.append(int(splitData[1]))
        else:
            y_light.append(int(splitData[1]))
    except:
        pass


    #TODO: Add your source code to publish data to the server

def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = 0

    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['valueLED'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if jsonobj['params'] == False:
                cmd = 0
            else:
                cmd = 1
        if jsonobj['method'] == "setFAN":
            temp_data['valueFAN'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if jsonobj['params'] == False:
                cmd = 2
            else:
                cmd = 3
    except:
        pass

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message
plt.figure(figsize=(12,8))
def animate(i):
    # x.append(x_temp)
    # y.append(y_temp)
    plt.cla()
    plt.plot(range(len(y_light)),y_light)
    plt.plot(range(len(y_temp)), y_temp,'r')

    plt.legend(["Light", "Temp"], loc=2)
    plt.title("Graph for temperature and light value")
    plt.xlabel("Times")
    plt.ylabel("Values")

    if len(bbc_port) >  0:
        readSerial()
ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.tight_layout()
plt.show()

while True:

    if len(bbc_port) >  0:
        readSerial()
       # ax.plot(x,y,)

    time.sleep(1)