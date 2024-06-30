import numpy as np
from utlty import gen_l_l_idxs, gen_sud_var_fac_lnks, get_obs_var, \
	 var_dict, fac_dict, val_sud, reg_funcs, get_sud_rows
import copy
import json
import datetime


class isud:
	"""
	This cls. inits. sud_inv and performs sud_inv_iters.
	"""
	def __init__(self, A, max_iters=100, stp_val=0.75, var_ops_unchng_iters=5,
				 ap_op=True, web_op=False, init_A=None, dbg_op=False):
		"""
		Init. the invers.

		Input:
			- A: blnk_sud to invert
			- max_iters: Max. iters for invers.
			- stp_val: Val. to stp. the iters.
			- var_ops_unchng_iters: Unchng var_ops for these iters.
			- ap_op: Flg. for ap_op
			- web_op: Flg. for web_op

			- init_A: init_A to get A; this is for the web por. might not be needed if we are able to do it there
			- dbg_op: Dbg_op_flg
		"""
		self.A = A
		self.max_iters = max_iters
		self.stp_val = stp_val
		self.ap_op = ap_op
		self.web_op = web_op
		self.var_ops_unchng_iters = var_ops_unchng_iters
		self.dbg_op = dbg_op

		self.var_ops_prev_iters = []
		self.init_A = None
		self.blnk_A = None
		if init_A is not None:
			self.init_A = init_A
			self.blnk_A = copy.copy(A)

		self.isud_lbl_str = 'iters: {0}, val_sud: {1}'
		self.siz_sud = A.shape[0]
		self.sud_inv = None

		self.init_inv()

	def init_inv(self,):
		"""
		This is for init. inv.
		"""
		n_vars = self.siz_sud * self.siz_sud
		n_facs = 2 * self.siz_sud
		var_poss_vals = list(np.arange(self.siz_sud) + 1)
		facs_func_nams = ['unq_elems' for _ in range(n_facs)]
		vars_obs = get_obs_var(self.A)
		var_fac_lnk = gen_sud_var_fac_lnks(int(np.sqrt(n_vars)))
		self.sud_inv = vars_facs(n_vars, n_facs, self.stp_val, var_poss_vals,
								 self.max_iters, facs_func_nams, vars_obs,
								 var_fac_lnk, self.dbg_op)

	def get_isud(self, vars_op, iter_idx):
		"""
		This is for accessing rows of isud and isud_lbl_str at iter_idx.

		Input:
			- vars_op: l_of_vars_op
			- iter_idx: iter_idx

		Output:
			- A_rows: Rows of isud at iter_idx
			- isud_lbl_str: isud_lbl at iter_idx
		"""
		A = np.zeros((self.siz_sud, self.siz_sud), dtype='int')
		for idx, var_op in enumerate(vars_op):
			r_idx = int(idx / self.siz_sud)
			c_idx = int(idx % self.siz_sud)
			if var_op is None:
				var_op = 0
			A[r_idx, c_idx] = int(var_op)
		val_isud_lbl = 'No'
		if val_sud(A):
			val_isud_lbl = 'Yes'
		isud_lbl_str = \
			self.isud_lbl_str.format(iter_idx, val_isud_lbl)
		return get_sud_rows(A), isud_lbl_str

	# def var_not_chng(self, vars_op):
	# 	"""
	# 	This is to get if the vars_op is not changing in prev_iters
	# 	and also that it doesnt contain None.

	# 	Input:
	# 		- vars_op: vars_op for the given iter
	# 	Output:
	# 		- var_unchng_flg: Flg. if the vars_op is not changing
	# 		and doesnt contain None
	# 	"""
	# 	if None in vars_op:
	# 		self.var_ops_prev_iters = []
	# 		return False
	# 	else:
	# 		self.var_ops_prev_iters.append(vars_op)

	# 	var_unchng_flg = True
	# 	if len(self.var_ops_prev_iters) > 1:
	# 		for var_idx in range(self.sud_inv.n_vars):
	# 			var_op = self.var_ops_prev_iters[-2][var_idx]
	# 			if var_op != vars_op[var_idx]:
	# 				var_unchng_flg = False
	# 				break

	# 	if not var_unchng_flg:
	# 		self.var_ops_prev_iters = [vars_op]
	# 	elif len(self.var_ops_prev_iters) < self.var_ops_unchng_iters:
	# 		var_unchng_flg = False
	# 	return var_unchng_flg

	def rn_isud(self):
		"""
		This is for rn_isud_iters.
		"""
		for iter_idx in range(self.max_iters):
			vars_op = self.sud_inv.run_iter(iter_idx)
			# var_not_chng_flg = self.var_not_chng(vars_op)
			A, isud_lbl_str = self.get_isud(vars_op, iter_idx)
			# the init_A, blnk_A is for the web_op
			yield [A, isud_lbl_str, self.init_A, self.blnk_A]

			# if (self.sud_inv.all_vars_gt_stp_val or var_not_chng_flg) and \
			# 		isud_lbl_str.endswith('Yes'):
			if self.sud_inv.all_vars_gt_stp_val and isud_lbl_str.endswith('Yes'):
				break


class vars_facs:
	"""
	This is the cls. that inits. vars, facs and obtains the vars.
	after perform iters. on them.
	"""
	def __init__(self, n_vars, n_facs, stp_val, var_poss_vals,
				 max_iters, facs_func_nams, vars_obs, var_fac_lnk, dbg_op):
		"""
		Init. the vars_facs.

		Input:
			- n_vars: How many vars. in vars_facs
			- n_facs: How many facs. in vars_facs
			- stp_val: Stp_val to stp the iters.
			- var_poss_vals: Poss. vals. that vars can take
			- max_iters: Max. iters. for vars_facs
			- facs_func_nams: Facs. func_nams in vars_facs
			- vars_obs: The obs. vars. in vars. of vars_facs.
			- var_fac_lnk: Lnks bw. vars. and facs.
			- dbg_op: Flg for dbg
		"""
		self.n_vars = n_vars
		self.n_facs = n_facs
		self.stp_val = stp_val
		self.var_poss_vals = var_poss_vals
		self.max_iters = max_iters
		self.facs_func_nams = facs_func_nams
		self.vars_obs = vars_obs
		self.var_fac_lnk = var_fac_lnk
		self.dbg_op_flg = dbg_op

		assert n_vars == len(vars_obs)
		assert n_vars == len(var_fac_lnk)
		assert n_facs == len(facs_func_nams)

		# NS abt this
		self.max_eps = 0.03
		#

		self.n_poss_vals = len(var_poss_vals)
		self.vars_l = [copy.deepcopy(var_dict) for _ in range(n_vars)]
		self.facs_l = [copy.deepcopy(fac_dict) for _ in range(n_facs)]
		self.all_vars_gt_stp_val = False
		self.unknown_msg = np.ones(self.n_poss_vals) / self.n_poss_vals
		self.init_vars_facs()

	def init_vars_facs(self,):
		"""
		We perform the inits. of the vars_facs here.
		"""
		# Get fac_var_lnk from var_fac_lnk
		fac_var_lnk = []
		for fac_idx in range(self.n_facs):
			vars_lnk = []
			for var_idx, var_fac in enumerate(self.var_fac_lnk):
				if fac_idx in var_fac:
					vars_lnk.append(var_idx)
			fac_var_lnk.append(vars_lnk)

		# init_vars
		for var_idx in range(self.n_vars):
			self.vars_l[var_idx]['facs_lnk'] = self.var_fac_lnk[var_idx]
			if self.vars_obs[var_idx] is not None:
				init_var_val = self.vars_obs[var_idx]
				self.vars_l[var_idx]['obs_flg'] = True
				self.vars_l[var_idx]['obs_val'] = init_var_val
			else:
				init_var_val = copy.copy(self.unknown_msg)

			for fac_idx in range(self.n_facs):
				if fac_idx in self.var_fac_lnk[var_idx]:
					self.vars_l[var_idx]['var_to_facs'].append(init_var_val)
				else:
					self.vars_l[var_idx]['var_to_facs'].append(None)
			assert len(self.vars_l[var_idx]['var_to_facs']) == self.n_facs

		# init_facs: May need to do more here
		for fac_idx in range(self.n_facs):
			self.facs_l[fac_idx]['vars_lnk'] = fac_var_lnk[fac_idx]
			for var_idx in range(self.n_vars):
				if var_idx in fac_var_lnk[fac_idx]:
					self.facs_l[fac_idx]['fac_to_vars'].append(
						np.zeros(self.n_poss_vals))
				else:
					self.facs_l[fac_idx]['fac_to_vars'].append(None)

			assert len(self.facs_l[fac_idx]['fac_to_vars']) == self.n_vars
			fac_eval_func_nam = self.facs_func_nams[fac_idx]
			self.facs_l[fac_idx]['fac_eval_func_nam'] = fac_eval_func_nam
			for func in reg_funcs:
				if func.__name__ == fac_eval_func_nam:
					self.facs_l[fac_idx]['fac_eval_func'] = func
					break

			assert self.facs_l[fac_idx]['fac_eval_func'] is not None

			if len(fac_var_lnk[fac_idx]):
				for o_var_idx in fac_var_lnk[fac_idx]:
					w_o_var_idxs = []
					for var_idx in fac_var_lnk[fac_idx]:
						if o_var_idx == var_idx:
							continue
						w_o_var_idxs.append(var_idx)
					if len(w_o_var_idxs):
						self.facs_l[fac_idx]['o_var'][o_var_idx] = {
							'w_o_var_idxs': w_o_var_idxs,
							'w_o_var_idxs_l_l': \
								gen_l_l_idxs(len(w_o_var_idxs),
											 self.n_poss_vals)
						}
					else:
						self.facs_l[fac_idx]['o_var'][o_var_idx] = {
							'w_o_var_idxs': [],
							'w_o_var_idxs_l_l': None
						}

	def vars_to_facs(self,):
		"""
		We perform the vars_to_facs here.
		"""
		# vars_to_facs
		for var_idx in range(self.n_vars):
			for o_fac_idx in self.vars_l[var_idx]['facs_lnk']:
				w_o_fac_idxs = []
				for fac_idx in self.vars_l[var_idx]['facs_lnk']:
					if fac_idx == o_fac_idx:
						continue
					w_o_fac_idxs.append(fac_idx)

				if self.vars_l[var_idx]['obs_flg']:
					op_msg = self.vars_l[var_idx]['obs_val']
				# elif self.vars_l[var_idx]['unsure_flg']:
				# 	op_msg = self.vars_l[var_idx]['unsure_val']
				else:
					if len(w_o_fac_idxs):
						op_msg = np.ones(self.n_poss_vals)
						for w_o_fac_idx in w_o_fac_idxs:
							w_o_fac_msg = \
								self.facs_l[w_o_fac_idx]['fac_to_vars'][var_idx]
							op_msg = np.multiply(w_o_fac_msg, op_msg)
						op_msg_sum = np.sum(op_msg)
						if op_msg_sum != 0:
							op_msg = op_msg / op_msg_sum
						else:
							op_msg = copy.copy(self.unknown_msg)
					else:
						op_msg = copy.copy(self.unknown_msg)
				self.vars_l[var_idx]['var_to_facs'][o_fac_idx] = op_msg
				if self.dbg_op_flg:
					print('var_idx: {0} to o_fac_idx: {1}: op_msg: {2}'.format(var_idx,
																			   o_fac_idx,
																			   list(op_msg)))
		if self.dbg_op_flg:
			print('Waiting...')

	def facs_to_vars(self,):
		"""
		We perform the facs_to_vars here.
		"""
		# facs_to_vars: tbd
		for fac_idx in range(self.n_facs):
			for o_var_idx in self.facs_l[fac_idx]['vars_lnk']:
				w_o_var_idxs = \
					self.facs_l[fac_idx]['o_var'][o_var_idx]['w_o_var_idxs']
				if len(w_o_var_idxs):
					l_l_w_o_var_idxs_vals = \
						self.facs_l[fac_idx]['o_var'][o_var_idx]\
							['w_o_var_idxs_l_l']
										# might be some prob here
					fac_to_var_msg = np.zeros(self.n_poss_vals)
					for o_var_val_idx in range(self.n_poss_vals):
						s_op_val = 0
						for l_w_o_var_idxs_vals in l_l_w_o_var_idxs_vals:
							op_val = 1
							for idx, w_o_var_idx in enumerate(w_o_var_idxs):
								op_val *= \
									self.vars_l[w_o_var_idx]['var_to_facs'][fac_idx]\
										[l_w_o_var_idxs_vals[idx]]
							# ################# This has to be better ##############
							# tbc_var_idxs = copy.copy(l_w_o_var_idxs_vals)
							# tbc_var_idxs.append(o_var_val_idx)
							# assert len(tbc_var_idxs) == \
							# len(facs_l[fac_idx]['vars_lnk'])
							# op_val *= chk_unq_elems(tbc_var_idxs)
							# # This has to be better
							# ######################################################
							# IAT: For the above
							var_idx_vals = []
							for var_idx in self.facs_l[fac_idx]['vars_lnk']:
								if var_idx == o_var_idx:
									var_idx_vals.append(
										self.var_poss_vals[o_var_val_idx])
								else:
									for w_o_var_idx, w_o_var_idx_val in \
											zip(w_o_var_idxs, l_w_o_var_idxs_vals):
										if w_o_var_idx == var_idx:
											var_idx_vals.append(
												self.var_poss_vals[w_o_var_idx_val])
											break
							op_val *= self.facs_l[fac_idx]['fac_eval_func'](var_idx_vals)
							######################################################
							s_op_val += op_val
						fac_to_var_msg[o_var_val_idx] = s_op_val
					fac_to_var_msg_sum = np.sum(fac_to_var_msg)
					if fac_to_var_msg_sum != 0:
						fac_to_var_msg = fac_to_var_msg / fac_to_var_msg_sum
					else:
						# NS here
						fac_to_var_msg = copy.copy(self.unknown_msg)
					self.facs_l[fac_idx]['fac_to_vars'][o_var_idx] = fac_to_var_msg
				else:
					# NS here
					self.facs_l[fac_idx]['fac_to_vars'][o_var_idx] = \
						copy.copy(self.unknown_msg)

	def prod_incom_msg(self, iter_idx):
		"""
		We perform the prod_incom_msg here.
		Input:
			- iter_idx: Ip. iter_idx of prod_incom_msg

		Output:
			- all_vars_gt_stp_val: Flg. to indicate if all vars. are
				gt. stp_val
			- vars_vals: vars_vals after prod_incom_msg
		"""
		# prod_incom_msg
		all_vars_gt_stp_val = True
		vars_vals = []
		# NS abt this
		# unsure_vars_idxs = []
		#
		if self.dbg_op_flg:
			print('iter_idx: ', iter_idx)
		for var_idx in range(self.n_vars):
			# NS abt this
			# self.vars_l[var_idx]['unsure_flg'] = False
			#
			if self.vars_l[var_idx]['obs_flg']:
				op_val = self.vars_l[var_idx]['obs_val']
			else:
				op_val = np.ones(self.n_poss_vals)
				for fac_idx in self.vars_l[var_idx]['facs_lnk']:
					fac_msg = self.facs_l[fac_idx]['fac_to_vars'][var_idx]
					op_val = np.multiply(fac_msg, op_val)

			if np.sum(op_val) > 0:
				op_val = op_val / np.sum(op_val)
				max_idx = 0
				max_val = op_val[max_idx]
				for m_idx in range(1, self.n_poss_vals):
					if op_val[m_idx] > max_val:
						max_idx = m_idx
						max_val = op_val[max_idx]
				# max_idxs = [max_idx]
				# for val_idx in range(self.n_poss_vals):
				# 	if val_idx == max_idx:
				# 		continue
				# 	elif max_val - op_val[val_idx] < self.max_eps:
				# 		max_idxs.append(val_idx)

				# if len(max_idxs) == 1:
				# 	vars_vals.append(self.var_poss_vals[max_idxs[0]])
				# else:
				# 	# NS abt this
				# 	var_dict = {'var_idx': var_idx, 'max_idxs': max_idxs}
				# 	unsure_vars_idxs.append(var_dict)
				# 	if len(unsure_vars_idxs) == 1:
				# 		vars_vals.append(self.var_poss_vals[max_idxs[0]])
				# 	else:
				# 		vars_vals.append(None)
				#
				vars_vals.append(self.var_poss_vals[max_idx])
				if np.max(op_val) <= self.stp_val:
					all_vars_gt_stp_val = False
			else:
				all_vars_gt_stp_val = False
				vars_vals.append(None)

			if self.dbg_op_flg:
				print('var_idx: {0}, var_val: {1}'.format(var_idx, vars_vals[var_idx]))
				print('op_val: {0}'.format(op_val))
		# if self.dbg_op_flg:
		# 	print('unsure_vars_idxs: ', unsure_vars_idxs)
		# NS abt this
		# if len(unsure_vars_idxs) > 1:
		# 	unsure_var_idx = unsure_vars_idxs[0]['var_idx']
		# 	unsure_msg = np.zeros(self.n_poss_vals)
		# 	unsure_msg[unsure_vars_idxs[0]['max_idxs'][0]] = 1
		# 	self.vars_l[unsure_var_idx]['unsure_flg'] = True
		# 	self.vars_l[unsure_var_idx]['unsure_val'] = \
		# 			unsure_msg
		# 	if self.dbg_op_flg:
		# 		print('unsure_var_idx: ', unsure_var_idx)
		# 		print('unsure_msg: ', list(unsure_msg))
		if self.dbg_op_flg:
			print('Waiting....')
		return all_vars_gt_stp_val, vars_vals

	def run_iter(self, iter_idx=None):
		"""
		We perform a run_iter here.
		Input:
			- iter_idx: Iter_idx

		Output:
			- vars_vals: var_vals after a run_iter
		"""
		self.facs_to_vars()

		self.all_vars_gt_stp_val, vars_vals = self.prod_incom_msg(iter_idx)

		self.vars_to_facs()
		return vars_vals

	def run_iters(self,):
		"""
		We perform run_iters here.
		"""
		for idx in range(self.max_iters):
			vars_vals = self.run_iter(idx)
			print(vars_vals)
			if self.all_vars_gt_stp_val:
				break
		return vars_vals
