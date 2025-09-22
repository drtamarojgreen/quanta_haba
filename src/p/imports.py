import re

# A comprehensive list of Python standard library modules
# A more robust solution would use a library like `isort` or `stdlibs`.
STD_LIB_MODULES = set([
    'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio',
    'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex',
    'bisect', 'builtins', 'bz2', 'calendar', 'cgi', 'cgitb', 'chunk',
    'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections', 'colorsys',
    'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars',
    'copy', 'copyreg', 'cProfile', 'csv', 'ctypes', 'curses', 'dataclasses',
    'datetime', 'dbm', 'decimal', 'difflib', 'dis', 'distutils', 'doctest',
    'email', 'encodings', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp',
    'fileinput', 'fnmatch', 'formatter', 'fractions', 'ftplib', 'functools',
    'gc', 'getopt', 'getpass', 'gettext', 'glob', 'grp', 'gzip', 'hashlib',
    'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp', 'importlib',
    'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3',
    'linecache', 'locale', 'logging', 'lzma', 'mailbox', 'mailcap', 'mmap',
    'modulefinder', 'multiprocessing', 'netrc', 'nntplib', 'numbers',
    'operator', 'optparse', 'os', 'pathlib', 'pdb', 'pickle', 'pickletools',
    'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'pprint',
    'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc',
    'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource',
    'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors',
    'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib',
    'sndhdr', 'socket', 'socketserver', 'sqlite3', 'ssl', 'stat',
    'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau',
    'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile',
    'telnetlib', 'tempfile', 'termios', 'textwrap', 'threading',
    'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace', 'traceback',
    'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing',
    'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings',
    'wave', 'weakref', 'webbrowser', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc',
    'zipapp', 'zipfile', 'zipimport', 'zlib'
])

def sort_imports_logic(full_text_content):
    """
    Takes the full string content of a Python file and returns the content
    with the import block sorted according to PEP 8.
    """
    if not full_text_content.strip():
        return ""

    lines = full_text_content.splitlines()

    # Find the end of the import block
    import_block_end_index = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not (stripped.startswith('import ') or stripped.startswith('from ') or stripped.startswith('#')):
            import_block_end_index = i
            break
    else: # If the whole file is imports
        import_block_end_index = len(lines)

    import_lines = lines[:import_block_end_index]
    other_code_lines = lines[import_block_end_index:]

    if not any(line.strip().startswith(('import ', 'from ')) for line in import_lines):
        return full_text_content

    std_lib, third_party, local = [], [], []

    for line in import_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue  # Preserve comments and blank lines within the block for now

        # Heuristic to get the base module
        if stripped.startswith('from '):
            module_name = stripped.split(' ')[1].split('.')[0]
        else: # import ...
            module_name = stripped.split(' ')[1].split(',')[0].split('.')[0]

        if stripped.startswith('from .'):
            local.append(line)
        elif module_name in STD_LIB_MODULES:
            std_lib.append(line)
        else:
            third_party.append(line)

    std_lib.sort()
    third_party.sort()
    local.sort()

    # Build the new import block
    sorted_block = []
    if std_lib:
        sorted_block.extend(std_lib)
    if third_party:
        if sorted_block: sorted_block.append('')
        sorted_block.extend(third_party)
    if local:
        if sorted_block: sorted_block.append('')
        sorted_block.extend(local)

    # Reconstruct the full text
    # Add a blank line after the import block if there's other code
    new_import_section = "\n".join(sorted_block)
    if other_code_lines:
        # Ensure there are two blank lines after imports, as per PEP 8
        new_import_section += "\n\n"

    new_full_text = new_import_section + "\n".join(other_code_lines)

    return new_full_text
