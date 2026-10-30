# MakeWeYarn – Database Setup Guide

## 1. Overview

MakeWeYarn uses PostgreSQL as its relational database for storing subscriber information, service plans, and subscription records.

## 2. Database Configuration

The application uses environment variables to establish its database connection.

Configure the following variables in the root `.env` file:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

**Security:** Never commit `.env` or expose database credentials in source control.

## 3. Database Tables

The application currently uses three core tables:

- `subscribers` – Stores subscriber information.
- `plans` – Stores available telecom service plans.
- `subscriptions` – Links subscribers to their selected plans.

## 4. Subscription Constraints

The subscriptions table enforces:

- A primary key on `id`.
- Foreign keys referencing `subscribers` and `plans`.
- A status constraint allowing only `active` and `cancelled`.

## 5. Preventing Duplicate Active Subscriptions

MakeWeYarn enforces a business rule that prevents a subscriber from having multiple active subscriptions to the same service plan.

PostgreSQL implements this using a partial unique index:

```sql
CREATE UNIQUE INDEX unique_active_subscription_per_plan
ON subscriptions (subscriber_id, plan_id)
WHERE status = 'active';
```

### How it works

- A subscriber can have only one active subscription to a particular plan.
- Cancelled subscriptions do not participate in the uniqueness rule.
- A subscriber can subscribe to the same plan again after cancellation.
- PostgreSQL independently enforces this rule, protecting against concurrent requests.

## 6. API-Level Validation

The Flask application checks for an existing active subscription before inserting a new record.

If a duplicate is detected, the API returns:

- HTTP status: `409 Conflict`
- Error: `Subscriber already has an active subscription to this plan.`

## 7. Database Verification

To inspect the subscriptions table and its indexes:

```bash
psql -U makeweyarn_user -d makeweyarn -c "\d subscriptions"
```

The expected index is:

`unique_active_subscription_per_plan`

## 8. Deployment Considerations

The partial unique index must be created in every new database environment after the subscriptions table has been created.

Database initialization or migration procedures should include this SQL statement to ensure consistent enforcement across development, testing, and production environments.