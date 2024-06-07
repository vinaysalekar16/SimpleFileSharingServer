import secrets

# Generate a random secret key
secret_key = secrets.token_urlsafe(16)  # Generates a 16-byte URL-safe random string

print("Secret Key:", secret_key)
