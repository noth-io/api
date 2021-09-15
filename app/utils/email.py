from fastapi import HTTPException
import requests, json
import schemas
from core.config import settings

def send(user: schemas.User, type: str, token: str):
    if type == "confirm":
        subject = "User email confirmation"
        htmlContent = "<html><head></head><body><a href='%s/register/confirm/%s'>Click here to confirm your email</a></body></html>" % (settings.NOTH_UI_URL, token)

    if type == "authentication":
        subject = "User authentication email"
        htmlContent = "<html><head></head><body><a href='%s/login/mail/%s'>Click here to authenticate</a></body></html>" % (settings.NOTH_UI_URL, token)

    # Build mail API Call
    headers = { "accept": "application/json", "api-key": settings.MAIL_API_KEY, "content-type": "application/json" }
    payload = {  
        "sender": {  
            "name": settings.MAIL_SENDER_NAME,
            "email": settings.MAIL_SENDER_EMAIL
        },
        "to": [  
            {  
                "email": user.email,
                "name": "%s %s" % (user.firstname, user.lastname)
            }
        ],
        "subject": subject,
        "htmlContent": htmlContent
    }

    # Send mail
    r = requests.post(settings.MAIL_API_URL, headers=headers, data=json.dumps(payload))
    if r.status_code != 201:
        raise HTTPException(status_code=500)