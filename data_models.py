from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)
    books = db.relationship('Book', backref='author', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Author {self.name}>"

    def __str__(self):
        return f"{self.name}, born {self.birth_date}"


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    cover_url = db.Column(db.String(250), nullable=True)

    def __repr__(self):
        return f"<Book {self.title} ({self.rating})>"

    def __str__(self):
        return f"{self.title}, published {self.publication_year}, rating: {self.rating}"
