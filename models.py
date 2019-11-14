import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, event, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship

__all__ = ['Session', 'User', 'Book', 'Shop', 'Order', 'OrderItem', 'shop_book_association_table']

DB_URI = 'sqlite:///sample.db'

engine = create_engine(DB_URI)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


# Enabling foreign keys constraints check for sqlite db
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")


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


shop_book_association_table = Table(
    'shop_book_association',
    Base.metadata,
    Column('shop_id', Integer, ForeignKey('shops.id')),
    Column('book_id', Integer, ForeignKey('books.id'))
)


class Shop(Base):
    __tablename__ = 'shops'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    address = Column(String(150), nullable=False)
    post_code = Column(String(15))
    books = relationship('Book', secondary=shop_book_association_table)

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
    # Clearing all tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Creating test data
    import random
    # noinspection SpellCheckingInspection
    test_books = (
        ('Don Quixote', 'Miguel de Cervantes Saavedra', '9780486821955'),
        ('Alices adventures in wonderland', 'Lewis Carroll', '9781786751041'),
        (
            'The annotated Huckleberry Finn : Adventures of Huckleberry Finn (Tom Sawyer\'s comrade)',
            'Mark Twain',
            '393020398'
        ),
        ('The adventures of Tom Sawyer', 'Mark Twain', '1402714602'),
        ('Treasure Island', 'Robert Louis Stevenson', '684171600'),
        ('Pride and prejudice', 'Jane Austen', '679601686'),
        ('Wuthering Heights', 'Emily Brontë', '140434186'),
        ('Jane Eyre', 'Charlotte Brontë', '679405828'),
        ('Moby Dick', 'Herman Melville', '895773228'),
        (
            'The scarlet letter : complete, authoritative text with biographical background and critical history '
            'plus essays from five contemporary critical perspectives with introductions and bibliographies',
            'Nathaniel Hawthorne',
            '312060246'
        ),
    )
    # noinspection SpellCheckingInspection
    test_shops = (
        ('Powell\'s City of Books', '1005 W Burnside St, Portland, OR, United States', '97209'),
        ('Barnes & Noble', '33 E 17th St, New York, NY, United States', '10003'),
        ('Cook & Book', 'Place du Temps Libre 1, 1200 Woluwe-Saint-Lambert, Belgium', ''),
        ('John K. King Used & Rare Books', '901 W Lafayette Blvd, Detroit, MI, United States', '48226'),
        ('Waterstones', '203-206 Piccadilly, St. James\'s, London, United Kingdom', 'W1J 9HD'),
        ('Strand Book Store', '828 Broadway, New York, NY, United States', '10003'),
    )
    # noinspection SpellCheckingInspection
    test_users = (
        ('Anton', 'Lapshin', None, 'iambacon@ya.ru'),
        ('Russell', 'Slater', 'B.', 'RussellBSlater@rhyta.com'),
        ('Robert', 'Willett', 'S.', 'RobertSWillett@rhyta.com'),
        ('Claude', 'Davis', 'D.', 'ClaudeDDavis@teleworm.us'),
        ('Francis', 'Gallo', 'M.', 'FrancisMGallo@rhyta.com'),
        ('Everett', 'Carroll', 'E.', 'EverettECarroll@jourrapide.com'),
    )

    # Filling db with test data
    test_book_objects = [Book(name=book[0], author=book[1], isbn=book[2]) for book in test_books]
    test_shop_objects = [
        Shop(
            name=shop[0],
            address=shop[1],
            post_code=shop[2],
            books=random.sample(test_book_objects, random.randint(1, len(test_books)))
        ) for shop in test_shops
    ]
    test_user_objects = [
        User(name=user[0], surname=user[1], fathers_name=user[2], email=user[3]) for user in test_users
    ]

    Session().add_all(test_book_objects + test_shop_objects + test_user_objects)
    Session().commit()
