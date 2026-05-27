"""
Server launcher for the Panel HoloViz app. Call with a workbook path:

python panel_server.py "C:\path\to\file.xlsx"

This script starts a Panel server hosting the interactive datashader plot.
"""
import sys
import os
import panel as pn
from panel_app import create_app

if __name__ == '__main__':
    wb = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), 'he test.xlsx')
    app = create_app(wb)
    pn.serve(app, port=5006, show=True, allow_websocket_origin=['localhost:5006'])
