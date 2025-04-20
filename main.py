from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot actif"

if __name__ == '__main__':
    app.run(debug=True)

import os

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
