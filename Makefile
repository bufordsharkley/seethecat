freeze:
	    env/bin/python freeze.py

server: freeze
	    python -m SimpleHTTPServer
