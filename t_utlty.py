import numpy as np
from utlty import chk_single_elem_flg, val_sud, \
	gen_sud, blnk_sud, unq_elems, \
	gen_l_l_idxs, inc_l_idxs, gen_sud_var_fac_lnks, \
	get_obs_var

# chk_single_elem_flg
a = np.asarray([1, 2, 3, 4, 5, 1, 2])
assert chk_single_elem_flg(a, 3)
assert chk_single_elem_flg(a, 4)
assert chk_single_elem_flg(a, 5)
assert not chk_single_elem_flg(a, 1)
assert not chk_single_elem_flg(a, 2)
assert not chk_single_elem_flg(a, 6)

# unq_elems
a = np.asarray([1, 2, 3, 4])
assert unq_elems(list(a))
a = np.asarray([1, 1, 2, 3, 4])
assert not unq_elems(list(a))
a = np.asarray([0, 1, 0, 2])
assert not unq_elems(list(a))
A = np.asarray([[1, 2, 3, 4], [2, 1, 4, 3],
				[3, 4, 2, 1], [4, 3, 1, 2]])
for idx in range(4):
	assert unq_elems(list(A[idx, :]))
	assert unq_elems(list(A[:, idx]))

# val_sud
A = np.asarray([[1, 2], [2, 1]])
assert val_sud(A)
A = np.asarray([[1, 2], [1, 2]])
assert not val_sud(A)
A = np.asarray([[1, 2, 3], [3, 1, 2], [2, 3, 1]])
assert val_sud(A)
A = np.asarray([[1, 2, 3], [3, 2, 1], [2, 3, 1]])
assert not val_sud(A)

# gen_sud and val_sud
for N in range(2, 10):
	print('gen_sud({0})'.format(N))
	for idx in range(100):
		A = gen_sud(N)
		assert val_sud(A)


# gen_sud and blnk_sud
N_ = [4, 9]
blnk_elems_ = [2, 20]
for N, blnk_elems in zip(N_, blnk_elems_):
	A = gen_sud(N)
	blnk_A = blnk_sud(A, blnk_elems)
	nz = 0
	for r_idx in range(N):
		for c_idx in range(N):
			if blnk_A[r_idx, c_idx] == 0:
				nz += 1
	assert nz == blnk_elems

# inc_l_idxs
l_idxs = [0, 1, 1]
inc_l_idxs(l_idxs, 2)
assert (l_idxs[0] == 1 and 
		l_idxs[1] == 0 and
		l_idxs[2] == 0)

l_idxs = [0, 1, 2, 1]
inc_l_idxs(l_idxs, 3)
assert (l_idxs[0] == 0 and
		l_idxs[1] == 1 and
		l_idxs[2] == 2 and
		l_idxs[3] == 2)

# gen_l_l_idxs
l_l_idxs = gen_l_l_idxs(1, 3)
for idx, l_idxs in enumerate(l_l_idxs):
	assert l_idxs[0] == idx

l_l_idxs = gen_l_l_idxs(2, 3)
l_l_idxs_t = [[0, 0], [0, 1], [0, 2],
			  [1, 0], [1, 1], [1, 2],
			  [2, 0], [2, 1], [2, 2]]
for l_idx in l_l_idxs_t:
	assert l_idx in l_l_idxs
assert len(l_l_idxs) == len(l_l_idxs_t)

# gen_sud_var_fac_lnks
var_fac_sud = [[0, 2], [0, 3], 
			   [1, 2], [1, 3]]
l_l_idxs = gen_sud_var_fac_lnks(2)
for l_idxs in l_l_idxs:
	assert l_idxs in var_fac_sud
assert len(l_l_idxs) == len(var_fac_sud)

var_fac_sud = [[0, 3], [0, 4], [0, 5],
			   [1, 3], [1, 4], [1, 5],
			   [2, 3], [2, 4], [2, 5]]
l_l_idxs = gen_sud_var_fac_lnks(3)
for l_idxs in l_l_idxs:
	assert l_idxs in var_fac_sud
assert len(l_l_idxs) == len(var_fac_sud)

# get_obs_var
A = np.asarray([[1, 0], [0, 0]])
var_obs = get_obs_var(A)
assert var_obs[0][0] == 1
assert var_obs[0][1] == 0
for obs_val in var_obs[1:]:
	assert obs_val is None

A = np.asarray([[1, 2, 3], [0, 0, 0], [0, 0, 0]])
var_obs = get_obs_var(A)
assert var_obs[0][0] == 1
assert var_obs[0][1] == 0
assert var_obs[0][2] == 0

assert var_obs[1][0] == 0
assert var_obs[1][1] == 1
assert var_obs[1][2] == 0

assert var_obs[2][0] == 0
assert var_obs[2][1] == 0
assert var_obs[2][2] == 1
for obs_val in var_obs[3:]:
	assert obs_val is None
