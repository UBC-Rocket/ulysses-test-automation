""" The sender program for sending messages at a high frequency """
import time
import random
import shutil
from pathlib import Path
from Utilities.serial_test import SerialTest

def generate_message(count):
    message = ','.join(str(round(random.uniform(0, 361), 2)) for _ in range(count)) + '\r\n'
    return message

def high_freq_send(device, ser, freq):
    '''Send messages at a high frequency over the serial connection.'''
    period = 1/freq
    print(f"======Sending messages at {freq} Hz. Press Ctrl+C to stop.======")

    try:
        count = 14  #number of values in each message
        next_time = time.perf_counter()
        while True:
            # Calculate the next send time
            next_time += period

            message = generate_message(count)
            device.send_message(ser, message)
            #print(message)
            #count += 1
            
            delay = next_time - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            else:
                next_time = time.perf_counter()

    except KeyboardInterrupt:
        print(f"\nHigh frequency sending terminated.")

if __name__ == "__main__":
    device1 = SerialTest("/dev/cu.+", 57600)
    #device1.print_desired_devices()


    ser_obj1 = device1.try_open_port("/dev/cu.usbserial-BG013W95") #change this line to change sending device
    
    #delete everything in the log folder at the beginning of the test
    project_root = Path(__file__).resolve().parent.parent
    folder_location = project_root / "logs" #logs folder in project root
        
    if folder_location.is_dir():
        shutil.rmtree(folder_location)

    high_freq_send(device1, ser_obj1, 10) # edit the last parameter to change the sending frequency
    device1.close_port(ser_obj1)
        
    
