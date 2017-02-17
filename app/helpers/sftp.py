import io
import os.path
import tempfile
import subprocess
import sys
import zipfile

__doc__ = """
Example:

python -m app.helpers.sftp < test-output.zip

"""


class SFTP:

    @staticmethod
    def operations(locn, home=".", mkdirs=False):
        """
        Returns a sequence of commands to copy a file tree from local 'locn' to server 'home'.

        """
        rv = []
        pos = len(locn.split(os.sep))
        for n, (root, dirs, files) in enumerate(os.walk(locn)):
            # We are walking the local file tree
            if n == 0:
                rv.append("cd {0}\n".format(home))
                crumbs = []
            else:
                crumbs = [".."] * (len(root.split(os.sep)) - pos)

            # Navigate to the same spot remotely
            dest = root.split(os.sep)[pos:]
            if dest:
                rv.append("cd {0}\n".format(os.path.join(*dest)))

            if mkdirs:
                rv.extend(["mkdir {0}\n".format(os.path.basename(i)) for i in dirs])

            # Place files
            rv.extend(["put {0}\n".format(os.path.join(root, i)) for i in files])

            # Go back to the home location
            if crumbs:
                rv.append("cd {0}\n".format(os.path.join(*crumbs)))

        return rv

    @staticmethod
    def transfer(cmds, user, host, port, root, quiet=True):
        """
        Connects to an sftp server and plays a sequence of commands.

        """
        kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL} if quiet else {}
        with subprocess.Popen(
            ["sftp", "-P", str(port), "{user}@{host}".format(user=user, host=host)],
            stdin=subprocess.PIPE, **kwargs
        ) as proc:
            for cmd in cmds:
                proc.stdin.write(cmd.encode("utf-8"))
            proc.stdin.write("bye\n".encode("utf-8"))
        return proc.returncode

    def __init__(self, logger, host, user, passwd, port=22):
        self.logger = logger
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port

    @staticmethod
    def unzip_and_deliver(self, folder, zip_contents):
        with tempfile.TemporaryDirectory(dir="tmp") as locn:
            with zipfile.ZipFile(io.BytesIO(zip_contents)) as payload:
                payload.extractall(locn)
                cmds = SFTP.operations(locn)
                rv = SFTP.transfer(
                    cmds, user=self.user, host=self.host, port=self.port, quiet=True
                )
        if rv == 0:
            self.logger.info("Successfully delivered zip to FTP", host=self.host)
            return True
        else:
            self.logger.error("Failed to deliver zip to FTP", host=self.host)
            return False


def run():
    """
    Reads a ZIP file from stdin and copies the contents to the correct locations on an
    SFTP server.

    Parameters are configured to match the test container in sdx-compose.

    """
    subprocess.check_output(
        ["ssh-keygen", "-f", os.path.expanduser("~/.ssh/known_hosts"), "-R", "[0.0.0.0]:2222"]
    )

    with tempfile.TemporaryDirectory() as locn:
        with zipfile.ZipFile(sys.stdin.buffer) as payload:
            payload.extractall(locn)
            cmds = SFTP.operations(locn, home="public", mkdirs=True)
            rv = SFTP.transfer(
                cmds, user="testuser", host="0.0.0.0", port=2222, root="public", quiet=False
            )
            return rv


if __name__ == "__main__":
    run()
