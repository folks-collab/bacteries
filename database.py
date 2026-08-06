import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String


engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost/bacteries")
Session = sessionmaker(bind=engine)
Base = declarative_base()
s = Session()

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256))
    adress = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=1)
    y_speed = Column(Integer, default=0)
    x_speed = Column(Integer, default=0)

    def __init__(self, name, adress):
        self.name = name
        self.adress = adress

Base.metadata.create_all(engine)


        
