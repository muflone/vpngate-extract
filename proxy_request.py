##
#     Project: VPNGate Extractor
# Description: Extract OpenVPN hosts from vpngate.com
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2019 Fabio Castelli
#     License: GPL-3+
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##

import socket
import urllib.request

class ProxyRequest(object):
    def __init__(self, *, proxy: dict) -> None:
        self.urllib_opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({'http': proxy,
                                         'https': proxy}))
        self.__timeout = 10
        self.exception = None

    @property
    def timeout(self) -> int:
        """
        Get the connection timeout.

        :return: connection timeout in seconds
        """
        return self.__timeout

    @timeout.setter
    def timeout(self, new_value: int) -> None:
        """
        Set connection timeout.

        :param new_value: new timeout value
        :return: None
        """
        if new_value > 0:
            self.__timeout = new_value
        else:
            raise AssertionError('Invalid value for timeout')

    def open(self, *, url: str, retries : int = 1) -> bytes:
        """
        Open the requested url.

        :param url: the resource to download
        :param retries: the number of retries to attempt to download the url
        :return: the downloaded content
        """
        for attempt in range(retries):
            self.exception = None
            result = None
            try:
                result = self.urllib_opener.open(url,
                                                 timeout=self.__timeout).read()
                break
            except (urllib.request.URLError, socket.timeout) as error:
                self.exception = error
        return result
