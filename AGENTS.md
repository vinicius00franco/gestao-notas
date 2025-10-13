---
applyTo: "**"
---
# Project general coding standards

## Naming Conventions
- Use PascalCase for component names, interfaces, and type aliases
- Use camelCase for variables, functions, and methods
- Prefix private class members with underscore (_)
- Use ALL_CAPS for constants

## Error Handling
- Use try/catch blocks for async operations
- Implement proper error boundaries in React components
- Always log errors with contextual information

## Logging Standards for Refactoring and Implementation

### Mandatory Logging Requirements
- **All refactoring and new implementations MUST include relevant logs**
- Add structured logs at key execution points (start, success, failure, important state changes)
- Use appropriate log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include contextual information: user_id, request_id, operation_type, execution_time
- Log business-critical operations and data transformations

### Log Format Standards
```python
# Django logging example
import logging
logger = logging.getLogger(__name__)

# Success operations
logger.info("Operation completed", extra={
    'operation': 'nota_fiscal_processing',
    'job_uuid': str(job.uuid),
    'execution_time_ms': execution_time,
    'status': 'success'
})

# Error operations
logger.error("Operation failed", extra={
    'operation': 'nota_fiscal_processing',
    'job_uuid': str(job.uuid),
    'error': str(e),
    'status': 'error'
})
```

### Validation and Testing Using Grafana Logs
- **Use Grafana dashboard (http://localhost:3000) to validate implementations**
- Monitor logs during development and testing phases
- Verify log patterns match expected behavior
- Use log queries to troubleshoot issues:

```
# Monitor specific operations
{container_name="django_api"} |= "nota_fiscal_processing"

# Check error patterns
{container_name="django_api"} |= "ERROR" |= "operation"

# Monitor performance
{container_name="django_api"} |= "execution_time_ms"
```

### Testing Validation Process
1. **Before testing**: Check baseline logs in Grafana
2. **During testing**: Monitor real-time logs for expected patterns
3. **After testing**: Verify log completeness and accuracy
4. **Error scenarios**: Ensure error logs provide sufficient debugging information

## Django REST API Best Practices

### Models
- Use descriptive names for models and fields
- Include UUID fields for unique identification and API exposure
- Implement proper relationships (ForeignKey, ManyToMany, etc.)
- Add Meta class with db_table, indexes, constraints, and verbose_name
- Use validators for field validation where appropriate
- Implement __str__ method for readable representations

### Serializers
- Use ModelSerializer for database models
- Validate data in serializers using validate methods
- Handle nested serializers for complex relationships
- Use depth parameter for automatic nested serialization
- Use SerializerMethodField for computed fields
- Implement create and update methods when needed

### Views and ViewSets
- Use generics views (e.g., ListAPIView, RetrieveAPIView) or APIView for operations
- Implement proper permissions classes
- Use select_related and prefetch_related in querysets for optimization
- Use pagination for list views
- Handle exceptions with try/except blocks
- Return appropriate HTTP status codes
- Use action decorators for custom endpoints

### Authentication and Permissions
- Implement custom JWT authentication classes for specific use cases
- Use token-based authentication (JWT preferred)
- Use AllowAny as default permission class, with custom permissions where needed
- Secure sensitive endpoints
- Validate user permissions in views

### API Design
- Follow RESTful conventions
- Use consistent URL patterns
- Implement proper HTTP methods (GET, POST, PUT, DELETE)
- Expose UUID fields instead of numeric IDs in API responses
- Use query parameters for filtering and searching
- Return consistent JSON responses

### Error Handling
- Use Django's built-in exception handling
- Implement custom exception classes
- Return meaningful error messages
- Log errors for debugging
- **MANDATORY**: Add structured logs for all API operations
- Include request context in error logs (user, endpoint, parameters)
- Log performance metrics for slow operations (>1s execution time)

### Testing
- Write comprehensive unit and integration tests for models, serializers, and views
- Use Django's TestCase and APITestCase
- Test authentication and permissions
- Mock external dependencies
- **MANDATORY**: Validate test results using Grafana logs
- Monitor log patterns during test execution
- Verify error handling produces expected log entries
- Use log queries to confirm test scenarios:
  ```
  # Test-specific logs
  {container_name="django_api"} |= "test_" |= "operation"
  
  # Integration test validation
  {container_name="django_api"} |= "integration_test"
  ```

### Performance
- Use select_related and prefetch_related for optimization
- Implement caching where appropriate
- Use pagination to limit response size
- Optimize database queries

### Migrations (Django ORM approach)
- Use Django's built-in migration system (`makemigrations` and `migrate`)
- Keep migrations in sync with model changes
- Run `makemigrations` after model changes and `migrate` to apply them
- Use descriptive migration names when creating migrations manually

## React Native Best Practices

### Component Structure
- Use functional components with hooks
- Separate business logic from presentation using container/presentational pattern
- Use TypeScript for type safety
- Implement proper component composition
- Use class components only for error boundaries
- Create reusable UI components in a dedicated components folder

### State Management
- Use Zustand for global state management
- Use TanStack React Query for server state and caching
- Use useState for local component state
- Avoid prop drilling with proper state management
- Implement state persistence when needed
- Create custom hooks for reusable business logic

### Navigation
- Use React Navigation library with bottom tabs and stack navigators
- Implement proper navigation structure
- Handle deep linking
- Use navigation guards for protected routes

### Performance
- Optimize images and assets
- Use FlatList with proper keyExtractor
- Implement memoization with useMemo and useCallback
- Avoid unnecessary re-renders
- Use Hermes engine optimizations

### Error Handling
- Implement error boundaries for crash protection
- Handle network errors gracefully with React Query
- Provide user-friendly error messages
- Log errors for debugging

### Styling and Design System
- Use StyleSheet for consistent styling
- Implement a centralized design system with tokens (colors, spacing, typography, shadows)
- Create a theme provider for dynamic theming support
- Use consistent spacing, colors, and typography across components
- Implement responsive design with scalable units
- Use platform-specific styles when needed
- Follow design system guidelines with theme colors and component variants

### Testing
- Write unit tests with Jest
- Test components with React Native Testing Library
- Implement integration tests
- Test on multiple devices and OS versions

### Security
- Secure sensitive data storage
- Implement proper authentication flows
- Validate user inputs
- Use HTTPS for API calls

### Code Organization and Maintainability
- Separate concerns with proper folder structure (components, screens, services, store, theme, types, hooks)
- Use custom hooks for reusable logic and side effects
- Implement proper import/export patterns
- Follow component naming conventions
- Use Expo for development and building
- Create utility functions and helpers for common operations
- Implement proper error boundaries and fallback UI
- Use TypeScript interfaces for type safety across components
- Maintain consistent code formatting and linting rules


## Testing Best Practices

Usar o banco de dados real mesmo para teste com diferença de usar transacoes no banco dados para modificar os dados e depois roolback em caso de testes dos endpoints e usar o banco de dados real (e nao de dteste ou algo do tipo) para criar as estruturas das tabelas

### Exemplo de teste usando curl

```bash
cd /home/vinicius/Downloads/estudo/engenharia-software/gestao_notas && curl -X POST http://localhost:8000/api/processar-nota/ -F "arquivo=@media/notas_fiscais_uploads/nota-fiscal.jpeg" -H "Content-Type: multipart/form-data"
```

## Database Information

**PostgreSQL Version:**
```
PostgreSQL 14.19 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
```

**Database Name:**
```
gestaonotas
```

**Commands to check database info:**
```bash
# Check PostgreSQL version
docker-compose -f infra/docker-compose.yml exec web python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT version()'); print(cursor.fetchone())"

# Check database name
docker-compose -f infra/docker-compose.yml exec web python manage.py shell -c "from django.db import connection; print('Database:', connection.settings_dict['NAME'])"
```

## Docker Containers

**Container Names:**
```
nginx
worker
web
db
rabbitmq
```

## Celery and Async Processing Logging

### Mandatory Celery Task Logging
- **All Celery tasks MUST include comprehensive logging**
- Log task start, progress, completion, and failure states
- Include task_id, job_uuid, and execution context
- Monitor worker performance and queue status

### Celery Log Examples
```python
# Task start
logger.info("Celery task started", extra={
    'task_name': 'processar_nota_fiscal_task',
    'task_id': self.request.id,
    'job_uuid': str(job_uuid),
    'worker': self.request.hostname
})

# Task completion
logger.info("Celery task completed", extra={
    'task_name': 'processar_nota_fiscal_task',
    'task_id': self.request.id,
    'job_uuid': str(job_uuid),
    'execution_time_ms': execution_time,
    'result': 'success'
})
```

### Monitoring Celery with Grafana
```
# Monitor worker activity
{container_name="celery_worker"} |= "task_name"

# Check task failures
{container_name="celery_worker"} |= "ERROR" |= "task_id"

# Monitor queue performance
{container_name="celery_worker"} |= "execution_time_ms"
```