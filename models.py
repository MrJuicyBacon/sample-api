from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


DB_URI = 'sqlite:///sample.db'

engine = create_engine(DB_URI)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50))
    fathers_name = Column(String(50))
    email = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'{self.name} {self.surname}'


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    author = Column(String(50), nullable=False)
    isbn = Column(String(25), nullable=False)

    def __repr__(self):
        return f'{self.name} ({self.author})'


class Shop(Base):
    __tablename__ = 'shops'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    address = Column(String(150), nullable=False)
    post_code = Column(String(15))

    def __repr__(self):
        return f'{self.name} ({self.address})'


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    reg_date = Column(Date, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'Order {self.id}'


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('orders.id'), nullable=False)
    book_id = Column(ForeignKey('books.id'), nullable=False)
    shop_id = Column(ForeignKey('shops.id'), nullable=False)

    def __repr__(self):
        return f'OrderItem {self.id}'


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
