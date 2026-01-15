from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, time, timedelta
from parking.models import User, PermitType, ParkingLot, ParkingSpot, Vehicle, Event, Session


# =============================================================================
# MODEL TESTS
# =============================================================================

class UserModelTest(TestCase):
    """Test User model"""

    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))

    def test_create_user_without_username_raises_error(self):
        """Test that creating user without username raises ValueError"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_with_permit_type(self):
        """Test user with assigned permit type"""
        permit = PermitType.objects.create(name='Student')
        user = User.objects.create_user(
            username='student',
            password='pass123',
            first_name='Student',
            last_name='User',
            permit_type=permit
        )
        self.assertEqual(user.permit_type.name, 'Student')

    def test_user_id_property(self):
        """Test that user.id returns user_id"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.id, user.user_id)

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(str(user), 'testuser')


class PermitTypeModelTest(TestCase):
    """Test PermitType model"""

    def test_create_permit_type(self):
        """Test creating a permit type"""
        permit = PermitType.objects.create(name='Faculty')
        self.assertEqual(permit.name, 'Faculty')

    def test_permit_type_str_representation(self):
        """Test permit type string representation"""
        permit = PermitType.objects.create(name='Student')
        self.assertEqual(str(permit), 'Student')


class ParkingLotModelTest(TestCase):
    """Test ParkingLot model"""

    def test_create_parking_lot(self):
        """Test creating a parking lot"""
        lot = ParkingLot.objects.create(
            parking_lot_name='Test Lot',
            occupancy=0
        )
        self.assertEqual(lot.parking_lot_name, 'Test Lot')
        self.assertEqual(lot.occupancy, 0)

    def test_parking_lot_str_representation(self):
        """Test parking lot string representation"""
        lot = ParkingLot.objects.create(parking_lot_name='Perry Street')
        self.assertEqual(str(lot), 'Perry Street')

    def test_parking_lot_with_permit_types(self):
        """Test parking lot with assigned permit types"""
        lot = ParkingLot.objects.create(parking_lot_name='Faculty Lot')
        permit1 = PermitType.objects.create(name='Faculty')
        permit2 = PermitType.objects.create(name='Staff')
        lot.permit_types.add(permit1, permit2)
        self.assertEqual(lot.permit_types.count(), 2)


class ParkingSpotModelTest(TestCase):
    """Test ParkingSpot model"""

    def test_create_parking_spot(self):
        """Test creating a parking spot"""
        lot = ParkingLot.objects.create(
            parking_lot_name='Test Lot',
            occupancy=0
        )
        spot = ParkingSpot.objects.create(
            parking_lot=lot,
            availability=True
        )
        self.assertTrue(spot.availability)
        self.assertEqual(spot.parking_lot, lot)

    def test_parking_spot_str_representation(self):
        """Test parking spot string representation"""
        lot = ParkingLot.objects.create(parking_lot_name='Test Lot')
        spot = ParkingSpot.objects.create(parking_lot=lot)
        self.assertIn('Test Lot', str(spot))

    def test_spot_availability_default(self):
        """Test that spot availability defaults to True"""
        lot = ParkingLot.objects.create(parking_lot_name='Test Lot')
        spot = ParkingSpot.objects.create(parking_lot=lot)
        self.assertTrue(spot.availability)

    def test_spots_related_name(self):
        """Test that parking lot can access spots via related_name"""
        lot = ParkingLot.objects.create(parking_lot_name='Test Lot')
        ParkingSpot.objects.create(parking_lot=lot)
        ParkingSpot.objects.create(parking_lot=lot)
        self.assertEqual(lot.spots.count(), 2)


class VehicleModelTest(TestCase):
    """Test Vehicle model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='carowner',
            password='pass123',
            first_name='Car',
            last_name='Owner'
        )

    def test_create_vehicle(self):
        """Test creating a vehicle"""
        vehicle = Vehicle.objects.create(
            make='Toyota',
            model='Camry',
            owner=self.user
        )
        self.assertEqual(vehicle.make, 'Toyota')
        self.assertEqual(vehicle.model, 'Camry')
        self.assertEqual(vehicle.owner, self.user)

    def test_vehicle_str_representation(self):
        """Test vehicle string representation"""
        vehicle = Vehicle.objects.create(
            make='Honda',
            model='Civic',
            owner=self.user
        )
        self.assertIn('Honda', str(vehicle))
        self.assertIn('Civic', str(vehicle))
        self.assertIn('carowner', str(vehicle))

    def test_user_vehicles_related_name(self):
        """Test user can access vehicles via related_name"""
        Vehicle.objects.create(make='Toyota', model='Camry', owner=self.user)
        Vehicle.objects.create(make='Honda', model='Accord', owner=self.user)
        self.assertEqual(self.user.vehicles.count(), 2)

    def test_vehicle_deleted_when_user_deleted(self):
        """Test vehicle is deleted when owner is deleted (CASCADE)"""
        Vehicle.objects.create(make='Toyota', model='Camry', owner=self.user)
        user_id = self.user.user_id
        self.user.delete()
        self.assertEqual(Vehicle.objects.filter(owner_id=user_id).count(), 0)


class EventModelTest(TestCase):
    """Test Event model"""

    def test_create_event(self):
        """Test creating an event"""
        event = Event.objects.create(
            event_name='Football Game',
            date=date.today(),
            time_start=time(14, 0)
        )
        self.assertEqual(event.event_name, 'Football Game')

    def test_event_str_representation(self):
        """Test event string representation"""
        today = date.today()
        event = Event.objects.create(
            event_name='Basketball Game',
            date=today,
            time_start=time(19, 0)
        )
        self.assertIn('Basketball Game', str(event))

    def test_event_with_restricted_lots(self):
        """Test event with restricted parking lots"""
        event = Event.objects.create(
            event_name='Concert',
            date=date.today(),
            time_start=time(20, 0)
        )
        lot1 = ParkingLot.objects.create(parking_lot_name='Lot A')
        lot2 = ParkingLot.objects.create(parking_lot_name='Lot B')
        event.restricted_lots.add(lot1, lot2)
        self.assertEqual(event.restricted_lots.count(), 2)


class SessionModelTest(TestCase):
    """Test Session model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='parker',
            password='pass123',
            first_name='Parker',
            last_name='User'
        )
        self.lot = ParkingLot.objects.create(parking_lot_name='Test Lot')
        self.spot = ParkingSpot.objects.create(parking_lot=self.lot)
        self.vehicle = Vehicle.objects.create(
            make='Ford',
            model='Focus',
            owner=self.user
        )

    def test_create_session(self):
        """Test creating a parking session"""
        session = Session.objects.create(
            parking_spot=self.spot,
            user=self.user,
            vehicle=self.vehicle
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.parking_spot, self.spot)
        self.assertIsNotNone(session.start_time)
        self.assertIsNone(session.end_time)

    def test_session_str_representation(self):
        """Test session string representation"""
        session = Session.objects.create(
            parking_spot=self.spot,
            user=self.user
        )
        self.assertIn('parker', str(session))

    def test_session_without_vehicle(self):
        """Test session can be created without vehicle"""
        session = Session.objects.create(
            parking_spot=self.spot,
            user=self.user
        )
        self.assertIsNone(session.vehicle)

    def test_user_sessions_related_name(self):
        """Test user can access sessions via related_name"""
        Session.objects.create(parking_spot=self.spot, user=self.user)
        self.assertEqual(self.user.sessions.count(), 1)


# =============================================================================
# API TESTS
# =============================================================================

class DashboardAPITest(APITestCase):
    """Test Dashboard API endpoint"""

    def setUp(self):
        """Set up test data"""
        # Clear cache to ensure fresh data for each test
        cache.clear()
        self.lot = ParkingLot.objects.create(
            parking_lot_name='Test Lot',
            occupancy=0
        )
        for i in range(7):
            ParkingSpot.objects.create(
                parking_lot=self.lot,
                availability=True
            )
        for i in range(3):
            ParkingSpot.objects.create(
                parking_lot=self.lot,
                availability=False
            )

    def test_dashboard_returns_lot_data(self):
        """Test dashboard endpoint returns lot information"""
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        lot_data = response.data[0]
        self.assertEqual(lot_data['name'], 'Test Lot')
        self.assertEqual(lot_data['total_spots'], 10)
        self.assertEqual(lot_data['available_spots'], 7)
        self.assertEqual(lot_data['occupancy_percent'], 30.0)

    def test_dashboard_empty_lot(self):
        """Test dashboard with lot that has no spots"""
        empty_lot = ParkingLot.objects.create(parking_lot_name='Empty Lot')
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Find the empty lot in response
        empty_lot_data = next(
            (lot for lot in response.data if lot['name'] == 'Empty Lot'), None
        )
        self.assertIsNotNone(empty_lot_data)
        self.assertEqual(empty_lot_data['occupancy_percent'], 0)

    def test_dashboard_multiple_lots(self):
        """Test dashboard returns multiple lots"""
        ParkingLot.objects.create(parking_lot_name='Lot B')
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class RegisterAPITest(APITestCase):
    """Test User Registration API"""

    def test_register_user(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_without_username(self):
        """Test registration fails without username"""
        data = {
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_without_password(self):
        """Test registration fails without password"""
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Test registration fails with duplicate username"""
        User.objects.create_user(
            username='existinguser',
            password='pass123',
            first_name='Existing',
            last_name='User'
        )
        data = {
            'username': 'existinguser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_returns_user_id(self):
        """Test registration returns user_id"""
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertIn('user_id', response.data)


class AuthTokenAPITest(APITestCase):
    """Test JWT Authentication"""

    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='authuser',
            password='authpass123',
            first_name='Auth',
            last_name='User'
        )

    def test_obtain_token(self):
        """Test obtaining JWT token"""
        data = {
            'username': 'authuser',
            'password': 'authpass123'
        }
        response = self.client.post('/api/token/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        """Test token request with invalid credentials fails"""
        data = {
            'username': 'authuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/token/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Test refreshing JWT token"""
        # First get tokens
        data = {
            'username': 'authuser',
            'password': 'authpass123'
        }
        token_response = self.client.post('/api/token/', data, format='json')
        refresh_token = token_response.data['refresh']

        # Now refresh
        response = self.client.post(
            '/api/token/refresh/',
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class ProfileAPITest(APITestCase):
    """Test User Profile API"""

    def setUp(self):
        """Set up test user"""
        self.permit = PermitType.objects.create(name='Student')
        self.user = User.objects.create_user(
            username='profileuser',
            password='pass123',
            first_name='Profile',
            last_name='User',
            permit_type=self.permit
        )

    def test_profile_requires_auth(self):
        """Test profile endpoint requires authentication"""
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_user_data(self):
        """Test authenticated user can access profile"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')
        self.assertEqual(response.data['first_name'], 'Profile')


class ActiveEventsAPITest(APITestCase):
    """Test Active Events API"""

    def test_active_events_empty(self):
        """Test active events endpoint with no events"""
        response = self.client.get('/api/events/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_active_events_returns_today_events(self):
        """Test active events returns events for today"""
        Event.objects.create(
            event_name='Today Event',
            date=date.today(),
            time_start=time(10, 0)
        )
        Event.objects.create(
            event_name='Tomorrow Event',
            date=date.today() + timedelta(days=1),
            time_start=time(10, 0)
        )
        response = self.client.get('/api/events/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['event_name'], 'Today Event')


class LotsForPermitAPITest(APITestCase):
    """Test Lots for Permit API"""

    def setUp(self):
        """Set up test data"""
        self.student_permit = PermitType.objects.create(name='Student')
        self.faculty_permit = PermitType.objects.create(name='Faculty')

        self.student_lot = ParkingLot.objects.create(parking_lot_name='Student Lot')
        self.student_lot.permit_types.add(self.student_permit)

        self.faculty_lot = ParkingLot.objects.create(parking_lot_name='Faculty Lot')
        self.faculty_lot.permit_types.add(self.faculty_permit)

        self.shared_lot = ParkingLot.objects.create(parking_lot_name='Shared Lot')
        self.shared_lot.permit_types.add(self.student_permit, self.faculty_permit)

    def test_anonymous_user_gets_all_lots(self):
        """Test anonymous user gets all lots"""
        response = self.client.get('/api/lots/for-my-permit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_user_with_permit_gets_filtered_lots(self):
        """Test user with permit gets only accessible lots"""
        user = User.objects.create_user(
            username='student',
            password='pass123',
            first_name='Student',
            last_name='User',
            permit_type=self.student_permit
        )
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/lots/for-my-permit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Student should see Student Lot and Shared Lot
        self.assertEqual(len(response.data), 2)
        lot_names = [lot['parking_lot_name'] for lot in response.data]
        self.assertIn('Student Lot', lot_names)
        self.assertIn('Shared Lot', lot_names)
        self.assertNotIn('Faculty Lot', lot_names)


class ParkingLotViewSetAPITest(APITestCase):
    """Test ParkingLot ViewSet API"""

    def setUp(self):
        """Set up test data"""
        self.lot = ParkingLot.objects.create(
            parking_lot_name='Test Lot',
            occupancy=5
        )

    def test_list_parking_lots(self):
        """Test listing all parking lots"""
        response = self.client.get('/api/lots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_parking_lot(self):
        """Test retrieving a single parking lot"""
        response = self.client.get(f'/api/lots/{self.lot.parking_lot_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['parking_lot_name'], 'Test Lot')

    def test_create_parking_lot(self):
        """Test creating a new parking lot"""
        data = {'parking_lot_name': 'New Lot', 'occupancy': 0}
        response = self.client.post('/api/lots/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ParkingLot.objects.filter(parking_lot_name='New Lot').exists())


class ParkingSpotViewSetAPITest(APITestCase):
    """Test ParkingSpot ViewSet API"""

    def setUp(self):
        """Set up test data"""
        self.lot = ParkingLot.objects.create(parking_lot_name='Test Lot')
        self.spot = ParkingSpot.objects.create(
            parking_lot=self.lot,
            availability=True
        )

    def test_list_parking_spots(self):
        """Test listing all parking spots"""
        response = self.client.get('/api/spots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_spots_by_lot(self):
        """Test filtering spots by parking lot"""
        other_lot = ParkingLot.objects.create(parking_lot_name='Other Lot')
        ParkingSpot.objects.create(parking_lot=other_lot)

        response = self.client.get(f'/api/spots/?parking_lot={self.lot.parking_lot_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_spot_availability(self):
        """Test updating a spot's availability"""
        response = self.client.patch(
            f'/api/spots/{self.spot.parking_spot_id}/',
            {'availability': False},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.spot.refresh_from_db()
        self.assertFalse(self.spot.availability)


class VehicleViewSetAPITest(APITestCase):
    """Test Vehicle ViewSet API"""

    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='vehicleowner',
            password='pass123',
            first_name='Vehicle',
            last_name='Owner'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='pass123',
            first_name='Other',
            last_name='User'
        )

    def test_vehicle_list_requires_auth(self):
        """Test vehicle list requires authentication"""
        response = self.client.get('/api/vehicles/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_vehicles(self):
        """Test user only sees their own vehicles"""
        Vehicle.objects.create(make='Toyota', model='Camry', owner=self.user)
        Vehicle.objects.create(make='Honda', model='Civic', owner=self.other_user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/vehicles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['make'], 'Toyota')

    def test_create_vehicle(self):
        """Test creating a vehicle"""
        self.client.force_authenticate(user=self.user)
        data = {'make': 'Ford', 'model': 'Focus'}
        response = self.client.post('/api/vehicles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Vehicle should be owned by authenticated user
        vehicle = Vehicle.objects.get(make='Ford')
        self.assertEqual(vehicle.owner, self.user)

    def test_delete_own_vehicle(self):
        """Test deleting own vehicle"""
        vehicle = Vehicle.objects.create(make='Toyota', model='Camry', owner=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/vehicles/{vehicle.vehicle_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Vehicle.objects.filter(vehicle_id=vehicle.vehicle_id).exists())
