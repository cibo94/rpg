from rpg.plugin import Plugin
from rpg.utils import rpm_dir_dump
import re


# priority list - here are all default directory paths
PRIO = [
    "%{_mandir}",
    "%{_defaultdocdir}",
    "%{_defaultlicencedir}",
    "%{_fileattrsdir}",
    "%{fmoddir}",
    "%{_includedir}",
    "%{_sbindir}",
    "%{_bindir}",
    "%{_libdir}",
    "%{_libexecdir}",
    "%{_infodir}",
    "%{_datadir}",
    "%{_sharedstatedir}",
    "%{_localstatedir}",
    "%{_sysconfdir}",
]


class FindFilePlugin(Plugin):

    # expand %dump, gets dir macros and sort them by len and by prio
    # (priority is for duplicates like _kde4_dir and _libdir where defaultly
    #  _libdir should be picked)
    MACROS = sorted(rpm_dir_dump(), reverse=True,
                    key=lambda x: len(x[0]) * 2 + (1 if x[1] in PRIO else 0))

    def installed(self, project_dir, spec, sack):
        """ Finds files that will be installed and
            replaces prefix with rpm macro """

        def relative(_file, _relative):
            return "/" + str(_file.relative_to(_relative))

        def append(_file, _spec):
            _spec.files.add((_file, None, None))

        def find_n_replace(_file, f, *r):
            match = re.search("^" + f[0], _file)
            if match:
                return f[1] + _file[len(match.group(0)):]
            else:
                return find_n_replace(_file, *r) if r else _file

        def ite(_spec, _proj_dir, f, *r):
            if f.is_file():
                append(find_n_replace(relative(f, _proj_dir), *self.MACROS),
                       _spec)
            if r:
                ite(_spec, _proj_dir, *r)

        def iterate(_spec, _proj_dir, _glob):
            if _glob:
                ite(_spec, _proj_dir, *_glob)

        iterate(spec, project_dir, list(project_dir.glob('**/*')))
