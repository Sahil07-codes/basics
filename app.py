import os
import threading
import base64
import shutil
import time
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from github import Github

load_dotenv()

app = Flask(__name__)

def generate_application(task_id, brief, attachments, user_login):
    """
    Generates the application files based on the brief and attachments.
    This function simulates an LLM call by using a different template based on the task_id.
    """
    repo_dir = f"./{task_id}"
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    os.makedirs(repo_dir)

    html_content = ""
    if "sum-of-sales" in task_id:
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Summary</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Sales Summary</h1>
        <p>Total Sales: <span id="total-sales"></span></p>
    </div>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            fetch('data.csv')
                .then(response => response.text())
                .then(data => {{
                    const rows = data.trim().split('\\n');
                    const headers = rows[0].split(',');
                    const salesIndex = headers.indexOf('sales');
                    let totalSales = 0;
                    for (let i = 1; i < rows.length; i++) {{
                        const values = rows[i].split(',');
                        totalSales += parseFloat(values[salesIndex]);
                    }}
                    document.getElementById('total-sales').textContent = totalSales.toFixed(2);
                }});
        }});
    </script>
</body>
</html>"""
    elif "markdown-to-html" in task_id:
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown to HTML</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/default.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
</head>
<body>
    <div id="markdown-output"></div>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            fetch('input.md')
                .then(response => response.text())
                .then(text => {{
                    document.getElementById('markdown-output').innerHTML = marked.parse(text);
                    hljs.highlightAll();
                }});
        }});
    </script>
</body>
</html>"""
    elif "github-user-created" in task_id:
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub User Created Date</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>GitHub User Created Date</h1>
        <form id="github-user-form">
            <div class="mb-3">
                <label for="username" class="form-label">GitHub Username</label>
                <input type="text" class="form-control" id="username" required>
            </div>
            <button type="submit" class="btn btn-primary">Get Created Date</button>
        </form>
        <p class="mt-3">Account Created At: <span id="github-created-at"></span></p>
    </div>
    <script>
        document.getElementById('github-user-form').addEventListener('submit', function(event) {{
            event.preventDefault();
            const username = document.getElementById('username').value;
            const token = new URLSearchParams(window.location.search).get('token');
            const headers = {{}};
            if (token) {{
                headers['Authorization'] = `token ${{token}}`;
            }}
            fetch(`https://api.github.com/users/${{username}}`, {{ headers }})
                .then(response => response.json())
                .then(data => {{
                    const createdAt = new Date(data.created_at);
                    document.getElementById('github-created-at').textContent = createdAt.toISOString().split('T')[0];
                }});
        }});
    </script>
</body>
</html>"""
    else:
        # Default fallback
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{task_id}</title>
</head>
<body>
    <h1>{brief}</h1>
</body>
</html>"""

    with open(os.path.join(repo_dir, "index.html"), "w") as f:
        f.write(html_content)

    # Handle attachments
    if attachments:
        for attachment in attachments:
            file_name = attachment['name']
            file_url = attachment['url']
            try:
                header, encoded = file_url.split(",", 1)
                data = base64.b64decode(encoded)
                with open(os.path.join(repo_dir, file_name), "wb") as f:
                    f.write(data)
            except Exception as e:
                print(f"Error decoding attachment {file_name}: {e}")

    # Generate README.md
    readme_content = f"""
# {task_id}

{brief}

## Summary

This project is a single-page application generated based on a task brief.

## Setup

1.  Clone the repository.
2.  Open `index.html` in your web browser.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
"""
    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write(readme_content)

    # Generate MIT License
    license_content = f"""MIT License

Copyright (c) 2024 {user_login}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    with open(os.path.join(repo_dir, "LICENSE"), "w") as f:
        f.write(license_content)

    return repo_dir


@app.route('/api-endpoint', methods=['POST'])
def api_endpoint():
    data = request.get_json()
    if not data or 'secret' not in data:
        return jsonify({"error": "Invalid request"}), 400

    if data['secret'] != os.getenv('SECRET'):
        return jsonify({"error": "Invalid secret"}), 403

    # Process the request in a separate thread
    thread = threading.Thread(target=process_request, args=(data,))
    thread.start()

    return jsonify({"message": "Request received and is being processed."}), 200

def deploy_to_github(task_id, repo_dir, brief, round_num):
    """
    Deploys the generated application to GitHub Pages.
    """
    try:
        g = Github(os.getenv("GITHUB_TOKEN"))
        user = g.get_user()

        repo_exists = False
        try:
            repo = user.get_repo(task_id)
            repo_exists = True
            print(f"Repository {task_id} already exists. Updating it.")
        except Exception:
            repo = user.create_repo(task_id, private=False, auto_init=False)
            print(f"Repository {task_id} created successfully.")

        # Upload or update files
        for root, _, files in os.walk(repo_dir):
            for file in files:
                filepath = os.path.join(root, file)
                with open(filepath, "rb") as f:
                    content = f.read()
                repo_path = os.path.relpath(filepath, repo_dir)

                try:
                    # Check if file exists
                    existing_file = repo.get_contents(repo_path)
                    repo.update_file(repo_path, f"Update {file}", content, existing_file.sha)
                    print(f"File {repo_path} updated.")
                except Exception:
                    # If file doesn't exist, create it
                    repo.create_file(repo_path, f"Add {file}", content)
                    print(f"File {repo_path} created.")

        # Enable GitHub Pages if it's the first round
        if not repo_exists:
            repo.edit(has_pages=True)
            print("GitHub Pages enabled.")

        pages_url = f"https://{user.login}.github.io/{task_id}/"

        # Poll for GitHub Pages deployment
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(pages_url)
                if response.status_code == 200:
                    print("GitHub Pages is live.")
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(10)
        else:
            print("GitHub Pages did not become live in time.")
            return None, None, None, None

        commits = repo.get_commits()
        latest_commit_sha = commits[0].sha

        return repo.html_url, latest_commit_sha, pages_url, user.login

    except Exception as e:
        print(f"Error deploying to GitHub: {e}")
        return None, None, None, None

def notify_evaluation_service(email, task, round_num, nonce, repo_url, commit_sha, pages_url, evaluation_url):
    """
    Notifies the evaluation service with the deployment details.
    """
    payload = {
        "email": email,
        "task": task,
        "round": round_num,
        "nonce": nonce,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url,
    }

    max_retries = 5
    delay = 1  # Initial delay in seconds

    for i in range(max_retries):
        try:
            response = requests.post(evaluation_url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                print("Successfully notified evaluation service.")
                return True
            else:
                print(f"Failed to notify evaluation service. Status code: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to evaluation service: {e}")

        time.sleep(delay)
        delay *= 2  # Exponential backoff

    print("Could not notify evaluation service after multiple retries.")
    return False

def process_request(data):
    task_id = data.get('task')
    brief = data.get('brief')
    attachments = data.get('attachments', [])
    email = data.get('email')
    round_num = data.get('round')
    nonce = data.get('nonce')
    evaluation_url = data.get('evaluation_url')

    print(f"Processing task: {task_id}")

    g = Github(os.getenv("GITHUB_TOKEN"))
    user_login = g.get_user().login

    # 1. Generate application
    repo_dir = generate_application(task_id, brief, attachments, user_login)
    print(f"Application generated in {repo_dir}")

    # 2. Deploy to GitHub
    repo_url, commit_sha, pages_url, _ = deploy_to_github(task_id, repo_dir, brief, round_num)

    if repo_url:
        print(f"Deployment successful: {repo_url}")
        # 3. Notify evaluation service
        notify_evaluation_service(email, task_id, round_num, nonce, repo_url, commit_sha, pages_url, evaluation_url)
    else:
        print("Deployment failed.")

    # Clean up local directory
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)

if __name__ == '__main__':
    app.run(port=5000)