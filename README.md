# LLM Code Deployment Project

This project is an application that can build, deploy, and update an application based on a given brief.

## Features

- Receives and verifies a request containing an app brief.
- Uses an LLM-assisted generator to build the app.
- Deploys the app to GitHub Pages.
- Pings an evaluation API with repo details.
- Handles update requests to modify the deployed application.

## Setup

1. Clone the repository.
2. Install the dependencies: `pip install -r requirements.txt`
3. Create a `.env` file and add your `SECRET` and `GITHUB_TOKEN`.
4. Run the application: `python app.py`

## Usage

Send a POST request to the `/api-endpoint` with the application brief in JSON format.

## License

This project is licensed under the MIT License.