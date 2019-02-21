from bookmarkserver.app import bookmark_server
from waitress import serve
if __name__ == "__main__":
    ENV=bookmark_server.config.get("ENV",'').lower()
    port = bookmark_server.config.get("PORT")
    if ENV =='development' or ENV =='testing':
        bookmark_server.run(host='0.0.0.0',port=port)
    else:
        serve(bookmark_server,host='0.0.0.0', port=port)