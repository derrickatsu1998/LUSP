# ============================================================
# SESSION SECURITY
# ============================================================

# Required for django-session-security
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_WARN_AFTER = 840   # 14 minutes (warn user)
SESSION_SECURITY_EXPIRE_AFTER = 900  # 15 minutes (auto logout)

# Fallback for session_security - required to prevent errors
if not SESSION_EXPIRE_AT_BROWSER_CLOSE:
    # This is only reached if SESSION_EXPIRE_AT_BROWSER_CLOSE is False
    # but we set it to True above, so this is safe
    pass

# Optional: Disable session security warnings during build
import sys
if 'manage.py' in sys.argv[0] and 'collectstatic' in sys.argv:
    # During collectstatic, we don't need session security
    SESSION_SECURITY_INSECURE = True