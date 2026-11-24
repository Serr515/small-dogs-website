from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT.parent / 'questions.sqlite3'


class Site(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path != '/api/questions':
            return self.send_error(404)
        if self.headers.get('X-Feedback') != '1':
            return self.send_error(403)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 40000:
                return self.send_error(413)
            data = parse_qs(self.rfile.read(size).decode(), max_num_fields=2)
            message = data['message'][0].strip()
            contact = data['contact'][0].strip()
            if not (0 < len(message) <= 3000 and 0 < len(contact) <= 200):
                return self.send_error(400)
        except (ValueError, KeyError):
            return self.send_error(400)
        try:
            with sqlite3.connect(DATABASE) as db:
                db.execute('CREATE TABLE IF NOT EXISTS questions (created TEXT DEFAULT CURRENT_TIMESTAMP, contact TEXT, message TEXT)')
                db.execute('INSERT INTO questions(contact,message) VALUES (?,?)', (contact, message))
        except sqlite3.Error:
            return self.send_error(503)
        self.send_response(204)
        self.end_headers()


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 18743), Site).serve_forever()
