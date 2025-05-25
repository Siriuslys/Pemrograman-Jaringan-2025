import json
import logging
import shlex

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self,string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")

        # Handle special cases for UPLOAD command that may contain spaces in base64
        if string_datamasuk.lower().startswith('upload'):
            parts = string_datamasuk.split(' ', 2)  # Split into max 3 parts
            if len(parts) >= 3:
                c_request = parts[0].strip().lower()
                filename = parts[1].strip()
                file_content = parts[2].strip()
                params = [filename, file_content]
            else:
                return json.dumps(dict(status='ERROR',data='UPLOAD command format salah'))
        else:
            c = shlex.split(string_datamasuk.lower())
            if not c:
                return json.dumps(dict(status='ERROR',data='request kosong'))
            c_request = c[0].strip()
            params = [x for x in c[1:]]

        try:
            logging.warning(f"memproses request: {c_request}")
            cl = getattr(self.file,c_request)(params)
            return json.dumps(cl)
        except AttributeError:
            return json.dumps(dict(status='ERROR',data='request tidak dikenali'))
        except Exception as e:
            return json.dumps(dict(status='ERROR',data=str(e)))
 
if __name__=='__main__':
    #contoh pemakaian
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET pokijan.jpg"))