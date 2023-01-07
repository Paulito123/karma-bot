from sqlalchemy import Column, DateTime, Integer, String, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Any, Union, Dict, Tuple
from connect import engine, session
from datetime import datetime
from config import Config

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
    
    def get_update_metrics() -> Union[Tuple, None]:
        return session.query(
                func.max(Contributor.updated_at),
                func.count(Contributor.id)
            ).first()
    
    def get_contributors(self) -> Union[Dict, None]:
        try:
            metrics = self.get_update_metrics()
            dict_out = {
                "timestamp_last_update": datetime.strftime(metrics[0], Config.FORMAT_TIMESTAMP_TZ),
                "data": []
            }
            contrib_list = session\
                .query(
                    Contributor.discord_id, 
                    Contributor.address,
                    Contributor.history,
                    Contributor.is_active)\
                .all()
            for contrib in contrib_list:
                obj_out = {
                    "discord_id": contrib[0],
                    "address": contrib[1],
                    "history": contrib[2],
                    "is_active": contrib[3]
                }
                dict_out['data'].append(obj_out)
            return dict_out
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
            return None

    def upload_contributors_json(identities: Dict) -> bool:
        try:
            for contrib in identities['data']:
                id = session.query(Contributor.id).where(Contributor.discord_id==contrib['discord_id']).first()
                c = Contributor(
                    discord_id = contrib['discord_id'],
                    address = contrib['address'],
                    history = contrib['history'],
                    is_active = contrib['is_active']
                )
                if id:
                    c.id = id[0]
                    session.merge()
                else:
                    session.add(c)
            session.commit()
            return True
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
            return False