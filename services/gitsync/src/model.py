from sqlalchemy import Column, DateTime, Integer, String, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List
from connect import engine, session
from datetime import datetime

Base = declarative_base()


class Contributor(Base):
    __tablename__ = "contributor"

    id = Column(Integer, primary_key=True)
    # Link to physical person
    discord_id = Column(BigInteger, nullable=False, unique=True)
    # Link to on-chain identity
    address = Column(String(32), nullable=True)
    # A history of address changes is kept in json format
    history = Column(JSONB, nullable=True)
    # indicator if account is still active/enabled 1 = Yes, 0 = No
    is_active = Column(Integer, nullable=False, default=0)
    # technical timestamp fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def load_contrib_data(data: List) -> None:
        try:
            for contrib in data:
                Contributor.upsert(
                    discord_id = int(contrib["discord_id"]),
                    address = contrib["address"],
                    history = contrib["history"]
                )
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
    
    def generate_file_content() -> List:
        try:
            list_out = []
            contrib_list = session\
                .query(
                    Contributor.discord_id, 
                    Contributor.address,
                    Contributor.history,
                    Contributor.created_at,
                    Contributor.updated_at)\
                .all()
            for contrib in contrib_list:
                obj_out = {
                    "discord_id": contrib[0],
                    "address": contrib[1],
                    "history": contrib[2],
                    "created_at": contrib[3],
                    "updated_at": contrib[4]
                }
                list_out.append(obj_out)
            return list_out
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
        return []
