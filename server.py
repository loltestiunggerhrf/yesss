from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    port = 8080
    print(f"🚀 Server is running! Visit: http://127.0.0.1:{port}/")
    app.run(host="0.0.0.0", port=port)
