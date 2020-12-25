from flask_sqlalchemy import SQLAlchemy

from . import DomainRepository

db = SQLAlchemy()
__all__ = ['DomainRepository']
