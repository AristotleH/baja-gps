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

    fol = doc.newfolder(name='Tracks')
    trk = fol.newgxtrack(name=current.strftime("%Y-%m-%d_%H-%M-%S"))

    #from simplekml documentation
    trk.stylemap.normalstyle.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
    trk.stylemap.normalstyle.linestyle.color = '99ffac59'
    trk.stylemap.normalstyle.linestyle.width = 6
    trk.stylemap.highlightstyle.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
    trk.stylemap.highlightstyle.iconstyle.scale = 1.2
    trk.stylemap.highlightstyle.linestyle.color = '99ffac59'
    trk.stylemap.highlightstyle.linestyle.width = 8

    while True:
        try:
            #read a line of data from the serial input
            data = uartSerial.readline()

            #if the string of data containing gps data is found
            if data.find(b"GGA") > 0:
                #parse the byte type as a string into gps data variables
                gps = pynmea2.parse(data.decode("utf-8"))

                gpsParsed = "LAT: " + str(gps.latitude) + ", LON: " + str(gps.longitude)
                gpsParsed += ", ALT: " + str(gps.altitude) + " " + str(gps.altitude_units)
                #print the data
                print(gpsParsed)

                current = datetime.utcnow()
                now = current.strftime("%Y-%m-%dT%H:%M:%SZ")

                #save point to kml object
                if (float(gps.latitude) != 0):
                    log.write(gpsParsed + "\n")
                    coordTuple = (float(gps.latitude), float(gps.longitude), float(gps.altitude))
                    trk.newgxcoord(coordTuple)
                    trk.newwhen(now)
                    kml.save(fileName + ".kml")

                #write the data to the file
                time.sleep(0.1)

        #when ctrl-c is pressed
        except KeyboardInterrupt:
            trk.newwhen(all_times)
            trk.newgxcoord(all_coords)

            #get current time, write logging end time, and stop script
            log.write("END_LOG: " + current.strftime("%Y-%m-%d_%H-%M-%S"))
            print("\nStopping script!")
            exit()