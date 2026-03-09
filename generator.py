import secrets

SHORT_URL_LENGTH = 10
def generate_short_url():
    return secrets.token_urlsafe(SHORT_URL_LENGTH)
