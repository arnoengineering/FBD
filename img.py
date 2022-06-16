type hint
save seting
layered toolbar


save_load 3:00
toolbar 320
clean 4

python
amazon
save by current clicked item else dia
statusbar percent'status bar stats'
patient_time = {'claassens': 30, 'dehlen': 20, 'lategan': 15}
print
email
call_list = {}
current vs preset

walk_in_list = {}
# tool-list: add prefernce, add away, force update, split into two docs per day,
    # run solver, rerun solver, save solver, export solver,
    # doc time behind

#
# def doc_behind(doc):
#     td = patient_time[doc] * docs_list[doc]['patients behind']
#     si = '-' if td < 0 else '+'  # todo hour format
#     docs_list[doc]['ontime delta'] = f't {si} {abs(td)}'


#
# def walk_in(date):
#     if weekday(date) <=1: # sunday or monday
#         n_d = date-1
#     else:
#         n_d = date
#     walk_in_list[date-1] = call_list[n_d]


# minimize cost where call = 1-n, and call != people away

if not func:
    func = self.run_cmd
for wig_name, opt in in_ls.items():
    lab = QLabel(wig_name)
    print('i', wig_name)
    k = QComboBox()
    k.addItems(opt)
    k.setCurrentText(opt[0])
    k.currentTextChanged.connect(lambda x: func(wig_name, x))
    out_ls[wig_name] = k
    self.tool_layout.addWidget(lab, m, n)
    self.tool_layout.addWidget(k, m + 1, n)
    n += 1
    if n > 4:
        m += 2
        n = 0
return n, m