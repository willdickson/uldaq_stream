#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Wrapper call demonstrated:        ai_device.a_in_scan()

Purpose:                          Performs a continuous scan of the range
                                  of A/D input channels

Demonstration:                    Displays the analog input data for the
                                  range of user-specified channels using
                                  the first supported range and input mode

Steps:
1.  Call get_daq_device_inventory() to get the list of available DAQ devices
2.  Create a DaqDevice object
3.  Call daq_device.get_ai_device() to get the ai_device object for the AI
    subsystem
4.  Verify the ai_device object is valid
5.  Call ai_device.get_info() to get the ai_info object for the AI subsystem
6.  Verify the analog input subsystem has a hardware pacer
7.  Call daq_device.connect() to establish a UL connection to the DAQ device
8.  Call ai_device.a_in_scan() to start the scan of A/D input channels
9.  Call ai_device.get_scan_status() to check the status of the background
    operation
10. Display the data for each channel
11. Call ai_device.scan_stop() to stop the background operation
12. Call daq_device.disconnect() and daq_device.release() before exiting the
    process.
"""
from __future__ import print_function
import signal
from time import sleep
from os import system
from sys import stdout

from uldaq import (get_daq_device_inventory, DaqDevice, AInScanFlag, ScanStatus,
                   ScanOption, create_float_buffer, InterfaceType, AiInputMode)




def main():

    """Analog input scan example."""
    daq_device = None
    ai_device = None
    status = ScanStatus.IDLE
    device_number = 0

    range_index = 0
    interface_type = InterfaceType.ANY
    low_channel = 0
    high_channel = 3
    rate = 20000          # sample rate
    dt = 0.1              # how often save a chunk of data 
    buffer_margin = 20
    samples_per_channel = int(buffer_margin*dt*rate) 
    print(samples_per_channel)
    scan_options = ScanOption.CONTINUOUS
    flags = AInScanFlag.DEFAULT
    datafile = 'data.txt'

    done = False
    def sigint_handler(sig, frame):
        nonlocal done
        done = True
    signal.signal(signal.SIGINT,sigint_handler)

    try:
        # Get descriptors for all of the available DAQ devices.
        devices = get_daq_device_inventory(interface_type)
        number_of_devices = len(devices)
        if number_of_devices == 0:
            raise RuntimeError('Error: No DAQ devices found')
        print('Found', number_of_devices, 'DAQ device(s):')
        print('using device', device_number)
        descriptor_index = device_number
        if descriptor_index not in range(number_of_devices):
            raise RuntimeError('Error: Invalid descriptor index')

        # Create the DAQ device from the descriptor at the specified index.
        daq_device = DaqDevice(devices[descriptor_index])

        # Get the AiDevice object and verify that it is valid.
        ai_device = daq_device.get_ai_device()
        if ai_device is None:
            raise RuntimeError('Error: The DAQ device does not support analog '
                               'input')

        # Verify the specified device supports hardware pacing for analog input.
        ai_info = ai_device.get_info()
        if not ai_info.has_pacer():
            raise RuntimeError('\nError: The specified DAQ device does not '
                               'support hardware paced analog input')

        # Establish a connection to the DAQ device.
        descriptor = daq_device.get_descriptor()
        print('\nConnecting to', descriptor.dev_string, '- please wait...')
        # For Ethernet devices using a connection_code other than the default
        # value of zero, change the line below to enter the desired code.
        try:
            daq_device.connect(connection_code=0)
        except TypeError:
            daq_device.connect()

        # The default input mode is SINGLE_ENDED.
        input_mode = AiInputMode.SINGLE_ENDED
        # If SINGLE_ENDED input mode is not supported, set to DIFFERENTIAL.
        if ai_info.get_num_chans_by_mode(AiInputMode.SINGLE_ENDED) <= 0:
            input_mode = AiInputMode.DIFFERENTIAL

        # Get the number of channels and validate the high channel number.
        number_of_channels = ai_info.get_num_chans_by_mode(input_mode)
        if high_channel >= number_of_channels:
            high_channel = number_of_channels - 1
        channel_count = high_channel - low_channel + 1

        # Get a list of supported ranges and validate the range index.
        ranges = ai_info.get_ranges(input_mode)
        if range_index >= len(ranges):
            range_index = len(ranges) - 1

        # Allocate a buffer to receive the data.0
        data = create_float_buffer(channel_count, samples_per_channel)

        print('\n', descriptor.dev_string, ' ready', sep='')
        print('    Function demonstrated: ai_device.a_in_scan()')
        print('    Channels: ', low_channel, '-', high_channel)
        print('    Input mode: ', input_mode.name)
        print('    Range: ', ranges[range_index].name)
        print('    Samples per channel: ', samples_per_channel)
        print('    Rate: ', rate, 'Hz')
        print('    Scan options:', display_scan_options(scan_options))

        # Start the acquisition.
        rate = ai_device.a_in_scan(
                low_channel, 
                high_channel, 
                input_mode, 
                ranges[range_index], 
                samples_per_channel, 
                rate, 
                scan_options, 
                flags, 
                data
                ) 

        print()
        print('acquiring data ..', end='')
        stdout.flush()

        with open(datafile,'w') as f:

            save_count = 0
            last_save_index = 0
            buffer_size = samples_per_channel*channel_count

            while not done:

                # Get the status of the background operation
                status, transfer_status = ai_device.get_scan_status()
                current_index = transfer_status.current_index
                if current_index < 0:
                    continue
                num_to_save = (current_index - last_save_index)%buffer_size + channel_count

                # Write data to file
                for i in range(num_to_save):
                    if i%channel_count == 0:
                        f.write('{} '.format(save_count))
                        save_count += 1
                    save_index = (last_save_index + i)%buffer_size
                    f.write('{}'.format(data[save_index])) 
                    if i%channel_count == (channel_count-1):
                        f.write('\n')
                    else:
                        f.write(' ')
                last_save_index = (current_index + channel_count)%buffer_size

                sleep(dt)
            print('done')



    except RuntimeError as error:
        print('\n', error)

    finally:
        if daq_device:
            # Stop the acquisition if it is still running.
            if status == ScanStatus.RUNNING:
                ai_device.scan_stop()
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()


def display_scan_options(bit_mask):
    """Create a displays string for all scan options."""
    options = []
    if bit_mask == ScanOption.DEFAULTIO:
        options.append(ScanOption.DEFAULTIO.name)
    for option in ScanOption:
        if option & bit_mask:
            options.append(option.name)
    return ', '.join(options)


def reset_cursor():
    """Reset the cursor in the terminal window."""
    stdout.write('\033[1;1H')


def clear_eol():
    """Clear all characters to the end of the line."""
    stdout.write('\x1b[2K')


if __name__ == '__main__':

    main()
