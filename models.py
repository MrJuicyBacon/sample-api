from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = ['Session', 'User', 'Book', 'Shop', 'Order', 'OrderItem']

DB_URI = 'sqlite:///sample.db'

engine = create_engine(DB_URI)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def class_attrs_to_dict(in_object, attrs):
    attrs_dict = {}
    for attr in attrs:
        attrs_dict[attr] = getattr(in_object, attr)
    return attrs_dict


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50))
    fathers_name = Column(String(50))
    email = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'{self.name} {self.surname}'

    def as_dict(self):
        fields = ['id', 'name', 'surname', 'fathers_name', 'email']
        return class_attrs_to_dict(self, fields)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    author = Column(String(50), nullable=False)
    isbn = Column(String(25), nullable=False)

    def __repr__(self):
        return f'{self.name} ({self.author})'

    def as_dict(self):
        fields = ['id', 'name', 'author', 'isbn']
        return class_attrs_to_dict(self, fields)


class Shop(Base):
    __tablename__ = 'shops'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    address = Column(String(150), nullable=False)
    post_code = Column(String(15))

    def __repr__(self):
        return f'{self.name} ({self.address})'

    def as_dict(self):
        fields = ['id', 'name', 'address', 'post_code']
        return class_attrs_to_dict(self, fields)


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    reg_date = Column(Date, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'Order {self.id}'

    def as_dict(self):
        fields = ['id', 'reg_date']
        return class_attrs_to_dict(self, fields)


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('orders.id'), nullable=False)
    book_id = Column(ForeignKey('books.id'), nullable=False)
    book_quantity = Column(Integer, nullable=False)
    shop_id = Column(ForeignKey('shops.id'), nullable=False)

    def __repr__(self):
        return f'OrderItem {self.id}'


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
