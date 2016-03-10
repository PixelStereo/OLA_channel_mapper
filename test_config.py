#!/usr/bin/env python
# coding=utf-8

"""
test configuration class.

some simple tests.
"""

import sys
import os
import json

version = """08.03.2016 12:30 stefan"""


class MapConfig():
    """abstract the reading / writing of configuration parameters."""

    default_config = {
        'universe': {
            'input': 1,
        },
        'map': {
            'channels': [0, 1, ],
            'repeat': True,
        },
    }

    def __init__(self, filename=None):
        """initialize config to defaults."""
        self.filename = filename
        self.config = {}
        if self.filename is not None:
            if os.path.isfile(filename):
                print("read config from file.")
                self.read_from_file()
            else:
                print("no config file found. writing defaults.")
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
        # make a clean copy
        # result = obj_1.copy()
        if (isinstance(result, dict) and isinstance(obj_2, dict)):
            print("obj_1 and obj_2 are dicts.")
            print("obj_1: {}".format(obj_1))
            print("obj_2: {}".format(obj_2))
            for key in obj_2:
                print("key: {}".format(key))
                if key in result:
                    print("key is in result - so merge:")
                    result[key] = self.merge_deep(result[key], obj_2[key])
                    # self.merge_deep(result[key], obj_2[key])
                else:
                    print("just copy.")
                    result[key] = obj_2[key]
        else:
            print("NO dicts.")
            print("result: {}".format(result))
            print("obj_1: {}".format(obj_1))
            print("obj_2: {}".format(obj_2))
            print("set")
            result = obj_2
            print("result: {}".format(result))
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
        print("config_temp:      {}".format(config_temp))
        print("default_config:   {}".format(self.default_config))
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
    filename = "test.json"
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

    # # wait for user to hit key.
    # try:
    #     raw_input(
    #         "\n\n" +
    #         42*'*' +
    #         "\nhit a key to stop the mapper\n" +
    #         42*'*' +
    #         "\n\n"
    #     )
    # except KeyboardInterrupt:
    #     print("\nstop.")
    # except:
    #     print("\nstop.")
    #
    # # as last thing we save the current configuration.
    # print("\nwrite config.")
    # my_config.write_to_file()

    # ###########################################
