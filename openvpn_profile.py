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

class OpenVPNProfile(object):
    def __init__(self, template_path: str) -> None:
        """
        New instance of OpenVPNProfile
        :param template_path: specify the file path for the ovpn template file
        """
        with open(template_path, 'r') as template_file:
            self.template_text = template_file.read()

    def create(self, filepath: str, protocol: str, host: str, port: int) -> None:
        """
        Create the OpenVPN profile to <filepath>
        :param filepath: filename path where to save the profile file
        :param protocol: specify the protocol used for the connection, can only
                         be either tcp or udp
        :param host: specify the hostname or IP address where to connect
        :param port: specify the port number used for connection
        :return: None
        """
        with open(filepath, mode='w', newline='\r\n') as profile_file:
            profile_file.write(self.template_text.format(PROTOCOL=protocol,
                                                         HOST=host,
                                                         PORT=port))
