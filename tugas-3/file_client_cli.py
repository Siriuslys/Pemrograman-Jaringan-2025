import socket
import json
import base64
import logging
import os

server_address=('0.0.0.0',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False
    finally:
        sock.close()
        
def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        print(f"File {namafile} berhasil didownload")
        return True
    else:
        print(f"Gagal: {hasil.get('data', 'Unknown error')}")
        return False
 
def remote_upload(local_filename="", remote_filename=""):
    """Upload file ke server"""
    try:
        if not os.path.exists(local_filename):
            print(f"File {local_filename} tidak ditemukan")
            return False

        # Read and encode file
        with open(local_filename, 'rb') as fp:
            file_content = fp.read()
            file_content_b64 = base64.b64encode(file_content).decode()

        # Use remote filename if provided, otherwise use local filename
        if not remote_filename:
            remote_filename = os.path.basename(local_filename)

        command_str = f"UPLOAD {remote_filename} {file_content_b64}"
        hasil = send_command(command_str)

        if hasil and hasil['status']=='OK':
            print(f"File {local_filename} berhasil diupload sebagai {remote_filename}")
            return True
        else:
            print(f"Gagal upload: {hasil.get('data', 'Unknown error') if hasil else 'Connection error'}")
            return False
    except Exception as e:
        print(f"Error upload: {e}")
        return False
 
def remote_delete(filename=""):
    """Hapus file dari server"""
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)

    if hasil and hasil['status']=='OK':
        print(f"File {filename} berhasil dihapus")
        return True
    else:
        print(f"Gagal hapus: {hasil.get('data', 'Unknown error') if hasil else 'Connection error'}")
        return False
 
def main_menu():
    """Menu interaktif untuk client"""
    while True:
        print("\n=== FILE SERVER CLIENT ===")
        print("1. List files (LIST)")
        print("2. Download file (GET)")
        print("3. Upload file (UPLOAD)")
        print("4. Delete file (DELETE)")
        print("5. Exit")

        choice = input("Pilih menu (1-5): ").strip()

        if choice == '1':
            print("\nMengambil daftar file...")
            remote_list()

        elif choice == '2':
            filename = input("Nama file yang akan didownload: ").strip()
            if filename:
                print(f"Downloading {filename}...")
                remote_get(filename)
            else:
                print("Nama file tidak boleh kosong")
                
        elif choice == '3':
            local_file = input("Path file lokal yang akan diupload: ").strip()
            remote_name = input("Nama file di server (kosong=sama dengan nama lokal): ").strip()
            if local_file:
                print(f"Uploading {local_file}...")
                remote_upload(local_file, remote_name)
            else:
                print("Path file tidak boleh kosong")
        
        elif choice == '4':
            filename = input("Nama file yang akan dihapus: ").strip()
            if filename:
                confirm = input(f"Yakin ingin menghapus {filename}? (y/n): ").strip().lower()
                if confirm == 'y':
                    print(f"Deleting {filename}...")
                    remote_delete(filename)
                else:
                    print("Batal menghapus")
            else:
                print("Nama file tidak boleh kosong")

        elif choice == '5':
            print("Keluar dari program")
            break

        else:
            print("Pilihan tidak valid")
        
        
if __name__=='__main__':
    # Set server address
    server_address=('127.0.0.1',6666)

    # Setup logging
    logging.basicConfig(level=logging.WARNING)

    # Test basic functionality
    print("Testing basic functionality...")
    print("1. Testing LIST:")
    remote_list()

    print("\n2. Testing UPLOAD:")
    # Create a test file
    test_content = "Hello World! This is a test file."
    with open("test_upload.txt", "w") as f:
        f.write(test_content)
    remote_upload("test_upload.txt", "uploaded_test.txt")

    print("\n3. Testing LIST after upload:")
    remote_list()

    print("\n4. Testing GET:")
    remote_get("uploaded_test.txt")

    print("\n5. Testing DELETE:")
    remote_delete("uploaded_test.txt")
    
    print("\n5. Testing DELETE:")
    remote_delete("uploaded_test.txt")

    print("\n6. Testing LIST after delete:")
    remote_list()

    # Start interactive menu
    print("\nStarting interactive menu...")
    main_menu()