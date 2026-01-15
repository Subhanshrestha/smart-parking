# ParkGrid Todo List

## Future Improvements (from README)

- [ ] Campus map view with lot locations
- [ ] Historical occupancy charts
- [ ] Peak hours prediction
- [ ] Mobile app
- [ ] Push notifications when spots open

## Frontend Enhancements

- [ ] Switch from polling to WebSocket for real-time updates
  - WebSocket infrastructure already exists (`ws://localhost:8000/ws/parking/`)
  - Consumer ready at `parking.consumers.ParkingConsumer`
- [ ] Add loading states and error handling UI
- [ ] Implement dark mode toggle
- [ ] Add accessibility improvements (ARIA labels, keyboard navigation)
- [ ] Responsive design improvements for mobile browsers

## Backend Enhancements

- [ ] Add rate limiting to API endpoints
- [ ] Implement API versioning
- [ ] Add pagination to list endpoints
- [ ] Create admin dashboard for lot management
- [ ] Add email verification for user registration
- [ ] Implement password reset functionality

## Simulation & IoT

- [x] Real-time simulation with daily schedule patterns (`simulate_realtime` command)
- [ ] Add configurable schedules per lot (different patterns for different lots)
- [ ] Create event-based simulation (game day parking restrictions)
- [ ] Add occupancy history logging to database
- [ ] MQTT integration for real IoT sensors

## Testing

- [x] Unit tests for all models
- [x] API endpoint tests
- [x] Authentication tests
- [ ] WebSocket consumer tests
- [ ] Frontend component tests (React Testing Library)
- [ ] End-to-end tests (Cypress or Playwright)
- [ ] Load testing for API endpoints

## CI/CD

- [x] GitHub Actions workflow for backend tests
- [x] Frontend build verification
- [x] Code linting (Ruff for Python, ESLint for JS)
- [x] Security scanning (Bandit, Safety)
- [x] Docker build verification
- [ ] Automated deployment to staging
- [ ] Production deployment pipeline
- [ ] Database migration checks in CI

## Documentation

- [ ] API documentation (Swagger/OpenAPI)
- [ ] Developer setup guide improvements
- [ ] Architecture decision records (ADRs)
- [ ] Contributing guidelines

## Database & Performance

- [ ] Add database indexes for frequently queried fields
- [ ] Implement caching (Redis) for dashboard data
- [ ] Database connection pooling for production
- [ ] Query optimization for large datasets

## Security

- [ ] Add CSRF protection for non-API views
- [ ] Implement request signing for IoT sensors
- [ ] Add audit logging for admin actions
- [ ] Security headers configuration
- [ ] Input validation improvements

## DevOps

- [ ] Kubernetes deployment manifests
- [ ] Terraform infrastructure as code
- [ ] Monitoring and alerting (Prometheus/Grafana)
- [ ] Centralized logging (ELK stack)
- [ ] Health check endpoints

---

## Priority Legend

High priority items to tackle first:
1. Switch frontend to WebSocket (infrastructure ready)
2. Historical occupancy charts (valuable feature)
3. API documentation (developer experience)
4. Frontend tests (code quality)
