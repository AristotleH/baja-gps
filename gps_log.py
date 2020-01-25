import pynmea2
import serial
import time
from datetime import datetime

#establish connection with serial input
uartSerial = serial.Serial("/dev/ttyS0", 9600, timeout=1)

#get current time and generate file name
current = datetime.now()
fileName = "/home/pi/GPS/" + current.strftime("%Y-%m-%d_%H-%M-%S_gpsLog.txt")

#create file and write the logging start time to file
log = open(fileName, "a+")
log.write("START_LOG: " + current.strftime("%Y-%m-%d_%H-%M-%S"))

while True:
    try:
        #read a line of data from the serial input
        data = uartSerial.readline()

        #if the string of data containing gps data is found
        if data.find(b"GGA") > 0:
            #parse the byte type as a string into gps data variables
            gps = pynmea2.parse(data.decode("utf-8"))

            gpsParsed = "LAT: " + str(gps.latitude) + ", LON: " + str(gps.longitude)
            gpsParsed += str(gps.altitude) + " " + str(gps.altitude_units)
            #print the data
            print(gpsParsed)

            #write the data to the file
            log.write(gpsParsed + "\n")
            time.sleep(1)
    #when ctrl-c is pressed
    except KeyboardInterrupt:
        #get current time, write logging end time, and stop script
        log.write("END_LOG: " + current.strftime("%Y-%m-%d_%H-%M-%S"))
        print("\nStopping script!")
        exit()