term = []
for t,o in enumerate(term):
    addExactlyone(o['val'] if o['val']['pre'] not in term[:t] or o['val']['co'] not in term[t])
    # condition for o#
"""stat widget
select list of days 
on day popup
save doc
select day week month, year, doc on doc_data off percentage, an on an off... 
per doc stats
add menubar"""