from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import difflib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collaborative_editing.db'
db = SQLAlchemy(app)

class Projectio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    versions = db.relationship('Versions', backref='projectio', lazy=True)

    def __repr__(self):
        return f'<Projectio {self.prompt_name}>'

class Versions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    projectio_id = db.Column(db.Integer, db.ForeignKey('projectio.id'), nullable=False)

    def __repr__(self):
        return f'<Version {self.version_number} of Projectio {self.projectio_id}>'

    @staticmethod
    def get_diff(old_content, new_content):
        differ = difflib.Differ()
        diff = list(differ.compare(old_content.splitlines(), new_content.splitlines()))
        return '\n'.join(diff)

# Create the database tables
with app.app_context():
    db.create_all()