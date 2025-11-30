""" Test sending sample flight data for visualization purposes, flight data is in .csv format in Utilties directory """
import time
import random
import shutil
import numpy as np
import pandas as pd
from pathlib import Path
from Utilities.serial_test import SerialTest

class messageStruct:

    alt = 0
    Vx = 0
    Vy = 0
    Vz = 0
    velocity = 0
    roll = 0
    pitch = 0
    yaw = 0
    temp = 0
    vertAng = 0
    latAng = 0
    pressure = 0
    batt = 0

    def __init__(self, alt, Vx, Vy, Vz, velocity, roll, pitch, yaw, temp, vertAng, latAng, pressure, batt):
        
        self.alt = alt
        self.Vx = Vx
        self.Vy = Vy
        self.Vz = Vz
        self.velocity = velocity
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.temp = temp
        self.vertAng = vertAng
        self.latAng = latAng
        self.pressure = pressure
        self.batt = batt

def initMessages(data):
    resultData = []
    for i, row in data.iterrows():
        # print(row.keys())
        message = messageStruct(
            row['Altitude (m)'],
            row['Velocity X (m/s)'],
            row['Velocity Y (m/s)'],
            row['Velocity Z (m/s)'],
            row['Total velocity (m/s)'],
            row['Roll rate (°/s)'],
            row['Angle of attack (°)'],
            row['Yaw rate (°/s)'],
            row['Air temperature (°C)'],
            row['Vertical orientation (zenith) (°)'],
            row['Lateral orientation (azimuth) (°)'],
            row['Air pressure (mbar)'],
            row['Battery']
        )
        resultData.append(message)
    
    return resultData

def high_freq_send(device, ser, freq, messages, duration = 5):
    '''Send messages at a high frequency over the serial connection.'''
    period = 1/freq
    print(f"======Sending messages at {freq} Hz. Press Ctrl+C to stop.======")

    try:
        count = 14  #number of values in each message
        start_time = time.time()
        next_time = time.perf_counter()
        for message in messages:
            
            signal = str(message.Vx) + "," + str(message.Vy) + "," + str(message.Vz) + "," + str(message.roll) + "," + str(message.pitch) + "," + str(message.yaw) + "," + str(message.pressure) + "," + str(message.alt) + "," + str(0) + "," + str(message.vertAng) + "," + str(message.velocity) + "," + str(message.temp) + "," + str(0) + "," + str(message.batt)

            print(signal)

            device.send_message(ser, signal)
            
            delay = next_time - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            else:
                next_time = time.perf_counter()

    except KeyboardInterrupt:
        print(f"\nHigh frequency sending terminated.")

def initData():
    df = pd.read_csv("Tests/Utilities/SampleFlightData.csv")

    v_total = df['Total velocity (m/s)']
    zenith_rad = np.deg2rad(df['Vertical orientation (zenith) (°)'])
    azimuth_rad = np.deg2rad(df['Lateral orientation (azimuth) (°)'])

    df['Velocity X (m/s)'] = v_total * np.sin(zenith_rad) * np.sin(azimuth_rad)
    df['Velocity Y (m/s)'] = v_total * np.sin(zenith_rad) * np.cos(azimuth_rad)
    df['Velocity Z (m/s)'] = v_total * np.cos(zenith_rad)

    return df


if __name__ == "__main__":
    data = initData()
    messages = initMessages(data)

    device1 = SerialTest("/dev/cu.+", 57600)
    device1.print_desired_devices()

    ser_obj1 = device1.try_open_port("/dev/cu.usbserial-BG013W95") #change this line to change sending device   

    high_freq_send(device1, ser_obj1, 10, messages)