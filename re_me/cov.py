from res_info import *
import math
# import m


def setup_page(sec):
    for x in sec:
        x_c = Experience(*x)
        x_c.insert()


class Resume:
    def __init__(self, c_info, work, project, vol, info, tech, p_info):
        # work
        self.main_space = 2
        self.loc_run = 0
        self.page_setup = {
            "margin": 1,
            "fontFamily": "Arial",
            "line spacing": 2
        }

        # head
        self.terms = detect_day(c_info[1])
        co_info = [c_info[0], self.terms[0], self.terms[1]]
        self.head = Header(**p_info)
        self.head.insert()

        # coop
        self.co_op = CoOp(*co_info)
        self.tech = Volunteering(tech, "Technical Skils")
        self.head.insert()

        # job info
        self.work_title = SectionTitle("Work experience")
        self.work_title.insert()
        setup_page(work)

        # project
        self.pro_title = SectionTitle("project Experience")
        self.work_title.insert()
        setup_page(project)

        # Voluntering
        self.vol = Volunteering(vol)
        self.head.insert()
        # add info
        self.info = Volunteering(info, "Additional info")
        self.head.insert()


class CoverLetter:
    def __init__(self, company, rep, title="Co-Op Student Opertunity", benifits=None):
        self.sig = ""
        if benifits:
            self.body_ex = benifits
        else:
            self.body_ex = ""
        self.text = f"""
        
{company}
{rep}


Re: {title}

I am hoping that you would consider employing me for the summer. Having just finished my {term[0]} academic term in 
Mechanical Engineering, I am an enthusiastic, motivated student with lots to offer. 

Engineering and all its branches intrigue me, but I love the mechanics of machines the most.  
Having grown up in rural Alberta, I have spent countless hours in the garage, working on my dirtbike, or the quad. 
Thus I have learnt some things about machinery. 

I have just completed the course on SolidWorks, and have done my own projects using it. Actually, 
I spend a lot of my free time in this program, designing new ideas and personal projects. I have built numerous software 
applications for aiding in my school and social life. My projects include both software and physical integration. 
I am trying different things with the 3D printer.

My computer skills are good, and I’m very comfortable working with Excel and Word. I love data, and spreadsheets, 
and flowsheets. I am also fluent in Python, with a basic knowledge in C++. I have had ample time working with 
Raspberry Pi/ Arduino - with multiple projects in each.

Finally, I am willing and excited to learn new techniques and get hands-on experience. Considering my project 
background, I think I will be an excellent addition to your team at Benchmark.

Yours sincerely,
{self.sig}

Arno Claassens
"""


def rev_cron(ls):
    def last_work(job):
        m, y = job.end.split(" ")
        mo = m_ls.index(m)/12
        return int(y) + mo

    m_ls = []
    ls_n = ls.sorted(key=last_work)
    return ls_n


def detect_day(d):  # todo calc een if pres, date
    # fall
    # tod = date.today()
    co_op_plan = ["A1", "A2", "E", "A3", "A4", "W1", "A5", "W2", "W3", "A6", "W4", "A7", "W5", "A8"]
    term_index = co_op_plan.index(d)
    st_month = ["September ", "January ", "May "]
    year = 2019 + math.ceil(term_index / 3)
    month = st_month[term_index % 3]
    a_d = month + str(year)
    terms = [sum(map(lambda x: y.startswith(x), co_op_plan)) for y in ["A", "W"]]
    return terms, a_d


# todo calc completed terms: job start---look at scedual
# c_info, work, project, vol, info, tech, p_info
Resume(coop_info, all_work, all_proj_ex, all_volunter, all_info, all_xp, personal_info)
