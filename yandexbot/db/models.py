from sqlalchemy import Column, Date, Float, Integer, String

from db.base import Base


class Expence(Base):
    __tablename__ = "expence"
    id = Column("expence", Integer, primary_key=True)
    name = Column("name", String)
    user_id = Column("user_id", Integer)
    cost = Column("cost", Float)
    expence_date = Column("expence_date", Date)
