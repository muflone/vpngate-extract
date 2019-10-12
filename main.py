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

from vpngate_extractor import constants
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
    proxies_queue = asyncio.Queue()
    # Add proxies list
    producer_proxy = ProducerProxy(proxies_queue)
    await producer_proxy.execute()
    # List of running worker tasks
    tasks = []
    for name in range(constants.RUNNING_TASKS):
        # For each runner add an empty value to feed it with at the end
        await proxies_queue.put(None)
        tasks.append(worker(proxies_queue, name))
    await asyncio.wait(tasks)

if __name__ == '__main__':
    asyncio.run(main())