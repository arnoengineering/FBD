def set_combo(self, in_ls, out_ls, n=0, m=0, func=None):
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

    def set_norm(self, in_ls, out_ls, n=0, m=0, func=None, ty='but'):

        if not func:
            func = self.run_cmd
        if ty == 'but':
            for wig_name in in_ls:
                k = QPushButton(wig_name)
                out_ls[wig_name] = k
                self.tool_layout.addWidget(k, m, n)
                k.clicked.connect(partial(func, wig_name))
                n += 1

                if n > 4:
                    m += 1
                    n = 0

        elif ty == 'da':
            for wig_name in in_ls:
                lab = QLabel(wig_name)
                print('i', wig_name)
                da = QDateEdit()
                da.setDate(QDate.currentDate())
                da.setCalendarPopup(True)
                da.dateChanged.connect(lambda x: func(x))
                # da.bud
                out_ls[wig_name] = da
                self.tool_layout.addWidget(lab, m, n)
                self.tool_layout.addWidget(da, m + 1, n)
                n += 1

                if n > 4:
                    m += 2
                    n = 0
        return n, m