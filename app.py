from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os

from data_models import db, Author, Book

# Flask app, Secret Key
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mysecretkey")

# Database config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'library.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy init with app
db.init_app(app)

with app.app_context():
    db.create_all()

'''
Routes
'''

@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'title')
    search_query = request.args.get('search', '').strip()
    search_field = request.args.get('search_field', 'title')

    query = Book.query.join(Author)

    if search_query:
        if search_field == 'author':
            query = query.filter(Author.name.ilike(f'%{search_query}%'))
        else:
            query = query.filter(Book.title.ilike(f'%{search_query}%'))

    if sort_by == 'author':
        books = query.order_by(Author.name).all()
    else:
        books = query.order_by(Book.title).all()

    return render_template('home.html', books=books, sort_by=sort_by,
                           search_query=search_query, search_field=search_field)

# Add Author
@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        date_of_death_str = request.form.get('date_of_death')

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
        date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        flash(f"Author '{name}' added successfully!", "success")
        return redirect(url_for('add_author'))

    return render_template('add_author.html')

# Add Book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')
        rating = request.form.get('rating')

        # Cover-URL automatisch generieren
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg" if isbn else None

        book = Book(
            title=title,
            isbn=isbn,
            publication_year=int(publication_year) if publication_year else None,
            author_id=int(author_id),
            rating=int(rating) if rating else None,
            cover_url=cover_url
        )
        db.session.add(book)
        db.session.commit()
        flash(f"Book '{title}' added successfully!", "success")
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)

# Book detail
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

# Author detail
@app.route('/author/<int:author_id>')
def author_detail(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('author_detail.html', author=author)

# Delete Book
@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author
    db.session.delete(book)
    db.session.commit()

    if not author.books:
        db.session.delete(author)
        db.session.commit()
        flash(f"Book '{book.title}' and its author '{author.name}' were deleted!", "success")
    else:
        flash(f"Book '{book.title}' deleted successfully!", "success")

    return redirect(url_for('home'))

# Delete Author
@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash(f"Author '{author.name}' and all their books were deleted.", "success")
    return redirect(url_for('home'))

# Run app
if __name__ == '__main__':
    app.run(debug=True)
