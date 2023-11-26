import pandas as pd
from sqlalchemy import Column, Integer, String, Table, MetaData
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
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
        self.__dict__.pop('_sa_instance_state')
        return self.__dict__


# Base.metadata.drop_all(bind=engine)
if not inspector.has_table("users"):
    # 创建表
    Base.metadata.create_all(engine)
    users = pd_txt_library(user_info_file)

    # ORM操作
    with Session(engine) as session:
        for index, user in enumerate(users):
            # 插入
            new_user = User(username=user['username'], password=user['password'])
            session.add(new_user)
        # 提交变更
        session.flush()
        session.commit()


def user_delete(username):
    with Session(engine) as session:
        users = session.query(User).filter(User.username == username and User.deleted == 0).all()
        if len(users):
            for user in users:
                user.deleted = 1
            # 提交事务
            session.add(user)
        session.commit()
        session.flush()


def user_quantity_stage(username):
    with Session(engine) as session:
        result = session.query(User).filter(User.username == username and User.deleted == 0).first()
        if result:
            # 修改数量加1
            result.stage += 1
            result.step = 0
            # 提交事务
            session.commit()
            session.flush()


def user_quantity_step(username):
    with Session(engine) as session:
        result = session.query(User).filter(User.username == username).first()
        if result:
            # 修改数量加1
            result.step += 1
            # 提交事务
            session.commit()
            session.flush()


def user_query(username):
    with Session(engine) as session:
        return session.query(User).filter(User.username == username).first()


def user_all():
    with Session(engine) as session:
        return session.query(User).filter(User.deleted == 0).all()


if __name__ == '__main__':
    users = user_all()
    for user in users:
        print(user.dict())
