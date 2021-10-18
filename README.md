<h1 align="center">GSH OPC UA HMI Client and Server Platform </h1>
<div align="center">
<br>

<div align="left">
    
## Project library dependecy:

ASYNCIO OPC UA : - https://github.com/FreeOpcUa/opcua-asyncio : 

Installation with pip

    pip install asyncua

PyQt5 : - https://pypi.org/project/PySide2/

Installation with pip

    pip install PySide2
    pip install PyQt5

Installing Qt from the main website:
    
    https://www.qt.io/download
    Go to the bottom and find "Download for open source users"
    Then go to bottom of this page find "Download the Qt online installer"
    
Use the included Designer software to start making GUI's
    

## Clarifying general terms:

opcua-asyncio is an asyncio-based asynchronous OPC UA client and server based on python-opcua, removing support of python < 3.7.
Asynchronous programming allows for simpler code (e.g. less need for locks) and potentially performance gains.

Qt is set of cross-platform C++ libraries that implement high-level APIs for accessing many aspects of modern desktop and mobile systems. These include location and positioning services, multimedia, NFC and Bluetooth connectivity, a Chromium based web browser, as well as traditional UI development.

PyQt5 is a comprehensive set of Python bindings for Qt v5. It is implemented as more than 35 extension modules and enables Python to be used as an alternative application development language to C++ on all supported platforms including iOS and Android.

## PyQt5 HMI

Implemented

* Not started yet.

Not yet implemented:

* Main homepage that show each machine module.
* Lot Entry page
* Lot info page
* Event Log Page
* IO List Page
* IO Module Page
* Main Motor Page
* Station Page
* Vision Page
* ~~Tower Light page~~ Moved into settings page
* Life Cycle page
* Settings Page


                                                                                                                                
Implemented

* read/set attributes and browse
* getting nodes by path and nodeids
* getting nodes form pre-built server modeler
* adding nodes to address space
* read from the correct PLC relay by referencing Nodes Display Name
* write to node of current value of PLC relay/data memory
* datachange events will trigger write to PLC relay/data memory
* multithreaded application to prevent GUI freeze
* read and write relay/data memory from client to server
* reduced input delay by imlpmenting asynchronous input output method
* ~~server configuration and server settings file~~ Not Needed
* ~~server event and alarm logs~~ Not Needed
* ~~Server certificate and key for encryption~~ (removed implementatiuon of server encryption as it current SSL key generation does not meet security criteria, Not Needed)
* Light tower settings
* User level Restrictions settings
* User password change settings
* Light Tower input that correspond with device mode
* Re-configure pyqt signals data flow foir better efficiency
* 

                                                                                                                               
                                                                                                                                
Tested clients: uaexpert

To DO:

* ~~Integrate with new ui file~~ Done
* Server logs export to CSV/TXT
* ~~Integration with PyQt5 HMI~~ Done
* ~~Require server certificate to start connection with OPC server.~~ Not needed
* Client logs export to CSV/TXT
* ~~event and alarm logs (moved from server side to client side)~~ Done
* ~~Server events/methods~~ Not needed
* 
* ~~Mean Time Between Failure (MTBF) calculation using server method~~
* ~~Mean Time Between Action (MTBF) calculation using server method~~
* Alarm list which user can choose if a certain alarm causes soft jam (software jam) or hard jam (hardware jam)
* MTBF and MTBA calculation as perusing soft jam and hard jam counting for the day.
* ~~Unit per Hour (UPH) calculation using server method~~ Done
* Manual input of motor for PLC Motion Card
