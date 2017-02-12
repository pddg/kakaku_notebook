from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from .base import Base


class NoteBook(Base):
    __tablename__ = "notepc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    manufacturer = Column(String)
    inch = Column(Float)
    weight = Column(Float)
    width = Column(Float)
    height = Column(Float)
    depth = Column(Float)
    battery = Column(Float)
    memory = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, name: str, manufacturer: str, inch: float, weight: float=0.0,
                 width: float=0.0, height: float=0.0, depth: float=0.0, battery: float=0.0, memory: int=0):
        self.name = name
        self.manufacturer = manufacturer
        self.inch = inch
        self.weight = weight
        self.width = width
        self.height = height
        self.depth = depth
        self.battery = battery
        self.memory = memory

    def __repr__(self):
        return "<NoteBook '{name}'>".format(name=self.name)
