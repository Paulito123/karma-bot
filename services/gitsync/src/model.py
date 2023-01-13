from sqlalchemy import Column, DateTime, Integer, String, func, BigInteger, Text
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


class PaymentProposal(Base):
    __tablename__ = "paymentproposal"

    id = Column(Integer, primary_key=True)
    # name of the discord account
    discord_name = Column(String(64), nullable=True)
    # link to on-chain identity
    address_recipient = Column(String(32), nullable=True)
    # links and descriptions to the issue
    issue_details = Column(JSONB, nullable=True)
    # amount of the bounty
    amount = Column(BigInteger, nullable=True)
    # memo regarding the payment
    memo = Column(String(500), nullable=True)
    # payment tx hash
    tx_hash = Column(String(500), nullable=True)
    # technical timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GithubIssue(Base):
    __tablename__ = "githubissue"

    # Primary key
    id = Column(Integer, primary_key=True)
    # Github issue id
    giid = Column(BigInteger, unique=True, nullable=False)
    repository = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    title = Column(String(500), nullable=False)
    state = Column(String(100), nullable=False)
    # TODO check updated at fields (nullable yes or no)
    giupdated_at = Column(DateTime(), nullable=False)
    # nullable fields
    closed_at = Column(DateTime(), nullable=True)
    closed_by = Column(String(200), nullable=True)
    assignees = Column(JSONB, nullable=True)
    labels = Column(JSONB, nullable=True)
    milestone = Column(String(200), nullable=True)
    # technical dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def upload_gh_response(gh_response_list: List) -> None:
        for issue_gh in gh_response_list:
            issue_db = session\
                .query(GithubIssue.id, GithubIssue.giupdated_at)\
                .where(GithubIssue.giid==issue_gh.id)\
                .first()
            if issue_db and issue_gh.updated_at > issue_db[1]:
                # update existing record
                g = GithubIssue()
                g.id = issue_db[0]
            elif not issue_db:
                # new record in db
                g = GithubIssue()
            else:
                g = None
            
            if g:
                g.giid = issue_gh.id,
                g.repository = issue_gh.repository,
                g.url = issue_gh.url,
                g.body = issue_gh.body,
                g.title = issue_gh.title,
                g.state = issue_gh.state,
                g.giupdated_at = issue_gh.updated_at,
                g.closed_at = issue_gh.closed_at,
                g.closed_by = issue_gh.closed_by,
                g.assignees = issue_gh.assignees,
                g.labels = issue_gh.labels,
                g.milestone = issue_gh.milestone
                session.merge(g)
                session.commit()
            

Base.metadata.create_all(engine)
