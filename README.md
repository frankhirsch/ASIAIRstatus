# ASIAIRstatus

The Python source code will allow to fetch ANY (or selected) events sent out from [ZWO ASIAIR](https://astronomy-imaging-camera.com/product-category/asiair) to a local [MQTT broker](https://mosquitto.org) and log them to local files. To run the code the script will require 5 parameters:
1. IP address of ASIAIR
2. Service port of ASIAIR (4400 = Guiding & Telescope, 4700 = Imaging, FindStar, Annotate, PlateSolve...)
3. ASIAIR identifier
4. IP address of MQTT broker
5. Port of MQTT broker

**To start run**

`./socket.py 192.168.178.100 4400 asiairPro 192.168.178.200 1883`

**Features**
1. Does automatically reconnect on connection loss (TCP socket stream)
2. Event filter to reduce amount of messages/logging
3. Handles some issues with undefined character encodings (INDI telescope control)
4. Add current unix timestamp and identifier to MQTT payload & topic

**Purpose**

With the given information in MQTT it's possible to notify specific events (3rd party notification in workflow tools such as [Node Red](https://nodered.org)) which is still a missing feature in ASIAIR itself, having in mind longer (unattended) imaging sessions without the need of staying awake the whole night to manually scan for potential issues ruining the whole night.

*Possible events might be*
1. Guide star lost
2. Guide calibration failed
3. Autofocus result/failed
4. Meridian flip...

**Node Red sample flow**

The provided Node Red flow is a basic sample illustrating how the MQTT messaging pipeline can be integrated into a user specific Pushover account

![Node Red sample flow](/node-red/node_red.png)
