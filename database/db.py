from sqlalchemy import Column, DateTime, String, Integer, create_engine, Float, BIGINT, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(
    'postgresql://postgres:P110605m@localhost:5433/grn'
)
Base = declarative_base()
session = scoped_session(sessionmaker(bind=engine))
Base.query = session.query_property()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tid = Column(BIGINT, unique=True)
    username = Column(String)
    balance_rub = Column(Float, default=0)
    balance_eur = Column(Float, default=0)
    rating = Column(Float, default=0)
    status = Column(String, default='user')  # user, admin, support


class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    buyer_tid = Column(BIGINT)
    seller_tid = Column(BIGINT)
    text = Column(String)
    rating = Column(Float)
    order_id = Column(BIGINT, unique=True)


class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_id = Column(BIGINT)
    buyer_tid = Column(BIGINT)
    seller_tid = Column(BIGINT)
    summa = Column(Float)
    coin = Column(String)  # eur, rub
    ifelse = Column(String)
    status = Column(String)  # active, success, canceled, dispute, wait


class TopUps(Base):
    __tablename__ = 'topups'
    id = Column(Integer, primary_key=True)
    topup_id = Column(String, unique=True)
    tid = Column(BIGINT)
    sum = Column(Float)
    type = Column(String)  # cryptobot, lava, iban
    status = Column(String, default='wait')  # wait, success, canceled


Base.metadata.create_all(bind=engine)
