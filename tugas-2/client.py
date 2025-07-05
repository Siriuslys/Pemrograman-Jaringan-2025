import socket
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def request_time(server_address, server_port):
    """
    Fungsi ini mengirimkan request waktu ke server dan menerima respon.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info(f"Mencoba koneksi ke {server_address}:{server_port}")
    
    try:
        sock.connect((server_address, server_port))
        
        message = "TIME\r\n"
        logging.info(f"[CLIENT] Mengirim: '{message.strip()}'")
        sock.sendall(message.encode('utf-8'))
        
        data = sock.recv(1024).decode('utf-8')
        logging.info(f"[CLIENT] Menerima: '{data.strip()}'")

        quit_message = "QUIT\r\n"
        logging.info(f"[CLIENT] Mengirim: '{quit_message.strip()}'")
        sock.sendall(quit_message.encode('utf-8'))

    except ConnectionRefusedError:
        logging.error(f"Koneksi ditolak. Pastikan server berjalan di {server_address}:{server_port}")
    except Exception as e:
        logging.error(f"Terjadi error: {e}")
    finally:
        logging.info("Menutup socket.")
        sock.close()

if __name__ == '__main__':
    server_host = '127.0.0.1' 
    server_port = 45000       

    for i in range(3):
        logging.info(f"\n--- Request ke-{i+1} ---")
        request_time(server_host, server_port)
        time.sleep(1) 
