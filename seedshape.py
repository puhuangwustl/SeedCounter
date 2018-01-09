#!/usr/bin/python
import sys
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('input',help='image input',type=str)
parser.add_argument('-t','--threshold',help='manual threshold (automatic if not set)',type=int)
parser.add_argument('-m','--min',help='min object size in pixel',type=int,default=1000)
parser.add_argument('-M','--max',help='max object size in pixel',type=int,default=100000000)
parser.add_argument('-n','--no_table_head',help='do not print table head',action='store_true',default=False)
parser.add_argument('-o','--output',help='output image path (show image)',type=str)
args=vars(parser.parse_args())

import matplotlib
if args['output']:
	matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
#import matplotlib.cm as cm
import cv2

print  >>sys.stderr, 'reading image...'
im=plt.imread(args['input'])

# use red/2+green/2-blue/4
im_grey=im[...,2]/2+im[...,1]/2-im[...,0]/4       ############################ flexible

print  >>sys.stderr, 'find threshold...'
if args['threshold']:
	T=args['threshold']
else:
	import mahotas
	T=mahotas.thresholding.otsu(im_grey)
print  >>sys.stderr, 'threshold:',T
print  >>sys.stderr, 'masking original image...'

ret, thresh = cv2.threshold(im_grey, T, 255, cv2.THRESH_BINARY)
thresh_cp=thresh.copy()
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

def longaxis(cnt):
	maxl=0
	l=len(cnt)
	for i in range(l):
		for j in range(i,l):
			ax=cv2.norm(cnt[i],cnt[j])
			if ax>maxl:
				maxl,a,b=ax,cnt[i],cnt[j]
	return maxl,tuple(a[0]),tuple(b[0])

print >>sys.stderr, 'analysis'
wid=len(im_grey[1])
leng=len(im_grey)
## set as mask to lure out the original images for light 
## bigarea exclusion .... in case that two seeds overlapping
## centeroid detection, valid contour into single image for further EFA analysis rotation? ... maybe no need or not worth??? not sure yet
if not args['no_table_head']:
	print '#Input_file\tOutput_file\tObject_number\tArea\tLong\tWid_adj\tLong_ellipse\tWid_ellipse\tMoment_1\tMoment_2\tMoment_3\tMoment_4\tMoment_5\tMoment_6\tMoment_7'
count=0
fig=plt.figure()
for i in contours:
	a=cv2.contourArea(i) # area
	# area threshold; no touch edge and no small noisy background spots
	if a<args['max'] and a>args['min'] and np.min(i)>1 and np.max(i[...,0]<wid-1) and np.max(i[...,-1]<leng-1):
		#print a
		count+=1
		# plot sign and text
		d=map(list,i[1])[0] # marker for plotting
		plt.plot(d[0],d[1],'o',color='r')
		plt.text(d[0],d[1],str(count),color='r',fontsize=20)
		# basic metrics
		tmp=longaxis(i) # contour long axis
		cv2.line(im,tmp[1],tmp[2],(0,0,255),5)  # plot long axis
		metric=[a,tmp[0],a/tmp[0]]  # area,longaxis,adjusted_width
		# ellipse fitting
		tmp=cv2.fitEllipse(i) # ellipse fitting and long short axis
		ellipsefit=tmp[1][::-1] # ellipse fitting and long short axis
		cv2.ellipse(im,tmp,(0,255,0),5) # plot ellipse
		# moments
		moments=zip(*cv2.HuMoments(cv2.moments(i)))[0]	# moments
		#moments[-1]=abs(moments[-1]) # if need to exclude sign of last moment ...
		print '\t'.join([args['input'],str(args['output']),str(count),'\t'.join(map(str,metric)),'\t'.join(map(str,ellipsefit)),'\t'.join(map(str,moments))])

plt.imshow(im)
if not args['output']:
	plt.show()
else:
	plt.savefig(args['output'])

