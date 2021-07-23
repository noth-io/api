from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    firstname = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    fido2credential = db.relationship("Fido2Credential")

    def json (self):
        json = {}
        json['id'] = self.id
        json['username'] = self.username
        json['email'] = self.email
        json['firstname'] = self.firstname
        json['surname'] = self.surname
        return json

    def __repr__(self):
        return '<User %r>' % self.username

class Fido2Credential(db.Model):
    __tablename__ = 'fido2credential'
    id = db.Column(db.Integer, primary_key=True)
    attestation = db.Column(db.LargeBinary, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '%s' % self.attestation
