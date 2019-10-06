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

from vpngate_extractor import constants
from vpngate_extractor.extractor import Extractor

if __name__ == '__main__':
    # Prepares proxy list
    with open(constants.PROXY_LIST_FILENAME, 'r') as proxy_file:
        proxy_list = ['{HOST}'.format(HOST=proxy.strip())
                      for proxy in proxy_file.readlines()
                      if not proxy.startswith('#')]
    # Execute extractor
    extractor = Extractor()
    extractor.execute(proxy_list)