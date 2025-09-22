from service.download_service import DownloadPytubefixService, DownloadYtDlpService


def get_download_service() -> DownloadPytubefixService:
    return DownloadPytubefixService()

def get_download_ytdlp_service() -> DownloadYtDlpService:
    return DownloadYtDlpService()