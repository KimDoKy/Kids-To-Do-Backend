import databases
import datetime
import ormar
import sqlalchemy

from .config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()

class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True)
    email: str = ormar.String(max_length=128, unique=True, nullable=False)
    active: bool = ormar.Boolean(default=True, nullable=True)
    username: str = ormar.String(max_length=30, nullable=True)
    password: str = ormar.String(max_length=254, nullable=False)


class Mission(ormar.Model):
    class Meta(BaseMeta):
        tablename = "missions"

    id: int = ormar.Integer(primary_key=True)
    title: str = ormar.String(max_length=128)
    comp_cur: int = ormar.Integer()
    comp_tot: int = ormar.Integer()
    owner: int = ormar.ForeignKey(User)


class Board(ormar.Model):
    class Meta(BaseMeta):
        tablename = "boards"

    id: int = ormar.Integer(primary_key=True)
    title: str = ormar.String(max_length=128)
    content: str = ormar.String(max_length=256)
    writer: int = ormar.ForeignKey(User)
    created_at: datetime.datetime = ormar.DateTime(
        default=datetime.datetime.now(), name="created_at"
    )
    updated_at: datetime.datetime = ormar.DateTime(
        default=datetime.datetime.now(), name="updated_at"
    )

engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)
