import socket
import threading
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProcessTheClient(threading.Thread):
    """
    Kelas ini menangani setiap koneksi klien secara terpisah dalam sebuah thread.
    """
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        logging.info(f"Menangani koneksi dari: {self.address}")
        try:
            while True:
                data = self.connection.recv(1024).decode('utf-8')
                request = data.strip() 

                if request.startswith("TIME") and request.endswith(""):
                    logging.info(f"[SERVER] Menerima request dari {self.address}: '{request}'")
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    response = f"JAM {current_time}\r\n"
                    self.connection.sendall(response.encode('utf-8'))
                    logging.info(f"[SERVER] Mengirim respon ke {self.address}: '{response.strip()}'")
                elif request == "QUIT":
                    logging.info(f"[SERVER] Klien {self.address} meminta QUIT.")
                    break 
                elif not data:
                    logging.info(f"[SERVER] Tidak ada data dari {self.address}, menutup koneksi.")
                    break 
                else:
                    error_response = "ERR: Format request tidak valid. Gunakan 'TIME<CR><LF>' atau 'QUIT<CR><LF>'\r\n"
                    self.connection.sendall(error_response.encode('utf-8'))
                    logging.warning(f"[SERVER] Menerima request tidak valid dari {self.address}: '{request}'")

        except Exception as e:
            logging.error(f"Error saat memproses klien {self.address}: {e}")
        finally:
            logging.info(f"Menutup koneksi dengan {self.address}")
            self.connection.close()

class Server(threading.Thread):
    """
    Kelas ini berfungsi sebagai server utama yang mendengarkan koneksi masuk.
    """
    def __init__(self, port):
        self.the_clients = []
        self.port = port
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(5)
        logging.info(f"Server mendengarkan di port {self.port}...")

        while True:
            connection, client_address = self.my_socket.accept()
            logging.info(f"Menerima koneksi baru dari {client_address}")
            
            clt = ProcessTheClient(connection, client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    server_port = 45000
    svr = Server(server_port)
    svr.start()

if __name__ == "__main__":
    main()
