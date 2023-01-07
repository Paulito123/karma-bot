from sqlalchemy import Column, DateTime, Integer, String, func, Boolean, BigInteger, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, AnyStr, Tuple
from datetime import datetime
from src.connect import engine, session
from json import dumps, loads
from .config import Config


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

    def __init__(self, discord_id: Integer, address: AnyStr="", is_active: Integer=0):
        self.discord_id = discord_id
        self.address = address
        self.is_active = is_active
    
    def upsert(
        discord_id: Integer, 
        address: AnyStr, 
        history: AnyStr) -> None:
            contrib = Contributor(discord_id)
            contrib.address = address
            contrib.history = history
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
            return dumps(list_out)
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
        return []
            
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
    
    def get_active_contributor_by_discord_id(discord_id: int) -> Tuple:
        return session\
            .query(
                Contributor.id, 
                Contributor.address, 
                Contributor.history)\
            .where(
                Contributor.discord_id==discord_id, 
                Contributor.is_active==1)\
            .first()
    
    def get_contributor_by_discord_id(discord_id: int) -> Tuple:
        return session\
            .query(
                Contributor.id, 
                Contributor.address, 
                Contributor.history, 
                Contributor.is_active)\
            .where(
                Contributor.discord_id==discord_id)\
            .first()
    
    def __change_status(discord_id: int, is_act: int):
        try:
            c = update(Contributor)
            c = c.values({"is_active": is_act})
            c = c.where(Contributor.discord_id == discord_id)
            engine.execute(c)
            return True
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
            return False
    
    def activate_contributor(self, discord_id: int) -> Boolean:
        return self.__change_status(discord_id, 1)
    
    def deactivate_contributor(self, discord_id: int) -> Boolean:
        return self.__change_status(discord_id, 0)
    
    def add_address(self, discord_id: int, new_address: AnyStr) -> Boolean:
        try:
            # checking history
            cobj = self.get_active_contributor_by_discord_id(discord_id)
            old_address = cobj[1]
            if cobj[2] and len(cobj[2]['history']) > 0:
                # get existing object
                hobj = cobj[2]
            else:
                # create history object
                hobj = {
                    "history": []
                }

            c = update(Contributor)
            c = c.values({"address": new_address})
            if old_address and len(old_address) == 32:
                hobj["history"].append(
                    {
                        "address": old_address, 
                        "timestamp_end": f"{datetime.strftime(datetime.now(), Config.FORMAT_TIMESTAMP)}"
                    }
                )
                c = c.values({"history": hobj})
            c = c.where(Contributor.discord_id == discord_id)
            engine.execute(c)
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
            return False
        return True
    
    def add_contributor(discord_id: int) -> None:
        c = session\
            .query(Contributor.id)\
            .where(Contributor.discord_id==discord_id)\
            .first()
        if not c:
            contrib = Contributor(
                discord_id = discord_id,
                is_active = 1
            )
            session.add(contrib)
            session.commit()


Base.metadata.create_all(engine)
