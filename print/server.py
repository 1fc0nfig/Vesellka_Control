# Python script that listen for incoming serial data and executes the image.py script
# Path: print/server.py
# Compare this snippet from print/image.py:

import serial
import os
import time
import argparse

# create argument parser
parser = argparse.ArgumentParser()
# add argument for serial port
parser.add_argument("-p", "--port", help="Serial port, 'ls /dev/tty*' on UNIX based systems", required=True)
parser.add_argument("-b", "--baud", help="Baud rate, default: 9600", default=9600)

last_track = None

# parse arguments
args = parser.parse_args()

# try to open serial port
try:
    serial = serial.Serial(args.port, args.baud, timeout=1)
    print("Serial port opened: " + args.port)
    print("Baud rate: " + str(args.baud))
    start = time.time()
# if serial port cannot be opened
except serial.SerialException as e:
    # print error message
    print("Error: Serial port cannot be opened")
    print(str(e))
    # exit script
    exit()

# listen for incoming serial data
while True:
    try:
      # read serial port
      data = serial.readline()
      # convert from binary array to string
      data = data.decode("utf-8")
      # remove line break
      data = data.rstrip()
      # check if data is equal to "print"
      # check if 5 seconds have passed since last print
      if data == "print" and time.time() - start > 5 and last_track != None:
          # start timer
          start = time.time()
          # execute image.py script
          print("Executing image.py")
          try:
            # TODO Print track specific image
            # Execute the command and capture the output
            output = os.popen('python3 image.py').read()
            print(output)
            print("––––––––")
          except:
            print("Error: image.py cannot be executed")
            pass
      if "TRACK" in data and time.time() - start > 5:
          last_track = data
          print(data)
          
    except KeyboardInterrupt:
        print("Exiting...")
        serial.close()
        exit()
