import socket, time, sys, json, time
import paho.mqtt.client as mqtt
import logging

_debug = True
_trace = True

logging.basicConfig(filename="./ASIAIR_"+str(sys.argv[2])+".log",
                    filemode="a",
                    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                    datefmt="%H:%M:%S",
                    level=logging.DEBUG)


# create socket object
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get connection details from params
asisair_host  = str(sys.argv[1])
asisair_port  = int(sys.argv[2])
asisair_ident = str(sys.argv[3])
mqtt_host     = str(sys.argv[4])
mqtt_port     = int(sys.argv[5])


# PORT 4400 = Guiding & Telescope
# PORT 4700 = Imaging, FindStar, Annotate, PlateSolve, CameraControlChange, PiStatus
# Topics to include (wildcard for all)
'''
Alert
Annotate
AutoFocus
AutoGoto
AviRecord
Calibrating
CalibrationComplete
CalibrationFailed
CalibrationFailed
CalibrationFailed
CameraControlChange
CoolerPower
Exposure
FocuserMove
GuideStarLostTooMuch
GuideStep
GuidingStopped
INDIServer
LockPositionLost
LockPositionSet
LoopingExposures
LoopingExposuresStopped
LoopingFrames
PiStatus
PlateSolve
RestartGuide
ScopeHome
ScopeTrack
SettleBegin
SettleDone
Settling
StarLost
StarSelected
StartCalibration
StartGuiding
Temperature
Version

Nginx                       // Related to video stacking
RTMP                        // Related to video stacking
'''
topics = ['*']


#if _debug: print('connecting ASIAIR: ' + str(asisair_host) + ':' + str(asisair_port))
#clientSocket.connect((asisair_host, asisair_port))
## keep track of connection status
#connected = True
reconnect = 0
retry     = 0

# setup
if _debug: print("connecting MQTT: " + str(mqtt_host) + ':' + str(mqtt_port))
clientMQTT = mqtt.Client()
clientMQTT.connect(mqtt_host, mqtt_port, 60)

while True:
    # attempt to send and receive wave, otherwise reconnect
    try:
        message = b""
        while True:
            c = clientSocket.recv(1)
            if c == b"\n":
                break
            elif c == b"":
                if _debug: print("force reconnect")
                clientSocket.close()
            else:
                message += c
        x = message
        # replace bad characters
        message = message.replace(b"<\x90\xadE\xb6>", b"???")
        message = message.replace(b"<\xe8>", b"???")
        message = message.decode('iso-8859-1')
        message = json.loads(message)
        message['utime'] = int(time.time())
        message['instance'] = asisair_ident
        if message["Event"] in topics or "*" in topics:
            if _debug: print(asisair_host + ":" + str(asisair_port) + " -> " + str(json.dumps(message)))
            #if _debug: print(asisair_host + ":" + str(asisair_port) + " -> " + str(json.dumps(x)))
            y = clientMQTT.publish(asisair_ident + "/" + message["Event"], str(json.dumps(message)))
        else:
            if _debug: print(str(asisair_host) + ":" + str(asisair_port) + "(ignored event: " + message["Event"] + ") -> " + str(json.dumps(message)))
            pass
        logging.debug(str(x))
        reconnect += 1
    except socket.error:
        connected = False
        while not connected:
            # attempt to reconnect, otherwise sleep for 2 seconds
            try:
                # socket and reset connection status
                clientSocket.close()
                clientSocket = None
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.settimeout(2)
                clientSocket.connect((asisair_host, asisair_port))
                clientSocket.settimeout(None)
                connected = True
                if reconnect == 0: 
                    if _debug: print("initial connection successful")
                    x = {'Event': "Connected", 'instance': asisair_ident, 'utime': int(time.time())} 
                    y = clientMQTT.publish(asisair_ident + "/Connected", str(json.dumps(x)))
                    print()
                if reconnect >= 1: 
                    if _debug: print("reconnect successful")
                retry = 0
                
                #except socket.error as error:
            except OSError as error:
                if(clientSocket is not None):
                    clientSocket.close()
                #if _debug: print("socket error, retry in 10 seconds [" + str(reconnect) + "/" + str(retry) + "]: " + str(error))
                # if reconnect > 0 and retry == 0 an existing connection has been lost
                if reconnect > 0 and retry == 0:
                    if _debug: print("connection lost [" + str(reconnect) + "/" + str(retry) + "]: " + str(error))
                    x = {'Event': "Disconnected", 'instance': asisair_ident, 'utime': int(time.time())} 
                    y = clientMQTT.publish(asisair_ident + "/Disconnected", str(json.dumps(x)))
                # if reconnect == 0 and retry == 0 the initial connection did fail (first attempt)
                elif reconnect == 0 and retry == 0:
                    if _debug: print("initial connection failed [" + str(reconnect) + "/" + str(retry) + "]: " + str(error))
                # if reconnect == 0 and retry > 0 the initial connection did fail (additional attempts)
                elif reconnect == 0 and retry > 0:
                    if _debug: print("initial connection still not available [" + str(reconnect) + "/" + str(retry) + "]: " + str(error))
                else:
                    if _debug: print("reconnect failed [" + str(reconnect) + "/" + str(retry) + "]: " + str(error))
                connected = False
                retry += 1
                #time.sleep(1)
            
clientSocket.close()
if _debug: print("ENDE...")
