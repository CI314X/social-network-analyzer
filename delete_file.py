import os
import stat


def delete_file(filename: str) -> None:

    # change rights
    os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)

    try:
        os.remove(filename)
    except OSError:
        pass

