import logging
import os


class ProjectBuilder:

    def build(self, project_source_dir, project_target_dir, build_command):
        """Builds project in given project_target_dir then cleans this
           directory, build_params is list of command strings.
           returns list of files that should be installed or error string"""
        logging.debug('build(%s, %s, %s)' % (repr(project_source_dir),
                      repr(project_target_dir), repr(build_command)))
        os.chdir(project_target_dir)
        build_command.execute_from(project_source_dir)
