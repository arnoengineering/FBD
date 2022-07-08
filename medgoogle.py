import pandas as pd
from absl import app
from absl import flags
from PyQt5.QtCore import QDate

from google.protobuf import text_format
from ortools.sat.python import cp_model

FLAGS = flags.FLAGS
flags.DEFINE_string('output_proto', '',
                    'Output file to write the cp_model proto to.')
flags.DEFINE_string('params', 'max_time_in_seconds:10.0',
                    'Sat solver parameters.')

# todo hard vs soft away
# todo calendar add dates add aways, export exel

# todo how to add reqyests
        # todo walkin not as bad,
        # todo class?

class SchedualOptomizer:
    def __init__(self):
        self.app = app
        self.num_employees = 5
        self.num_weeks = 4
        # Penalty for exceeding the cover constraint per shift type.

        self.shifts = ['Off', 'Call', 'Walkin']
        self.num_days = self.num_weeks * 7

    def run_main(self):
        self.app.run(self.run_scedual)

    def run_scedual(self, _=None):
        self.solve_shift_scheduling(FLAGS.params, FLAGS.output_proto)

    def set_constraints(self, data,day,num_day=None):
        if num_day is not None:
            self.num_days = num_day
        self._set_constraints(data,day)

    def _set_constraints(self, data:pd.DataFrame,day:QDate):
        # todo combo contraints
        print('optom init')
        self.data = data
        self.day = day
        self.data.fillna(0)
        print('got data')
        self.doc = self.data.columns
        self.model = cp_model.CpModel()
        self.weekly_sum_constraints = []
        # Weekly sum constraints on shifts days:
        #     (shift, hard_min, soft_min, min_penalty,
        #             soft_max, hard_max, max_penalty)
        self.shift_constraints = [('Off', 0, 1, 2, 1, 2, 7),
                            ('Call', 0, 1, 2, 2, 3, 7)]
        self.penalized_transitions = [
            ('Call', 'Call', 7),  # no doubles.
            ('Walk_in', 'Walk_in', 7),
        ]
        # self.requests = [(3, 0, 5, -2),
        #     (4, 1, 10, -2),
        #     (2, 0, 4, 4)]  # todo chech here
        self.excess_cover_penalties = (2, 2,0)
        self.fixed_assignments = []

        self.weekly_cover_demands = []
        # daily demands for work shifts (call, walkin) for each day
        # of the week starting on Monday.

        for x in range(7):
            if x < 5:  # sat sun
                walk_in_need = 1
            else:
                walk_in_need = 0
            self.weekly_cover_demands.append((1, walk_in_need))
        print('fin data')

    def solve_shift_scheduling(self, params, output_proto):
        print('starting solve')
        work = {}

        print('Loading vars')
        for e in self.doc:
            for s in self.shifts:
                for d in range(self.num_days):
                    print(f'e: {e}, s: {s}, d: {d}')
                    work[e, s, d] = self.model.NewBoolVar(f'Doctor{e}_{s}_{d}')

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

        #     # Exactly one shift per day.
        # for e in range(num_employees):
        #     for w in range(num_weeks):
        #         for d in range(7):
        #             if d > 4:
        #                 n = 1
        #             else:
        #                 n = 0
        #             model.AddExactlyOne(work[e, s, d + w * 7] for s in range(num_shifts - n))  # leftoves in off
        # for d in range(num_days-2,num_days):
        #
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
            print('m:',m)
            for n in range(1,c):
                print('n:', n)
                da = self.data.iloc[m,n]
                print('data: ', da)
                try:
                    print('try')
                    shif, weight = da.split('_',1)
                    weight = int(weight)
                    print(f'shif, weight: ({shif}, {weight})')
                except TypeError or ValueError:
                    print('try failed')
                    continue
                doc =list(self.doc)[n]
                day = self.day.daysto(self.data.iloc[m,0])
                if day < 0:
                    continue
                print(f'doc,day : ({doc},{day})')
                if weight == 5:
                    print('weight = 5')
                    self.model.Add(work[doc, shif, day] == 1)
                elif weight !=0:
                    # since neg is pos
                    print('weight != 5')
                    obj_bool_vars.append(work[doc, shif, day])
                    obj_bool_coeffs.append(-weight)

        # Shift constraints
        for ct in self.shift_constraints:
            shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
            for e in self.doc:
                works = [work[e, shift, d] for d in range(self.num_days)]
                variables, coeffs = self.add_soft_sequence_constraint(
                    self.model, works, hard_min, soft_min, min_cost, soft_max, hard_max,
                    max_cost,f'shift_constraint(Doctor {e}, {shift})')
                obj_bool_vars.extend(variables)
                obj_bool_coeffs.extend(coeffs)

        # # Weekly sum constraints
        # for ct in self.weekly_sum_constraints:
        #     shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
        #     for e in range(self.num_employees):
        #         for w in range(self.num_weeks):
        #             works = [work[e, shift, d + w * 7] for d in range(7)]
        #             variables, coeffs = self.add_soft_sum_constraint(
        #                 self.model, works, hard_min, soft_min, min_cost, soft_max,
        #                 hard_max, max_cost, f'weekly_sum_constraint(Doctor {e}, {shift}, week {w})')
        #             obj_int_vars.extend(variables)
        #             obj_int_coeffs.extend(coeffs)

        # Penalized transitions
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

        # # Cover constraints
        # for s in range(1, self.num_shifts):
        #     for w in range(self.num_weeks):
        #         for d in range(7):
        #             works = [work[e, s, w * 7 + d] for e in range(self.num_employees)]
        #             # Ignore Off shift.
        #             min_demand = self.weekly_cover_demands[d][s - 1]
        #             worked = self.model.NewIntVar(min_demand, self.num_employees, '')
        #             self.model.Add(worked == sum(works))
        #             over_penalty = self.excess_cover_penalties[s - 1]
        #             if over_penalty > 0:
        #                 name = 'excess_demand(shift=%i, week=%i, day=%i)' % (s, w, d)
        #                 excess = self.model.NewIntVar(0, self.num_employees - min_demand, name)
        #                 self.model.Add(excess == worked - min_demand)
        #                 obj_int_vars.append(excess)
        #                 obj_int_coeffs.append(over_penalty)

        # Objective
        self.model.Minimize(
            sum(obj_bool_vars[i] * obj_bool_coeffs[i]
                for i in range(len(obj_bool_vars))) +
            sum(obj_int_vars[i] * obj_int_coeffs[i]
                for i in range(len(obj_int_vars))))

        if output_proto:
            print('Writing proto to %s' % output_proto)
            with open(output_proto, 'w') as text_file:
                text_file.write(str(self.model))

        # Solve the model.
        solver = cp_model.CpSolver()
        if params:
            text_format.Parse(params, solver.parameters)
        solution_printer = cp_model.ObjectiveSolutionPrinter()
        status = solver.Solve(self.model, solution_printer)

        # Print solution.
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print()
            header = '          '
            for w in range(self.num_weeks):
                header += 'M T W T F S S '
            print(header)
            for e in range(self.num_employees):
                schedule = ''
                for d in range(self.num_days):
                    for s in range(self.num_shifts):
                        if solver.BooleanValue(work[e, s, d]):
                            schedule += self.shifts[s] + ' '
                print('worker %i: %s' % (e, schedule))
                # todo add to dataframe
            print()
            print('Penalties:')
            for i, var in enumerate(obj_bool_vars):
                if solver.BooleanValue(var):
                    penalty = obj_bool_coeffs[i]
                    if penalty > 0:
                        print('  %s violated, penalty=%i' % (var.Name(), penalty))
                    else:
                        print('  %s fulfilled, gain=%i' % (var.Name(), -penalty))

            for i, var in enumerate(obj_int_vars):
                if solver.Value(var) > 0:
                    print('  %s violated by %i, linear penalty=%i' %
                          (var.Name(), solver.Value(var), obj_int_coeffs[i]))

        print()
        print('Statistics')
        print('  - status          : %s' % solver.StatusName(status))
        print('  - conflicts       : %i' % solver.NumConflicts())
        print('  - branches        : %i' % solver.NumBranches())
        print('  - wall time       : %f s' % solver.WallTime())

    def add_soft_sequence_constraint(self, works, hard_min, soft_min, min_cost,
                                     soft_max, hard_max, max_cost, prefix):
        """Sequence constraint on true variables with soft and hard bounds.
      This constraint look at every maximal contiguous sequence of variables
      assigned to true. If forbids sequence of length < hard_min or > hard_max.
      Then it creates penalty terms if the length is < soft_min or > soft_max.
      Args:
        model: the sequence constraint is built on this model.
        works: a list of Boolean variables.
        hard_min: any sequence of true variables must have a length of at least
          hard_min.
        soft_min: any sequence should have a length of at least soft_min, or a
          linear penalty on the delta will be added to the objective.
        min_cost: the coefficient of the linear penalty if the length is less than
          soft_min.
        soft_max: any sequence should have a length of at most soft_max, or a linear
          penalty on the delta will be added to the objective.
        hard_max: any sequence of true variables must have a length of at most
          hard_max.
        max_cost: the coefficient of the linear penalty if the length is more than
          soft_max.
        prefix: a base name for penalty literals.
      Returns:
        a tuple (variables_list, coefficient_list) containing the different
        penalties created by the sequence constraint.
      """
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
                    name = ': under_span(start=%i, length=%i)' % (start, length)
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
                    name = ': over_span(start=%i, length=%i)' % (start, length)
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
        """Sum constraint with soft and hard bounds.
      This constraint counts the variables assigned to true from works.
      If forbids sum < hard_min or > hard_max.
      Then it creates penalty terms if the sum is < soft_min or > soft_max.
      Args:
        works: a list of Boolean variables.
        hard_min: any sequence of true variables must have a sum of at least
          hard_min.
        soft_min: any sequence should have a sum of at least soft_min, or a linear
          penalty on the delta will be added to the objective.
        min_cost: the coefficient of the linear penalty if the sum is less than
          soft_min.
        soft_max: any sequence should have a sum of at most soft_max, or a linear
          penalty on the delta will be added to the objective.
        hard_max: any sequence of true variables must have a sum of at most
          hard_max.
        max_cost: the coefficient of the linear penalty if the sum is more than
          soft_max.
        prefix: a base name for penalty variables.
      Returns:
        a tuple (variables_list, coefficient_list) containing the different
        penalties created by the sequence constraint.
      """
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
    """Filters an isolated sub-sequence of variables assined to True.
  Extract the span of Boolean variables [start, start + length), negate them,
  and if there is variables to the left/right of this span, surround the span by
  them in non negated form.
  Args:
    works: a list of variables to extract the span from.
    start: the start to the span.
    length: the length of the span.
  Returns:
    a list of variables which conjunction will be false if the sub-list is
    assigned to True, and correctly bounded by variables assigned to False,
    or by the start or end of works.
  """
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
