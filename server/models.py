from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    # Add serialization rules
    serialize_rules = ('-signups.activities',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship('Signup', back_populates='activities', cascade='all, delete-orphan')

    campers = association_proxy('signups', 'camper', creator=lambda camper_obj: Signup(camper=camper_obj))
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    # Add serialization rules
    serialize_rules = ('-signups.campers',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # Add relationship
    signups = db.relationship('Signup', back_populates='campers', cascade='all, delete-orphan')

    activities = association_proxy('signups', 'activity', creator=lambda activity_obj: Signup(activity=activity_obj))
    
    
    # Add validation
    @validates('name')
    def validate_name (self, key, value):
        if not value or not value.strip():
            raise ValueError('Name must be present and not empty.')
        return value
    
    @validates('age')
    def validate_age (self, key, value):
        if value is None:
            raise ValueError('Age must be provided.')
        
        if not (8 <= value <= 18):
            raise ValueError('Age must be integer between 8 and 18.')
        
        return value
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    # Add serialization rules
    serialize_rules = ('-activities.signups', '-campers.signups',)

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    
    # Add relationships
    activities = db.relationship('Activity', back_populates='signups')
    campers = db.relationship('Camper', back_populates='signups')
    
    # Add validation
    @validates('time')
    def validate_time(self, key, value):
        if 0 <= value <= 23:
            return value
        else:
            raise ValueError ('Time must be an integer between 0 and 23.')

    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
