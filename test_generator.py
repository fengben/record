
N = ['Hello', 'World', 18, 'Apple', 'None']
hh = (s.lower() for s in N if isinstance(s,str) ==True)
print (hh)
#for item in hh:
#    print item
print (next(hh))
#print hh.next()
#print hh.next()
#print hh.next()