from sim import Gate, Circuit

def assert_eq(a,b,msg=None):
    if a!=b:
        raise AssertionError(msg or f"{a} != {b}")

# Test 1: simple AND
c = Circuit()
in1 = Gate('in1','INPUT')
in2 = Gate('in2','INPUT')
g_and = Gate('gand','AND')
out = Gate('out','OUTPUT')
c.add_gate(in1); c.add_gate(in2); c.add_gate(g_and); c.add_gate(out)
c.connect('in1','gand','a')
c.connect('in2','gand','b')
c.connect('gand','out','a')
c.set_input_value('in1', True)
c.set_input_value('in2', False)
vals = c.evaluate()
assert_eq(vals['gand'], False, 'AND gate wrong')
assert_eq(vals['out'], False, 'OUTPUT wrong')

c.set_input_value('in2', True)
vals = c.evaluate()
assert_eq(vals['gand'], True, 'AND gate wrong after change')
assert_eq(vals['out'], True, 'OUTPUT wrong after change')

# Test NOT
c = Circuit()
a = Gate('a','INPUT'); n = Gate('n','NOT'); o = Gate('o','OUTPUT')
c.add_gate(a); c.add_gate(n); c.add_gate(o)
c.connect('a','n','a'); c.connect('n','o','a')
c.set_input_value('a', True)
vals = c.evaluate()
assert_eq(vals['n'], False, 'NOT wrong')
assert_eq(vals['o'], False, 'OUTPUT of NOT wrong')

# Test XOR/NAND/NOR
c = Circuit()
i1 = Gate('i1','INPUT'); i2 = Gate('i2','INPUT')
x = Gate('x','XOR'); nand = Gate('nand','NAND'); nor = Gate('nor','NOR')
out1 = Gate('out1','OUTPUT'); out2 = Gate('out2','OUTPUT'); out3 = Gate('out3','OUTPUT')
for g in [i1,i2,x,nand,nor,out1,out2,out3]:
    c.add_gate(g)
c.connect('i1','x','a'); c.connect('i2','x','b'); c.connect('x','out1','a')
c.connect('i1','nand','a'); c.connect('i2','nand','b'); c.connect('nand','out2','a')
c.connect('i1','nor','a'); c.connect('i2','nor','b'); c.connect('nor','out3','a')
c.set_input_value('i1', True); c.set_input_value('i2', False)
vals = c.evaluate()
assert_eq(vals['x'], True, 'XOR wrong')
assert_eq(vals['nand'], True, 'NAND wrong')
assert_eq(vals['nor'], False, 'NOR wrong')

# Test cycle detection
c = Circuit()
a = Gate('a','INPUT'); b = Gate('b','AND')
c.add_gate(a); c.add_gate(b)
c.connect('a','b','a'); c.connect('b','a','a')  # creates cycle
c.set_input_value('a', True)
threw = False
try:
    c.evaluate()
except RuntimeError:
    threw = True
assert_eq(threw, True, 'Cycle not detected')

# Test isolated node behavior
c = Circuit()
iso = Gate('iso','AND')
c.add_gate(iso)
vals = c.evaluate()
assert_eq(vals['iso'], False, 'Isolated non-input should be False')
inp = Gate('in','INPUT')
c.add_gate(inp)
c.set_input_value('in', True)
vals = c.evaluate()
assert_eq(vals['in'], True, 'Isolated input should return its value')

print('ALL TESTS PASSED')
