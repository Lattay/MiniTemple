import unittest
from MiniTemple import (
    Template,
    compile_text,
    render_text
)

class TestTemple(unittest.TestCase):

    def __init__(self, arg):
        unittest.TestCase.__init__(self, arg)
        self.maxDiff = None

    def test_render_text(self):

        # Simple copy
        self.assertEqual('Nothing special', render_text('Nothing special', {}))

        # Print variable
        self.assertEqual('A variable !',
                render_text('<%= a_var %>', {'a_var' : 'A variable !'}))

        # If statement
        tmpl = '''<% if a_bool: %>OK<% else: %>Nope'''
        self.assertEqual('OK', render_text(tmpl, {'a_bool' : True}))
        self.assertEqual('Nope', render_text(tmpl, {'a_bool' : False}))

        # Loop statement
        tmpl = '<% for i in range(n): echo(i) %>'
        self.assertEqual('0\n1\n2\n3\n', render_text(tmpl, {'n' : 4}))

    def test_compile_text(self):

        # reproductibility
        tmpl = '''
Here is a slightly more complex example.
Indeed it should show <%= some_var %> and also
<% for i in l :
    if i % 2:
        write(i)
    # some loops
    #end
#end
%>
The purpose is to test in one shot the mecanisms of <% write(name) %>
because what is important here is that <%= func_name %> reproduce
same results with same entries.
'''

        res_exp = '''
Here is a slightly more complex example.
Indeed it should show some variable and also
1357
The purpose is to test in one shot the mecanisms of MiniTemple
because what is important here is that compile_text reproduce
same results with same entries.
'''
        t = compile_text(tmpl)
        res1 = t.render(
            some_var='some variable',
            l=[1,2,3,4,5,6,7,8],
            name='MiniTemple',
            func_name='compile_text'
        )
        self.assertEqual(res_exp, res1)
        res2 = t.render(
            some_var='some variable',
            l=[1,2,3,4,5,6,7,8],
            name='MiniTemple',
            func_name='compile_text'
        )
        self.assertEqual(res1, res2)

    def test_error(self):
        tmpl = '''
<% if a_bool: %>
OK
<% #end %>
<% else: %>
Nope'''
        try:
            render_text(tmpl, {'a_bool' : False})
        except Exception as e:
            self.assertIsInstance(e, SyntaxError)
        else:
            self.fail("Here should have been an error.")


if __name__ == '__main__':
    unittest.main()
