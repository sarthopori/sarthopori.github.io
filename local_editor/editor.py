import json
from flask import Flask, render_template, request, redirect
import git
import os

app = Flask(__name__)

# Correctly locate the repository root from the script's location
repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
json_path = os.path.join(repo_path, '_data', 'content.json')
repo = git.Repo(repo_path)

@app.route('/')
def editor():
    try:
        # Pull the latest changes from GitHub to prevent conflicts
        repo.remotes.origin.pull()
        print("Successfully pulled latest changes.")
    except git.GitCommandError as e:
        print(f"Could not pull changes: {e}. Working with local version.")

    # Read the content file
    with open(json_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return render_template('edit.html', content=content)

@app.route('/save', methods=['POST'])
def save():
    # Read the existing content
    with open(json_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    # Update the content from the form
    for key in content.keys():
        if key in request.form:
            content[key] = request.form[key]

    # Write the new content back to the file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully saved content to {json_path}")

    # Commit and push the changes to GitHub
    try:
        repo.index.add([json_path])
        repo.index.commit('Updated website content via local editor')
        repo.remotes.origin.push()
        print("Successfully committed and pushed to GitHub.")
    except Exception as e:
        print(f"An error occurred during git operations: {e}")

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=9000)
