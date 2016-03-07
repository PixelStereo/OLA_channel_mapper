#!/usr/bin/env python
# coding=utf-8

"""
ola dmx receive example.

    https://www.openlighting.org/ola/developer-documentation/python-api/#Receiving_DMX
"""

from ola.ClientWrapper import ClientWrapper


def NewData(data):
    """print received data."""
    print(data)

universe = 1

wrapper = ClientWrapper()
client = wrapper.Client()
client.RegisterUniverse(universe, client.REGISTER, NewData)
wrapper.Run()
