from django.db import models
from urllib import request
import json
import pandas as pd

# Commands class - run all the things
# For payload and header information, refer to the BRAVIA Developer Knowledge Center
# (https://pro-bravia.sony.net/develop/)
class Commands(models.Model):

    def callAPI(self, url, payload, headers):
        try:
            data = json.dumps(payload).encode("utf-8")
            req = request.Request(url, data=data, headers=headers)
            response = request.urlopen(req)
            # Grab the result
            parsed = json.loads(response.read().decode('utf-8'))
        # Only issue really is that the TV returns an error or can't connect, data validation should be handled by the TV
        # so just return nothing
        except Exception as exp:
            return exp
        return parsed

    # Get all the available sources
    def getSources(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method" : "getCurrentExternalInputsStatus", "params" : [], "id" : 1, "version" : "1.1"}
        url = "http://" + IP + "/sony/avContent"

        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url,payload,{'Content-Type': 'application/json'})
            parsed = parsed['result']
        # Only issue really is that the TV returns an error or can't connect, data validation should be handled by the TV
        # so just return nothing
        except Exception as a:
            return a

        # Parse the result as a table, and remove inactive sources
        table = pd.DataFrame(parsed[0], columns=['title', 'label', 'connection', 'uri'])
        inactive_rows = table[table.connection == False].title
        active_rows = table[-table.title.isin(inactive_rows)]
        # Remove the connection row
        active_rows.drop('connection', axis=1, inplace=True)
        # Adjust column names
        active_rows.columns = ['Title', 'Friendly Name', 'URI (to change source)']

        # Return HTML table of sources and their URIs
        return active_rows.to_html(index=False, justify='center')

    # To use for friendly IRCC name mapping to true IRCC commands
    def getDict(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method": "getRemoteControllerInfo", "params": [], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/system"
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, {'Content-Type': 'application/json'})
            parsed = parsed['result']
        except Exception:
            return ""

        # Parse the result as a table
        table = pd.DataFrame(parsed[1], columns=['name', 'value'])
        # Rename the columns
        table.columns = ['Command Name', 'Command']
        # Return as a dictionary containing two lists (command names and commands)
        return table.to_dict('list')

    # Used to grab the current source
    def getCurrent(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method": "getPlayingContentInfo", "params": [], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/avContent"
        # Need to supply PSK for the current source
        headers = {
                    "Content-Type" : "application/json",
                    "X-Auth-PSK" : PSK
                  }
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return "Current source information unavailable"
        # Return the current source from the result
        return "Current source is: " + parsed[0]['title']

    # Used to grab the volume information
    def getVolume(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method": "getVolumeInformation", "params": [], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/audio"
        # Need to supply PSK for volume info
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }

        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return "Volume information unavailable"

        # Return the current volume from the result
        return "Current volume level is: " + str(parsed[0][0]['volume'])

    # Used to grab available applications
    def getApplications(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method": "getApplicationList", "params": [], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/appControl"
        # Need to supply PSK for application info
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }

        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return ""

        # Make sure pandas doesn't cut off URIs
        pd.set_option('display.max_colwidth', 0)

        # Convert result to a table
        table = pd.DataFrame(parsed[0], columns=['title', 'uri'])
        # Rename the columns
        table.columns = ['Title', 'URI (to change application)']
        # Return as a HTML table
        return table.to_html(index=False, justify='center')

    # Used to grab the current time
    def getTime(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method": "getCurrentTime", "params": [], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/system"
        # Don't actually need PSK for the time, but I've left it in
        headers = {
            "Content-Type" : "application/json",
            "X-Auth-PSK" : PSK
        }
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return ""
        # Return the current time
        return "Current time on TV is: " + parsed[0]

    # Used to grab model information
    def getModelInfo(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method": "getInterfaceInformation", "params": [], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/system"
        # Don't actually need PSK for the time, but I've left it in
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return ""

        # Extract the product name and model name (BRAVIA <some model>)
        return "Model information is: " + parsed[0]['productName'] + " " + parsed[0]['modelName']

    # Used to grab network information
    def getNetwork(self, IP, PSK):
        # Supply method name, and interface
        payload = {"method": "getNetworkSettings", "params": [{"netif": "eth0"}], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/system"
        # Need PSK for network information
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return ""
        # Extract the IP address and MAC address of the TV
        return "TV has IP: " + parsed[0][0]['ipAddrV4'] + " and MAC address: " + parsed[0][0]['hwAddr']

    # Used to toggle power
    def setPower(self, IP, PSK):
        status = False
        # Grab the current power status - to toggle on/off depending on current state
        if self.getPower(IP, PSK) == "standby":
            status = True
        else:
            status = False
        # Status will be based on the return from current power status
        payload = {"method": "setPowerStatus", "params": [{"status": status}], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/system"
        # Need to supply PSK to power on/off
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return ""
        # No need to return anything
        return ""

    # Grab the current power status
    def getPower(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method": "getPowerStatus", "params": [], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/system"
        # Not sure if PSK is needed
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return ""
        # Return the current status boolean
        return parsed[0]['status']

    # Used to grab the available IRCC commands
    def getControls(self, IP, PSK):
        # No parameters, just supply method name
        payload = {"method": "getRemoteControllerInfo", "params": [], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/system"
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, {"Content-Type": "application/json"})
            parsed = parsed['result']
        except Exception:
            return ""

        # Convert the result to a table of commands
        table = pd.DataFrame(parsed[1], columns=['name'])
        # Rename the column
        table.columns = ['Command Name']
        # Return the table as a HTML table
        return table.to_html(index=False, justify='center')

    # Used to set the volume level
    def setVolume(self, inVol, IP, PSK):
        # Need to supply PSK to change volume
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Supply the volume as a parameter
        payload = {"method": "setAudioVolume", "params": [{"volume" : inVol, "target" : ""}], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/audio"
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
        except Exception:
            return ""
        # Return nothing
        return ""

    # Used to change to an external source
    def setSource(self, inSrc, IP, PSK):
        # Need to supply PSK to change source
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Supply the external input URI as a parameter
        payload = {"method": "setPlayContent", "params": [{"uri" : inSrc}], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/avContent"
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
        except Exception:
            return ""
        # Return nothing
        return ""

    # Used to change to an application
    def setApp(self, inApp, IP, PSK):
        # Need to supply PSK to run application
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Supply the application URI as a parameter
        payload = {"method": "setActiveApp", "params": [{"uri" : inApp}], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/appControl"
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
        except Exception:
            return ""
        # Return nothing
        return ""

    def sendIRCC(self, inIRCC, IP, PSK):
        commandDict = self.getDict(IP, PSK)
        # Grab the index of the command in the Commands list from commandDict given the Command Name
        idx = commandDict['Command Name'].index(inIRCC)
        # Grab the real IRCC command at the given index
        inIRCC = commandDict['Command'][int(idx)]
        # For information on the XML body and headers, refer to the BRAVIA Developer Knowledge Center
        body = "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:X_SendIRCC xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\"><IRCCCode>" + inIRCC + "</IRCCCode></u:X_SendIRCC></s:Body></s:Envelope>"
        url = "http://" + IP + "/sony/ircc"
        headers = {
            "Host": IP,
            "Accept": "*/*",
            "Content-Type": "text/xml; charset=UTF-8",
            "SOAPACTION": "\"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC\"",
            "X-Auth-PSK": PSK,
            "Connection": "Keep-Alive",
            "Content-Length": str(len(body))
        }
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, body, headers)
        except Exception:
            return ""
        # Return nothing
        return ""

    def sendKeyboard(self, inKB, IP, PSK):
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Supply the application URI as a parameter
        payload = {"method": "setTextForm", "params": [{"uri": inKB}], "id": 1, "version": "1.0"}
        url = "http://" + IP + "/sony/appControl"
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
        except Exception:
            return ""
        # Return nothing
        return ""

    def getTV(self, IP, PSK):
        headers = {
            "Content-Type": "application/json",
            "X-Auth-PSK": PSK
        }
        # Need to supply a source to grab content for, in this instance it is tv:dvbt (digital TV)
        payload = {"method" : "getContentList", "params" : [{"source":"tv:dvbt", "stIx":0}], "id" :2, "version" : "1.2"}
        url = "http://" + IP + "/sony/avContent"
        # Try to connect to WebAPI with the payload as JSON
        try:
            parsed = self.callAPI(url, payload, headers)
            parsed = parsed['result']
        except Exception:
            return ""

        # Parse the result as a table
        table = pd.DataFrame(parsed[0], columns=['title', 'dispNum', 'uri'])
        # Rename the columns
        table.columns = ['Name', 'Channel Number', 'URI (to change source)']

        # Return HTML table of channels and their URIs
        return table.to_html(index=False, justify='center')