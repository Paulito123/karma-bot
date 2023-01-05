from sqlalchemy import Column, DateTime, Integer, String, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, AnyStr
from datetime import datetime
from src.connect import engine, session
from json import dumps


Base = declarative_base()


class Contributor(Base):
    __tablename__ = "contributor"

    id = Column(Integer, primary_key=True)
    # Link to physical person
    discord_id = Column(Integer, nullable=False, unique=True)
    # Link to on-chain identity
    address = Column(String(32), nullable=True)
    # A history of address changes is kept in json format
    history = Column(JSONB, nullable=True)
    # slow wallet indicator 1 = Yes, 0 = No
    is_slow = Column(Integer, nullable=False, default=0)
    # key role indicator 1 = Yes, 0 = No
    is_key_role = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __init__(self, discord_id: Integer):
        self.discord_id = discord_id
    
    def upsert(
        discord_id: Integer, 
        address: AnyStr, 
        history: AnyStr, 
        is_slow: Boolean = False, 
        is_key_role: Boolean = False) -> None:
            contrib = Contributor(discord_id)
            contrib.address = address
            contrib.history = history
            contrib.is_slow = is_slow
            contrib.is_key_role = is_key_role
            session.merge(contrib)
            session.commit()
    
    def generate_file_content() -> List:
        try:
            list_out = []
            contrib_list = session\
                .query(
                    Contributor.discord_id, 
                    Contributor.address,
                    Contributor.history,
                    Contributor.is_slow,
                    Contributor.is_key_role,
                    Contributor.created_at,
                    Contributor.updated_at)\
                .all()
            for contrib in contrib_list:
                obj_out = {
                    "discord_id": contrib[0],
                    "address": contrib[1],
                    "history": contrib[2],
                    "is_slow": bool(contrib[3]),
                    "is_key_role": bool(contrib[4]),
                    "created_at": contrib[5],
                    "updated_at": contrib[6]
                }
                list_out.append(obj_out)
            return dumps(list_out)
        except Exception as e:
            print(f"[{datetime.now()}]:[ERROR]:{e}")
        return []
            
    def load_contrib_data(data: List) -> None:
        print(f"data={data}")
        try:
            for contrib in data:
                Contributor.upsert(
                    discord_id = int(contrib["discord_id"]),
                    address = contrib["address"],
                    history = contrib["history"],
                    is_slow = contrib["is_slow"],
                    is_key_role = contrib["is_key_role"]
                )
        except Exception as e:
            print(f"[{datetime.now()}]:[ERROR]:{e}")


Base.metadata.create_all(engine)
