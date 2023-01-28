"""Handle pulling files from local paths"""

import os
import sys


def get_path(local_path: str) -> str:
    """Get real path from local path"""
    is_frozen = getattr(sys, 'frozen', False)
    file_path = sys.executable if is_frozen else __file__
    path_addition = '.' if is_frozen else "../.."
    return os.path.join(
        os.path.abspath(
            os.path.join(
                os.path.dirname(file_path),
                path_addition
            )
        ),
        local_path
    )
