import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()
__factory = None

def global_init(db_file: str):
    '''Подключение к базе данных'''
    global __factory
    db_file = db_file.strip()

    if __factory is not None:
        return

    if not db_file:
        raise Exception('Строка адреса базы данных пуста или неправильно указана')

    conn_str = f'sqlite:///./{db_file}?check_same_thread=False'
    print(f'\033[32m Подключение к базе данных по адресу {conn_str}.\033[0m')

    engine = sa.create_engine(conn_str, echo=False, pool_size=20, max_overflow=0)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


def close_all_session():
    orm.session.close_all_session()

