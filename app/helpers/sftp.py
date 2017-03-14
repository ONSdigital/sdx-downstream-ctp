import io
import os
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
    def transfer(cmds, user, host, port, privKey=None, quiet=True, log=None):
        """
        Connects to an sftp server and plays a sequence of commands.

        """
        args = [
            "sftp", "-o", "ControlPersist=true", "-o", "ControlMaster=auto",
            "-o", "ControlPath=~/.ssh/ssh-%r@%h:%p", "-b", "-", "-P", str(port),
            "{user}@{host}".format(user=user, host=host)
        ]

        if privKey is not None:
            args[-2:-1] = [str(port), "-i", privKey]

        if quiet:
            kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        else:
            kwargs = {}

        if log is not None:
            log.debug(args)

        with subprocess.Popen(args, stdin=subprocess.PIPE, **kwargs) as proc:
            for cmd in cmds:
                proc.stdin.write(cmd.encode("utf-8"))
            proc.stdin.write("bye\n".encode("utf-8"))

        return proc.returncode

    def __init__(self, logger, host, user, privKey=None, port=22):
        self.logger = logger
        self.host = host
        self.user = user
        self.privKey = privKey
        self.port = port

    def deliver_binary(self, folder, filename, data):
        with tempfile.NamedTemporaryFile(dir="tmp") as locn:
            locn.write(data)
            locn.flush()
            cmds = [
                "cd {0}\n".format(folder),
                "put {0} {1}\n".format(locn.name, filename),
                "bye\n"
            ]
            rv = self.transfer(
                cmds, user=self.user, host=self.host, port=self.port,
                privKey=self.privKey, quiet=False, log=self.logger
            )
        if rv != 0:
            msg = "Failed to deliver file to FTP"
            self.logger.error(msg, host=self.host)
            raise UserWarning(msg)

    def unzip_and_deliver(self, folder, zip_contents):
        with tempfile.TemporaryDirectory(dir="tmp") as locn:
            with zipfile.ZipFile(io.BytesIO(zip_contents)) as payload:
                payload.extractall(locn)
                cmds = self.operations(locn)
                rv = self.transfer(
                    cmds, user=self.user, host=self.host, port=self.port,
                    privKey=self.privKey, quiet=False, log=self.logger
                )
        if rv != 0:
            msg = "Failed to deliver file to FTP"
            self.logger.error(msg, host=self.host)
            raise UserWarning(msg)


def run():
    """
    Reads a ZIP file or text file from stdin and copies the contents to the correct
    location on an SFTP server.

    Parameters are configured to match the test container in sdx-compose.

    """
    subprocess.check_output(
        ["ssh-keygen", "-f", os.path.expanduser("~/.ssh/known_hosts"), "-R", "[0.0.0.0]:2222"]
    )

    user = "testuser"
    host = "0.0.0.0"
    port = 2222
    root = "public"

    try:
        with zipfile.ZipFile(sys.stdin.buffer) as payload:
            with tempfile.TemporaryDirectory() as locn:
                payload.extractall(locn)
                cmds = SFTP.operations(locn, home="public", mkdirs=True)
                rv = SFTP.transfer(
                    cmds, user="testuser", host="0.0.0.0", port=2222, quiet=False
                )
    except zipfile.BadZipFile:
        # Assume a text file
        sys.stdin.buffer.seek(0)
        data = sys.stdin.buffer.read()
        with tempfile.NamedTemporaryFile() as locn:
            locn.write(data)
            locn.flush()
            cmds = [
                "cd {0}\n".format(root),
                "put {0} {1}\n".format(locn.name, "data.txt"),
                "bye\n"
            ]
            rv = SFTP.transfer(cmds, user, host, port, quiet=False)
    return rv


if __name__ == "__main__":
    rv = run()
    sys.exit(rv)
