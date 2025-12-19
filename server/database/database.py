from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    StringField,
    DateTimeField,
    ListField,
    IntField,
    signals,
    ValidationError,
    connect
)

from datetime import datetime, timedelta
import os, re, uuid

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")
connect(host=MONGO_URI)

PHONE_RE = re.compile(r'^09\d{9}$')
OTP_TTL = timedelta(minutes=3)
TOKEN_TTL = timedelta(days=3)

def generate_uid():
    return uuid.uuid4().hex

def _pre_save_update_timestamp(sender, document, **kwargs):
    document.updated_at = datetime.utcnow()
    if hasattr(document, 'uid') and not document.uid:
        document.uid = generate_uid()

class BaseUser(Document):
    meta = {'abstract': True}
    
    uid = StringField(required=True, unique=True)
    number = StringField(required=True, regex=PHONE_RE)
    fname = StringField(max_length=70)
    lname = StringField(max_length=70)
    gender = StringField(choices=("man", "woman"), required=False)
    age = IntField(min_value=10, max_value=99)

    otp = StringField(null=True)
    otp_set_at = DateTimeField(null=True)
    token = StringField(null=True)
    token_set_at = DateTimeField(null=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    @property
    def otp_value(self):
        if self.otp and self.otp_set_at and datetime.utcnow() - self.otp_set_at > OTP_TTL:
            self.otp, self.otp_set_at = None, None
            self.save()
        return self.otp

    @property
    def token_value(self):
        if self.token and self.token_set_at and datetime.utcnow() - self.token_set_at > TOKEN_TTL:
            self.token, self.token_set_at = None, None
            self.save()
        return self.token

    def clean(self):
        self.updated_at = datetime.utcnow()

        if not getattr(self, 'uid', None):
            self.uid = generate_uid()

        if self.age is not None and not (10 <= self.age <= 99):
            raise ValidationError("age must be two digits (10–99).")

        if not PHONE_RE.match(self.number or ""):
            raise ValidationError("number must start with 09 and be 11 digits.")

        if self.fname:
            self.fname = self.fname.lower()
        if self.lname:
            self.lname = self.lname.lower()
        if self.gender:
            self.gender = self.gender.lower()

class User(BaseUser):
    meta = {'collection': 'users'}

class Specialties(BaseUser):
    meta = {'collection': 'specialties'}
    tag = ListField(StringField(), default=list)  
    about = StringField(max_length=250, default="")
    educert = StringField(max_length=150, default="")
    available_slots = ListField(StringField())
    def clean(self):
        super().clean()

        if self.educert:
            self.educert = self.educert.lower()
        if self.about:
            self.about = self.about.lower()
        valid_tags = {"law", "edu"}
        if not self.tag:
            raise ValidationError("tag is required for specialists")
        if len(self.tag) != 1:
            raise ValidationError("only one tag is allowed")
        tag_lower = self.tag[0].lower()
        if tag_lower not in valid_tags:
            raise ValidationError("tag must be 'law' or 'edu'")
        self.tag = [tag_lower] 

signals.pre_save.connect(_pre_save_update_timestamp, sender=User)
signals.pre_save.connect(_pre_save_update_timestamp, sender=Specialties)
