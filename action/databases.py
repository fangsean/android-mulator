import collections
from abc import ABC
from typing import Any, Dict

import pandas as pd
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import declarative_base

# 指定数据库路径和引擎
from config import user_info_file, db_file

engine = create_engine('sqlite:///%s' % db_file)
Base = declarative_base()
inspector = inspect(engine)
conn = engine.connect()


def pd_txt_library(index_library_path):
    df = pd.read_csv(index_library_path, delimiter='\t')
    return df.to_dict('records')


# 定义ORM类
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    stage = Column(Integer, default=0)
    step = Column(Integer, default=0)
    deleted = Column(Integer, default=0)

    def dict(self):
        if '_sa_instance_state' in self.__dict__:
            self.__dict__.pop('_sa_instance_state')
        return self.__dict__


class UserAction:

    def __init__(self, engine):
        self.engine = engine
        self.session_maker = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        self.init_db()
        self._queue = collections.deque(self.user_all())

    # Base.metadata.drop_all(bind=engine)
    def init_db(self):
        if not inspector.has_table("users"):
            # 创建表
            Base.metadata.create_all(engine)
        users = pd_txt_library(user_info_file)
        # ORM操作
        session = self.session_maker()
        for index, user in enumerate(users):
            # 插入
            username = user['username']
            password = user['password']
            users = session.query(User).filter(User.username == username and User.deleted == 0).first()
            if not users:
                new_user = User(username=username, password=password)
                session.add(new_user)
        # 提交变更
        session.commit()

    def user_delete(self, username):
        session = self.session_maker()
        users = session.query(User).filter(User.username == username and User.deleted == 0).all()
        if len(users):
            for user in users:
                user.deleted = 1
            # 提交事务
            session.add(user)
        session.commit()

    def user_quantity_stage(self, username):
        session = self.session_maker()
        result = session.query(User).filter(User.username == username and User.deleted == 0).first()
        if result:
            # 修改数量加1
            result.stage += 1
            result.step = 0
            # 提交事务
            session.commit()

    def user_quantity_step(self, username):
        session = self.session_maker()
        result = session.query(User).filter(User.username == username).first()
        if result:
            # 修改数量加1
            result.step += 1
            # 提交事务
            session.commit()

    def user_query(self, username):
        session = self.session_maker()
        return session.query(User).filter(User.username == username).first()

    def user_all(self):
        session = self.session_maker()
        return session.query(User).filter(User.deleted == 0).order_by(User.stage, User.step).all()

    def get_task(self):
        if self._queue:
            return self._queue.popleft()
        return None

    def put_task(self, user):
        if self._queue:
            self._queue.append(user)

user_action = UserAction(engine)

if __name__ == '__main__':
    action = UserAction(engine)
    while True:
        item = action.get_task()
        if not item:
            break
        print(item.dict())
