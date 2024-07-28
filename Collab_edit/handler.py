from database import app, db, Projectio, Versions
from sqlalchemy import inspect

# Create an application context
with app.app_context():
    # Check if tables exist
    inspector = inspect(db.engine)
    print(inspector.get_table_names())  # Should print ['projectio', 'versions']

    # Try adding a new project
    new_project = Projectio(prompt_name="Test Prompt", user_id=1)
    db.session.add(new_project)
    db.session.commit()

    # Retrieve the project
    project = Projectio.query.filter_by(prompt_name="Test Prompt").first()
    print(project)  # Should print something like <Projectio Test Prompt>

    # Add a version to the project
    new_version = Versions(content="This is a test prompt.", version_number=1, projectio_id=project.id)
    db.session.add(new_version)
    db.session.commit()

    # Retrieve the version
    version = Versions.query.filter_by(projectio_id=project.id).first()
    print(version)  # Should print something like <Version 1 of Projectio 1>

    # Test the diff function
    old_content = "This is a test prompt."
    new_content = "This is an updated test prompt."
    diff = Versions.get_diff(old_content, new_content)
    print(diff)  # Should print the differences between the two strings