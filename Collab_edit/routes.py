from flask import Flask, jsonify, request, render_template_string
from database import db, Projectio, Versions
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collaborative_editing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# HTML template for the form. Alag se file nahi bayi iski kyuki zyada kuch tha nahi HTML ka 
FORM_TEMPLATE = '''
<!doctype html>
<html>
  <body>
    <h2>Add New Project</h2>
    <form method="post">
      Prompt Name: <input type="text" name="prompt_name"><br>
      User ID: <input type="number" name="user_id"><br>
      Date (YYYY-MM-DD HH:MM:SS): <input type="text" name="date"><br>
      <input type="submit" value="Add Project">
    </form>
    
    <h2>Compare Texts</h2>
    <form action="/compare_texts" method="post">
      Text 1: <textarea name="text1"></textarea><br>
      Text 2: <textarea name="text2"></textarea><br>
      <input type="submit" value="Compare">
    </form>
  </body>
</html>
'''

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        prompt_name = request.form['prompt_name']
        user_id = int(request.form['user_id'])
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        
        new_project = Projectio(prompt_name=prompt_name, user_id=user_id, date=date)
        db.session.add(new_project)
        db.session.commit()
        return jsonify({"message": f"Added project: {new_project.prompt_name}", "id": new_project.id}), 201
    return render_template_string(FORM_TEMPLATE)

@app.route('/projects', methods=['GET'])
def list_projects():
    projects = Projectio.query.all()
    return jsonify([{"id": p.id, "prompt_name": p.prompt_name, "user_id": p.user_id, "date": p.date} for p in projects])

@app.route('/add_version', methods=['POST'])
def add_version():
    data = request.json
    project = Projectio.query.get(data['projectio_id'])
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    new_version = Versions(
        content=data['content'],
        version_number=len(project.versions) + 1,
        projectio_id=project.id
    )
    db.session.add(new_version)
    db.session.commit()
    return jsonify({"message": f"Added version {new_version.version_number} to project {project.prompt_name}", "id": new_version.id}), 201

@app.route('/versions/<int:project_id>', methods=['GET'])
def get_versions(project_id):
    versions = Versions.query.filter_by(projectio_id=project_id).order_by(Versions.version_number).all()
    return jsonify([{"id": v.id, "version_number": v.version_number, "date": v.date, "content": v.content} for v in versions])

@app.route('/compare_texts', methods=['POST'])
def compare_texts():
    text1 = request.form['text1']
    text2 = request.form['text2']
    diff = Versions.get_diff(text1, text2)
    return jsonify({"diff": diff})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)