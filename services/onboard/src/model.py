from sqlalchemy import Column, DateTime, Integer, String, func, BigInteger, Text, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, AnyStr, Union, Dict, Tuple
from connect import engine, session
from datetime import datetime
from config import Config
from github import PaginatedList

Base = declarative_base()


class OboardLog(Base):
    __tablename__ = "onboardlog"

    id = Column(Integer, primary_key=True)
    # Link to Discord account
    discord_id = Column(BigInteger, nullable=False)
    discord_name = Column(String(40), nullable=False)
    address = Column(String(64), nullable=False, unique=True)
    # indicator if account is open for onboarding 1 = Yes, 0 = No
    is_request_open = Column(Integer, nullable=False, default=0)
    message = Column(Text, nullable=True)
    # technical timestamp fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def queue_onboard_request(discord_id: int, discord_name: AnyStr, address: AnyStr) -> Dict:
        req = session\
            .query(OboardLog)\
            .where(OboardLog.address == address)\
            .first()
        
        if req:
            return {"status": "failed", "message": "Onboard request already in queue"}
        
        o = OboardLog(
            discord_id = discord_id,
            discord_name = discord_name,
            address = address
        ) 
        
        session.add(o)
        return {"status": "success", "message": "Onboard request queued"}
    
    def close_onboard_request(address: AnyStr) -> Dict:
        try:
            o = update(OboardLog)
            o = o.values({"is_request_open": 1})
            o = o.where(OboardLog.address == address)
            engine.execute(o)
            return {"status": "success", "message": "Onboard request closed successfully"}
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
            return {"status": "failed", "message": "Onboard request not closed"}


# Base.metadata.create_all(engine)
