from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from ..models import BaseModel
from ..models import Domain

__all__ = ['BaseModel', 'Domain']
