import serial

ser = serial.Serial('COM9', '57600', timeout=2)
#ser.write('your command\r\n'.encode('ascii'))  # convert to ASCII before sending it
buf = ser.read(200)  # read 100 bytes

print(buf)