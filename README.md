# GitHub Webhook Monitor

This is a Flask and MongoDB application that receives and displays GitHub webhook events (`push`, `pull_request`, `merge`) on a simple UI.

### How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/webhook-repo.git
    cd webhook-repo
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up the environment:**
    - Create a `.env` file.
    - Add your MongoDB connection string to it:
      ```
      MONGO_URI="your-mongodb-connection-string"
      ```

4.  **Run the Flask server:**
    ```bash
    python app.py
    ```
    The server will run on `http://127.0.0.1:5001`.

5.  **Expose the server with ngrok:**
    ```bash
    ngrok http 5001
    ```

6.  **Set up the webhook** in your `action-repo` settings, pointing the **Payload URL** to your ngrok address + `/webhook`.
