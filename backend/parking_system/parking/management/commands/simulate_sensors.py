import random
import time
from django.core.management.base import BaseCommand
from parking.models import ParkingSpot, ParkingLot


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
        self.stdout.write(self.style.SUCCESS(f'Starting sensor simulation (every {interval}s)...'))
        self.stdout.write('Press Ctrl+C to stop\n')

        try:
            while True:
                spot = random.choice(ParkingSpot.objects.all())
                old_status = spot.availability
                
                # 60% chance to flip status, 40% chance to stay same
                if random.random() < 0.6:
                    spot.availability = not spot.availability
                    spot.save()
                    
                    # Update lot occupancy
                    lot = spot.parking_lot
                    lot.occupancy = lot.spots.filter(availability=False).count()
                    lot.save()

                    action = "DEPARTED" if spot.availability else "PARKED"
                    self.stdout.write(
                        f'[{lot.parking_lot_name}] Spot {spot.parking_spot_id}: {action} '
                        f'(Lot: {lot.occupancy}/{lot.spots.count()} occupied)'
                    )
                
                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nSimulation stopped.'))