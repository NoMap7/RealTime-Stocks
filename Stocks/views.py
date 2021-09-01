from django.http.response import HttpResponse
from django.shortcuts import render
from yahoo_fin.stock_info import *
from threading import Thread
from queue import Queue
from asgiref.sync import sync_to_async, async_to_sync
# from django.http import HttpResponse

# Create your views here.
def pickStocks(request):
    stocks = tickers_nifty50()
    # print(stocks)
    return render(request, 'Stocks/pickStocks.html', {'title': 'Pick Stocks', 'stocks': stocks})

@sync_to_async
def checkAuthenticated(request):
    if not request.user.is_authenticated:
        return False
    else:
        return True

async def trackStocks(req):
    is_loggedin = await checkAuthenticated(req)
    if not is_loggedin:
        return HttpResponse('Login first')
    selected_stocks = req.GET.getlist('pickStocks')
    data = {}
    all_stocks = tickers_nifty50()
    for st in selected_stocks:
        if st in all_stocks:
            pass
        else:
            return HttpResponse('Error')
    
    threads_count = len(selected_stocks)
    threads = []
    que = Queue()
    for i in range(threads_count):
        thread = Thread(target= lambda q, arg1: q.put({selected_stocks[i]: get_quote_table(arg1)}), args=(que, selected_stocks[i]))
        threads.append(thread)
        threads[i].start()
    for thread in threads:
        thread.join()
    while not que.empty():
        data.update(que.get())

    return render(req, 'Stocks/trackStocks.html', {'title': 'Live Tracker', 'data': data, 'room_name': 'track'})