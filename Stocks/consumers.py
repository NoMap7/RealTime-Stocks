from os import name
from Stocks.models import StockxUser
import json
import copy
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class StockConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def addToCeleryBeat(self, selected_stocks):
        task = PeriodicTask.objects.filter(name='every-10-seconds')
        if len(task) > 0:
            task = task.first()
            args = json.loads(task.args)
            args = args[0]
            for st in selected_stocks:
                if st not in args:
                    args.append(st)
            task.args = json.dumps([args])
            task.save()
        else:
            schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
            task = PeriodicTask.objects.create(interval=schedule, name='every-10-seconds', task='Stocks.tasks.update_stock', args = json.dumps([selected_stocks]))

    @sync_to_async
    def addToStockxUser(self, selected_stocks):
        user = self.scope["user"]
        for st in selected_stocks:
            stock, created = StockxUser.objects.get_or_create(stock = st)
            stock.user.add(user)

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'stock_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Parse query_string
        query_params = parse_qs(self.scope["query_string"].decode())
        print(query_params)
        selected_stocks = query_params['pickStocks']
        
        # Add to celery_beat
        await self.addToCeleryBeat(selected_stocks)

        # Add stocks to StockxUser model
        await self.addToStockxUser(selected_stocks)

        await self.accept()

    @sync_to_async
    def helper_func(self):
        user = self.scope["user"]
        stocks = StockxUser.objects.filter(user__id = user.id)
        task = PeriodicTask.objects.get(name= 'every-10-seconds')
        args = json.loads(task.args)
        args = args[0]
        for st in stocks:
            st.user.remove(user)
            if st.user.count() == 0:
                args.remove(st.stock)
                st.delete()
        if args == None:
            args = []
        if len(args) == 0:
            task.delete()
        else:
            task.args = json.dumps([args])
            task.save()

    async def disconnect(self, close_code):
        await self.helper_func()

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_update',
                'message': message
            }
        )

    @sync_to_async
    def getUserStocks(self):
        user = self.scope["user"]
        user_stocks = user.stockxuser_set.values_list('stock', flat=True)
        return list(user_stocks)

    # Receive message from room group
    async def send_stock_update(self, event):
        message = event['message']
        message = copy.copy(message)

        user_stocks = await self.getUserStocks()
        for key in list(message.keys()):
            if key in user_stocks:
                pass
            else:
                del message[key]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))