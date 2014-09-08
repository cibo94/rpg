from pathlib import Path
from support import RpgTestCase
from rpg.command import Command
import subprocess


class PluginEngineTest(RpgTestCase):

    def test_command_concat(self):
        cmd = Command("cd %s" % self.test_project_dir)
        cmd.append_cmdlines("cmake ..")
        cmd.append_cmdlines(["make", "make test"])
        self.assertRaises(TypeError, cmd.append_cmdlines, 4)
        expected = "cd %s\ncmake ..\nmake\nmake test" % self.test_project_dir
        self.assertEqual(expected, str(cmd))

    def test_command_execute_from(self):
        cmd = Command("pwd\ncd c\npwd")
        output = cmd.execute_from(self.test_project_dir)
        path = self.test_project_dir.resolve()
        expected = "%s\n%s/c\n" % (path, path)
        self.assertEqual(expected, output)

        # doesn't add 'cd work_dir' during execute to command lines
        cur_dir = Path('.')
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            cmd.execute_from(cur_dir)
        expected = "Command '['/bin/sh', '-c', 'cd %s && pwd && cd c && pwd" \
            "']' returned non-zero exit status 1" % cur_dir.resolve()
        self.assertEqual(expected, str(ctx.exception))
