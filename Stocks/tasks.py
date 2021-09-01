import asyncio
from celery import shared_task
from yahoo_fin.stock_info import *
from threading import Thread
from queue import Queue
from channels.layers import get_channel_layer
import simplejson as json

@shared_task(bind = True)
def update_stocks(self, selected_stocks):
    data = {}
    all_stocks = tickers_nifty50()
    for st in selected_stocks:
        if st in all_stocks:
            pass
        else:
            selected_stocks.remove(i)
    
    threads_count = len(selected_stocks)
    threads = []
    que = Queue()
    for i in range(threads_count):
        # thread = Thread(target= lambda q, arg1: q.put({selected_stocks[i]: json.loads(json.dumps(get_quote_table(arg1), ignore_nan=True))}), args=(que, selected_stocks[i]))
        thread = Thread(target= lambda q, arg1: q.put({selected_stocks[i]: json.loads(json.dumps(get_quote_table(arg1), ignore_nan=True))}), args=(que, selected_stocks[i]))
        threads.append(thread)
        threads[i].start()
    for thread in threads:
        thread.join()
    while not que.empty():
        data.update(que.get())

    # Send data to group to be broadcasted to sockets
    channel_layer = get_channel_layer()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(channel_layer.group_send('stock_track', {
        'type': 'send_stock_update',
        'message': data,
    }))

    return 'Done'