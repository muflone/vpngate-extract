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

# Application name
APP_NAME = 'VPNGate Extractor'
# Application version
VERSION = '0.3.0'
# Proxy list file
PROXY_LIST_FILENAME = 'proxy_list.csv'
# Source page
PAGE_URL = 'https://www.vpngate.net/en/'
# Requested country to filter hosts
REQUESTED_COUNTRY = 'Italy'
# Destination folder
DESTINATION_OVPN_PROFILES_FOLDER = 'ovpn_profiles'
# OpenVPN template for auto-generation
OVPN_TEMPLATE = 'ovpn_template.txt'
# Delay for each download
DELAY_FOR_EACH_PROXY = 0
DELAY_FOR_EACH_DOWNLOAD = 1
# Connection timeout
CONNECTION_TIMEOUT = 30
# Operational mode
MODE_DOWNLOAD_PROFILES = 'download'
MODE_GENERATE_PROFILES = 'generate'
# Verbose level for messages
VERBOSE_LEVEL = 1
# Running tasks for concurrent processing
RUNNING_TASKS = 30
