'''Serial communication test module. Includes functionalities for listing ports, opening/closing ports,
sending/receiving messages, and logging sent/received messages to NDJSON files.'''

import serial
import serial.tools.list_ports
import re
import time
import json
from collections import deque
import threading
from pathlib import Path

class SerialTest:
    '''Class for serial communication tests.'''
    def __init__(self, standard_name_pattern, baud, timeout = 1.0):
        self.standard_name_pattern = standard_name_pattern
        self.baud = baud
        self.timeout = timeout
        #for json use
        self._log_buffer = deque()
        self._last_flush_time = time.perf_counter()
        self._batch_size = 100 #number of messages to batch before writing to file
        self._max_interval = 0.5  # seconds
        self.stop_event = threading.Event() #used for terminate receiving externally


    def _log_message(self, log_path, message):
        '''Log message to NDJSON file with batching.'''
        '''Creates a folder named "logs" in the root folder'''

        project_root = Path(__file__).resolve().parent.parent
        folder_location = project_root / "logs" #logs folder in project root

        folder_location.mkdir(parents=True, exist_ok=True) #ensure logs directory exists
        file = folder_location / log_path #use logs directory
        entry = {
            "time": time.perf_counter(), #timestamp in seconds
            "message": message #the raw message
        }

        self._log_buffer.append(json.dumps(entry))
        #flush buffer to file if batch size or time interval exceeded
        now = time.perf_counter()
        if(len(self._log_buffer) >= self._batch_size) or (now - self._last_flush_time) >= self._max_interval:
            with open(file, "a") as f:
                f.write("\n".join(self._log_buffer) + "\n")
            self._log_buffer.clear()
            self._last_flush_time = now


    def list_serial_ports(self):
        '''List all available serial ports.'''
        ports = serial.tools.list_ports.comports() #get a list of all available ports
        result = [] #list to hold port names
        for port in ports:
            #use .device to get the port name
            result.append(port.device)
        return result
    

    def print_available_ports(self):
        '''Print all available serial ports.'''
        ports = self.list_serial_ports() #get available ports
        if ports:
            print("\nAvailable serial ports:")
            for port in ports:
                print(f" - {port}")
        else:
            print("No serial ports found.")
    

    def find_desired_devices(self):
        '''Find desired devices connected to the system by filtering standard names.'''
        ports = self.list_serial_ports()
        desired_devices = [] #list to hold desired devices
        #standard names for desired devices
        text = self.standard_name_pattern
        for port in ports:
            if re.fullmatch(text, port):
                desired_devices.append(port)
        return desired_devices


    def print_desired_devices(self):
        '''Print desired devices found.'''
        desired_devices = self.find_desired_devices()
        if desired_devices:
            print("\nFound desired devices:")
            for device in desired_devices:
                print(f" - {device}")
        else:
            print("\nNo desired devices found.")


    def try_open_port(self, device):
        """
        Try opening the candidate port with given settings.
        Return a serial object for ones that succeeded.
        Return None if failed.
        """
        opened = {}
        try:
            # Set up serial connection with specified parameters
            ser = serial.Serial(
                port = device,
                baudrate = self.baud,
                timeout = self.timeout,
                bytesize = serial.EIGHTBITS,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                xonxoff = False,
                rtscts = False,
                dsrdtr = False
            )
            if ser.is_open:
                opened[device] = ser
                print(f"Opened port {device} at {self.baud} baud.")
                return opened[device] #return the serial object
            else:
                ser.close()
                print(f"Failed to open port {device}.")
                return None #return None if failed
        except serial.SerialException as e:
            print(f"Error opening port {device}: {e}")
            return None
        
    
    def close_port(self, ser):
        """Close the given serial connection."""
        try:
            if ser.is_open:
                ser.close() #close the port
                print(f"Closed port {ser.port}.")
            else:
                print(f"Port {ser.port} is already closed.")
        except Exception as e:
            print(f"Error closing port: {e}")


    def send_message(self, ser, message):
        '''Send a message through the serial connection.
        Make sure the message ends with \r\n
        Make sure the devices has quitted the AT mode before sending messages.'''

        log_path = "sent_messages.ndjson" #adjust this line to change log file name for sent messages
        try:
            ser.reset_input_buffer() #clear input buffer before sending
            ser.reset_output_buffer() #clear output buffer before sending
            ser.write(message.encode()) # make sure the message is in bytes
            ser.flush()
            #time.sleep(0.5) # wait for the message to be sent. Comment out if needed (e.g. for high freq. sending).
            print("Message sent.")

            self._log_message(log_path, message) #log the sent message

        except Exception as e:
            print(f"Error sending message: {e}")


    def receive_message(self, ser):
        """Receive messages from the serial connection.
            Log the raw messages into a NDJSON file.
            The serial connection will be closed by the program when done.
            This method terminates receiving by keyboard interrupt instead of
            external code."""
        try:
            try:
                log_path = "received_messages.ndjson" #adjust this line to change log file name for received messages
                print(f"Waiting to receive message... Press Ctrl+C to stop.")
                while True:
                    data_in_waiting = ser.in_waiting
                    if data_in_waiting > 0:

                        #receive_time = time.perf_counter() #for measuring elapsed time of the program, mainly used when measuring delay. Comment out if not needed.
                        
                        message = ser.readline()
                        if not message:
                            continue

                        print(f"\nReceived raw message: ", message) #raw messages are in bytes

                        # Decode and print the message
                        message = message.decode('utf-8', errors='ignore')
                        self._log_message(log_path, message) #log the raw message into a ndjson file

                        #logged_time = time.perf_counter() #for measuring elapsed time of the program, comment out during real test.
                        #elapsed_time = logged_time - receive_time

                        print(f"Decoded message: {message}")
                        #print(f"Elapsed time to log message: {elapsed_time} seconds")

                    #time.sleep(0.01)  # Small delay to prevent high CPU usage

            except KeyboardInterrupt:
                print(f"Reception interrupted by user.") #pause receiving when pressed control+C
            
            finally:
                ser.close()
                print(f"Serial connection closed.") #close the serial connection when done

        except Exception as e:
            print(f"Error receiving message: {e}")


    def receive_message_et(self, ser):
        """Receive messages from the serial connection.
            Log the raw messages into a NDJSON file.
            The serial connection will be closed by the program when done.
            This method terminates the receiving process by external programs
            instead of keyboard termination."""
        try:
            log_path = "received_messages.ndjson" #adjust this line to change log file name for received messages
            print(f"Waiting to receive message...")

            while not self.stop_event.is_set():
                data_in_waiting = ser.in_waiting
                if data_in_waiting > 0:

                    #receive_time = time.perf_counter() #for measuring elapsed time of the program, mainly used when measuring delay. Comment out if not needed.
                        
                    message = ser.readline()
                    if not message:
                        continue

                    print(f"\nReceived raw message: ", message) #raw messages are in bytes

                    # Decode and print the message
                    message = message.decode('utf-8', errors='ignore')
                    self._log_message(log_path, message) #log the raw message into a ndjson file

                    #logged_time = time.perf_counter() #for measuring elapsed time of the program, comment out during real test.
                    #elapsed_time = logged_time - receive_time

                    print(f"Decoded message: {message}")
                    #print(f"Elapsed time to log message: {elapsed_time} seconds")

                #time.sleep(0.01)  # Small delay to prevent high CPU usage

        except Exception as e:
            print(f"Error receiving message: {e}")

        finally:
            ser.close()
            print(f"Serial connection closed.") #close the serial connection when done

    def stop_receiving(self):
        """Stop the receive loop"""
        self.stop_event.set()


"""
'''========== example of how we can use the SerialTest class =========='''

if __name__ == "__main__":
    device1 = SerialTest("/dev/cu.+", 57600) #adjust the standard name pattern and baud rate as needed
    device1.print_desired_devices() #print found desired devices

    device2 = SerialTest("/dev/cu\.usbserial-.+", 57600)
    device2.print_desired_devices()

    ser_obj1 = device1.try_open_port("/dev/cu.usbserial-ABSCDQOT") #select the desired device port according to their name pattern being printed out eariler
    ser_obj2 = device2.try_open_port("/dev/cu.usbserial-BG005USC")

    device1.send_message(ser_obj1, "how are you?\r\n") #send a test message. Put the object generated by the try_open_port function as a parameter here.
    device2.receive_message(ser_obj2)
    device1.close_port(ser_obj1) #close the port when done

====== Example of using receive_message_et to stop receiving by code ======
    # Run receive loop in a separate thread
    recv_thread = threading.Thread(target=device1.receive_message_et, args=(ser_obj1,))
    recv_thread.start()

    --- Do other works ---

    # Stop receiving
    device1.stop_receiving()
    recv_thread.join()
    print("Receiver stopped fully")

"""