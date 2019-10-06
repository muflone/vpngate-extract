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

import os.path
import time
import urllib.parse

from bs4 import BeautifulSoup

from vpngate_extractor import constants
from vpngate_extractor.openvpn_profile import OpenVPNProfile
from vpngate_extractor.proxy_request import ProxyRequest


# Column index where lookup the country
TABLE_COLUMN_COUNTRY = 0
# Text for country lookup
TABLE_COLUMN_COUNTRY_TITLE = 'Country(Physical location)'
# Column index with server hostname
TABLE_COLUMN_HOSTNAME = 1
# Column index where lookup the hyperlink configuration
TABLE_COLUMN_CONFIG = 6
# Table hosts ID
TABLE_HOSTS_ID = 'vg_hosts_table_id'

with open(constants.PROXY_LIST_FILENAME, 'r') as proxy_file:
    proxy_list = ['{HOST}'.format(HOST=proxy.strip())
                  for proxy in proxy_file.readlines()
                  if not proxy.startswith('#')]

openvpn_profile = OpenVPNProfile('ovpn_template.txt')

for (proxy_index, proxy) in enumerate(proxy_list):
    configuration_urls = []
    proxy_request = ProxyRequest(proxy=proxy)
    proxy_request.timeout = constants.CONNECTION_TIMEOUT
    # Download index page using proxy
    time.sleep(constants.DELAY_FOR_EACH_PROXY)
    if constants.VERBOSE_LEVEL > 0:
        print('Connecting using proxy {INDEX} of {TOTALS} ({PERCENT:.2f}%): {URL}'.format(
            INDEX=proxy_index + 1,
            TOTALS=len(proxy_list),
            PERCENT=(proxy_index + 1) / len(proxy_list) * 100,
            URL=proxy))
    page_content = proxy_request.open(url=constants.PAGE_URL)
    if proxy_request.exception:
        if constants.VERBOSE_LEVEL > 1:
            print('  > Unable to connect:', proxy_request.exception)
        continue
    else:
        page_content = page_content.decode('utf-8')
    if constants.VERBOSE_LEVEL > 1:
        print('  > Connection established, downloading index')
    # Apply page fixes for broken tables
    page_content = page_content.replace(
        "<td class='vg_table_header'><b>Score</b><BR>(Quality)</td>\r\n</td>",
        "<td class='vg_table_header'><b>Score</b><BR>(Quality)</td>")
    page_content = page_content.replace(
        "<td class='vg_table_header'><b>Score</b><br/>(Quality)</td>\r\n</tr></table></span></p></td>",
        "<td class='vg_table_header'><b>Score</b><BR>(Quality)</td>")

    # Find the servers table (which has Country on the first line)
    bsoup = BeautifulSoup(page_content, 'html.parser')
    for hosts_table in bsoup.find_all('table', id=TABLE_HOSTS_ID):
        table_rows = hosts_table.find_all('tr')
        table_cells = table_rows[0].find_all('td')
        # Find the cell with the country title
        if table_cells[TABLE_COLUMN_COUNTRY].get_text() == TABLE_COLUMN_COUNTRY_TITLE:
            # Process the hosts table
            for table_row in table_rows:
                table_cells = table_row.find_all('td')
                # Skip rows with the country title
                if table_cells[TABLE_COLUMN_COUNTRY].get_text() == TABLE_COLUMN_COUNTRY_TITLE:
                    continue
                # Find any host with the requested country
                if table_cells[TABLE_COLUMN_COUNTRY].get_text() == constants.REQUESTED_COUNTRY:
                    if constants.VERBOSE_LEVEL > 1:
                        print('  > Saved host to download',
                              table_cells[TABLE_COLUMN_HOSTNAME].get_text())
                    # Save data
                    config_links = table_cells[TABLE_COLUMN_CONFIG].find_all('a')
                    for link in config_links:
                        configuration_urls.append(
                            urllib.parse.urljoin(constants.PAGE_URL, link.get('href')))
                else:
                    pass
                    if constants.VERBOSE_LEVEL > 2:
                        print('  > Skipping invalid country',
                            table_cells[TABLE_COLUMN_COUNTRY].get_text())

    # Cycle each configuration_url
    for (url_index, url) in enumerate(configuration_urls):
        if constants.DOWNLOAD_PROFILES:
            if constants.VERBOSE_LEVEL > 1:
                print('  > Downloading configuration {INDEX} of {TOTALS} hosts'.format(
                    INDEX=url_index + 1,
                    TOTALS=len(configuration_urls)
                ))
            page_content = proxy_request.open(url=url, retries=3)
            if proxy_request.exception:
                if constants.VERBOSE_LEVEL > 1:
                    print('  > Unable to download configuration index:',
                          proxy_request.exception)
                continue
            # Parse each configuration page
            bsoup = BeautifulSoup(page_content, 'html.parser')
            # Cycle over each link, ending with '.ovpn'
            profile_number = 0
            profiles_list = [link
                             for link in bsoup.find_all('a')
                             if link.get('href').endswith('.ovpn')]
            for link in profiles_list:
                # Delay before download
                time.sleep(constants.DELAY_FOR_EACH_DOWNLOAD)
                # Download data
                profile_number += 1
                full_url = urllib.parse.urljoin(constants.PAGE_URL, link.get('href'))
                if constants.VERBOSE_LEVEL > 1:
                    print('  > Downloading profile {INDEX} of {TOTALS}: {URL}'.format(
                        INDEX=profile_number,
                        TOTALS=len(profiles_list),
                        URL=full_url
                    ))
                page_content = proxy_request.open(url=full_url, retries=10)
                if not proxy_request.exception:
                    # Save configuration file
                    destination_path = os.path.join(
                        constants.DESTINATION_OVPN_PROFILES_FOLDER,
                        link.get('href').split('/')[-1])
                    with open(destination_path, 'wb') as destination_file:
                        destination_file.write(page_content)
                else:
                    # Error during configuration download
                    if constants.VERBOSE_LEVEL > 1:
                        print('  > Unable to download the configuration:',
                              proxy_request.exception)
        if constants.AUTOGENERATED_PROFILES:
            # Generate OpenVPN profiles
            parts_url = urllib.parse.urlsplit(url)
            arguments_dict = {key: value[0]
                              for (key, value)
                              in urllib.parse.parse_qs(parts_url.query).items()}
            for destination_host_type in ('fqdn', 'ip'):
                for port_type in ('tcp', 'udp'):
                    if arguments_dict[port_type] != '0':
                        destination_path = os.path.join(
                            constants.DESTINATION_OVPN_PROFILES_FOLDER,
                            'vpngate_{HOST}_{PROTOCOL}_{PORT}.ovpn'.format(
                                HOST=arguments_dict[destination_host_type],
                                PROTOCOL=port_type,
                                PORT=arguments_dict[port_type]
                            ))
                        openvpn_profile.create(filepath=destination_path,
                                               protocol=port_type,
                                               host=arguments_dict[destination_host_type],
                                               port=arguments_dict[port_type])
# Completion phase
if constants.VERBOSE_LEVEL > 0:
    print('Operation completed')