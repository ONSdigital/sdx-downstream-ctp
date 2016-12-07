from app import settings
import io
from ftplib import FTP


def get_ftp_folder(survey):
    if 'heartbeat' in survey and survey['heartbeat'] is True:
        return settings.FTP_HEARTBEAT_FOLDER
    else:
        return settings.FTP_FOLDER


def connect_to_ftp():
    ftp = FTP(settings.FTP_HOST)
    ftp.login(user=settings.FTP_USER, passwd=settings.FTP_PASS)
    return ftp


def process_file_to_ftp(folder, filename):
    try:
        settings.logger.debug("Processing file", folder=folder, filename=filename)
        ftp = connect_to_ftp()
        f = open(filename)
        deliver_binary_to_ftp(ftp, folder, filename, f.read())
        f.close()
        ftp.quit()
        return True

    except (RuntimeError) as e:
        settings.logger.error("Exception processing file", exception=e)
        return False


def deliver_binary_to_ftp(ftp, folder, filename, data):
    stream = io.BytesIO(data)
    ftp.cwd(folder)
    ftp.storbinary('STOR ' + filename, stream)
