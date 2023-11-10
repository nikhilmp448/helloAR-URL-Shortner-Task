from flask import Flask, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import random
import string

app = Flask(__name__)

# Configure SQLite database using Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


migrate = Migrate(app, db)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(6), unique=True, nullable=False)
    long_url = db.Column(db.String(255), nullable=False)
    hits = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<URL {self.short_url}: {self.long_url}>"

def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/api/create', methods=['POST'])
def create_short_url():
    long_url = request.form.get('long_url')
    short_url = generate_short_url()

    new_url = URL(short_url=short_url, long_url=long_url)

    db.session.add(new_url)
    db.session.commit()

    return jsonify({'short_url': short_url})

@app.route('/api/search', methods=['GET'])
def search_urls():
    term = request.args.get('term')
    results = []

    # Search for URLs with a title containing the given term
    urls = URL.query.filter(URL.long_url.ilike(f'%{term}%')).all()

    for url in urls:
        results.append({'title': url.long_url, 'url': url.short_url})

    return jsonify({'results': results})

@app.route('/<short_url>', methods=['GET'])
def redirect_to_long_url(short_url):
    # Query the database for the short URL
    url = URL.query.filter_by(short_url=short_url).first()

    if url:
        # Increment the hit count
        url.hits += 1
        db.session.commit()

        # Redirect to the long URL
        return redirect(url.long_url)
    else:
        return "Short URL not found", 404

if __name__ == '__main__':
    # Create database tables before running the app
    db.create_all()
    app.run(debug=True)
