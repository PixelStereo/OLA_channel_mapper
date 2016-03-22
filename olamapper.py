#!/usr/bin/env python
# coding=utf-8

"""
ola channel mapper.

    read a configuration file and map channels from one universe to a second.

    history:
        see git commits

    todo:
        ~ all fine :-)
"""


import sys
import os
import array

from configdict import ConfigDict
from olathreaded import OLAThread, OLAThread_States


version = """08.03.2016 12:30 stefan"""


##########################################
# globals


##########################################
# functions


##########################################
# classes


class OLAMapper(OLAThread):
    """Class that extends on OLAThread and implements the Mapper functions."""

    def __init__(self, config):
        """init mapper things."""
        # super(OLAThread, self).__init__()
        OLAThread.__init__(self)

        self.config = config
        # print("config: {}".format(self.config))

        self.universe = self.config['universe']['output']
        # self.channel_count = 512
        # self.channel_count = 50
        self.channel_count = self.config['universe']['channel_count']
        self.channels_out = array.array('B')

        # self.channels = []
        for channel_index in range(0, self.channel_count):
            self.channels_out.append(0)

    def ola_connected(self):
        """register receive callback and switch to running mode."""
        self.client.RegisterUniverse(
            self.config['universe']['input'],
            self.client.REGISTER,
            self.dmx_receive_frame
        )
        # python3 syntax
        # super().ola_connected()
        # python2 syntax
        # super(OLAThread, self).ola_connected()
        # explicit call
        OLAThread.ola_connected(self)

    def dmx_receive_frame(self, data):
        """receive one dmx frame."""
        # print(data)
        self.map_channels(data)
        # temp_array = array.array('B')
        # for channel_index in range(0, self.channel_count):
        #     temp_array.append(self.channels[channel_index])

    def map_channels(self, data_input):
        """remap channels according to map tabel."""
        # print("map channels:")
        # print("data_input: {}".format(data_input))
        data_input_length = data_input.buffer_info()[1]
        # print("data_input_length: {}".format(data_input_length))
        # print("map: {}".format(self.config['map']))

        map = self.config['map']

        data_output = array.array('B')

        # for channel_index in range(0, data_input_length):
        #     data_output.append(data_input[channel_index])
        channel_output_count_temp = len(map['channels'])
        if map['repeat'] is True:
            channel_output_count_temp = self.channel_count
        elif isinstance(map['repeat'], int):
            channel_output_count_temp = self.channel_count

        for channel_output_index in range(0, channel_output_count_temp):
            # calculate map_index
            map_index = channel_output_index % len(map['channels'])
            # print("map_index: {}".format(map_index))

            # get map channel
            map_value = map['channels'][map_index]
            if map['repeat'] and map['offset']:
                loop_index = channel_output_index // len(map['channels'])
                if isinstance(map['repeat'], int) and map['repeat_reverse']:
                    map_value = map_value + (
                        ((map['repeat']-1) - loop_index) *
                        map['offset_count']
                    )
                else:
                    map_value = map_value + (loop_index * map['offset_count'])
            # print("map_value: {}".format(map_value))

            # check if map_value is in range of input channels
            if map_value < data_input_length:
                try:
                    self.channels_out[channel_output_index] = (
                        data_input[map_value]
                    )
                except Exception as e:
                    raise
                    print(
                        (
                            "additional info:\n" +
                            "  channel_output_index: {}\n" +
                            "  map_value: {}\n"
                        ).format(
                            channel_output_index,
                            map_value
                        )
                    )
            else:
                # don't alter data
                pass

        self.dmx_send_frame(
            self.config['universe']['output'],
            self.channels_out
        )


##########################################
if __name__ == '__main__':

    print(42*'*')
    print('Python Version: ' + sys.version)
    print(42*'*')
    print(__doc__)
    print(42*'*')

    # parse arguments
    filename = "map.json"
    # only use args after script name
    arg = sys.argv[1:]
    if not arg:
        print("using standard values.")
        print(" Allowed parameters:")
        print("   filename for config file       (default='map.json')")
        print("")
    else:
        filename = arg[0]
        # if len(arg) > 1:
        #     pixel_count = int(arg[1])
    # print parsed argument values
    print('''values:
        filename :{}
    '''.format(filename))

    default_config = {
        'universe': {
            'input': 1,
            'output': 2,
            'channel_count': 300,
        },
        'map': {
            'channels': [
                -1,
                -1,
                -1,
                -1,
                30,
                31,
                -1,
                -1,
                -1,
                -1,
                22,
                23,
                -1,
                -1,
                -1,
                -1,
                14,
                15,
                -1,
                -1,
                -1,
                -1,
                6,
                7,
                28,
                29,
                26,
                27,
                24,
                25,
                20,
                21,
                18,
                19,
                16,
                17,
                12,
                13,
                10,
                11,
                8,
                9,
                4,
                5,
                2,
                3,
                0,
                1,
            ],
            'repeat': 5,
            'repeat_reverse': True,
            'offset': True,
            'offset_count': 32,
        },
    }
    my_config = ConfigDict(default_config, filename)
    print("my_config.config: {}".format(my_config.config))

    my_mapper = OLAMapper(my_config.config)

    my_mapper.start_ola()

    # wait for user to hit key.
    try:
        raw_input(
            "\n\n" +
            42*'*' +
            "\nhit a key to stop the mapper\n" +
            42*'*' +
            "\n\n"
        )
    except KeyboardInterrupt:
        print("\nstop.")
    except:
        print("\nstop.")

    # blocks untill thread has joined.
    my_mapper.stop_ola()

    # as last thing we save the current configuration.
    print("\nwrite config.")
    my_config.write_to_file()

    # ###########################################
