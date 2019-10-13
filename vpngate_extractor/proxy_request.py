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

import aiohttp


class ProxyRequest(object):
    def __init__(self,
                 *,
                 proxy: str) -> None:
        """
        ProxyRequest object to send an HTTP request using a proxy URL

        :param proxy: URL of the proxy to use
        """
        self.proxy = proxy
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
    def timeout(self,
                new_timeout: int) -> None:
        """
        Set connection timeout.

        :param new_timeout: new timeout value
        """
        if new_timeout > 0:
            self.__timeout = new_timeout
        else:
            raise AssertionError('Invalid value for timeout')

    async def open(self,
                   *,
                   url: str,
                   retries: int = 1) -> bytes:
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
                connector = aiohttp.TCPConnector(force_close=True)
                async with aiohttp.ClientSession(connector=connector) as http:
                    timeout = aiohttp.ClientTimeout(
                        total=self.__timeout,
                        connect=self.__timeout,
                        sock_connect=self.__timeout,
                        sock_read=self.__timeout)
                    async with http.get(url,
                                        proxy=self.proxy,
                                        timeout=timeout) as request:
                        result = await request.text(encoding='utf-8')
            except (aiohttp.client.ClientError) as error:
                self.exception = error
        return result
