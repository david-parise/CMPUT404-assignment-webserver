#  coding: utf-8 
from base64 import decode
from genericpath import isfile
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        message = "OK"
        code = 200
        
        decoded_data = self.data.decode("utf-8")
        decoded_data = decoded_data.split(" ")
        
        method = decoded_data[0]
        path = decoded_data[1]
        if path.startswith(os.getcwd() + "/www"): 
            url = path
            norm_url = os.path.normpath(path)
        else:
            url = os.path.join(os.getcwd() + "/www" + path)
            norm_url = os.path.normpath(os.getcwd() + "/www" + path)

        if method != "GET":
            code = 405
            message = self.response(code, url)
        
        elif not norm_url.startswith(os.getcwd() + "/www"):  
            code = 404
            message = self.response(code, url)
        
        elif os.path.isfile(url):
            code = 200
            message = self.response(code, url)
            
        elif os.path.isdir(url):
            if url[-1] == "/":
                url += "index.html"
                if os.path.isfile(url):
                    code = 200
                    message = self.response(code, url)
                else:
                    code = 404
                    message = self.response(code, url)
            else:
                code = 301
                message = self.response(code, path)
                
        elif not os.path.exists(url):
            if url[-1] == "/":
                url += "index.html"
                if os.path.isfile(url):
                    code = 200
                    message = self.response(code, url)
                else:
                    code = 404
                    message = self.response(code, url)
            else:
                code = 404
                message = self.response(code, url)
        
        self.request.sendall(bytearray(message,'utf-8'))
    
    
    def response(self, code, url):
        
        message = ""
        
        if code == 404:
            message = "HTTP/1.1 404 Not Found\nContent-Type: text/html; charset=UTF-8\n\nPAGE NOT FOUND\n"
        
        elif code == 405:
            message = "HTTP/1.1 405 Not Allowed\n\nMETHOD NOT ALLOWED\n"
        
        elif code == 301:
            message = "HTTP/1.1 301 Moved Permanently\nLocation: " + url + "/\n\nPAGE HAS BEEN MOVED PERMANENTLY\n"
        
        elif code == 200:
            message = "HTTP/1.1 200 OK\n"
            
            if url.endswith(".html"):
                message += "Content-Type: text/html; charset=UTF-8\n\n"
            
            elif url.endswith(".css"):
                message += "Content-Type: text/css; charset=UTF-8\n\n"
            
            else:
                message += "Content-Type: text/plain; charset=UTF-8\n\n"
            
            with open(url, "r") as f:
                message += f.read()
        
        return message
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
