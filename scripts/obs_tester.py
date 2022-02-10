
import simpleobsws
import logging
logging.basicConfig(level=logging.DEBUG)
import asyncio

ws = simpleobsws.WebSocketClient(url = 'ws://localhost:4444', password = 'N3ruMACim7Oh0VEW')


async def make_request():
    await ws.connect() # Make the connection to obs-websocket
    await ws.wait_until_identified() # Wait for the identification handshake to complete

    request = simpleobsws.Request('GetVersion') # Build a Request object

    ret = await ws.call(request) # Perform the request
    if ret.ok(): # Check if the request succeeded
        print("Request succeeded! Response data: {}".format(ret.responseData))
    
    # request = simpleobsws.Request('StartRecord') # Build a Request object

    # ret = await ws.call(request) # Perform the request
    # if ret.ok(): # Check if the request succeeded
    #     print("Request succeeded! Response data: {}".format(ret.responseData))

    # await ws.disconnect() # Disconnect from the websocket server cleanly

loop = asyncio.get_event_loop()
loop.run_until_complete(make_request())

