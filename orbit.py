# todo add legend, aply changes, saveas

# append pref

# add info to say that cha3nges not permminent, will edit other

# remember self.shifts, current should always be wrie, todo add redo undo

class DocClinic(DocStatus):  # self.doc_dataframe_items
    def __init__(self, par, df, **kwargs):
        super().__init__(par, df, **kwargs)

    # def reset_table(self):
    #     dd = self.par.doc_data
    #     r, c = dd.shape
    #     self.reset_table_main(dd, r, c)

    # def reset_table_main(self, dd, r, c):
    #     self.setHorizontalHeaderLabels(list(dd.columns))
    #     self.setRowCount(c)
    #     self.setColumnCount(r)
    #     for n in range(r):
    #         for m in range(c):
    #             self.setItem(m,n, QTableWidgetItem(str(dd.iloc[n, m])))


class DayStatus(DocStatus):
    def __init__(self, par, df, **kwargs):
        self.day_range = 30
        self.piv_kwargs = {'index': ['Doc'], 'columns': ['Shift'], 'values': 'Days', 'aggfunc': 'count',
                           'fill_value': 0}
        super().__init__(par, df, **kwargs)

    def reset_table(self):
        # self.clear()
        # dd = self.par.current_schedule
        # self.df = pd.pivot_table(self.df_init, **self.piv_kwargs)
        # self.dataView.model()._data = self.df
        pass


  self.tool_tip = {'solve': 'Uses Linear optimization to solve current schedule using active preferences\n'
                                  'currently working to add compair',
                         self.wn: 'Show/Hide Weeknumbers on calendar',
                         'Today': 'focus on today in calendar',
                         'Save': 'save items to csv, jason, excel',
                         'Load': 'Load items from csv, jason, excel:  WIP',
                         'Add': 'all current dates are added with doc and pref to date',
                         'Apply': 'applies all active edits to current schedule',
                         'Cal Exp': 'export all to .ics format\ncal can be imported to excel',
                         'Email': 'email selected docs with selected cals: WIP',
                         'Date Start': 'if mode = range, from date start to end',
                         'Mode': 'Single: add multiple dates based on selections\n'
                                 'Range: add all dates in selected range',
                         'Start Week Format': 'start week on sunday or monday',
                         'Setting Mode': 'current shift to edit',
                         'Want Shift': 'if current pref is posive or negative',
                         'Pref': 'how much is opinion worth (1-4): or 5 = garentied',
                         'Date Format': 'how dates showup in all locations',
                         'Weekday Format': 'how days of week are formated',
                         'Editing': 'editing the curret scedule with direct effects or editing the prefernces to solve',
                         'bold': 'current widget text: Bold',
                         'underline': 'current widget text: Underline',
                         'italic': 'current widget text: Italic',
                         'Left': 'align text left',
                         'Center': 'align text center',
                         'Right': 'align text right',
                         'Top': 'align text vertically top',
                         'CenterV': 'align text vertically center',
                         'Bottom': 'align text vertically bottom'