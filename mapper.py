#!/usr/bin/env python
# coding=utf-8

"""
ola channel mapper.

    read a inifile for configuration and map acording the file channels from
    one universe to a second.

    history:
        see git commits

    todo:
        ~ all fine :-)
"""


import sys
import time
import ConfigParser
import array
import socket
from ola.ClientWrapper import ClientWrapper
from ola.OlaClient import OLADNotRunningException

version = """07.03.2016 15:00 stefan"""


##########################################
# globals

wrapper = None
client = None

universe = -1
global_universe_list = []
global_flag_got_universes = False

##########################################
# functions


def DmxSent(state):
    """react on ola state."""
    if not state.Succeeded():
        wrapper.Stop()
        print("warning: dmxSent does not Succeeded.")


def SendDMXFrame():
    """send one dmx frame (on multiple universes)."""
    global frame_count
    if (frame_count == -1) or (frame_count > 0):
        if not frame_count == -1:
            frame_count = frame_count - 1

        # schdule a function call in 100ms
        # we do this first in case the frame computation takes a long time.
        wrapper.AddEvent(TICK_INTERVAL, SendDMXFrame)

        # compute frame here
        data = array.array('B')
        global pixel_count
        global strobe_state

        for index_pixel in range(1, pixel_count+1):
            if strobe_state:
                data.append(255)
                data.append(0)
                data.append(255)
            else:
                data.append(0)
                data.append(255)
                data.append(0)
        try:
            if universe == -1:
                # send to universe list
                for uni in global_universe_list:
                    wrapper.Client().SendDmx(uni, data, DmxSent)
            else:
                # send
                wrapper.Client().SendDmx(universe, data, DmxSent)
        except OLADNotRunningException:
            wrapper.Stop()
            print("olad not running anymore.")

        # invert
        if strobe_state:
            strobe_state = False
        else:
            strobe_state = True
    elif frame_count == 0:
        wrapper.Stop()
        print("all frames send.")


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


class OLAThread(threading.Thread):
    """connect to olad in a threaded way."""

    def __init__(self):
        """create new OLAThread instance."""
        super(OLAThread, self).__init__()

        self.flag_connected = False
        self.flag_wait_for_ola = False
        self.wrapper = None
        self.client = None

    def run(self):
        """run thread and connect to ola."""
        self.connect()

    def connect(self):
        """connect to ola."""
        print("waiting for olad....")
        self.flag_connected = False
        self.flag_wait_for_ola = True
        while (not self.flag_connected) & self.flag_wait_for_ola:
            try:
                # print("get wrapper")
                self.wrapper = ClientWrapper()
            except OLADNotRunningException:
                time.sleep(0.5)
            else:
                self.flag_connected = True

        if self.flag_connected:

            self.flag_wait_for_ola = False
            print("get client")
            self.client = self.wrapper.Client()

            print("run ola wrapper.")
            try:
                self.wrapper.Run()
            except KeyboardInterrupt:
                self.wrapper.Stop()
                print("\nstopped")
            except socket.error as error:
                print("connection to OLAD lost:")
                print("   error: " + error.__str__())
                self.flag_connected = False
            # except Exception as error:
            #     print(error)
        else:
            print("\nstopped waiting for olad.")

    def disconnect(self):
        """stop ola wrapper."""
        if self.flag_wait_for_ola:
            print("stop search for ola wrapper.")
            self.flag_wait_for_ola = False
        if self.flag_connected:
            print("stop ola wrapper.")
            self.wrapper.Stop()


class Mapper(OLAThread):
    """Class that extends on OLAThread and implements the Mapper functions."""

    def __init__(self, config):
        """init mapper things."""
        super(OLAThread, self).__init__()

        self.config = config

        # register callback on received dmx data
        self.client.RegisterUniverse(
            config.universe.,
            client.REGISTER,
            dmx_receive_frame
        )

        self.universe = universe
        self.channel_count = 512
        self.channels = {
            'in': array.array('B'),
            'out': array.array('B'),
        }

        # self.channels = []
        # for channel_index in range(0, self.channel_count):
        #     self.channels.append(0)

    def map_channels(self):
        """remap channels according to map tabel."""
        # temp_array = array.array('B')
        # for channel_index in range(0, self.channel_count):
        #     temp_array.append(self.channels[channel_index])
        # dmx_send_frame()
        pass

    def dmx_receive_frame(self, data):
        """receive one dmx frame."""
        print(data)
        # self.map_channels(data)
        # temp_array = array.array('B')
        # for channel_index in range(0, self.channel_count):
        #     temp_array.append(self.channels[channel_index])

    def dmx_send_frame(self):
        """send data as one dmx frame."""
        if self.flag_connected:
            try:
                temp_array = array.array('B')
                for channel_index in range(0, self.channel_count):
                    temp_array.append(self.channels[channel_index])

                # print("temp_array:{}".format(temp_array))
                # print("send frame..")
                self.wrapper.Client().SendDmx(
                    self.universe.out,
                    # self.channels,
                    temp_array,
                    self.dmx_send_callback
                )
                # print("done.")
            except OLADNotRunningException:
                self.wrapper.Stop()
                print("olad not running anymore.")
        else:
            # throw error
            pass

    def dmx_send_callback(self, state):
        """react on ola state."""
        if not state.Succeeded():
            self.wrapper.Stop()
            print("warning: dmxSent does not Succeeded.")
        else:
            print("send frame succeeded.")


class MapConfig():
    """abstract the reading / writing of configuration parameters."""

    self.default_config = {
        'universe': {
            'in': 0,
            'out': 0,
        },
        'map': {
            'channels': [],
            'repeate': False,
        },
    }

    def __init__(self, filename=None):
        """initialize config to defaults."""
        self.filename = filename
        if self.filename is not None:
            if os.path.isfile(filename):
                read_from_file()
            else:
                write_to_file()
        else:
            self.config = self.default_config.copy()

    def set_filename(filename):
        """set new filename."""
        self.filename = filename

    def read_from_file(filename=None):
        """read configuration from file."""
        if filename is not None:
            self.filename = filename
        config_temp = {}
        with open(self.filename, 'r') as f:
            config_temp = json.load(f)
            f.closed
        # do a merge with the defaults.
        self.config = self.default_config.copy()
        self.config.update(config_temp)

    def write_to_file(filename=None):
        """write configuration to file."""
        if filename is not None:
            self.filename = filename
        if filename is not None:
            with open(self.filename, 'w') as f:
                json.load(
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

    my_mapper = Mapper(my_config.config)

    my_mapper.start()

    # wait for user to hit key.
    input()

    my_mapper.disconnect()
    # wait for thread to finish.
    my_mapper.join()

    # as last thing we save the current configuration.
    my_config.write_to_file()

    # ###########################################
