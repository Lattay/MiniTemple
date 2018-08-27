import re
import os
from sys import stderr

name = 'MiniTemple'


class Template:
    """
        Template is a class to load, parse, compile and render templates.
    """
    __cache = {}
    tags = ('<%', '%>')
    indent = '    '

    def __init__(self, **args):
        """
            Optional arguments :
            file : a filename in a string (default None)
            text : a text in a string to be compiled as a template (default None)
            caching : a boolean that enable loading already compiled template from cache (default True)
            tags : a tuple with the opening and closings tags (strings) (default ('<%', '%>'))
            debug : a bool enabling printing the python code to be interpreted to produce the rendered \
output (default False)
        """
        # get options
        self.file = args.get('file', None)
        self.text = args.get('text', None)
        self.caching = args.get('caching', True)
        self.tags = args.get('tags', self.tags)
        self.debug = args.get('debug', False)
        self.__basedir = None
        self.__src = None
        self.__output = []
        self.__hash = None
        self.__code = None

        # check validity of tags
        if len(self.tags[0]) < 2 or len(self.tags[1]) < 2:
            return ValueError('Both tags must be at least to characters long.')
        if '\\' in ''.join(self.tags):
            return ValueError('\\ is forbidden in tags.')

        if self.file:
            self.__basedir = os.path.dirname(self.file)

            self.__hash = self.file
            self.__mtime = os.path.getmtime(self.file)

            self.file = os.path.abspath(self.file)

        elif self.text:
            self.__basedir = os.getcwd()

            self.__hash = hash(self.text)
            self.__mtime = None

            self.__src = self.text

        else:
            raise AttributeError(
                    'Either text or file must be supplied to Template.')

    def __load_file(self):  # read file into self.__src
        """
            Read the file and put the content in self.__src
        """
        if self.file:
            with open(self.file) as f:
                self.__src = f.read()
        else:
            raise ValueError('Filename cannot be empty.')

    # compile or get from cache the template ready to render
    def compile(self):
        """
            If caching is enable look in cache for the compiled template.
            If caching is disable or the compiled template is not in cache,
            compile the template and put the result in cache.
        """

        # use cached code if it exists and is up to date
        if self.caching and self.__hash in self.__cache \
                and self.__cache[self.__hash][0] == self.__mtime:
            self.__code = self.__cache[self.__hash][1]
            if self.debug:
                print('Code loaded from cache', file=stderr)
        # compile
        else:
            if self.file:
                self.__load_file()
                filename = self.file
            else:
                filename = 'a string template'

            code = ''.join(self.__parse())
            self.__code = compile(code, filename, 'exec')
            self.__cache[self.__hash] = (self.__mtime, self.__code)
            if self.debug:
                print(code, file=stderr)

        return self

    def __parse(self, indent_init=0):
        """
            Parse the template file and convert it into plain Python code ready to be compiled.
        """
        rawcode = []
        stack = []
        otag, ctag = self.tags

        splitre = re.compile(r'{}(.*?){}'.format(
                re.escape(otag), re.escape(ctag)
            ), re.DOTALL
        )

        indent_lvl = indent_init

        self.__src = self.__src.replace('\\'+otag, '\\'.join(otag))\
            .replace('\\'+ctag, '\\'.join(ctag))

        for i, snip in enumerate(splitre.split(self.__src)):
            snip = snip.replace('\\'.join(otag), otag)\
                .replace('\\'.join(ctag), ctag)
            if i % 2:  # between tags
                if len(stack) > 0:
                    rawcode.append(indent_lvl * self.indent)
                    rawcode.append('write("""{}""")\n'.format(''.join(stack)))
                    stack.clear()

                codelines = snip.split('\n')

                offset = []
                for line in codelines:
                    sline = line.lstrip()
                    if sline.rstrip() == '':
                        pass
                    elif sline.startswith('#'):
                        if sline.rstrip() == '#end':
                            indent_lvl -= 1
                            if indent_lvl > indent_init:
                                offset.pop()
                        elif sline[:8] == '#include':
                            files = sline.rstrip().split(' ')
                            files.pop(0)
                            rawcode.append('\n')
                            for f in files:
                                if f != '':
                                    fpath = os.path.join(self.__basedir, f)
                                    t = Template(file=fpath)
                                    t.__load_file()
                                    rawcode.extend(t.__parse(indent_lvl))
                                    rawcode.append('\n')
                    elif sline.startswith('='):
                        rawcode.append(indent_lvl * self.indent)
                        rawcode.append('write(' + sline[1:] + ')\n')

                    elif (sline.startswith('else') and sline.rstrip().endswith(':'))\
                            or (sline.startswith('elif') and sline.rstrip().endswith(':')):
                        if indent_lvl < 1:
                            raise SyntaxError(
                                'Unexpected else or elif in snippet "' + sline + '".'
                            )
                        rawcode.append((indent_lvl-1)*self.indent)
                        rawcode.append(sline + '\n')

                    else:
                        if len(offset) == 0:
                            offset.append(len(line) - len(sline))
                        elif len(line) - len(sline) > offset[-1]:
                            offset.append(len(line) - len(sline))
                            indent_lvl += 1
                        elif len(line) - len(sline) < offset[-1]:
                            offset.pop()
                            indent_lvl -= 1

                        rawcode.append(indent_lvl*self.indent)
                        rawcode.append(sline + '\n')

                    if indent_lvl < indent_init:
                        raise IndentationError(
                            'Indentation too low in snippet "' + sline + '".'
                        )

                if sline.rstrip().endswith(':'):
                    indent_lvl += 1

            else:  # out of tags
                snip.replace('\\', r'\\')
                snip.replace('"', r'\"')
                stack.append(snip)

        if len(stack) > 0:
            rawcode.append(indent_lvl * self.indent)
            rawcode.append('write("""{}""")\n'.format(''.join(stack)))

        return rawcode

    def __echo(self, args):
        """
            Print several arguments separated with spaces and append a newline
        """

        self.__output.append(' '.join([str(a) for a in args]))
        self.__output.append('\n')

    def __write(self, string):
        """
            Just write the given string without end of line.
        """
        self.__output.append(str(string))

    def render(self, **scope):
        """
            Render the previously compiled template with all provided arguments as variables in scope.
        """
        if self.__code is None:
            self.compile()
        self.__output.clear()

        scope['echo'] = lambda *l: self.__echo(l)
        scope['write'] = lambda s: self.__write(s)

        exec(self.__code, scope)

        return ''.join(self.__output)


# compile file and return Template ready to be rendered
def compile_file(filename, **options):
    """
        Compile a template from the file and return the object ready to be rendered.

        Optional arguments :
        caching : a boolean that enable loading already compiled template from cache (default True)
        tags : a tuple with the opening and closings tags (strings) (default ('<%', '%>')
    """

    options['file'] = filename
    options['text'] = None
    return Template(**options).compile()


# compile file and return directly the result
def render_file(filename, scope, **options):
    """
        Compile a template from the file and render it with the provided scope dictionnary.

        Optional arguments :
        caching : a boolean that enable loading already compiled template from cache (default True)
        tags : a tuple with the opening and closings tags (strings) (default ('<%', '%>')
    """
    options['file'] = filename
    options['text'] = None
    return Template(**options).compile().render(**scope)


# compile text and return Template ready to be rendered
def compile_text(text, **options):
    """
        Compile a template from a string and return the object ready to be rendered.

        Optional arguments :
        caching : a boolean that enable loading already compiled template from cache (default True)
        tags : a tuple with the opening and closings tags (strings) (default ('<%', '%>')
    """
    options['file'] = None
    options['text'] = text
    return Template(**options).compile()


# compile text and return directly the result
def render_text(text, scope, **options):
    """
        Compile a template from a string and render it with the provided scope dictionnary.

        Optional arguments :
        caching : a boolean that enable loading already compiled template from cache (default True)
        tags : a tuple with the opening and closings tags (strings) (default ('<%', '%>')
    """
    options['file'] = None
    options['text'] = text
    return Template(**options).compile().render(**scope)
