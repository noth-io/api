from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Fido2Credential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attestation = db.Column(db.LargeBinary, unique=True, nullable=False)

    def __repr__(self):
        return '%s' % self.attestation
