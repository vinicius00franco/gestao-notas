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

### Testing
- Write comprehensive unit and integration tests for models, serializers, and views
- Use Django's TestCase and APITestCase
- Test authentication and permissions
- Mock external dependencies

### Performance
- Use select_related and prefetch_related for optimization
- Implement caching where appropriate
- Use pagination to limit response size
- Optimize database queries

### Migrations (SQL-first guidelines)
- Prefer raw SQL migrations (use `migrations.RunSQL`) when a change must be applied atomically and idempotently across different environments (local, CI, production).
- Write SQL migrations defensively using `IF NOT EXISTS` / `ADD COLUMN IF NOT EXISTS` and safe `UPDATE` statements to avoid duplicate-column or constraint errors when applying to databases that may already have parts of the schema.
- Keep schema-changing SQL in a separate `.sql` file and load it in the migration (example pattern exists in `apps/empresa/migrations/0003_add_senha_hash.py`).
- Avoid mixing raw SQL and Django `AddField`/`AlterField` for the same column; if you add a column with SQL, do not later add it again with Django operations.
- When adding columns via SQL, initialize values (e.g., `UPDATE ... SET col = '' WHERE col IS NULL`) to maintain compatibility with NOT NULL constraints applied later.
- For complex migrations that depend on data transformation, split into smaller steps: (1) add nullable column via RunSQL, (2) backfill data, (3) alter to NOT NULL using another RunSQL after verification.
- Document the intention of each SQL migration in the migration file and include idempotency notes so other developers understand safety considerations.

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