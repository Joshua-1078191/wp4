from database import engine
from models import Basis

Basis.metadata.create_all(bind=engine)