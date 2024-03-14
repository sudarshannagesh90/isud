import tkinter as tk
import copy
from utlty import gen_sud, blnk_sud, val_sud
from gen_var_facs import isud
import time
import numpy as np
import datetime
from tkinter.filedialog import askopenfilename
import os

isud_lbls = []
gsud_lbls = []
bsud_lbls = []

def load_sud():
	'''
	We load-sud here.
	'''
	filepath = askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
	if not filepath:
		return
	global init_A, blnk_A
	assert os.path.exists(filepath)
	with open(filepath, 'r') as f:
		fl_l = f.readlines()
	N = int(fl_l[0].strip())
	blnk_elems = int(fl_l[1].strip())
	sud_siz_ent.delete(0, tk.END)
	sud_siz_ent.insert(0, str(N))
	sud_blnk_perc_ent.delete(0, tk.END)
	sud_blnk_perc_ent.insert(0, str(blnk_elems))
	elems = fl_l[2].strip().split(',')
	init_A = np.zeros((N, N), dtype='int')
	blnk_A = np.zeros((N, N), dtype='int')
	c_idx, r_idx = 0, -1
	for idx, elem in enumerate(elems):
		if idx % N == 0:
			r_idx += 1
			c_idx = 0
		init_A[r_idx, c_idx] = int(elem)
		c_idx += 1
	if not val_sud(init_A):
		tk.messagebox.showinfo(title='Not val_sud', message='val_sud(init_A): False')
		return
	elems = fl_l[3].strip().split(',')
	c_idx, r_idx = 0, -1
	for idx, elem in enumerate(elems):
		if idx % N == 0:
			r_idx += 1
			c_idx = 0
		blnk_A[r_idx, c_idx] = int(elem)
		c_idx += 1
	gen_sud_lbls(N)

def save_sud():
	'''
	We save-a-sud here.
	'''
	N = int(sud_siz_ent.get().strip())
	assert N >= 3
	blnk_elems = int(sud_blnk_perc_ent.get().strip())
	fl_name = 'saved_sud_{0}.txt'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
	fl_str = str(N) + '\n' + str(blnk_elems) + '\n'
	elems = []
	for row in init_A:
		for elem in row:
			elems.append(str(elem))
	fl_str += ','.join(elems) + '\n'
	elems = []
	for row in blnk_A:
		for elem in row:
			elems.append(str(elem))
	fl_str += ','.join(elems)	
	with open(fl_name, 'w') as f:
		f.write(fl_str)
	fl_name = os.path.join(os.getcwd(), fl_name)
	tk.messagebox.showinfo(title='Saved as', message=fl_name)

def gen_sud_btn():
	'''
	We gen-sud here.
	'''
	global init_A, blnk_A
	N = int(sud_siz_ent.get().strip())
	assert N >= 3
	init_A = gen_sud(N)
	blnk_elems = int(int(sud_blnk_perc_ent.get().strip()) * N * N / 100)
	blnk_A = blnk_sud(init_A, blnk_elems)
	gen_sud_lbls(N)	

def gen_sud_lbls(N):
	'''
	We gen_sud_lbls here for init_sud, blnk_sud and rn_isud. 
	'''
	global A, isud_lbls, gsud_lbls, bsud_lbls, init_A
	for lbls in [isud_lbls, gsud_lbls, bsud_lbls]:
		for lbl in lbls:
			lbl.destroy()
	assert N >= 3	
	blnk_elems = int(int(sud_blnk_perc_ent.get().strip()) * N * N / 100)
	A = copy.copy(blnk_A)
	isud_lbls = []
	gsud_lbls = []
	bsud_lbls = []
	iter_idx_val_sud_lbl['text'] = ''
	sud_frm_lbl['text'] = 'init_sud'
	blnk_sud_frm_lbl['text'] = 'blnk_sud'
	for r_idx in range(N):
		for c_idx in range(N):
			g_sud_lbl = tk.Label(master=sud_frm_frm_sud_frm, 
								 text=str(init_A[r_idx, c_idx]),
								 relief=tk.RAISED)
			if blnk_A[r_idx, c_idx] != 0:
				b_sud_lbl = tk.Label(master=blnk_sud_frm_frm_sud_frm, 
									 text=str(blnk_A[r_idx, c_idx]),
									 relief=tk.RAISED)
				isud_lbl = tk.Label(master=rn_isud_frm_frm_sud_frm,
									text=str(A[r_idx, c_idx]),
									relief=tk.RAISED)
			else:
				b_sud_lbl = tk.Label(text='  ', bg='white', 
									 master=blnk_sud_frm_frm_sud_frm,
									 relief=tk.RAISED)
				isud_lbl = tk.Label(text='  ', bg='white',
								    master=rn_isud_frm_frm_sud_frm,
								    relief=tk.RAISED)
			g_sud_lbl.grid(row=r_idx, column=c_idx, padx=2, pady=2, 
						   sticky='nsew')
			b_sud_lbl.grid(row=r_idx, column=c_idx, padx=2, pady=2, 
						   sticky='nsew')
			isud_lbl.grid(row=r_idx, column=c_idx, padx=2, pady=2,
						  sticky='nsew')
			isud_lbls.append(isud_lbl)
			gsud_lbls.append(g_sud_lbl)
			bsud_lbls.append(b_sud_lbl)

def rn_isud():
	'''
	We call isud here for performing iters. 
	'''
	global A, isud_lbls
	max_iters = int(isud_max_iters_ent.get().strip())
	stp_val = float(isud_stp_val_ent.get().strip())
	iter_dbg_flg = int(iter_dbg_chk_bx.getvar(str(iter_dbg_chk_bx.cget('variable'))))
	sud_inv = isud(A, max_iters=max_iters, stp_val=stp_val, ap_op=True, 
				   dbg_op=iter_dbg_flg)
	ap_op_iters = sud_inv.rn_isud()
	for ap_op_iter in ap_op_iters:
		A_op = ap_op_iter[0]
		iter_idx_val_sud_lbl['text'] = ap_op_iter[1]
		elem_idx = 0
		for row in A_op:
			for elem in row:
				isud_lbls[elem_idx]['text'] = elem
				elem_idx += 1
		window.update()

window = tk.Tk()
window.geometry("800x400+500+100")       # https://www.geeksforgeeks.org/python-geometry-method-in-tkinter/  (for dimension and position of window on desktop)

window.rowconfigure([2, 3, 4, 5], weight=1, minsize=100)
window.columnconfigure([0, 1, 2], weight=1, minsize=200)

gen_sud_frm = tk.Frame(master=window)					# Title frame
gen_sud_btn_frm = tk.Frame(master=window)				# sud_btn frame
ent_sud_siz_frm = tk.Frame(master=window)				# ent_sud_siz frame
rn_isud_btn_frm = tk.Frame(master=window)				# rn_isud_btn frame 
sud_frm = tk.Frame(master=window, relief=tk.RAISED)		# compl_sud frame
blnk_sud_frm = tk.Frame(master=window, relief=tk.RAISED)# blnk_sud frame
rn_isud_frm = tk.Frame(master=window, relief=tk.RAISED) # rn_isud frame

gen_sud_lbl = tk.Label(master=gen_sud_frm, text='isud',
					   font='Helvetica')

gen_sud_btn = tk.Button(master=gen_sud_btn_frm, text='gen-a-sud',
					    font='Helvetica', relief=tk.RAISED, 
					    command=gen_sud_btn)
load_sud_btn = tk.Button(master=gen_sud_btn_frm, text='load-a-sud',
						 font='Helvetica', relief=tk.RAISED,
						 command=load_sud)
save_sud_btn = tk.Button(master=gen_sud_btn_frm, text='save-a-sud',
						 font='Helvetica', relief=tk.RAISED,
						 command=save_sud)

sud_siz_lbl = tk.Label(master=ent_sud_siz_frm, text='Enter N (>= 3):',
					   font='Helvetica')
sud_siz_ent = tk.Entry(master=ent_sud_siz_frm, width=10)
sud_siz_ent.insert(0, '5')
sud_blnk_perc_lbl = tk.Label(master=ent_sud_siz_frm, text='Enter blnk_perc:',
							 font='Helvetica')
sud_blnk_perc_ent = tk.Entry(master=ent_sud_siz_frm, width=10)
sud_blnk_perc_ent.insert(0, '50')

isud_max_iters_lbl = tk.Label(master=rn_isud_btn_frm, text='max_iters:',
							  font='Helvetica')
isud_max_iters_ent = tk.Entry(master=rn_isud_btn_frm,
							  relief=tk.RAISED, font='Helvetica', width=10)
isud_max_iters_ent.insert(0, '30')
isud_stp_val_lbl = tk.Label(master=rn_isud_btn_frm, text='stp_val:',
							font='Helvetica')
isud_stp_val_ent = tk.Entry(master=rn_isud_btn_frm, textvariable='0.75',
							relief=tk.RAISED, font='Helvetica', width=10)
isud_stp_val_ent.insert(0, '0.49')
rn_isud_btn = tk.Button(master=rn_isud_btn_frm, text='rn-isud',
					    font='Helvetica', relief=tk.RAISED, command=rn_isud)
iter_dbg_chk_bx = tk.Checkbutton(master=rn_isud_btn_frm, text='iter-dbg')

gen_sud_lbl.pack()
gen_sud_btn.grid(row=0,column=1, pady=5)
load_sud_btn.grid(row=1,column=0, padx=5)
save_sud_btn.grid(row=1,column=1)

sud_siz_lbl.grid(row=0, column=0)
sud_siz_ent.grid(row=0, column=1)
sud_blnk_perc_lbl.grid(row=1, column=0)
sud_blnk_perc_ent.grid(row=1, column=1)
isud_max_iters_lbl.grid(row=0, column=0)
isud_max_iters_ent.grid(row=0, column=1, columnspan=2)
isud_stp_val_lbl.grid(row=1, column=0)
isud_stp_val_ent.grid(row=1, column=1, columnspan=2)
rn_isud_btn.grid(row=2, column=1)
iter_dbg_chk_bx.grid(row=2, column=2)

gen_sud_frm.grid(row=0, column=1, sticky='ew', padx=2, pady=2)
gen_sud_btn_frm.grid(row=1, column=0)
ent_sud_siz_frm.grid(row=1, column=1)
rn_isud_btn_frm.grid(row=1, column=2)
sud_frm.grid(row=2, column=0, rowspan=4, pady=3, padx=3, sticky='nsew')
blnk_sud_frm.grid(row=2, column=1, rowspan=4, pady=3, padx=3, sticky='nsew')
rn_isud_frm.grid(row=2, column=2, rowspan=4, pady=3, padx=3, sticky='nsew')

sud_frm_frm = tk.Frame(master=sud_frm)
sud_frm_frm_lbl_frm = tk.Frame(master=sud_frm_frm)
sud_frm_frm_sud_frm = tk.Frame(master=sud_frm_frm)
blnk_sud_frm_frm = tk.Frame(master=blnk_sud_frm)
blnk_sud_frm_frm_lbl_frm = tk.Frame(master=blnk_sud_frm_frm)
blnk_sud_frm_frm_sud_frm = tk.Frame(master=blnk_sud_frm_frm)
rn_isud_frm_frm = tk.Frame(master=rn_isud_frm)
rn_isud_frm_frm_lbl_frm = tk.Frame(master=rn_isud_frm_frm)
rn_isud_frm_frm_sud_frm = tk.Frame(master=rn_isud_frm_frm)
sud_frm_frm.pack()
sud_frm_frm_lbl_frm.pack()
sud_frm_frm_sud_frm.pack()
sud_frm_lbl = tk.Label(master=sud_frm_frm_lbl_frm, text='',
				   	   font='Helvetica')
sud_frm_lbl.pack()
blnk_sud_frm_frm.pack()
blnk_sud_frm_frm_lbl_frm.pack()
blnk_sud_frm_frm_sud_frm.pack()
blnk_sud_frm_lbl = tk.Label(master=blnk_sud_frm_frm_lbl_frm, text='',
				   	   		font='Helvetica')
blnk_sud_frm_lbl.pack()
rn_isud_frm_frm.pack()
rn_isud_frm_frm_lbl_frm.pack()
rn_isud_frm_frm_sud_frm.pack()
iter_idx_val_sud_lbl = tk.Label(master=rn_isud_frm_frm_lbl_frm, text='',
							  	font='Helvetica')
iter_idx_val_sud_lbl.pack()

window.mainloop()
