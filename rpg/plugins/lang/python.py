from rpg.plugin import Plugin
from rpg.command import Command
from rpg.utils import rpm_dir_dump


MACROS = rpm_dir_dump()


def macrofy(path):
    """ find prefix in path and replace it with macro """
    for m in MACROS:
        if path.startswith(m[0]):
            return m[1] + path[len(m[0]):]


class PythonPlugin(Plugin):

    def patched(self, project_dir, spec, sack):
        """ Find python dependencies """
        for item in list(project_dir.glob('**/*.py')):
            spec.required_files |= set(Command(
                self.python_interpret + " -c \"" +
                "from modulefinder import ModuleFinder; " +
                "mod = ModuleFinder(); " +
                "mod.run_script('" + str(item) + "'); " +
                "print('\\n'.join([mod.__file__ " +
                "for _, mod in mod.modules.items() "
                "if mod.__file__ and " +
                "mod.__file__.startswith('/usr/lib')]))\""
            ).execute().split('\n'))

    def installed(self, project_dir, spec, sack):
        """ Compiles all python files depending on which python version they
            are and appends them into files macro """
        for py_file in list(project_dir.glob('**/*.py')):
            Command([self.python_interpret + ' ' + sw +
                     ' -c \'import compileall; compileall.compile_file("' +
                     str(py_file) + '")\'' for sw in ["-O", ""]]).execute()
        spec.files.update([
            (macrofy("/" + str(_f.relative_to(project_dir))), None, None)
            for _f in project_dir.glob('**/*.py*')
        ])
