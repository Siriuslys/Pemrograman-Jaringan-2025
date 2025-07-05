import sys
import os.path
import uuid
from glob import glob
from datetime import datetime

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.png'] = 'image/png' # Tambahkan tipe untuk PNG
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'
        self.types['.py'] = 'text/x-python' # Tambahkan tipe untuk Python files

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append(f"HTTP/1.0 {kode} {message}\r\n")
        resp.append(f"Date: {tanggal}\r\n")
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append(f"Content-Length: {len(messagebody)}\r\n")
        for kk in headers:
            resp.append(f"{kk}:{headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp)
        
        if (type(messagebody) is not bytes):
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self, data):
        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if (method == 'GET'):
                if object_address == '/list':
                    return self.http_list_files(all_headers)
                else:
                    return self.http_get(object_address, all_headers)
            elif (method == 'POST'): 
                body_start_index = data.find("\r\n\r\n")
                if body_start_index != -1:
                    request_body = data[body_start_index + 4:]
                else:
                    request_body = ""
                return self.http_post(object_address, all_headers, request_body)
            elif (method == 'PUT'): 
                body_start_index = data.find("\r\n\r\n")
                if body_start_index != -1:
                    request_body = data[body_start_index + 4:]
                else:
                    request_body = ""
                return self.http_put(object_address, all_headers, request_body)
            elif (method == 'DELETE'):
                return self.http_delete(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    def http_list_files(self, headers):
        """
        Mengembalikan daftar file di direktori server sebagai HTML.
        """
        thedir = './'
        files = [f for f in os.listdir(thedir) if os.path.isfile(os.path.join(thedir, f))]
        
        file_list_html = "<h1>Daftar File di Server</h1><ul>"
        for f in files:
            file_list_html += f"<li><a href='/{f}'>{f}</a></li>"
        file_list_html += "</ul>"

        headers = {'Content-type': 'text/html'}
        return self.response(200, 'OK', file_list_html, headers)

    def http_get(self, object_address, headers):
        files = glob('./*')
        thedir = './'
        if (object_address == '/'):
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan', dict())

        if (object_address == '/video'):
            return self.response(302, 'Found', '', dict(location='https://youtu.be/katoxpnTf04'))
        if (object_address == '/santai'):
            return self.response(200, 'OK', 'santai saja', dict())

        object_address = object_address[1:] # Hapus '/' di awal
        full_path = os.path.join(thedir, object_address)

        if not os.path.isfile(full_path):
            return self.response(404, 'Not Found', '', {})
        
        try:
            with open(full_path, 'rb') as fp:
                isi = fp.read()
            
            fext = os.path.splitext(full_path)[1]
            content_type = self.types.get(fext, 'application/octet-stream') # Default jika tipe tidak ditemukan
            
            headers = {'Content-type': content_type}
            return self.response(200, 'OK', isi, headers)
        except Exception as e:
            print(f"Error reading file: {e}")
            return self.response(500, 'Internal Server Error', '', {})

    def http_post(self, object_address, headers, request_body):
        return self.response(405, 'Method Not Allowed', 'POST tidak didukung untuk operasi ini. Gunakan PUT untuk upload.', {})

    def http_put(self, object_address, headers, request_body):
        """
        Mengunggah file ke server. object_address adalah nama file.
        request_body adalah konten file.
        """
        filename = object_address[1:] # Hapus '/' di awal
        if not filename:
            return self.response(400, 'Bad Request', 'Nama file tidak boleh kosong', {})

        try:
            with open(filename, 'wb') as f:
                f.write(request_body.encode('latin-1')) # Menggunakan latin-1 untuk menangani byte secara langsung
            return self.response(201, 'Created', f'File {filename} berhasil diunggah', {})
        except Exception as e:
            print(f"Error uploading file: {e}")
            return self.response(500, 'Internal Server Error', f'Gagal mengunggah file: {e}', {})

    def http_delete(self, object_address, headers):
        """
        Menghapus file dari server. object_address adalah nama file.
        """
        filename = object_address[1:] 
        if not filename:
            return self.response(400, 'Bad Request', 'Nama file tidak boleh kosong', {})

        if not os.path.isfile(filename):
            return self.response(404, 'Not Found', f'File {filename} tidak ditemukan', {})

        try:
            os.remove(filename)
            return self.response(200, 'OK', f'File {filename} berhasil dihapus', {})
        except Exception as e:
            print(f"Error deleting file: {e}")
            return self.response(500, 'Internal Server Error', f'Gagal menghapus file: {e}', {})

