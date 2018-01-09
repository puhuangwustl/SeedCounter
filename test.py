#!/usr/bin/python

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import datetime
import base64
import json
import plotly
import io

app = dash.Dash()

app.scripts.config.serve_locally = True

app.layout = html.Div([
	dcc.Upload(
		id='upload-image',
		children=html.Div([
			'Drag and Drop or ',
			html.A('Select Files')
		]),
		style={
			'width': '100%',
			'height': '60px',
			'lineHeight': '60px',
			'borderWidth': '1px',
			'borderStyle': 'dashed',
			'borderRadius': '5px',
			'textAlign': 'center',
			'margin': '10px'
		},
		# Allow multiple files to be uploaded
		multiple=True
	),
	html.Div(id='output-image-upload'),
])

import numpy as np
data = np.zeros((10, 10, 3), dtype=np.uint8)
dd=data.tobytes()


testimg64=base64.b64encode(dd)
#print 'data:image/png;base64,'+testimg64

ffile=open('img/test.png','rb').read()
fcodes=base64.b64encode(ffile)

import cv2

import matplotlib.pyplot as plt
mat=plt.imread('img/test.png')
tmp=cv2.imencode('.png',mat)[1].tostring()

matimg=base64.b64encode(tmp)

def parse_contents(contents, filename, date):
	print matimg[:100]
	print fcodes[:100]
	print contents[:100]
	return html.Div([
		html.H5(filename),
		html.H6(datetime.datetime.fromtimestamp(date)),

		# HTML images accept base64 encoded strings in the same format
		# that is supplied by the upload
		html.Img(src='data:image/png;base64,{}'.format(matimg)),
		html.Img(src='data:image/png;base64,{}'.format(fcodes)),
		html.Img(src=contents),
		html.Hr(),
		html.Div('Raw Content'),
		html.Pre(contents[0:200] + '...', style={
			'whiteSpace': 'pre-wrap',
			'wordBreak': 'break-all'
		})
	])


@app.callback(Output('output-image-upload', 'children'),
			  [Input('upload-image', 'contents'),
			   Input('upload-image', 'filename'),
			   Input('upload-image', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
	if list_of_contents is not None:
		children = [
			parse_contents(c, n, d) for c, n, d in
			zip(list_of_contents, list_of_names, list_of_dates)]
		return children


app.css.append_css({
	'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
	app.run_server(debug=True)
