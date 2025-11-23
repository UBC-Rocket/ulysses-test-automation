""" General receiving program """

from Utilities.serial_test import SerialTest

if __name__ == "__main__":
    device1 = SerialTest("/dev/cu\.usbserial-.+", 57600)
    device1.print_desired_devices()
    ser_obj1 = device1.try_open_port("/dev/cu.usbserial-ABSCDQOT")

    device1.receive_message(ser_obj1)

