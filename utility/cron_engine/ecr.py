import serial
import json
import asyncio
import websockets


# Connect Serial

# ser = serial.Serial('COM14')
# print(ser.name)05 


# create handler for each connection
 
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

start_server = websockets.serve(handler, "localhost", 1337)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
