import os

from seaserver.app import app

if __name__ == "__main__":    
    port = int(os.environ.get('PORT', 5000))

    app.run(threaded=True, debug=True, host="localhost", port=port)