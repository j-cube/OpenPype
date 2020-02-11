import pyblish.api
import os
import subprocess
import pype.lib
try:
    import os.errno as errno
except ImportError:
    import errno


class ValidateFfmpegInstallef(pyblish.api.Validator):
    """Validate availability of ffmpeg tool in PATH"""

    order = pyblish.api.ValidatorOrder
    label = 'Validate ffmpeg installation'
    families = ['review']
    optional = True

    def is_tool(self, name):
        try:
            devnull = open(os.devnull, "w")
            subprocess.Popen(
                [name], stdout=devnull, stderr=devnull
            ).communicate()
        except OSError as e:
            if e.errno == errno.ENOENT:
                return False
        return True

    def process(self, instance):
        self.log.info("ffmpeg path: `{}`".format(
            pype.lib.get_path_to_ffmpeg()
        ))
        if self.is_tool(
                os.path.join(
                    pype.lib.get_path_to_ffmpeg(), "ffmpeg")) is False:
            self.log.error("ffmpeg not found in PATH")
            raise RuntimeError('ffmpeg not installed.')
