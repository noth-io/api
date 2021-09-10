from fastapi import APIRouter, Body, Depends, HTTPException, Cookie, Response, Request
from api import deps
from sqlalchemy.orm import Session
from crud import user as user_crud, credential as credential_crud
import models, schemas
from typing import Any, List
from utils.fido2.webauthn import PublicKeyCredentialRpEntity
from utils.fido2.client import ClientData
from utils.fido2.server import Fido2Server
from utils.fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from utils.fido2 import cbor
from core.config import settings
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import base64

router = APIRouter()

# Fido 2 variables
rp = PublicKeyCredentialRpEntity(settings.FIDO2_RP, settings.FIDO2_NAME)
server = Fido2Server(rp)
credentials = []
s = URLSafeTimedSerializer(settings.FIDO2_STATE_SECRET_KEY)

# GET ALL CURRENT USER FIDO 2 CREDENTIALS
@router.get("", response_model=List[schemas.Fido2Credential])
def get_user_fido2_credentials(db: Session = Depends(deps.get_db), user: schemas.User = Depends(deps.get_current_user_from_cookie)):
    #print(credential_crud.get_fido2credentials(db, user_id=user.id))
    return credential_crud.get_fido2credentials(db, user_id=user.id)

# REGISTER FIDO2 CREDENTIAL : BEGIN
@router.post("/register/begin")
def begin_register_fido2_credentials(request: Request, db: Session = Depends(deps.get_db), user: schemas.User = Depends(deps.get_current_user_from_cookie)):
    # Check if Android with user agent
    if "Android" in request.headers['User-Agent']:
        authenticator_attachment = "platform"
    else:
        authenticator_attachment = "cross-platform"

    registration_data, state = server.register_begin(
        {
            "id": bytes(user.id),
            "name": user.username,
            "displayName": user.firstname,
            "icon": "https://example.com/image.png",
        },
        credentials,
        user_verification="discouraged",
        authenticator_attachment=authenticator_attachment,
        resident_key="False"
    )

    #print("\n\n\n\n")
    #print(registration_data)
    #print("\n\n\n\n")
    response = Response(content=cbor.encode(registration_data))
    response.set_cookie("fido2register", value=s.dumps(state, salt='fido2register'), secure=True, max_age=120)
    return response 

# REGISTER FIDO2 CREDENTIAL : COMPLETE
@router.post("/register/complete")
async def complete_register_fido2_credentials(request: Request, db: Session = Depends(deps.get_db), user: schemas.User = Depends(deps.get_current_user_from_cookie)):
    # GET fido2registercookie
    state = s.loads(request.cookies.get('fido2register'), salt='fido2register', max_age=60)

    data = cbor.decode(await request.body())
    client_data = ClientData(data["clientDataJSON"])
    att_obj = AttestationObject(data["attestationObject"])
    #print("clientData", client_data)
    #print("AttestationObject:", att_obj)

    auth_data = server.register_complete(state, client_data, att_obj)

    # INSERT in DB
    #print(auth_data.credential_data) 
    #print(base64.b64encode(auth_data.credential_data))
    credential_crud.create_fido2credential(db, user_id=user.id, attestation=base64.b64encode(auth_data.credential_data))

    #print("REGISTERED CREDENTIAL:", auth_data.credential_data)
    response = Response(content=cbor.encode({"status": "OK"}))
    response.set_cookie("fido2register", secure=True, expires=0)
    return response 
"""
@router.post("", response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session = Depends(deps.get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return user_crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}")
def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    db_user = user_crud.delete_user(db, user_id=user_id)
    if db_user is False:
        raise HTTPException(status_code=404, detail="User not found")
    return { "message": "user deleted" }
"""


"""
# Fido 2 variables
rp = PublicKeyCredentialRpEntity(FIDO2_RP, FIDO2_NAME)
server = Fido2Server(rp)
credentials = []
s = URLSafeTimedSerializer(FIDO2STATE_SECRET)

@api.route('')
class FIDO2Creds(Resource):
    # Get all FIDO2 credentials for authenticated user
    @jwt_required(locations=["cookies"])
    def get(self):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        creds = Fido2Credential.query.filter_by(user_id=user.id)
        response = []
        for cred in creds:
            response.append(cred.json())

        resp = Response(response=json.dumps(response, default=str), status=200, mimetype="application/json")
        return resp



@api.route('/register/complete')
class Fido2RegisterComplete(Resource):
    @jwt_required(locations=["cookies"])
    def post(self):

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401)

        
        state = s.loads(request.cookies.get('fido2register'), salt='fido2register', max_age=60)

        data = cbor.decode(request.get_data())
        client_data = ClientData(data["clientDataJSON"])
        att_obj = AttestationObject(data["attestationObject"])
        print("clientData", client_data)
        print("AttestationObject:", att_obj)

        auth_data = server.register_complete(state, client_data, att_obj)

        # Add credential to DB
        db.session.add(Fido2Credential(attestation=auth_data.credential_data, user_id=user.id))
        db.session.commit()   

        print("REGISTERED CREDENTIAL:", auth_data.credential_data)
        msg = Response(response=cbor.encode({"status": "OK"}))
        msg.set_cookie("fido2register", "", secure=True, expires=0)
        return msg
"""