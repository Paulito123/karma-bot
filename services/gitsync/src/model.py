from sqlalchemy import Column, DateTime, Integer, String, func, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Any, Union, Dict, Tuple
from connect import engine, session
from datetime import datetime
from config import Config
from github import PaginatedList

Base = declarative_base()


class Contributor(Base):
    __tablename__ = "contributor"

    id = Column(Integer, primary_key=True)
    # Link to physical person
    discord_id = Column(BigInteger, nullable=False, unique=True)
    discord_name = Column(String(40), nullable=False)
    # Link to on-chain identity
    address = Column(String(32), nullable=True)
    # Optional twitter handle
    twitter_handle = Column(String(50), nullable=True)
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
                    Contributor.discord_name,
                    Contributor.address,
                    Contributor.twitter_handle,
                    Contributor.history,
                    Contributor.is_active)\
                .all()
            for contrib in contrib_list:
                obj_out = {
                    "discord_id": contrib[0],
                    "discord_name": contrib[1],
                    "address": contrib[2],
                    "twitter_handle": contrib[3],
                    "history": contrib[4],
                    "is_active": contrib[5]
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
                    discord_name = contrib['discord_name'],
                    address = contrib['address'],
                    twitter_handle = contrib['twitter_handle'],
                    history = contrib['history'],
                    is_active = contrib['is_active']
                )
                if id:
                    c.id = id[0]
                    session.merge(c)
                else:
                    session.add(c)
            session.commit()
            return True
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
            return False


# class GithubIssue(Base):
#     __tablename__ = "githubissue"

#     # Primary key
#     id = Column(Integer, primary_key=True)
#     # Github issue id
#     giid = Column(BigInteger, unique=True, nullable=False)
#     repository = Column(BigInteger, nullable=False)
#     url = Column(String(500), nullable=False)
#     title = Column(String(500), nullable=False)
#     state = Column(String(100), nullable=False)
#     giupdated_at = Column(DateTime(), nullable=False)
#     # nullable fields
#     # body = Column(Text, nullable=True)
#     closed_at = Column(DateTime(), nullable=True)
#     closed_by = Column(String(200), nullable=True)
#     # assignees = Column(JSONB, nullable=True)
#     labels = Column(JSONB, nullable=True)
#     # milestone = Column(String(200), nullable=True)
#     # unpaid, partial       --> unpaid issues that require attention
#     # paid, not required    --> paid issues that can be considered closed
#     payment_status = Column(String(50), nullable=False, default="unpaid")
#     # technical dates
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

#     def upload_gh_response(gh_response: PaginatedList) -> None:
#         page_index = 0
#         while True:
#             print(1)
#             current_page = gh_response.get_page(page_index)
#             print(2)
#             if len(current_page) == 0:
#                 break

#             for issue_gh in current_page:
#                 issue_db = session\
#                     .query(GithubIssue.id, GithubIssue.giupdated_at)\
#                     .where(GithubIssue.giid==issue_gh.id)\
#                     .first()
#                 if issue_db and issue_gh.updated_at > issue_db[1]:
#                     # update existing record
#                     g = GithubIssue()
#                     g.id = issue_db[0]
#                 elif not issue_db:
#                     # new record in db
#                     g = GithubIssue()
#                 else:
#                     g = None
                
#                 # print(f"{issue_gh.repository.__dict__}")

#                 if g:
#                     g.giid = issue_gh.id,
#                     g.repository = issue_gh.repository.id,
#                     g.url = issue_gh.url,
#                     # g.body = issue_gh.body,
#                     g.title = issue_gh.title,
#                     g.state = issue_gh.state,
#                     g.giupdated_at = issue_gh.updated_at,
#                     g.closed_at = issue_gh.closed_at,
#                     g.closed_by = issue_gh.closed_by.login if issue_gh.closed_by else None,
#                     # g.assignees = issue_gh.assignees,
#                     # g.labels = issue_gh.labels,
#                     # g.milestone = issue_gh.milestone.title if issue_gh.milestone else None,
#                     session.merge(g)
#                     session.commit()
#             page_index += 1
            
            


# 1. A new issue is closed
# 2. The newly closed issue is crawled
# 3. Payment proposal is created
# 4. Proposals are sent to a (list of) designated person(s) by repo
# class PaymentProposal(Base):
#     __tablename__ = "paymentproposal"

#     id = Column(Integer, primary_key=True)
#     # payment tx hash
#     tx_hash = Column(String(500), nullable=True)
#     # name and/or id of the discord account
#     discord_details = Column(JSONB, nullable=False)
#     # link to on-chain identity
#     address_recipient = Column(String(32), nullable=True)
#     # links and descriptions to the issue
#     issue_details = Column(JSONB, nullable=False)
#     # amount of the bounty
#     amount = Column(BigInteger, nullable=True)
#     # memo regarding the payment
#     memo = Column(String(500), nullable=True)
#     # technical timestamps
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

#     def create_payment_proposal(issue_details: Dict) -> bool:
#         try:
#             ...
#             return True
#         except:
#             ...
#             return False


#     def get_update_metrics() -> Union[Tuple, None]:
#         return session.query(
#                 func.max(PaymentProposal.updated_at),
#                 func.count(PaymentProposal.id)
#             ).first()

#     def get_payment_proposals(self) -> Union[Dict, None]:
#         """ Generate a payment proposal json dict """
#         try:
#             metrics = self.get_update_metrics()
#             dict_out = {
#                 "timestamp_last_update": datetime.strftime(metrics[0], Config.FORMAT_TIMESTAMP_TZ),
#                 "data": []
#             }
#             payprop_list = session\
#                 .query(
#                     PaymentProposal.tx_hash, 
#                     PaymentProposal.discord_details,
#                     PaymentProposal.address_recipient,
#                     PaymentProposal.issue_details,
#                     PaymentProposal.amount,
#                     PaymentProposal.memo)\
#                 .all()
#             for payprop in payprop_list:
#                 obj_out = {
#                     "tx_hash": payprop[0],
#                     "discord_details": payprop[1],
#                     "address_recipient": payprop[2],
#                     "issue_details": payprop[3],
#                     "amount": payprop[4],
#                     "memo": payprop[5]
#                 }
#                 dict_out['data'].append(obj_out)
#             return dict_out
#         except Exception as e:
#             print(f"[{datetime.now()}]:ERROR:{e}")
#             return None

#     def upload_payments_json(payment_proposals: Dict) -> bool:
#         """ Uploads a json file with payment proposals to the database """
#         try:
#             for payprop in payment_proposals['data']:
#                 id = session\
#                     .query(PaymentProposal.id)\
#                     .where(PaymentProposal.issue_details.issue_id==payprop['issue_details']['issue_id'])\
#                     .first()
#                 p = PaymentProposal(
#                     tx_hash = payprop['tx_hash'],
#                     discord_details = payprop['discord_details'],
#                     address_recipient = payprop['address_recipient'],
#                     issue_details = payprop['issue_details'],
#                     amount = int(payprop['amount']),
#                     memo = payprop['memo']
#                 )
#                 if id:
#                     p.id = id[0]
#                     session.merge(p)
#                 else:
#                     session.add(p)
#             session.commit()
#             return True
#         except Exception as e:
#             print(f"[{datetime.now()}]:ERROR:{e}")
#             return False


Base.metadata.create_all(engine)

# List issues that have no existing payment proposals
# /ls_is_open

# List issues that have payment proposals but cannot be closed yet 
# because more payment proposals must be generated in its context.
# /ls_is_partial

# List issues that either have no payment proposals because it is 
# not required or all the proposals have been created in its context.
# /ls_is_closed

# List all proposals that have a txhash
# /ls_prop_paid

# List all proposals that have no txhash
# /ls_prop_closed

# show details of a specified object
# /dtls_is <iid>
# /dtls_prop <ppid>

# Create a proposal for a specific issue
# /create_prop <iid>

# Edit the specified proposal
# /edit_prop <ppid>

# Close an issue (irreversable)
# /close_is <iid>