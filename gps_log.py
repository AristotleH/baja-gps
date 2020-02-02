import pynmea2
import serial
import time
from datetime import datetime
import simplekml

if __name__ == '__main__':
    #establish connection with serial input
    uartSerial = serial.Serial("/dev/ttyS0", 9600, timeout=1)

    #get current time and generate file name
    current = datetime.utcnow()
    fileName = "/home/pi/GPS/" + current.strftime("%Y-%m-%d_%H-%M-%S_gpsLog")

    #create file and write the logging start time to file
    log = open(fileName + ".txt", "a+")
    log.write("START_LOG: " + current.strftime("%Y-%m-%d_%H-%M-%S"))

    #create kml object
    kml = simplekml.Kml(name=current.strftime("%Y-%m-%d_%H-%M-%S_gpsLog"), open=1)
    doc = kml.newdocument(name='baja gps')


    all_coords = []
    all_times = []

    fol = doc.newfolder(name='Tracks')

    while True:
        try:
            #read a line of data from the serial input
            data = uartSerial.readline()

            #if the string of data containing gps data is found
            if data.find(b"GGA") > 0:
                #parse the byte type as a string into gps data variables
                gps = pynmea2.parse(data.decode("utf-8"))

                gpsParsed = "LAT: " + str(gps.latitude) + ", LON: " + str(gps.longitude)
                gpsParsed += "; Alt: " + str(gps.altitude) + " " + str(gps.altitude_units)
                #print the data
                print(gpsParsed)

                current = datetime.utcnow()
                now = current.strftime("%Y-%m-%dT%H:%M:%SZ")

                #save point to kml object
                if (float(gps.latitude) != 0):
                    coordTuple = (float(gps.latitude), float(gps.longitude), float(gps.altitude))
                    log.write(gpsParsed + "\n")
                    all_coords.append( (float(gps.latitude), float(gps.longitude), float(gps.altitude)) )
                    all_times.append(now)

                #write the data to the file
                time.sleep(1)

        #when ctrl-c is pressed
        except KeyboardInterrupt:
            current = datetime.utcnow()
            trk = fol.newgxtrack(name=current.strftime("%Y-%m-%d_%H-%M-%S"))

            trk.newwhen(all_times)
            trk.newgxcoord(all_coords)

            #get current time, write logging end time, and stop script
            log.write("END_LOG: " + current.strftime("%Y-%m-%d_%H-%M-%S"))
            kml.save(fileName + ".kml")
            print("\nStopping script!")
            exit()