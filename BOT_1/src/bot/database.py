from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price_btc = Column(Numeric(16, 8))
    price_ltc = Column(Numeric(16, 8))
    file_id = Column(String(255))
    stock = Column(Integer, default=0)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    crypto_address = Column(String(255))
    amount = Column(Numeric(16, 8))
    currency = Column(String(10))
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)