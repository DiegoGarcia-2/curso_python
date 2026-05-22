"""Extensiones compartidas de Flask para evitar importaciones circulares."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
