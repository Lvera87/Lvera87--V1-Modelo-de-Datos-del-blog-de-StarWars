# src/models.py
# Importaciones necesarias de Flask-SQLAlchemy y SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List # Para type hints en relaciones

# Inicialización de la extensión SQLAlchemy.
# En tu aplicación Flask, deberías inicializarla así:
# from flask import Flask
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db' # O tu URL de conexión
# db = SQLAlchemy(app)
# Por ahora, solo creamos la instancia base:
db = SQLAlchemy()

# --- Definición de Modelos ---

class User(db.Model):
    """
    Modelo para los usuarios registrados en el blog.
    """
    __tablename__ = "users" # Nombre explícito de la tabla

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False) # Guardar hash de contraseña, no texto plano
    first_name: Mapped[str] = mapped_column(String(80), nullable=True)
    last_name: Mapped[str] = mapped_column(String(80), nullable=True)
    subscription_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False) # Campo opcional para activar/desactivar usuarios

    # --- Relaciones ---
    # Relación con los planetas favoritos del usuario (a través de FavoritePlanet)
    favorite_planets: Mapped[List["FavoritePlanet"]] = relationship("FavoritePlanet", back_populates="user", cascade="all, delete-orphan")
    # Relación con los personajes favoritos del usuario (a través de FavoritePerson)
    favorite_people: Mapped[List["FavoritePerson"]] = relationship("FavoritePerson", back_populates="user", cascade="all, delete-orphan")
    # Relación con los vehículos favoritos del usuario (a través de FavoriteVehicle) - NUEVO
    favorite_vehicles: Mapped[List["FavoriteVehicle"]] = relationship("FavoriteVehicle", back_populates="user", cascade="all, delete-orphan")


    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        """Convierte el objeto User a un diccionario simple."""
        # Nota: Nunca serializar la contraseña.
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "subscription_date": self.subscription_date.isoformat() if self.subscription_date else None,
            "is_active": self.is_active,
            # Incluimos listas de IDs de favoritos
            "favorite_planet_ids": [fav.planet_id for fav in self.favorite_planets], # ojo esto es un bucle hay que estudiar mas 
            "favorite_person_ids": [fav.person_id for fav in self.favorite_people],
            "favorite_vehicle_ids": [fav.vehicle_id for fav in self.favorite_vehicles] # NUEVO
        }

class Planet(db.Model):
    """
    Modelo para almacenar información de los Planetas de Star Wars.
    Basado en la estructura de SWAPI.
    """
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    diameter: Mapped[str] = mapped_column(String(40), nullable=True)
    rotation_period: Mapped[str] = mapped_column(String(40), nullable=True)
    orbital_period: Mapped[str] = mapped_column(String(40), nullable=True)
    gravity: Mapped[str] = mapped_column(String(40), nullable=True)
    population: Mapped[str] = mapped_column(String(40), nullable=True)
    climate: Mapped[str] = mapped_column(String(100), nullable=True)
    terrain: Mapped[str] = mapped_column(String(100), nullable=True)
    surface_water: Mapped[str] = mapped_column(String(40), nullable=True)

    # --- Relaciones ---
    # Relación con los usuarios que han marcado este planeta como favorito
    favorited_by: Mapped[List["FavoritePlanet"]] = relationship("FavoritePlanet", back_populates="planet", cascade="all, delete-orphan")
    # Relación con los personajes que tienen este planeta como hogar (homeworld)
    residents: Mapped[List["Person"]] = relationship("Person", back_populates="homeworld")

    def __repr__(self):
        return f'<Planet {self.name}>'

    def serialize(self):
        """Convierte el objeto Planet a un diccionario simple."""
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "gravity": self.gravity,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "resident_ids": [resident.id for resident in self.residents]
        }

class Person(db.Model):
    """
    Modelo para almacenar información de los Personajes (People) de Star Wars.
    Basado en la estructura de SWAPI.
    """
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    height: Mapped[str] = mapped_column(String(20), nullable=True)
    mass: Mapped[str] = mapped_column(String(20), nullable=True)
    hair_color: Mapped[str] = mapped_column(String(50), nullable=True)
    skin_color: Mapped[str] = mapped_column(String(50), nullable=True)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=True)
    birth_year: Mapped[str] = mapped_column(String(20), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)

    # --- Claves Foráneas ---
    homeworld_id: Mapped[int] = mapped_column(Integer, ForeignKey("planets.id"), nullable=True)

    # --- Relaciones ---
    homeworld: Mapped["Planet"] = relationship("Planet", back_populates="residents")
    favorited_by: Mapped[List["FavoritePerson"]] = relationship("FavoritePerson", back_populates="person", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Person {self.name}>'

    def serialize(self):
        """Convierte el objeto Person a un diccionario simple."""
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "homeworld_id": self.homeworld_id,
        }

# --- NUEVO: Modelo Vehicle ---
class Vehicle(db.Model):
    """
    Modelo para almacenar información de los Vehículos de Star Wars.
    Basado en la estructura de SWAPI.
    """
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(200), nullable=False)
    cost_in_credits: Mapped[str] = mapped_column(String(40), nullable=True)
    length: Mapped[str] = mapped_column(String(20), nullable=True)
    max_atmosphering_speed: Mapped[str] = mapped_column(String(40), nullable=True)
    crew: Mapped[str] = mapped_column(String(40), nullable=True)
    passengers: Mapped[str] = mapped_column(String(40), nullable=True)
    cargo_capacity: Mapped[str] = mapped_column(String(40), nullable=True)
    consumables: Mapped[str] = mapped_column(String(40), nullable=True)
    vehicle_class: Mapped[str] = mapped_column(String(80), nullable=True)

    # --- Relaciones ---
    # Relación con los usuarios que han marcado este vehículo como favorito
    favorited_by: Mapped[List["FavoriteVehicle"]] = relationship("FavoriteVehicle", back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Vehicle {self.name}>'

    def serialize(self):
        """Convierte el objeto Vehicle a un diccionario simple."""
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "cost_in_credits": self.cost_in_credits,
            "length": self.length,
            "max_atmosphering_speed": self.max_atmosphering_speed,
            "crew": self.crew,
            "passengers": self.passengers,
            "cargo_capacity": self.cargo_capacity,
            "consumables": self.consumables,
            "vehicle_class": self.vehicle_class,
        }


# --- Modelos de Asociación para Favoritos ---

class FavoritePlanet(db.Model):
    """
    Modelo de asociación para registrar los planetas favoritos de cada usuario.
    """
    __tablename__ = "favorite_planets"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    planet_id: Mapped[int] = mapped_column(Integer, ForeignKey("planets.id"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="favorite_planets")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="favorited_by")

    def __repr__(self):
        return f'<FavoritePlanet User {self.user_id} -> Planet {self.planet_id}>'

    def serialize(self):
        """Convierte el objeto FavoritePlanet a un diccionario simple."""
        return {
            "user_id": self.user_id,
            "planet_id": self.planet_id,
        }

class FavoritePerson(db.Model):
    """
    Modelo de asociación para registrar los personajes favoritos de cada usuario.
    """
    __tablename__ = "favorite_people"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("people.id"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="favorite_people")
    person: Mapped["Person"] = relationship("Person", back_populates="favorited_by")

    def __repr__(self):
        return f'<FavoritePerson User {self.user_id} -> Person {self.person_id}>'

    def serialize(self):
        """Convierte el objeto FavoritePerson a un diccionario simple."""
        return {
            "user_id": self.user_id,
            "person_id": self.person_id,
        }

# --- NUEVO: Modelo FavoriteVehicle ---
class FavoriteVehicle(db.Model):
    """
    Modelo de asociación para registrar los vehículos favoritos de cada usuario.
    Implementa la relación Muchos-a-Muchos entre User y Vehicle.
    """
    __tablename__ = "favorite_vehicles"

    # Clave primaria compuesta
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), primary_key=True)
    # added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) # Opcional

    # --- Relaciones ---
    user: Mapped["User"] = relationship("User", back_populates="favorite_vehicles")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="favorited_by")

    def __repr__(self):
        return f'<FavoriteVehicle User {self.user_id} -> Vehicle {self.vehicle_id}>'

    def serialize(self):
        """Convierte el objeto FavoriteVehicle a un diccionario simple."""
        return {
            "user_id": self.user_id,
            "vehicle_id": self.vehicle_id,
            # Podrías serializar el objeto vehículo completo si es necesario
            # "vehicle_details": self.vehicle.serialize() if self.vehicle else None
        }

# --- Fin de los Modelos ---

# Para generar el diagrama (después de instalar eralchemy2 u otra herramienta similar):
# $ pipenv run eralchemy2 -i sqlite:///mydatabase.db -o diagram.png  (Ajusta la URI de tu DB)

