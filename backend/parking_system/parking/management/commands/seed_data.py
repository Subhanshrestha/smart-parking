from django.core.management.base import BaseCommand
from parking.models import PermitType, ParkingLot, ParkingSpot, User


class Command(BaseCommand):
    help = 'Seeds the database with initial parking data'

    def handle(self, *args, **options):
        # Create permit types (only if they don't exist)
        self.stdout.write('Creating permit types...')
        student, _ = PermitType.objects.get_or_create(name='Student')
        faculty, _ = PermitType.objects.get_or_create(name='Faculty')
        visitor, _ = PermitType.objects.get_or_create(name='Visitor')

        self.stdout.write('Creating parking lots...')
        lots_data = [
            ('Perry Street Lot', 25),
            ('The Cage', 40),
            ('Duck Pond Lot', 30),
            ('Drill Field Lot', 20),
            ('North End Lot', 35),
        ]

        for lot_name, num_spots in lots_data:
            lot, created = ParkingLot.objects.get_or_create(
                parking_lot_name=lot_name,
                defaults={'occupancy': 0}
            )
            lot.permit_types.add(student, faculty)
            
            if created:
                for i in range(num_spots):
                    spot = ParkingSpot.objects.create(
                        parking_lot=lot,
                        availability=True
                    )
                    spot.lot_permit_access.add(student, faculty)
                self.stdout.write(f'  Created {lot_name} with {num_spots} spots')
            else:
                self.stdout.write(f'  {lot_name} already exists, skipping')

        # Create test user (only if doesn't exist)
        self.stdout.write('Creating test user...')
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user(
                username='demo',
                password='demo123',
                first_name='Demo',
                last_name='User'
            )
            self.stdout.write('  Created user: demo / demo123')
        else:
            self.stdout.write('  User demo already exists')

        self.stdout.write(self.style.SUCCESS(f'\nDone! Total: {ParkingLot.objects.count()} lots with {ParkingSpot.objects.count()} spots'))
        self.stdout.write(self.style.SUCCESS('Test login: username=demo, password=demo123'))