# server/app.py
from flask import Flask, request, session, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, User, Recipe
from config import app, db, api

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            new_user = User(
                username=data.get('username'),
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            new_user.password_hash = data.get('password')
            
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            
            return new_user.to_dict(), 201
            
        except ValueError as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)  # FIXED: Using Session.get() instead of Query.get()
            if user:
                return user.to_dict(), 200
        
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter(User.username == username).first()
        
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return {}, 204
        
        return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        recipes = Recipe.query.all()
        return [recipe.to_dict() for recipe in recipes], 200
    
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        data = request.get_json()
        
        try:
            new_recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=user_id
            )
            
            db.session.add(new_recipe)
            db.session.commit()
            
            return new_recipe.to_dict(), 201
            
        except ValueError as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422

api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)