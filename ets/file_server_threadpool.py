from socket import *
import socket
import logging
from file_protocol import FileProtocol
import concurrent.futures
import sys

fp = FileProtocol()

def handle_client(connection, address):
    logging.warning(f"handling connection from {address}")
    buffer = ""
    try:
        connection.settimeout(1800)
        while True:
            data = connection.recv(1024*1024)
            if not data:
                break
            buffer += data.decode('utf-8', errors='ignore')
            while "\r\n\r\n" in buffer:
                command, buffer = buffer.split("\r\n\r\n", 1)
                hasil = fp.proses_string(command)
                response = hasil + "\r\n\r\n"
                connection.sendall(response.encode('utf-8'))
    except socket.timeout:
        logging.warning(f"Connection from {address} timed out")
    except ConnectionResetError:
        logging.warning(f"Connection from {address} was reset by peer")
    except UnicodeDecodeError:
        logging.warning(f"Unicode decode error for connection from {address}")
    except Exception as e:
        logging.warning(f"Error handling client {address}: {str(e)}")
    finally:
        logging.warning(f"connection from {address} closed")
        try:
            connection.close()
        except:
            pass


class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, pool_size=5):
        self.ipinfo = (ipaddress, port)
        self.pool_size = pool_size
        self.my_socket = None
        self.executor = None
        self.running = False

    def create_socket(self):
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.my_socket.settimeout(1.0)

    def run(self):
        self.create_socket()
        logging.warning(f"server running on ip address {self.ipinfo} with thread pool size {self.pool_size}")
        
        try:
            self.my_socket.bind(self.ipinfo)
            self.my_socket.listen(10)
            self.running = True
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.pool_size) as self.executor:
                while self.running:
                    try:
                        connection, client_address = self.my_socket.accept()
                        logging.warning(f"connection from {client_address}")
                        self.executor.submit(handle_client, connection, client_address)
                    except socket.timeout:
                        continue
                    except OSError as e:
                        if self.running:
                            logging.warning(f"Socket error: {str(e)}")
                        break
                        
        except KeyboardInterrupt:
            logging.warning("Server shutting down due to keyboard interrupt")
        except Exception as e:
            logging.error(f"Error in server: {str(e)}")
        finally:
            self.shutdown()

    def shutdown(self):
        logging.warning("Shutting down server...")
        self.running = False
        
        if self.my_socket:
            try:
                self.my_socket.close()
            except:
                pass

        if self.executor:
            self.executor.shutdown(wait=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='File Server')
    parser.add_argument('--port', type=int, default=6667, help='Server port (default: 6667)')
    parser.add_argument('--pool-size', type=int, default=5, help='Thread pool size (default: 5)')
    args = parser.parse_args()
    
    svr = Server(ipaddress='0.0.0.0', port=args.port, pool_size=args.pool_size)
    
    try:
        svr.run()
    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    main()