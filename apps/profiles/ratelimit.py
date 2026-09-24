from django.core.cache import cache


def get_client_ip(request):
    """
    Extracts the client IP address from the request, checking X-Forwarded-For
    for upstream proxy / load balancer termination (e.g. on Render).
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def is_rate_limited(request, action_key, max_attempts=5, timeout_seconds=600):
    """
    # SECURITY: Cache-based IP rate limiter for public forms.
    Caps submissions at max_attempts per IP per timeout_seconds (default: 5 per 10 mins).
    Returns True if throttled, False otherwise.
    """
    ip = get_client_ip(request)
    cache_key = f"rl:{action_key}:{ip}"
    try:
        current = cache.get(cache_key)
        if current is not None and current >= max_attempts:
            return True
        if current is None:
            cache.set(cache_key, 1, timeout=timeout_seconds)
        else:
            try:
                cache.incr(cache_key)
            except Exception:
                cache.set(cache_key, current + 1, timeout=timeout_seconds)
        return False
    except Exception:
        # Fail open if cache is unavailable so legitimate users are not blocked
        return False

