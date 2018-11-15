# MiniTemple

MiniTemple is a templating engine working with UTF-8 and inspired by EJS and PHP.
It is not designed specificaly for web technologies. Altought I wrote it to generate C++ files.

Just like PHP and EJS it print everything it meet until it enter a code block delimited by a specific pair of tags.
The default tags are `<%` and `%>` but can be easily replaced with any string of at least two characters.

As a simple pure python program it should be fully compatible with any interpreter for Python 3.
Also any valid Python 3 code can be embed into the templates.


## Printing text

There is three way to output text from a template :
- Outside of the tags everything is printed without modification with the exception 
of the escaped tags `\\<%` and `\\%>` wich are just tags on output
- Inside of the tags you can use the direct output : a '=' as the first non blank 
character of a line or of a code block will automatically output the evaluation 
of the rest of the line
- Inside of the tags you can explicitely use the python functions `echo` and `write`
to output text. `echo` output any number of argument separated by spaces and
append a newline at the end. Write just output one argument with no implicit
newline at the end.


## Including other templates

You can include other templates into the current one with the #include directive
followed by any number of file names separated by spaces. The file names are 
not strings, do not use " or '. If a filename is a relative path it it taken
relatively to the file being compiled. Absolute path are also valid. The 
included files are loaded in order of apparition and inherit from the level of 
indentation of the parent wich means that if you write :
```
<%
if some_condition:
    #include some_file
%>
```
The included file will only be executed if ```some_condition``` is true.

## The indentation

Indentation is a part of the syntax in python but here we mix at least two different languages that have different syntaxes.
Inside a pair of tags the indentation work just like standard python, you can code as usual. 
The specificity appear when you include a bit of text between two part of the same if block for example.
With MiniTemple you are not forced to match the indentations of two different code blocks if they are not in the same pair of tags.
That allow you to rather follow the indentation of the content for more readability.
The counterpart is that you may have to explicitaly decrease the indentation.
For example the following code :
```
<%
    if some_condition:
        do_something()
%>
Some content
<%
    do_something_else()
%>
```
is equivalent to :
```
<%
    if some_condition:
        do_something()
        echo("Some texte")
        do_something_else()
%>
```
but if you meant :
```
<%
    if some_condition:
        do_something()
    echo("Some texte")
    do_something_else()
%>
```
you could write :

```
<%
    if some_condition:
        do_something()
    #end
%>
Some texte
<%
    do_something_else()
%>
```

That can be important for loops for example. If you want to produce a HTML list, you would write :

```
<% for el in elements: %>
<li> <%= el %> </li>
<% #end %>
```

If you omit the final #end every thing else will also be in the for loop.

Note that if a line is a `else` or `elif` clause it is detected and the indentation is
decremented so you would __not__ write the following :

```
<% if a_bool: %>
OK
<% #end
   else: %>
Nope
```

but the more intuitive

```
<% if a_bool: %>
OK
<% else: %>
Nope
```

In case of nested __if__ blocks you have to use __#end__ to unindent the outer block:

```
<% if a_bool: %>
<%   if another_bool: %>
Here a_bool and another_bool are both true
<%   else: %>
Here a_bool is true but not another_bool
<% #end %>
<% else:
# the #end close the inner if block explicitely so the else is associated to the outer if %>
Here both conditions aree false 
```

## The scope

When you render a template you have to provide a scope wich will be used for execution of python code. 
If you use a variable that is neither declared in the file nor in the scope you will have an error.

## Installation

There is three ways to go :

1) The standard python way : use `pip install MiniTemple`
2) The git way : use `git clone https://github.com/Lattay/MiniTemple` in your project.
3) The brutal way : copy the *MiniTemple* directory to your project.

## Usage

You can use MiniTemple in a python program by importing the module :
```
from MiniTemple import compile_file

t = compile_file('some_file.mt')

print(t.render({'a_variable' : 5, 'another' : 'someValue'})
print(t.render({'a_variable' : 0, 'another' : 'someOtherValue'})
```

You can also use it in command line mode if you installed it with method 1 or 3.
The *-s* option allow you to provide a key/value pair for the scope. You can add as many as you want.
If possible the value will be converted to int or float or bool (if it match True or False). If no type match
the value will be passed as a string. The *-t* option allow you to provide the two tags you want to use.
```
$ python -m Minitemple.py a_template_file -t "<?" "?>" -s a_variable 5 -s another someValue
```
