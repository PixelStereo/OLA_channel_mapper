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
import time
import json
import array

from olathreaded import OLAThread, OLAThread_States


version = """08.03.2016 12:30 stefan"""


##########################################
# globals


##########################################
# functions


def get_unused_universes(state, universe_list):
    """fill global_universe_list with unused universes."""
    print("fill_universe_list:")
    # print("state {}".format(state))
    # print("universe_list {}".format(universe_list))
    global global_universe_list
    global global_flag_got_universes
    for universe in universe_list:
        # check if this universe has no input_port patched.
        if len(universe.input_ports) == 0:
            # if no input_port than add it to list.
            # print("u{} input_ports: {}".format(
            #     universe.id,
            #     universe.input_ports
            # ))
            global_universe_list.append(universe.id)
    print("global_universe_list: {}".format(global_universe_list))
    global_flag_got_universes = True
    wrapper.Stop()

##########################################
# classes


class Mapper(OLAThread):
    """Class that extends on OLAThread and implements the Mapper functions."""

    def __init__(self, config):
        """init mapper things."""
        # super(OLAThread, self).__init__()
        OLAThread.__init__(self)

        self.config = config
        # print("config: {}".format(self.config))

        self.universe = self.config['universe']['output']
        # self.channel_count = 512
        self.channel_count = 50
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
        if map['repeat']:
            channel_output_count_temp = self.channel_count

        for channel_output_index in range(0, channel_output_count_temp):
            # calculate map_index
            map_index = channel_output_index % len(map['channels'])
            # print("map_index: {}".format(map_index))

            # get map channel
            map_value = map['channels'][map_index]
            if map['repeat'] and map['offset']:
                loop_index = channel_output_index // len(map['channels'])
                map_value = map_value + (loop_index * map['offset_count'])
            # print("map_value: {}".format(map_value))

            # check if map_value is in range of input channels
            if map_value < data_input_length:
                self.channels_out[channel_output_index] = data_input[map_value]
            else:
                # don't alter data
                pass

        self.dmx_send_frame(
            self.config['universe']['output'],
            self.channels_out
        )


class MapConfig():
    """abstract the reading / writing of configuration parameters."""

    default_config = {
        'universe': {
            'input': 1,
            'output': 2,
        },
        'map': {
            'channels': [0, 1, 2, 3, 4, 4, 3, 2, 1, 0, ],
            'repeat': True,
            'offset': True,
            'offset_count': 5,
        },
    }

    def __init__(self, filename=None):
        """initialize config to defaults."""
        self.filename = filename
        self.config = {}
        if self.filename is not None:
            if os.path.isfile(filename):
                self.read_from_file()
            else:
                self.config = self.default_config.copy()
                self.write_to_file()
        else:
            self.config = self.default_config.copy()

    def merge_deep(self, obj_1, obj_2):
        """
        merge dicts deeply.

        obj_2 overwrittes keys with same values in obj_1.
        (if they are dicts its recusive merged.)
        """
        # work on obj_1
        result = obj_1
        # make copy
        # result = obj_1.copy()
        if (isinstance(result, dict) and isinstance(obj_2, dict)):
            for key in obj_2:
                if key in result:
                    result[key] = self.merge_deep(result[key], obj_2[key])
                else:
                    result[key] = obj_2[key]
        else:
            result = obj_2
        return result

    def set_filename(self, filename):
        """set new filename."""
        self.filename = filename

    def read_from_file(self, filename=None):
        """read configuration from file."""
        if filename is not None:
            self.filename = filename
        config_temp = {}
        with open(self.filename, 'r') as f:
            config_temp = json.load(f)
            f.closed
        # do a merge with the defaults.
        self.config = self.default_config.copy()
        self.merge_deep(self.config, config_temp)

    def write_to_file(self, filename=None):
        """write configuration to file."""
        if filename is not None:
            self.filename = filename
        if self.filename is not None:
            print("\nwrite file: {}".format(self.filename))
            with open(self.filename, 'w') as f:
                json.dump(
                    self.config,
                    f,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
                f.closed

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

    my_config = MapConfig(filename)
    print("my_config.config: {}".format(my_config.config))

    my_mapper = Mapper(my_config.config)

    my_mapper.start_ola()

    # wait for user to hit key.
    try:
        input(
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
