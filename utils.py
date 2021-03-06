#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-08-15 19:57:00
# @Author  : Mengji Zhang (zmj_xy@sjtu.edu.cn)

import gzip
from six.moves import cPickle
import numpy as np
import scipy.sparse as sp

def gen_adj_matrix(vertex,hood_indices,edge,sigma=1):
	adj_distance=np.zeros(shape=(len(vertex),len(vertex)))
	adj_angle=np.zeros(shape=(len(vertex),len(vertex)))
	for i,indices in enumerate(hood_indices):
		adj_distance[i,indices]=np.exp(-edge[i,:,0:1]*edge[i,:,0:1]/(2*sigma*sigma))
		adj_angle[i,indices]=edge[i,:,1:2]
	# #make it symmetric
	# adj_distance=adj_distance+np.multiply(adj_distance.T,(adj_distance.T>adj_distance))-np.multiply(adj_distance,(adj_distance.T>adj_distance))
	# adj_angle=adj_angle+np.multiply(adj_angle.T,(adj_angle.T>adj_angle))-np.multiply(adj_angle,(adj_angle.T>adj_angle))
	#normalization
	adj_distance=normalize(adj_distance+np.eye(adj_distance.shape[0]))
	adj_angle=normalize(adj_angle+np.eye(adj_angle.shape[0]))
	return adj_distance,adj_angle
def normalize(matrix):
	"""
	A/D
	"""
	rowsum=matrix.sum(axis=1)
	r_inv=np.power(rowsum,-1).flatten()
	r_inv[np.isinf(r_inv)]=0
	r_mat_inv=sp.diags(r_inv)
	matrix=r_mat_inv.dot(matrix)
	return matrix
def to_onehot(labels):
	onehots=np.zeros(shape=(len(labels),2))
	for i,l in enumerate(labels):
		if l==1:
			onehots[i,1]=1
		else:
			onehots[i,0]=1
	return onehots
def downsample(pairs):
	negative_idxs=[]
	positive_idxs=[]
	for i,p in enumerate(pairs):
		if p[-1]==-1:
			negative_idxs.append(i)
		else:
			positive_idxs.append(i)
	negative_idxs=np.array(negative_idxs)
	selected_idxs=np.random.choice(negative_idxs,size=np.sum(pairs[:,-1]==1),replace=False)
	all_idxs=[];all_idxs.extend(positive_idxs);all_idxs.extend(selected_idxs)
	return np.array(pairs[all_idxs])
def load_data(path):
	with gzip.open(path,"rb") as f:
		_,data=cPickle.load(f,encoding="latin1")

	graphs=[]
	for protein in data:
		r_vertex=protein["r_vertex"]
		l_vertex=protein["l_vertex"]
		complex_code=protein["complex_code"]
		r_edge=protein["r_edge"]
		l_edge=protein["l_edge"]
		label=protein["label"]
		r_hood_indices=protein["r_hood_indices"]
		l_hood_indices=protein["l_hood_indices"]
		# if "test" in path:
		if 1:
			label=downsample(label)

		r_adj_distance,r_adj_angle=gen_adj_matrix(r_vertex,r_hood_indices,r_edge)
		l_adj_distance,l_adj_angle=gen_adj_matrix(l_vertex,l_hood_indices,l_edge)
		#normalization on vertexs
		r_vertex=normalize(r_vertex)
		l_vertex=normalize(l_vertex)

		r_graph={"adj_distance":r_adj_distance,"adj_angle":r_adj_angle,"vertex":r_vertex}
		l_graph={"adj_distance":l_adj_distance,"adj_angle":l_adj_angle,"vertex":l_vertex}

		data={}
		data["ligand"]=l_graph
		data["receptor"]=r_graph
		if "train" in path:
			all_idxs=np.arange(len(label))
			np.random.shuffle(all_idxs)
			label=label[all_idxs,:]
		data["ligand_indices"]=label[:,0]
		data["receptor_indices"]=label[:,1]
		labels=to_onehot(label[:,2])
		data["label"]=labels
		data["complex_code"]=complex_code
		graphs.append(data)
	return graphs
def compute_accuracy(preds,trues):

	preds_=np.argmax(preds,axis=1)
	trues_=np.argmax(trues,axis=1)
	cnts=np.sum(preds_==trues_)
	return cnts/len(preds)

if __name__=="__main__":
	graphs=load_data("E:/proteins/test.cpkl.gz")
	print(graphs[0]["ligand"]["vertex"].shape)
