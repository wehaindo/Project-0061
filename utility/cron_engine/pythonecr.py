
'''
SMWinservice
by Davide Mastromatteo

Base class to create winservice in Python
-----------------------------------------

Instructions:

1. Just create a new class that inherits from this base class
2. Define into the new class the variables
   _svc_name_ = "nameOfWinservice"
   _svc_display_name_ = "name of the Winservice that will be displayed in scm"
   _svc_description_ = "description of the Winservice that will be displayed in scm"
3. Override the three main methods:
    def start(self) : if you need to do something at the service initialization.
                      A good idea is to put here the inizialization of the running condition
    def stop(self)  : if you need to do something just before the service is stopped.
                      A good idea is to put here the invalidation of the running condition
    def main(self)  : your actual run loop. Just create a loop based on your running condition
4. Define the entry point of your module calling the method "parse_command_line" of the new class
5. Enjoy
'''

import socket

import win32serviceutil

import servicemanager
import win32event
import win32service
import serial
import json
import asyncio
import websockets


class SMWinservice(win32serviceutil.ServiceFramework):
    '''Base class to create winservice in Python'''

    _svc_name_ = 'Python Serial Interface'
    _svc_display_name_ = 'Python Serial Interface Service'
    _svc_description_ = 'Python Serial Interface Service'

    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        '''
        Override to add logic before the start
        eg. running condition
        '''
        pass

    def stop(self):
        '''
        Override to add logic before the stop
        eg. invalidating running condition
        '''
        pass

    def main(self):
        '''
        Main class to be ovverridden to add logic
        '''
        self.start_server = websockets.serve(self.handler, "localhost", 1337)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()


    async def handler(websocket, path):
        data = await websocket.recv()
        # print(type(data))
        ser = serial.Serial('COM14')
        print(ser.name)    
        dict_data = json.loads(data)
        print(dict_data)
        if dict_data['type'] == "add_product":
            print("ADD Product")        
            reply = f"Data recieved as:  {data}!"    
            await websocket.send(reply)

        if dict_data['type'] == "bca_ecr":
            print("BCA ECR")        
            reply = f"Data recieved as:  {data}!"    
            arr_data = dict_data['value'].split(",")
            arr_str_data = ""
            for arr in arr_data:
                arr_str_data = arr_str_data + hex(int(arr)).split('x')[1].rjust(2,'0')
            print(arr_str_data)        
            ser.write(bytes.fromhex(arr_str_data))  

            for line in ser.read():
                print(line)
            
            #Waiting ACK
            if line == 6:
                print('Receive ACK')
                
            for i in range(0,200):
                print(ser.read())

            #ser.write(bytes.fromhex('06'))    
            await websocket.send(reply)
        
        ser.close()

# entry point of the module: copy and paste into the new module
# ensuring you are calling the "parse_command_line" of the new created class
if __name__ == '__main__':
    SMWinservice.parse_command_line()