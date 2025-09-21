# server/models.py
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
import bcrypt
from config import db

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)  # This must NOT be null
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    # Relationships
    recipes = db.relationship('Recipe', backref='user', cascade='all, delete-orphan')
    
    # Serialization rules
    serialize_rules = ('-recipes.user', '-_password_hash')
    
    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')
    
    @password_hash.setter
    def password_hash(self, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self._password_hash = bcrypt.hashpw(password, salt).decode('utf-8')
    
    def authenticate(self, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        return bcrypt.checkpw(password, self._password_hash.encode('utf-8'))
    
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username is required")
        if User.query.filter(User.username == username).first():
            raise ValueError("Username must be unique")
        return username
    
    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # This must NOT be null
    
    # Serialization rules
    serialize_rules = ('-user.recipes',)
    
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title is required")
        return title
    
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions:
            raise ValueError("Instructions are required")
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return instructions
    
    def __repr__(self):
        return f'<Recipe {self.title}>'