#!/usr/bin/env python3

import argparse
import textwrap
import xml.sax
import xml.sax.handler

class DeckException(Exception):
    pass

class DeckHandler(xml.sax.handler.ContentHandler):

    """Enumeration of different card zones."""
    ZONE_NONE = 0  # no zone
    ZONE_MAIN = 1  # maindeck
    ZONE_SIDE = 2  # sideboard

    def __init__(self, output):
        self.output = output
        self._zone = self.ZONE_NONE
        self._chars = ""

    def error(self, msg):
        self._file.close()
        raise DeckException("error on line {}: {}".format(
            self._locator.getLineNumber(), msg))

    def _card(self, attrs):
        if "number" not in attrs:
            self.error("card tag without number attribute")
        if "name" not in attrs:
            self.error("card tag without name attribute")
        return "{} {}\n".format(attrs["number"], attrs["name"])

    def startDocument(self):
        self._file = open(self.output, "w")

    def endDocument(self):
        self._file.close()

    def startElement(self, name, attrs):
        if name == "zone":
            if "name" not in attrs:
                self.error("zone tag without name attribute")
            zone = attrs["name"]
            if zone == "main":
                self._zone = self.ZONE_MAIN
            elif zone == "side":
                self._zone = self.ZONE_SIDE
            else:
                self.error("unknown zone name \"{}\"".format(zone))

        elif name == "card":
            if self._zone == self.ZONE_MAIN:
                self._file.write(self._card(attrs))
            elif self._zone == self.ZONE_SIDE:
                self._file.write("SB: " + self._card(attrs))
            else:
                self.error("card tag not in a valid zone")

    def characters(self, content):
        """Handle all text contents as comments."""
        for line in textwrap.wrap(content):
            self._file.write("// {}\n".format(line))

    def endElement(self, name):
        if name == "zone":
            self._zone = self.ZONE_NONE

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Cockatrice " \
            "decklists from XML format to plaintext format.")
    parser.add_argument("deck", type=str, nargs="+", help="a XML format deck")
    parser.add_argument("--suffix", type=str, default=".plain",
            help="suffix to add to filename for plaintext decks")
    args = parser.parse_args()

    for filename in args.deck:
        xml.sax.parse(filename, DeckHandler(filename + args.suffix))

# vim: set ts=4 sw=4 et :
