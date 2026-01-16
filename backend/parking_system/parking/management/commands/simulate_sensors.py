import random
import time
from django.core.management.base import BaseCommand
from parking.models import ParkingSpot
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Command(BaseCommand):
    help = 'Simulates IoT parking sensors updating spot availability'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=float,
            default=2.0,
            help='Seconds between sensor updates (default: 2)'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        channel_layer = get_channel_layer()
        
        self.stdout.write(self.style.SUCCESS(f'Starting sensor simulation (every {interval}s)...'))
        self.stdout.write('Press Ctrl+C to stop\n')

        try:
            while True:
                spot = random.choice(ParkingSpot.objects.all())
                
                if random.random() < 0.6:
                    spot.availability = not spot.availability
                    spot.save()
                    
                    lot = spot.parking_lot
                    lot.occupancy = lot.spots.filter(availability=False).count()
                    lot.save()

                    action = "DEPARTED" if spot.availability else "PARKED"
                    self.stdout.write(
                        f'[{lot.parking_lot_name}] Spot {spot.parking_spot_id}: {action} '
                        f'(Lot: {lot.occupancy}/{lot.spots.count()} occupied)'
                    )

                    # Broadcast to WebSocket
                    total = lot.spots.count()
                    available = total - lot.occupancy
                    async_to_sync(channel_layer.group_send)(
                        'parking_updates',
                        {
                            'type': 'parking_update',
                            'data': {
                                'lot_id': lot.parking_lot_id,
                                'lot_name': lot.parking_lot_name,
                                'spot_id': spot.parking_spot_id,
                                'available': spot.availability,
                                'available_spots': available,
                                'total_spots': total,
                                'occupancy_percent': round(lot.occupancy / total * 100, 1) if total > 0 else 0
                            }
                        }
                    )
                
                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nSimulation stopped.'))
