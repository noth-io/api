# coding=utf-8
import os

# ENV
ENV = os.getenv('NOTH_API_ENV')

# API
NOTH_UI_URL = os.getenv('NOTH_UI_URL')
AUTHENTICATED_COOKIE_DOMAIN = os.getenv('NOTH_API_AUTHENTICATED_COOKIE_DOMAIN')

# SESSION
FIDO2STATE_SECRET = os.getenv('NOTH_API_SESSION_SECRET_KEY')

# FIDO 2 RP CONFIG
FIDO2_NAME = os.getenv('NOTH_API_FIDO2_NAME')
FIDO2_RP = os.getenv('NOTH_API_FIDO2_RP')

# MAIL
MAIL_SENDER_NAME = os.getenv('NOTH_API_MAIL_SENDER_NAME')
MAIL_SENDER_EMAIL = os.getenv('NOTH_API_MAIL_SENDER_EMAIL')
MAIL_API_URL = os.getenv('NOTH_API_MAIL_API_URL')
MAIL_API_KEY = os.getenv('NOTH_API_MAIL_API_KEY')
MAIL_TOKEN_CONFIRM_SECRET = os.getenv('NOTH_API_MAIL_TOKEN_CONFIRM_SECRET')
MAIL_TOKEN_AUTHENTICATION_SECRET = os.getenv('NOTH_API_MAIL_TOKEN_AUTHENTICATION_SECRET')

# DB
DB_URL = os.getenv('NOTH_API_DB_URL')
DB_NAME = os.getenv('NOTH_API_DB_NAME')
DB_USER = os.getenv('NOTH_API_DB_USER')
DB_PASSWORD = os.getenv('NOTH_API_DB_PASSWORD')

# OAUTH2
OAUTH2_JWT_ENABLED = True
OAUTH2_JWT_ISS = 'https://authlib.org'
OAUTH2_JWT_KEY = 'secret-key'
OAUTH2_JWT_ALG = 'HS256'
OAUTH2_CONSENT_TOKEN_SECRET = 'secret'
OAUTH2_CONSENT_LIFETIME = 300
OAUTH2_CONSENT_UI_PATH = os.getenv('NOTH_UI_OAUTH2_CONSENT_UI_PATH')

# OTP
OTP_LIFETIME = os.getenv('NOTH_API_OTP_LIFETIME')

