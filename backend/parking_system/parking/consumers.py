import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from parking.models import ParkingLot, ParkingSpot


class ParkingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('parking_updates', self.channel_name)
        await self.accept()
        # Send initial state on connect
        initial_state = await self.get_all_lots_status()
        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'data': initial_state
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('parking_updates', self.channel_name)

    async def receive(self, text_data):
        """Handle incoming messages from client."""
        try:
            data = json.loads(text_data)
            msg_type = data.get('type')

            if msg_type == 'get_status':
                # Client requesting current status
                status = await self.get_all_lots_status()
                await self.send(text_data=json.dumps({
                    'type': 'status_update',
                    'data': status
                }))
            elif msg_type == 'get_lot_spots':
                # Client requesting spots for a specific lot
                lot_id = data.get('lot_id')
                if lot_id:
                    spots = await self.get_lot_spots(lot_id)
                    await self.send(text_data=json.dumps({
                        'type': 'lot_spots',
                        'lot_id': lot_id,
                        'data': spots
                    }))
        except json.JSONDecodeError:
            pass

    async def parking_update(self, event):
        """Broadcast parking update to connected client."""
        await self.send(text_data=json.dumps({
            'type': 'spot_update',
            'data': event['data']
        }))

    async def batch_update(self, event):
        """Broadcast batch of parking updates."""
        await self.send(text_data=json.dumps({
            'type': 'batch_update',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_all_lots_status(self):
        """Get current status of all parking lots."""
        lots = ParkingLot.objects.all().order_by('parking_lot_id')
        result = []
        for lot in lots:
            total = lot.spots.count()
            available = lot.spots.filter(availability=True).count()
            result.append({
                'lot_id': lot.parking_lot_id,
                'lot_name': lot.parking_lot_name,
                'total_spots': total,
                'available_spots': available,
                'occupancy': total - available,
                'occupancy_percent': round((total - available) / total * 100, 1) if total > 0 else 0
            })
        return result

    @database_sync_to_async
    def get_lot_spots(self, lot_id):
        """Get all spots for a specific lot."""
        spots = ParkingSpot.objects.filter(
            parking_lot_id=lot_id
        ).order_by('parking_spot_id')
        return [
            {
                'spot_id': spot.parking_spot_id,
                'available': spot.availability
            }
            for spot in spots
        ]
