import pandas as pd

from PyQt5.QtCore import QDate

from ortools.sat.python import cp_model


# todo hard vs soft away
# todo calendar add dates add aways, export exel

# todo how to add reqyests
# todo walkin not as bad,
# todo class?
# todo menu
class SchedualOptomizer:
    def __init__(self):
        # self.app = app
        self.num_employees = 5
        self.num_days = 30
        # Penalty for exceeding the cover constraint per shift type.

        self.shifts = ['Off', 'Call', 'Walkin']
        # self.num_days = self.num_weeks * 7

    def set_constraints(self, data, day, num_day=None):
        if num_day is not None:
            self.num_days = num_day
        self._set_constraints(data, day)

    def _set_constraints(self, data: pd.DataFrame, day: QDate):
        # todo combo contraints
        print('optom init')
        self.data = data
        self.sch_data = pd.DataFrame(columns=['Days', 'Doc', 'Shift'])
        self.day = day
        self.data.fillna(0)
        print('got data')
        self.doc = list(self.data.columns)[1:]
        self.model = cp_model.CpModel()
        self.weekly_sum_constraints = []
        # Weekly sum constraints on shifts days:
        #     (shift, hard_min, soft_min, min_penalty,
        #             soft_max, hard_max, max_penalty)
        self.shift_constraints = [('Off', 0, 1, 2, 1, 2, 7),
                                  ('Call', 0, 1, 2, 2, 3, 7)]
        self.penalized_transitions = [
            ('Call', 'Call', 7),  # no doubles.
            ('Walkin', 'Walkin', 7),
        ]
        self.excess_cover_penalties = (0, 2, 2, 0)
        self.fixed_assignments = []

    def solve_shift_scheduling(self):
        week_ls = self.day.weekNumber()
        week_cnt = 0
        for d in range(1, self.num_days):
            day = self.day.addDays(d)
            week_n = day.weekNumber()
            if week_n != week_ls:
                week_ls = week_n
                week_cnt += 1

        print('starting solve')
        work = {}
        work_away = {}

        print('Loading vars')
        for e in self.doc:
            for s in self.shifts:
                for d in range(self.num_days):
                    print(f'e: {e}, s: {s}, d: {d}')
                    work[e, s, d] = self.model.NewBoolVar(f'Doctor{e}_{s}_{d}')
                    work_away[e, s, d] = 0

        # Linear terms of the objective in a minimization context.
        # todo only one call per day
        obj_int_vars = []
        obj_int_coeffs = []
        obj_bool_vars = []
        obj_bool_coeffs = []

        # Exactly one shift per day.
        print('loading shifts')
        for e in self.doc:
            for d in range(self.num_days):
                print(f'e: {e}, d: {d}')
                self.model.AddExactlyOne(work[e, s, d] for s in self.shifts)  # leftoves in off

        print('loading day per day')
        for s in self.shifts[1:]:
            for d in range(self.num_days):
                print(f's: {s}, d: {d}')
                self.model.AddAtMostOne(work[e, s, d] for e in self.doc)

        # Employee requests
        print('loading reqests')
        r, c = self.data.shape
        print(f'shape = {r},{c}')
        for m in range(r):
            print('m:', m)
            for n in range(1, c):
                print('n:', n)
                da = self.data.iloc[m, n]
                print('data: ', da)
                try:
                    print('try')
                    shif, weight = da.split('_', 1)
                    weight = int(weight)
                    print(f'shif, weight: ({shif}, {weight})')

                except TypeError or ValueError:
                    print('try failed')
                    continue
                doc = self.doc[n - 1]
                day = self.day.daysTo(self.data.iloc[m, 0])
                if shif == 'Away':
                    shif = 'Off'
                    work_away[doc, shif, day] = 1

                if day < 0:
                    continue
                print(f'doc,day : ({doc},{day})')
                if weight == 5:
                    print('weight = 5')
                    self.model.Add(work[doc, shif, day] == 1)
                elif weight != 0:
                    # since neg is pos
                    print('weight != 5')
                    obj_bool_vars.append(work[doc, shif, day])
                    obj_bool_coeffs.append(-weight)
                    print('---------Loaded Weight--------')
                    print(f'W: {weight}\n Doc: {doc}\n Shift: {shif}\nDay: {day}\n--------')

        # Shift constraints
        print('starting shift constraints')
        for ct in self.shift_constraints:
            shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
            for e in self.doc:
                print(f'doc: {e}, Shift: {shift}')
                works = [work[e, shift, d] for d in range(self.num_days)]
                variables, coeffs = self.add_soft_sequence_constraint(works, hard_min, soft_min, min_cost, soft_max,
                                                                      hard_max,
                                                                      max_cost,
                                                                      f'shift_constraint(Doctor {e}, {shift})')
                print('ran vars')
                obj_bool_vars.extend(variables)
                obj_bool_coeffs.extend(coeffs)
                print('extend')

        print('sum contstaints temp unavail')
        # Weekly sum constraints

        for ct in self.weekly_sum_constraints:
            shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
            for e in self.doc:
                for w in range(week_cnt):
                    works = [work[e, shift, d] for d in range(self.num_days)]
                    variables, coeffs = self.add_soft_sum_constraint(works, hard_min, soft_min, min_cost, soft_max,
                                                                     hard_max, max_cost,
                                                                     f'weekly_sum_constraint(Doctor {e}, {shift}, week {w})')
                    obj_int_vars.extend(variables)
                    obj_int_coeffs.extend(coeffs)

        # Penalized transitions
        print('doing Penalized transitions')
        for previous_shift, next_shift, cost in self.penalized_transitions:
            for e in self.doc:
                for d in range(self.num_days - 1):
                    transition = [
                        work[e, previous_shift, d].Not(), work[e, next_shift,
                                                               d + 1].Not()
                    ]
                    if cost == 0:
                        self.model.AddBoolOr(transition)
                    else:
                        trans_var = self.model.NewBoolVar(f'transition (Doctor {e}, day {d})')
                        transition.append(trans_var)
                        self.model.AddBoolOr(transition)
                        obj_bool_vars.append(trans_var)
                        obj_bool_coeffs.append(cost)

        print('cover contstaints temp unavail')
        # Cover constraints
        for d in range(self.num_days):  # todo start end
            day = self.day.addDays(d)
            if day.dayOfWeek() < 6:
                cov = 1
            else:
                cov = 0
            min_demand = (1, cov)
            for n, s in enumerate(self.shifts[1:]):

                works = [work[e, s, d] for e in self.doc]
                # Ignore Off shift.

                worked = self.model.NewIntVar(min_demand[n], 1, '')
                self.model.Add(worked == sum(works))
                over_penalty = self.excess_cover_penalties[n]
                if over_penalty > 0:
                    name = f'excess_demand(shift={s}, day={d})'
                    excess = self.model.NewIntVar(0, len(self.doc) - min_demand[n], name)
                    self.model.Add(excess == worked - min_demand[n])
                    obj_int_vars.append(excess)
                    obj_int_coeffs.append(over_penalty)

        print('object')
        # Objective
        self.model.Minimize(
            sum(obj_bool_vars[i] * obj_bool_coeffs[i]
                for i in range(len(obj_bool_vars))) +
            sum(obj_int_vars[i] * obj_int_coeffs[i]
                for i in range(len(obj_int_vars))))

        # Solve the model.
        solver = cp_model.CpSolver()

        solution_printer = cp_model.ObjectiveSolutionPrinter()
        status = solver.Solve(self.model, solution_printer)

        # Print solution.
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print()
            day_info = {'Days': [], 'Doc': [], 'Shift': []}
            for d in range(self.num_days):

                for s in self.shifts:
                    for e in self.doc:
                        if solver.BooleanValue(work[e, s, d]):
                            if work_away[e, s, d] == 1:
                                s = 'Away'
                            day_info['Days'].append(self.day.addDays(d))
                            day_info['Doc'].append(e)
                            day_info['Shift'].append(s)

                            print('Day: {}, Call: {}, Walkin: {}'.format(d,e,s))
            self.sch_data = pd.DataFrame(day_info)
            print('\nPenalties:')
            for i, var in enumerate(obj_bool_vars):
                if solver.BooleanValue(var):
                    penalty = obj_bool_coeffs[i]
                    if penalty > 0:
                        print(f'  {var.Name()} violated, penalty={penalty}')
                    else:
                        print(f'  {var.Name()} fulfilled, gain={-penalty}')

            for i, var in enumerate(obj_int_vars):
                if solver.Value(var) > 0:
                    print(f'  {var.Name()} violated by {solver.Value(var)}, linear penalty={obj_int_coeffs[i]}')

        print('\nStatistics')
        print('  - status          : ', solver.StatusName(status))
        print('  - conflicts       : ', solver.NumConflicts())
        print('  - branches        : ', solver.NumBranches())
        print(f'  - wall time       : {solver.WallTime()} s')

    def add_soft_sequence_constraint(self, works, hard_min, soft_min, min_cost,
                                     soft_max, hard_max, max_cost, prefix):

        cost_literals = []
        cost_coefficients = []
        # Forbid sequences that are too short.
        for length in range(1, hard_min):
            for start in range(len(works) - length + 1):
                self.model.AddBoolOr(negated_bounded_span(works, start, length))

        # Penalize sequences that are below the soft limit.
        if min_cost > 0:
            for length in range(hard_min, soft_min):
                for start in range(len(works) - length + 1):
                    span = negated_bounded_span(works, start, length)
                    name = f': under_span(start={start}, length={length})'
                    lit = self.model.NewBoolVar(prefix + name)
                    span.append(lit)
                    self.model.AddBoolOr(span)
                    cost_literals.append(lit)
                    # We filter exactly the sequence with a short length.
                    # The penalty is proportional to the delta with soft_min.
                    cost_coefficients.append(min_cost * (soft_min - length))

        # Penalize sequences that are above the soft limit.
        if max_cost > 0:
            for length in range(soft_max + 1, hard_max + 1):
                for start in range(len(works) - length + 1):
                    span = negated_bounded_span(works, start, length)
                    name = ': over_span(start={start}, length={length})'
                    lit = self.model.NewBoolVar(prefix + name)
                    span.append(lit)
                    self.model.AddBoolOr(span)
                    cost_literals.append(lit)
                    # Cost paid is max_cost * excess length.
                    cost_coefficients.append(max_cost * (length - soft_max))

        # Just forbid any sequence of true variables with length hard_max + 1
        for start in range(len(works) - hard_max):
            self.model.AddBoolOr(
                [works[i].Not() for i in range(start, start + hard_max + 1)])
        return cost_literals, cost_coefficients

    def add_soft_sum_constraint(self, works, soft_min, hard_min, min_cost,
                                soft_max, hard_max, max_cost, prefix):

        cost_variables = []
        cost_coefficients = []
        sum_var = self.model.NewIntVar(hard_min, hard_max, '')
        # This adds the hard constraints on the sum.
        self.model.Add(sum_var == sum(works))

        # Penalize sums below the soft_min target.
        if soft_min > hard_min and min_cost > 0:
            delta = self.model.NewIntVar(-len(works), len(works), '')
            self.model.Add(delta == soft_min - sum_var)
            # TODO(user): Compare efficiency with only excess >= soft_min - sum_var.
            excess = self.model.NewIntVar(0, 7, prefix + ': under_sum')
            self.model.AddMaxEquality(excess, [delta, 0])
            cost_variables.append(excess)
            cost_coefficients.append(min_cost)

        # Penalize sums above the soft_max target.
        if soft_max < hard_max and max_cost > 0:
            delta = self.model.NewIntVar(-7, 7, '')
            self.model.Add(delta == sum_var - soft_max)
            excess = self.model.NewIntVar(0, 7, prefix + ': over_sum')
            self.model.AddMaxEquality(excess, [delta, 0])
            cost_variables.append(excess)
            cost_coefficients.append(max_cost)

        return cost_variables, cost_coefficients


def negated_bounded_span(works, start, length):
    sequence = []
    # Left border (start of works, or works[start - 1])
    if start > 0:
        sequence.append(works[start - 1])
    for i in range(length):
        sequence.append(works[start + i].Not())
    # Right border (end of works or works[start + length])
    if start + length < len(works):
        sequence.append(works[start + length])
    return sequence
