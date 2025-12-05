import sentry_sdk
from core.settings import sentry_settings


def init_sentry():
    if sentry_settings.enabled:
        sentry_sdk.init(
            dsn=sentry_settings.dsn,
            send_default_pii=True,
            traces_sample_rate=1.0,
        )
