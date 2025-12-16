"""Taskiq broker configuration."""

import sentry_sdk
from core.settings import sentry_settings, redis_settings
from domain.taskiq_middleware import ProgressStateMiddleware
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

if sentry_settings.enabled:
    sentry_sdk.init(
        dsn=sentry_settings.dsn,
        send_default_pii=True,
        traces_sample_rate=1.0,
    )

# Redis connection URL for broker
REDIS_URL = f"redis://{redis_settings.host}:{redis_settings.port}/0"

# Create result backend
result_backend = RedisAsyncResultBackend(REDIS_URL)

# Create broker with result backend and middleware
broker = (
    ListQueueBroker(REDIS_URL)
    .with_result_backend(result_backend)
    .with_middlewares(ProgressStateMiddleware())
)
