import re
import rpm
import os
import sys
import tempfile
import io
import locale


def path_to_str(path):
    """ Converts path to string with escaping what needs to be escaped """
    return re.sub(r"(\s)", r"\\\1", str(path))


def str_to_pkgname(string):
    """ Converts any string to format suitable for package name """
    return re.sub(r'[^0-9a-zA-Z]', '', string)


# This has been copied from:
#   https://github.com/phracek/rebase-helper
# returns tuple of directory and its rpm macro
def rpm_dir_dump():
    """
    Captures output of %dump macro
    :return: Raw %dump macro output as a list of lines
    """
    # %dump macro prints results to stderr
    # we cannot use sys.stderr because it can be modified by pytest
    err = sys.__stderr__.fileno()
    defenc = locale.getpreferredencoding()
    defenc = 'utf-8' if defenc == 'ascii' else defenc
    with tempfile.TemporaryFile(mode='w+b') as tmp:
        with os.fdopen(os.dup(err), 'wb') as copied:
            try:
                sys.stderr.flush()
                os.dup2(tmp.fileno(), err)
                try:
                    rpm.expandMacro('%dump')
                finally:
                    sys.stderr.flush()
                    os.dup2(copied.fileno(), err)
            finally:
                tmp.flush()
                tmp.seek(0, io.SEEK_SET)
                for macro in re.finditer(
                        "-14\: (\w+).*(?=\n-14)", tmp.read().decode(defenc)):
                    expanded = rpm.expandMacro("%" + macro.group(1))
                    if os.path.isdir(expanded) and expanded != '':
                        yield (expanded, "%{" + macro.group(1) + "}")
