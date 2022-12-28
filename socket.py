import socket, time, sys, json
import paho.mqtt.client as mqtt
  
# configure socket and connect to server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
topics = ['*', 'PiStatus', 'Version', 'INDIServer', 'LoopingExposures', 'LoopingExposuresStopped', 'Imaging', 'FindStar', 'Annotate', 'PlateSolve', 'CameraControlChange', 'Exposure', 'Temperature', 'CoolerPower']


host = sys.argv[1]
port = sys.argv[2]

# PORT 4400 = Guiding & Telescope
# PORT 4700 = Imaging, FindStar, Annotate, PlateSolve, CameraControlChange, PiStatus

clientSocket.connect((str(sys.argv[1]), int(sys.argv[2])))

# keep track of connection status
connected = True

clientMQTT = mqtt.Client()
clientMQTT.connect("192.168.178.161", 1900, 60)
  
while True:
    # attempt to send and receive wave, otherwise reconnect
    try:
        message = b""
        while True:
            c = clientSocket.recv(1)
            if c == b"\n":
                break
            else:
                message += c
        x = message
        message = message.replace(b"<\x90\xadE\xb6>", b"???")
        message = message.replace(b"<\xe8>", b"???")
        message = message.decode('iso-8859-1')
        message = json.loads(message)
        if message["Event"] in topics or "*" in topics:
            print(sys.argv[1] + ":" + str(sys.argv[2]) + " -> " + str(message))
            y = clientMQTT.publish(message["Event"], x)
            print()
        else:
            print(str(sys.argv[1]) + ":" + str(sys.argv[2]) + "(ignored event: " + message["Event"] + ") -> " + str(message))
    except socket.error:  
        # set connection status and recreate socket
        connected = False
        clientSocket = socket.socket()
        #print( "connection lost... reconnecting" )
        while not connected:
            # attempt to reconnect, otherwise sleep for 2 seconds
            try:
                clientSocket.connect((str(sys.argv[1]), int(sys.argv[2])))
                connected = True
                #print( "re-connection successful" )
            except socket.error:
                pass
clientSocket.close()