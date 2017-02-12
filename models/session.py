from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///sqlite.db", echo=False, pool_recycle=3600)
Sess = sessionmaker(bind=engine, expire_on_commit=False)


class Session(object):

    def __init__(self):
        self.session = Sess()

    def __enter__(self):
        return self.session

    def __exit__(self, *exception):
        if exception[0] is not None:
            self.session.rollback()
        self.session.close()
