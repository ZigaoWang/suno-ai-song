# Suno Music Generator

Welcome to the Suno Music Generator! This application allows users to generate music based on text prompts using Suno's `chirp-v3-5` model from Turbo AI from [turboai.io](https://turboai.io). It includes a frontend interface for inputting prompts and playing generated songs, as well as an admin dashboard for managing licenses.

> [!NOTE]
> ### Do You Want to Get 200 Songs for Free?
> We value contributions to the project! If you'd like to try out the application but don't have a license, you can generate 200 songs for free by opening a PR. Check [this](LICENSE_REQUESTS_INSTRUCTIONS.md) out for more information.

## Features

- Create lyrics using `gpt-4o-mini` model.
- Generate music based on lyrics and the text prompt using `chirp-v3-5` model.
- Play generated songs and view lyrics.
- Admin dashboard for managing licenses.
- License-based usage limits.
- Caching and displaying previously generated songs.

## Live Demo

A live demo of the application can be found [here](https://suno.zigao.wang).

## Getting Started

To get a local copy up and running, follow these steps:

### Prerequisites

- Python 3.8+
- Flask
- SQLAlchemy
- dotenv

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/ZigaoWang/suno-ai-song.git
    cd suno-ai-song
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory of the project and add your API keys and other configurations:

    ```bash
    touch .env
    ```

    Add the following content to your `.env` file:

    ```env
    API_KEY=your_turbo_api_key
    SECRET_KEY=your_flask_secret_key
    ADMIN_USERNAME=admin
    ADMIN_PASSWORD=admin_password
    OPENAI_API_KEY=your_openai_api_key
    OPENAI_BASE_URL=https://api.openai.com/v1
    ```

5. Initialize the SQLite database:

    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

6. Run the Flask application:

    ```bash
    flask run
    ```

The application will be available at `http://127.0.0.1:5000`.

## Configuration

Configuration is managed through environment variables. Make sure to set the following variables in your `.env` file:

- `API_KEY`: Your Turbo AI API key.
- `SECRET_KEY`: A secret key for Flask session management.
- `ADMIN_USERNAME`: The username for the admin dashboard.
- `ADMIN_PASSWORD`: The password for the admin dashboard.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `OPENAI_BASE_URL`: The base URL for OpenAI API requests.

## Usage

### Generating Music

1. Enter your license key in the input field and click "Activate".
2. Once activated, enter a text prompt and click "Generate".
3. The application will generate a song based on the prompt and display it in the playlist.

### Playing Songs

- Click on a song in the playlist to play it.
- The song's video and lyrics will be displayed in the "Now Playing" section.

## Admin Dashboard

The admin dashboard allows you to manage licenses for the application.

### Accessing the Admin Dashboard

1. Navigate to `/login` and log in with the admin username and password.
2. Once logged in, you can add, edit, and delete licenses.

### Adding a License

1. Enter the maximum number of songs and optional remarks in the form.
2. Click "Add License" to generate a new license key.

### Editing a License

1. Click "Edit" next to the license you want to modify.
2. Update the maximum number of songs and/or remarks.
3. Click "Update" to save changes.

### Deleting a License

1. Click "Delete" next to the license you want to remove.
2. Confirm the deletion in the popup dialog.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.