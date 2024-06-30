import numpy as np
import random
import copy

var_dict = {'facs_lnk': [],
			'var_to_facs': [],
			'obs_flg': False,
			'obs_val': None,
			'unsure_flg': False,
			'unsure_val': None}
fac_dict = {'vars_lnk': [],
			'fac_to_vars': [],
			'fac_eval_func': None,
			'fac_eval_func_nam': None,
			'o_var': {}}
			# might need better for this

reg_funcs = []

def get_sud_rows(A):
	N = len(A)
	A_rows = []
	for row in A:
		row_l = []
		for elem in row:
			if elem == 0:
				row_l.append('')
			else:
				row_l.append(str(elem))
		A_rows.append(row_l)
	return A_rows

def registry(func):
	reg_funcs.append(func)
	return func

def chk_single_elem_flg(elems, chk_elem):
	n_c = 0
	for elem in elems:
		if elem == chk_elem:
			n_c += 1
	if n_c == 1:
		return True
	else:
		return False

def val_sud(A):
	nr = np.shape(A)[0]
	nc = np.shape(A)[1]
	assert nr == nc
	sud_elems = list(np.arange(1, nr + 1))
	for r_idx in range(nr):
		for c_idx in range(nc):
			if A[r_idx, c_idx] not in sud_elems:
				return False
	
	v_sud = True
	for idx in range(nr):
		row = A[idx, :]
		col = A[:, idx]
		unq_row_flg = unq_elems(list(row))
		unq_col_flg = unq_elems(list(col))
		if not unq_row_flg or not unq_col_flg:
			v_sud = False
			break
	return v_sud

def gen_sud(N):
	sud_elems = list(np.arange(1, N + 1))
	v_sud = False
	iter_idx = 1
	while not v_sud:
		random.shuffle(sud_elems)
		A = [np.asarray(sud_elems)]
		while len(A) < N:
			poss_row_elems = list(np.arange(1, N + 1))
			random.shuffle(poss_row_elems)
			row_elems = np.zeros(N)
			for col_idx in range(N):
				exis_col_elems = []
				for row in A:
					exis_col_elems.append(row[col_idx])
				for poss_elem in poss_row_elems:
					if poss_elem not in exis_col_elems:
						row_elems[col_idx] = poss_elem
						poss_row_elems.remove(poss_elem)
						break
			A.append(row_elems)
		iter_idx += 1
		A = np.asarray(A, dtype='int')
		if val_sud(A):
			v_sud = True
			break
	return A

def blnk_sud(B, n_elems):
	nr = np.shape(B)[0]
	nc = np.shape(B)[1]
	assert nc == nr
	assert n_elems < nr * nc
	elem_idxs = []
	A = copy.copy(B)
	for r_idx in range(nr):
		for c_idx in range(nc):
			elem_idxs.append([r_idx, c_idx])
	random.shuffle(elem_idxs)
	for idx in range(n_elems):
		A[elem_idxs[idx][0], elem_idxs[idx][1]] = 0
	return A

@registry
def unq_elems(l_elems):
	assert len(l_elems)
	s_elems = set(l_elems)
	if len(s_elems) == len(l_elems):
		return 1
	else:
		return 0

@registry
def single_zero(l_elems):
	n_zeros = 0
	for elem in l_elems:
		if elem == 0:
			n_zeros += 1
	if n_zeros == 1:
		return 1
	else:
		return 0

def inc_l_idxs(l_idxs, poss_vals):
	len_l_idxs = len(l_idxs)
	for idx in range(len_l_idxs - 1, -1, -1):
		if l_idxs[idx] != poss_vals - 1:
			l_idxs[idx] += 1
			for idx1 in range(idx + 1, len_l_idxs):
				l_idxs[idx1] = 0
			break

def gen_l_l_idxs(n_idxs, poss_vals):
	assert poss_vals > 1
	l_idxs = [0 for idx in range(n_idxs)]
	l_l_idxs = [copy.copy(l_idxs)]
	iter_idx = 0
	while True:
		iter_idx += 1
		inc_l_idxs(l_idxs, poss_vals)
		l_l_idxs.append(copy.copy(l_idxs))	
		all_cmp = True
		for idx in l_idxs:
			if idx != poss_vals - 1:
				all_cmp = False
				break
		if all_cmp:
			break
	assert len(l_l_idxs) == poss_vals ** n_idxs
	return l_l_idxs

def gen_sud_var_fac_lnks(N):
	# Input:
	# N: siz. of sud. (how many rows or cols).
	# Let the facs be arrang. as 
	#			[F1_r, F2_r, F3_r, ..., Fn_r,
	#			 Fo_c, Fp_c, Fq_c, ...],
	# where r is for rows and c for cols. and 
	# var. as [[A1, A2], [A3, A4]].
	l_l_idxs = []
	for v_idx in range(N * N):
		l_l_idxs.append([int(np.floor(v_idx / N)), 
						 np.mod(v_idx, N) + N])
	return l_l_idxs

def get_obs_var(A, zero_one_sud=False):
	# Input:
	# A: sud_mat
	# Let vars be arrang. as 
	# [[A1, A2], [A3, A4]]
	n_r = np.shape(A)[0]
	n_c = np.shape(A)[1]
	assert n_r == n_c
	var_obs = []
	for r_idx in range(n_r):
		for c_idx in range(n_c):
			if A[r_idx, c_idx] != 0:
				if zero_one_sud:
					var_obs.append(np.asarray([0, 1]))
				else:
					obs_val = np.zeros(n_r)
					obs_val[int(A[r_idx, c_idx]) - 1] = 1
					var_obs.append(obs_val)
			else:
				var_obs.append(None) 
	return var_obs
