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

import asyncio
import timeit

from vpngate_extractor import constants
from vpngate_extractor.current_time import get_current_time
from vpngate_extractor.consumer_request import ConsumerRequest
from vpngate_extractor.producer_proxy import ProducerProxy

async def worker(proxies_queue: asyncio.Queue, name: int):
    consumer_request = ConsumerRequest()
    # This is used to start the loop only
    proxy_item = True
    # Cycle while there's a proxy from the queue
    while proxy_item:
        proxy_item = await proxies_queue.get()
        if proxy_item:
            # Extract data using the current proxy
            proxy_index, proxies_totals, proxy = proxy_item
            await consumer_request.execute(proxy_index, proxies_totals, proxy, name)
            proxies_queue.task_done()
        else:
            # A couple of None follows at the end of the Queue
            # in order to break the cycle
            proxies_queue.task_done()
            await proxies_queue.join()

async def main():
    if constants.VERBOSE_LEVEL >= 1:
        # Print starting time
        starting_time = timeit.default_timer()
        print('Starting time: {TIME}'.format(
            TIME=get_current_time()
        ))
    proxies_queue = asyncio.Queue()
    # Add proxies list
    producer_proxy = ProducerProxy(proxies_queue)
    await producer_proxy.execute()
    # List of running worker tasks
    tasks = []
    for name in range(1, constants.RUNNING_TASKS + 1):
        # For each runner add an empty value to feed it with at the end
        await proxies_queue.put(None)
        tasks.append(worker(proxies_queue, name))
    await asyncio.wait(tasks)
    if constants.VERBOSE_LEVEL >= 1:
        # Print elapsed time
        ending_time = timeit.default_timer()
        print('Ending time: {TIME}'.format(
            TIME=get_current_time()
        ))
        elapsed_time = int(ending_time - starting_time)
        print('Elapsed time: {HOURS:02}:{MINUTES:02}.{SECONDS:02}'.format(
            HOURS=elapsed_time // 3600,
            MINUTES=elapsed_time // 60,
            SECONDS=elapsed_time % 60
        ))

if __name__ == '__main__':
    asyncio.run(main())