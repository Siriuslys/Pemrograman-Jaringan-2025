from socket import *
import socket
import logging
from file_protocol import FileProtocol
import multiprocessing
import concurrent.futures
import threading
import time

fp = FileProtocol()

def handle_client(connection, address):
    logging.warning(f"handling connection from {address}")
    buffer = ""
    try:
        connection.settimeout(300)
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
    except Exception as e:
        logging.warning(f"Error handling client {address}: {str(e)}")
    finally:
        logging.warning(f"connection from {address} closed")
        try:
            connection.close()
        except:
            pass


class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, pool_size=5, use_threading=True):
        self.ipinfo = (ipaddress, port)
        self.pool_size = pool_size
        self.use_threading = use_threading
        self.my_socket = None
        self.executor = None
        self.running = False

    def create_socket(self):
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.my_socket.settimeout(1.0)

    def run(self):
        self.create_socket()
        
        logging.warning(f"server running on ip address {self.ipinfo} with {'thread' if self.use_threading else 'process'} pool size {self.pool_size}")
        
        try:
            self.my_socket.bind(self.ipinfo)
            self.my_socket.listen(10)
            self.running = True
            
            executor_class = (concurrent.futures.ThreadPoolExecutor 
                            if self.use_threading 
                            else concurrent.futures.ProcessPoolExecutor)
            
            with executor_class(max_workers=self.pool_size) as self.executor:
                while self.running:
                    try:
                        connection, client_address = self.my_socket.accept()
                        logging.warning(f"connection from {client_address}")
                        
                        if self.use_threading:
                            self.executor.submit(handle_client, connection, client_address)
                        else:
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


def handle_client_wrapper(conn_info):
    try:
        connection, address = conn_info
        return handle_client(connection, address)
    except Exception as e:
        logging.error(f"Error in wrapper: {str(e)}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='File Server')
    parser.add_argument('--port', type=int, default=6667, help='Server port (default: 6667)')
    parser.add_argument('--pool-size', type=int, default=5, help='Pool size (default: 5)')
    parser.add_argument('--use-processes', action='store_true', 
                       help='Use process pool instead of thread pool')
    args = parser.parse_args()
    
    svr = Server(
        ipaddress='0.0.0.0', 
        port=args.port, 
        pool_size=args.pool_size,
        use_threading=not args.use_processes
    )
    
    try:
        svr.run()
    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    logging.basicConfig(
        level=logging.WARNING, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()