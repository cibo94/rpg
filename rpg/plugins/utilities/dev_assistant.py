from rpg.plugins.misc.files_to_pkgs import FilesToPkgsPlugin
from rpg.utils import path_to_str
from rpg.plugin import Plugin
from yaml import load
import logging


class DevAssistant(Plugin):

    found_dev_assist = False
    devassist_config = ".devassistant"

    def extracted(self, project_dir, spec, sack):
        if (project_dir / self.devassist_config).is_file():
            self.found_dev_assist = True
            with open(path_to_str(project_dir / self.devassist_config),
                      'r') as config:
                data_yml = load(config)
                try:
                    if sack:
                        query = sack.query()
                    for deps in data_yml["dependencies"]:
                        for key in deps.keys():
                            pkg = deps[key]
                            if sack:
                                for _dep_pkg in pkg:
                                    for _pkg in query.filter(name=_dep_pkg):
                                        for _f in _pkg.files:
                                            FilesToPkgsPlugin()\
                                                .TRANSLATED[_f] = _pkg.name
                            spec.Requires.update(pkg)
                            spec.BuildRequires.update(pkg)
                except IndexError:
                    logging.warn("No DevAssistant dependencies found!")
