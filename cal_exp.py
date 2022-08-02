from ics import Calendar, Event
import ics


# import requests


class calendarEdit:
    def __init__(self, par, sch_data, file_pre='NewCal_'):
        self.par = par
        self.data = sch_data
        self.file_pre = file_pre
        self.cals = {}  # type per docter, per shift, unvesel, combo call wi
        self.shift_day = {}
        self.init_cals()
        # self.doc_save()

    def init_cals(self):
        print('\n----------------------\ninit Cals')
        for i in self.par.shifts + ['Call_Walkin', 'Universal']:
            self.cals[i] = Calendar()
            self.shift_day[i] = {}
        for j in self.par.cmd_ls['Active Doc']:
            self.cals[j] = Calendar()

    def doc_save(self):
        print('save_doc')

        def add_x(do, da, sh):
            if da not in self.shift_day[sh]:
                self.shift_day[sh][da] = Event(begin=da)
                self.shift_day[sh][da].name = shift + ": " + do
                self.shift_day[sh][da].description = f"Shift: {shift}\nDay: {da}\nDoctors:\n{do}"
            else:
                self.shift_day[sh][da].name += ', ' + do
            self.shift_day[sh][da].add_attendee(doc_p)
            self.shift_day[sh][da].description += f'\n{do}'

        for doc in self.par.cmd_ls['Active Doc']:
            doc_data = self.data[self.data['Doc'] == doc]
            doc_p = ics.Attendee(self.par.doc_data.loc[self.par.doc_data['Doc'] == doc, 'Email'], doc)
            for day_sh in doc_data.index:
                day = doc_data.loc[day_sh, 'Days']
                day = day.toString('yyyy-MM-dd')
                shift = doc_data.loc[day_sh, 'Shift']
                print(f'added doc: {doc}, day: {day}, shift: {shift}')
                add_x(doc, day, shift)
                add_x(doc, day, 'Universal')
                if shift in ['Call', 'Walkin']:
                    add_x(doc, day, 'Call_Walkin')

                e = Event(shift, day, attendees=[doc_p])
                print('all events created')
                self.cals[doc].events.add(e)
                print('added doc event')
        self.add_append()

    def add_append(self):
        print('add apend')
        for i, j in self.shift_day.items():
            cal = self.cals[i]
            for ij in j.values():
                cal.events.add(ij)
            print('added cal', i)

        file_ls = []
        for i, cal in self.cals.items():
            tit = self.file_pre + i + '.ics'
            with open(tit, 'w') as f:
                f.write(cal.serialize())
                print('saved cal: ', i)
                file_ls.append(tit)

        return file_ls
