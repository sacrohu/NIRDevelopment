import serial.tools.list_ports
import numpy as np
import json
import sys

# detection NIR spectrum by AS7263
try:
    print("start serial port")
    ser = serial.Serial("COM7", 115200, timeout=1)  # BauteRate 115200, serial port COM7
    print("serial port parameters：", ser)
    if not ser.is_open:
        print("fail to open serial port")
        sys.exit()
    print("success to open serial port")

    print("\nbegin to generate NIR dectection refence library")
    input("\nstart to detect the reference light ")
    serialcmd = sys.argv[1] + "\r\n"  # ATBURST = 10 , detect the NIR data for 10 times continuously
    result = ser.write(serialcmd.encode("ascii"))  # send AT command to serial ASCII string
    resultcmd = ser.readline().decode("ascii").replace("\n", "")  # read AT command result as ASCII string
    # print("AT command of NIR detection:", serialcmd.replace("\r\n", ""), resultcmd)
    irvalues = np.zeros((10, 6), np.float)  # store the NIR detection data
    iloop = 0
    while len(resultcmd) > 0:
        resultcmd = ser.readline().decode("ascii").replace("\n", "")  # read AT command result as ASCII string
        # print("AT command of NIR detection result:", resultcmd, "\n")
        if len(resultcmd) > 0:
            tmpvalue = list(map(int, resultcmd.split(', ')))    # Convert the ASCII string to a numeric sequence
            irvalues[iloop, :] = np.array(tmpvalue, dtype=float)
            iloop = iloop + 1
    irvalue0 = np.mean(irvalues, axis=0)  # get the mean value of NIR datas
    print("the measurement result of the reference NIR " + str(iloop) + "times:\n\t" + str(irvalue0))
    print("\nopen the nirdata file")
    firdata = open("nirdata.txt", "wt")  # store measurement into the local data file
    np.set_printoptions(precision=2)     # display the data format 0.02
    measuredata, irname, irmeasurement = [], [], np.array([])
    mloop = 0
    while True:
        nameinput = input("start to detect the sample name of library: ")
        if nameinput == "n":  # finish the NIR library and do the next step
            break
        serialcmd = sys.argv[1] + "\r\n"    # ATBURST = 10 , detect the NIR data for 10 times continuously
        result = ser.write(serialcmd.encode("ascii"))  # read AT command result as ASCII string
        resultcmd = ser.readline().decode("ascii").replace("\n", "")
        # print("NIR detection AT command and result: ", serialcmd.replace("\r\n", ""), resultcmd)
        irvalues = np.zeros((10, 6), np.float)
        iloop = 0
        while len(resultcmd) > 0:
            resultcmd = ser.readline().decode("ascii").replace("\n", "")   # read AT command result as ASCII string
            # print("AT command of NIR detection result:", resultcmd, "\n")
            if len(resultcmd) > 0:
                tmpvalue = list(map(int, resultcmd.split(', ')))    # Convert the ASCII string to a numeric sequence
                irvalues[iloop, :] = np.array(tmpvalue, dtype=float)
                iloop = iloop + 1
        irvalue1 = np.mean(irvalues, axis=0)  # get the mean value of NIR datas
        irvaluee = np.subtract(irvalue0, irvalue1)
        if np.sum(np.power(irvaluee, 2)) < 600:
            print("the measurement result of the library NIR: background light")
        else:
            irname.append(nameinput)
            tmpnparray = np.around(np.array(irvaluee))
            if mloop == 0:
                irmeasurement = tmpnparray
            else:
                irmeasurement = np.vstack([irmeasurement, tmpnparray])
            measuredata.append({"name": nameinput, "irdata": tmpnparray.tolist()})
            mloop = mloop + 1
            print("the sample name: " + nameinput + " - the measurement result of the library NIR:\n\t" + str(irvaluee))
    json.dump(measuredata, firdata)
    firdata.close()
    print("close the nirdata library file")
    print("the library NIR's information:\nname\tirdata")
    for data in measuredata:
        # print(data)
        print(data['name'], "\t", data['irdata'])
    print(irname)
    print(np.corrcoef(irmeasurement))

    print("\nbegin to detect the unknown object by the library NIR")
    todo = input("\ndetect the unknown object by the library NIR(?/n): ")
    while todo != "n":
        serialcmd = sys.argv[1] + "\r\n"    # ATBURST = 10 , detect the NIR data for 10 times continuously
        result = ser.write(serialcmd.encode("ascii"))  # read AT command result as ASCII string
        resultcmd = ser.readline().decode("ascii").replace("\n", "")
        # print("NIR detection AT command and result: ", serialcmd.replace("\r\n", ""), resultcmd)
        irvalues = np.zeros((10, 6), np.float)
        iloop = 0
        while len(resultcmd) > 0:
            resultcmd = ser.readline().decode("ascii").replace("\n", "")   # read AT command result as ASCII string
            # print("AT command of NIR detection result:", resultcmd, "\n")
            if len(resultcmd) > 0:
                tmpvalue = list(map(int, resultcmd.split(', ')))    # Convert the ASCII string to a numeric sequence
                irvalues[iloop, :] = np.array(tmpvalue, dtype=float)
                iloop = iloop + 1
        irvalue1 = np.mean(irvalues, axis=0)  # get the mean value of NIR datas
        irvaluee = np.subtract(irvalue0, irvalue1)
        if np.sum(np.power(irvaluee, 2)) < 600:
            print("the measurement result of the library NIR: background light")
        else:
            tmpirmeasurement = np.vstack([irmeasurement, np.around(np.array(irvaluee))])
            deResult = np.corrcoef(tmpirmeasurement)[mloop, :mloop]
            print("the NIR detection result of the unknown NIR object by the library NIR")
            print(irname)
            print(deResult)
            print("the unknown object is most like -", irname[np.argmax(deResult, axis=0)])
        todo = input("\ndetect the unknown object by the library NIR(?/n): ")

    ser.close()
    print("stop serial port")
except Exception as e:
    print("serial port unexception -", e)
