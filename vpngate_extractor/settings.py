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

import argparse

from . import constants
from .singleton import Singleton

@Singleton
class Settings(object):
    def __init__(self) -> None:
        """
        Parse command line arguments
        """
        parser = argparse.ArgumentParser(
            description='Get VPN hosts from vpngate')
        parser.add_argument('-u',
                            '--url',
                            type=str,
                            dest='url',
                            action='store',
                            default=constants.PAGE_URL,
                            help='URL for vpngate list')
        parser.add_argument('-p',
                            '--proxies',
                            type=str,
                            dest='proxies',
                            action='store',
                            default=constants.PROXY_LIST_FILENAME,
                            help='Filename with proxies list')
        parser.add_argument('-c',
                            '--country',
                            type=str,
                            dest='country',
                            action='store',
                            default=constants.REQUESTED_COUNTRY,
                            help='Country to look for extraction')
        parser.add_argument('-d',
                            '--destination',
                            type=str,
                            dest='destination',
                            action='store',
                            default=constants.DESTINATION_OVPN_PROFILES_FOLDER,
                            help='Directory where to store the results')
        parser.add_argument('-m',
                            '--mode',
                            type=str,
                            dest='mode',
                            action='store',
                            choices=('download', 'generate'),
                            default='generate',
                            help='Download or generate the OVPN profiles')
        parser.add_argument('-v',
                            '--verbose',
                            dest='verbose_level',
                            action='count',
                            default=0,
                            help='Verbose level')
        parser.add_argument('-r',
                            '--runners',
                            type=int,
                            dest='runners',
                            action='store',
                            default=constants.RUNNING_TASKS,
                            help='Running tasks in parallel')
        # Add arguments for downloads
        parser_group = parser.add_argument_group('Download options')
        parser_group.add_argument('-t',
                                  '--timeout',
                                  type=int,
                                  dest='timeout',
                                  action='store',
                                  default=constants.CONNECTION_TIMEOUT,
                                  help='Timeout in seconds for each '
                                       'connection')
        parser_group.add_argument('--delay-proxy',
                                  type=int,
                                  dest='delay_proxy',
                                  action='store',
                                  default=constants.DELAY_FOR_EACH_PROXY,
                                  help='Delay in seconds for each proxy')
        parser_group.add_argument('--delay-download',
                                  type=int,
                                  dest='delay_download',
                                  action='store',
                                  default=constants.DELAY_FOR_EACH_DOWNLOAD,
                                  help='Delay in seconds for each download')
        # Parse command line arguments
        self.__arguments = parser.parse_args()
        print(self.__arguments)

    @property
    def verbose_level(self) -> int:
        """
        Get the verbose level

        :return: numeric verbose level
        """
        return self.__arguments.verbose_level

    @property
    def url(self) -> str:
        """
        Get the page URL

        :return: URL of the requested page to download the hosts
        """
        return self.__arguments.url

    @property
    def destination_path(self) -> str:
        """
        Get the destination path

        :return: path of the destination folder
        """
        return self.__arguments.destination

    @property
    def proxies(self) -> str:
        """
        Get the proxies filename

        :return: path of the proxies list file
        """
        return self.__arguments.proxies

    @property
    def country(self) -> str:
        """
        Get the requested country to search

        :return: country to search in the contents
        """
        return self.__arguments.country

    @property
    def runners(self) -> int:
        """
        Get the number of runners to launch during the scan

        :return: runners count
        """
        return self.__arguments.runners

    @property
    def timeout(self) -> int:
        """
        Get the number of seconds for connection timeout

        :return: time in seconds
        """
        return self.__arguments.timeout

    @property
    def delay_for_proxy(self) -> int:
        """
        Get the number of seconds to delay for each proxy request

        :return: time in seconds
        """
        return self.__arguments.delay_proxy

    @property
    def delay_for_download(self) -> int:
        """
        Get the number of seconds to delay for each download

        :return: time in seconds
        """
        return self.__arguments.delay_download
