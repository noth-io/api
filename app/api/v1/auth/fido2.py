from utils.fido2.webauthn import PublicKeyCredentialRpEntity
from utils.fido2.client import ClientData
from utils.fido2.server import Fido2Server
from utils.fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from utils.fido2 import cbor
import models, schemas
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from core.config import settings
from fastapi import APIRouter, Body, Depends, HTTPException, Cookie, Response, Request
from api import deps
from crud import user as user_crud, credential as credential_crud
from sqlalchemy.orm import Session
import base64
from core import security, responses
from fastapi.responses import JSONResponse

router = APIRouter()

# Fido 2 variables
rp = PublicKeyCredentialRpEntity(settings.FIDO2_RP, settings.FIDO2_NAME)
server = Fido2Server(rp)
credentials = []
s = URLSafeTimedSerializer(settings.FIDO2_STATE_SECRET_KEY)

fido2_level = 4
fido2_step = 4

@router.post("/begin")
def begin_fido2_authentication(db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user), token_data: schemas.AuthTokenPayload = Depends(deps.get_current_authtoken)):

    # Check token step
    #if token_data.nextstep != 20:
    #    raise HTTPException(status_code=400, detail="Invalid authentication token step")

    # Get credential from DB
    db_fido2credentials = credential_crud.get_fido2credentials(db, user_id=user.id)
    if not db_fido2credentials:
        raise HTTPException(status_code=404, detail="no fido2 credential registered")
    for db_fido2credential in db_fido2credentials:
        #print(base64.b64decode(db_fido2credential.attestation))
        credentials.append(AttestedCredentialData(base64.b64decode(db_fido2credential.attestation)))

    auth_data, state = server.authenticate_begin(credentials,user_verification="discouraged")
    #print(state)
    #session["state"] = state
    #print(session)
    print("\n\n\n\n")
    print(auth_data)
    print("\n\n\n\n")

    response = Response(content=cbor.encode(auth_data))
    response.set_cookie("fido2auth", value=s.dumps(state, salt='fido2auth'), secure=True, max_age=120)
    return response

@router.post("/complete")
async def complete_fido2_authentication(request: Request, db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user), token_data: schemas.AuthTokenPayload = Depends(deps.get_current_authtoken)):

    # Check token step
    #if token_data.nextstep != 20:
    #    raise HTTPException(status_code=400, detail="Invalid authentication token step")

    # Get credential from DB
    db_fido2credentials = credential_crud.get_fido2credentials(db, user_id=user.id)
    if not db_fido2credentials:
        raise HTTPException(status_code=404, detail="no fido2 credential registered")
    for db_fido2credential in db_fido2credentials:
        #print(base64.b64decode(db_fido2credential.attestation))
        credentials.append(AttestedCredentialData(base64.b64decode(db_fido2credential.attestation)))

    print(await request.body())
    data = cbor.decode(await request.body())
    credential_id = data["credentialId"]
    client_data = ClientData(data["clientDataJSON"])
    auth_data = AuthenticatorData(data["authenticatorData"])
    signature = data["signature"]
    print("clientData", client_data)
    print("AuthenticatorData", auth_data)

    state = s.loads(request.cookies.get('fido2auth'), salt='fido2auth', max_age=60)

    server.authenticate_complete(
        state,
        credentials,
        credential_id,
        client_data,
        auth_data,
        signature,
    )

    session_token = security.create_session_token(user.email, loa=3)
    content = { "authenticated": True }
    response = JSONResponse(content=content)
    response.set_cookie(key="session", value=session_token, secure=True, domain=settings.COOKIE_DOMAIN, httponly=True)
    response.set_cookie(key="authenticated", value=True, secure=True, domain=settings.COOKIE_DOMAIN)
    response.set_cookie(key="username", value=user.email, secure=True, domain=settings.COOKIE_DOMAIN)
    return response