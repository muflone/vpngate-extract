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
import urllib

from bs4 import BeautifulSoup

from .current_time import get_current_time
from .openvpn_profile import OpenVPNProfile
from .proxy_request import ProxyRequest
from .settings import Settings


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


class ConsumerRequest(object):
    def __init__(self,
                 existing_profiles: list) -> None:
        """
        ConsumerRequest object to send requests to the server using a
        proxy URL
        :param existing_profiles: list with the downloaded profiles
        """
        self.settings = Settings.Instance()
        self.openvpn_profile = OpenVPNProfile(self.settings.openvpn_template)
        self.profiles = existing_profiles

    async def execute(self,
                      proxy_index: int,
                      proxies_totals: int,
                      proxy: str,
                      runner: int) -> None:
        """
        Process a request to get the VPN hosts using the specified proxy
        :param proxy_index: index in the proxies list
        :param proxies_totals: number of proxies in the list
        :param proxy: URL of the proxy to use
        :param runner: index of the processing runner
        :return:
        """
        configuration_urls = []
        request = ProxyRequest(proxy=proxy)
        request.timeout = self.settings.timeout
        # Download index page using proxy
        time.sleep(self.settings.delay_for_proxy)
        if self.settings.verbose_level >= 1:
            progress_percent = (proxy_index + 1) / proxies_totals * 100
            print('[{TIME}] #{RUNNER:04d} Connecting using proxy {INDEX} '
                  'of {TOTALS} ({PERCENT:.2f}%): '
                  '{URL}'.format(TIME=get_current_time(),
                                 RUNNER=runner,
                                 INDEX=proxy_index + 1,
                                 TOTALS=proxies_totals,
                                 PERCENT=progress_percent,
                                 URL=proxy))
        page_content = await request.open(url=self.settings.url)
        if request.exception:
            if self.settings.verbose_level >= 4:
                print('[{TIME}] #{RUNNER:04d} > Unable to connect: '
                      '{ERROR})'.format(TIME=get_current_time(),
                                        RUNNER=runner,
                                        ERROR=request.exception))
            return
        else:
            if self.settings.verbose_level >= 3:
                print('[{TIME}] #{RUNNER:04d} > Connection established, '
                      'downloading index'.format(
                            TIME=get_current_time(),
                            RUNNER=runner))
        # Apply page fixes for broken tables
        page_content = page_content.replace(
            "<td class='vg_table_header'><b>Score</b><BR>"
            "(Quality)</td>\r\n</td>",
            "<td class='vg_table_header'><b>Score</b><BR>(Quality)</td>")
        page_content = page_content.replace(
            "<td class='vg_table_header'><b>Score</b><br/>"
            "(Quality)</td>\r\n</tr></table></span></p></td>",
            "<td class='vg_table_header'><b>Score</b><BR>(Quality)</td>")

        # Find the servers table (which has Country on the first line)
        bsoup = BeautifulSoup(page_content, 'html.parser')
        for hosts_table in bsoup.find_all('table', id=TABLE_HOSTS_ID):
            table_rows = hosts_table.find_all('tr')
            table_cells = table_rows[0].find_all('td')
            # Find the cell with the country title
            cell_country = table_cells[TABLE_COLUMN_COUNTRY].get_text()
            if cell_country == TABLE_COLUMN_COUNTRY_TITLE:
                # Process the hosts table
                for table_row in table_rows:
                    table_cells = table_row.find_all('td')
                    # Skip rows with the country title
                    cell_country = table_cells[TABLE_COLUMN_COUNTRY].get_text()
                    if cell_country == TABLE_COLUMN_COUNTRY_TITLE:
                        continue
                    # Find any host with the requested country
                    if cell_country == self.settings.country:
                        if self.settings.verbose_level >= 2:
                            cell_hostname = (
                                table_cells[TABLE_COLUMN_HOSTNAME].get_text())
                            print('[{TIME}] #{RUNNER:04d} > '
                                  'New host to download: '
                                  '{URL}'.format(TIME=get_current_time(),
                                                 RUNNER=runner,
                                                 URL=cell_hostname))
                        # Save data
                        config_links = (
                            table_cells[TABLE_COLUMN_CONFIG].find_all('a'))
                        for link in config_links:
                            configuration_urls.append(
                                urllib.parse.urljoin(self.settings.url,
                                                     link.get('href')))
                    else:
                        if self.settings.verbose_level >= 4:
                            cell_country = (
                               table_cells[TABLE_COLUMN_COUNTRY].get_text())
                            print('[{TIME}] #{RUNNER:04d} > '
                                  'Skipping invalid country '
                                  '{COUNTRY}'.format(TIME=get_current_time(),
                                                     RUNNER=runner,
                                                     COUNTRY=cell_country))
        # Cycle each configuration_url
        for (url_index, url) in enumerate(configuration_urls):
            if self.settings.get_mode_download():
                if self.settings.verbose_level >= 2:
                    print('[{TIME}] #{RUNNER:04d} > '
                          'Downloading configuration {INDEX} of {TOTALS} '
                          'hosts'.format(TIME=get_current_time(),
                                         RUNNER=runner,
                                         INDEX=url_index + 1,
                                         TOTALS=len(configuration_urls)))
                page_content = request.open(url=url, retries=3)
                if request.exception:
                    if self.settings.verbose_level >= 2:
                        print('[{TIME}] #{RUNNER:04d} > '
                              'Unable to download configuration index: '
                              '{ERROR}'.format(TIME=get_current_time(),
                                               RUNNER=runner,
                                               ERROR=request.exception))
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
                    time.sleep(self.settings.delay_for_download)
                    # Download data
                    profile_number += 1
                    full_url = urllib.parse.urljoin(self.settings.url,
                                                    link.get('href'))
                    if self.settings.verbose_level >= 2:
                        print('[{TIME}] #{RUNNER:04d} > '
                              'Downloading profile {INDEX} of {TOTALS}: '
                              '{URL}'.format(TIME=get_current_time(),
                                             RUNNER=runner,
                                             INDEX=profile_number,
                                             TOTALS=len(profiles_list),
                                             URL=full_url))
                    page_content = request.open(url=full_url, retries=10)
                    if not request.exception:
                        # Save configuration file
                        destination_filename = link.get('href').split('/')[-1]
                        # Skip existing profiles
                        if destination_filename not in self.profiles:
                            destination_path = os.path.join(
                                self.settings.destination_path,
                                destination_filename)
                            with open(destination_path, 'wb') as profile_file:
                                profile_file.write(page_content)
                            self.profiles.append(destination_filename)
                    else:
                        # Error during configuration download
                        if self.settings.verbose_level >= 2:
                            print('[{TIME}] #{RUNNER:04d} > '
                                  'Unable to download the configuration: '
                                  '{ERROR}'.format(TIME=get_current_time(),
                                                   RUNNER=runner,
                                                   ERROR=request.exception))
            if self.settings.get_mode_generate():
                # Generate OpenVPN profiles
                parts_url = urllib.parse.urlsplit(url)
                arguments_dict = {key: value[0]
                                  for (key, value)
                                  in urllib.parse.parse_qs(
                                      parts_url.query).items()}
                for destination_host_type in ('fqdn', 'ip'):
                    for port_type in ('tcp', 'udp'):
                        if arguments_dict[port_type] != '0':
                            destination_filename = (
                                'vpngate_{HOST}_{PROTOCOL}_{PORT}.ovpn'.format(
                                    HOST=arguments_dict[destination_host_type],
                                    PROTOCOL=port_type,
                                    PORT=arguments_dict[port_type]))
                            # Skip existing profiles
                            if destination_filename not in self.profiles:
                                destination_path = os.path.join(
                                    self.settings.destination_path,
                                    destination_filename)
                                self.openvpn_profile.create(
                                    filepath=destination_path,
                                    protocol=port_type,
                                    host=arguments_dict[destination_host_type],
                                    port=arguments_dict[port_type])
                                self.profiles.append(destination_filename)
