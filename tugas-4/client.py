import sys
import socket
import json
import logging
import ssl
import os


logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_HOST = 'localhost'
THREAD_POOL_PORT = 8885
PROCESS_POOL_PORT = 8889

def make_socket(destination_address, port):
    """Membuat dan mengembalikan objek socket TCP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"Menghubungkan ke {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.error(f"Kesalahan saat membuat socket: {str(ee)}")
        return None

def make_secure_socket(destination_address, port):
    """
    Membuat dan mengembalikan objek socket SSL/TLS.
    Catatan: Untuk tujuan tugas ini, verifikasi sertifikat dinonaktifkan
    (context.check_hostname = False, context.verify_mode = ssl.CERT_NONE).
    Dalam produksi, ini harus diaktifkan.
    """
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"Menghubungkan secara aman ke {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        logging.warning(f"Sertifikat peer: {secure_socket.getpeercert()}")
        return secure_socket
    except Exception as ee:
        logging.error(f"Kesalahan saat membuat socket aman: {str(ee)}")
        return None

def send_command(command_str, host, port, is_secure=False):
    """
    Mengirimkan perintah HTTP ke server dan mengembalikan respons.
    """
    if is_secure:
        sock = make_secure_socket(host, port)
    else:
        sock = make_socket(host, port)

    if not sock:
        return "Gagal membuat koneksi socket."

    try:
        logging.warning(f"Mengirimkan perintah:\n{command_str}")
        sock.sendall(command_str.encode('latin-1')) 
        
        data_received = b"" # Menggunakan bytes untuk menerima data
        while True:
            data = sock.recv(2048)
            if data:
                data_received += data
                # Cek apakah header dan body sudah lengkap (dua CRLF)
                if b"\r\n\r\n" in data_received:
                    # Coba deteksi Content-Length untuk memastikan semua body diterima
                    headers_part, body_part = data_received.split(b"\r\n\r\n", 1)
                    headers_str = headers_part.decode('latin-1')
                    
                    content_length = 0
                    for line in headers_str.split('\r\n'):
                        if line.lower().startswith('content-length:'):
                            try:
                                content_length = int(line.split(':')[1].strip())
                                break
                            except ValueError:
                                pass
                    
                    if content_length > 0 and len(body_part) < content_length:
                        # Jika Content-Length ada dan body belum lengkap, terus terima data
                        continue
                    else:
                        break # Body sudah lengkap atau Content-Length tidak ada
            else:
                break # Tidak ada lagi data

        hasil = data_received.decode('latin-1') # Decode respons ke string
        logging.warning("Data diterima dari server:")
        return hasil
    except Exception as ee:
        logging.error(f"Kesalahan selama pengiriman/penerimaan data: {str(ee)}")
        return False
    finally:
        if sock:
            sock.close()

def list_files(host, port):
    """Mengirimkan permintaan GET untuk melihat daftar file."""
    cmd = f"""GET /list HTTP/1.0
Host: {host}
User-Agent: myclient/1.1
Accept: text/html

"""
    return send_command(cmd, host, port)

def upload_file(host, port, filename, content):
    """Mengirimkan permintaan PUT untuk mengunggah file."""
    cmd = f"""PUT /{filename} HTTP/1.0
Host: {host}
User-Agent: myclient/1.1
Content-Length: {len(content)}
Content-Type: text/plain

{content}""" # Konten file langsung ditambahkan setelah header
    return send_command(cmd, host, port)

def delete_file(host, port, filename):
    """Mengirimkan permintaan DELETE untuk menghapus file."""
    cmd = f"""DELETE /{filename} HTTP/1.0
Host: {host}
User-Agent: myclient/1.1

"""
    return send_command(cmd, host, port)

if __name__ == '__main__':
    # --- Contoh Penggunaan dengan Thread Pool Server (Port 8885) ---
    print("\n--- Menguji dengan Thread Pool Server (Port 8885) ---")
    
    # 1. List Files
    print("\n[Thread Pool] Mengambil daftar file...")
    response_list = list_files(SERVER_HOST, THREAD_POOL_PORT)
    print(response_list)

    # 2. Upload File
    test_filename_thread = "uploaded_thread.txt"
    test_content_thread = "Ini adalah file yang diunggah melalui thread pool server."
    print(f"\n[Thread Pool] Mengunggah file: {test_filename_thread}")
    response_upload = upload_file(SERVER_HOST, THREAD_POOL_PORT, test_filename_thread, test_content_thread)
    print(response_upload)

    # Verifikasi upload dengan list files lagi
    print("\n[Thread Pool] Mengambil daftar file setelah upload...")
    response_list_after_upload = list_files(SERVER_HOST, THREAD_POOL_PORT)
    print(response_list_after_upload)

    # 3. Delete File
    print(f"\n[Thread Pool] Menghapus file: {test_filename_thread}")
    response_delete = delete_file(SERVER_HOST, THREAD_POOL_PORT, test_filename_thread)
    print(response_delete)

    # Verifikasi delete dengan list files lagi
    print("\n[Thread Pool] Mengambil daftar file setelah delete...")
    response_list_after_delete = list_files(SERVER_HOST, THREAD_POOL_PORT)
    print(response_list_after_delete)


    print("\n--- Menguji dengan Process Pool Server (Port 8889) ---")

    # 1. List Files
    print("\n[Process Pool] Mengambil daftar file...")
    response_list_proc = list_files(SERVER_HOST, PROCESS_POOL_PORT)
    print(response_list_proc)

    test_filename_proc = "uploaded_process.txt"
    test_content_proc = "Ini adalah file yang diunggah melalui process pool server."
    print(f"\n[Process Pool] Mengunggah file: {test_filename_proc}")
    response_upload_proc = upload_file(SERVER_HOST, PROCESS_POOL_PORT, test_filename_proc, test_content_proc)
    print(response_upload_proc)

    print("\n[Process Pool] Mengambil daftar file setelah upload...")
    response_list_after_upload_proc = list_files(SERVER_HOST, PROCESS_POOL_PORT)
    print(response_list_after_upload_proc)


    print(f"\n[Process Pool] Menghapus file: {test_filename_proc}")
    response_delete_proc = delete_file(SERVER_HOST, PROCESS_POOL_PORT, test_filename_proc)
    print(response_delete_proc)

    
    print("\n[Process Pool] Mengambil daftar file setelah delete...")
    response_list_after_delete_proc = list_files(SERVER_HOST, PROCESS_POOL_PORT)
    print(response_list_after_delete_proc)
