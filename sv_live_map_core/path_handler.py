"""Handle pulling files from local paths"""

import os
import sys

def get_path(local_path: str) -> str:
    """Get real path from local path"""
    file_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    return os.path.join(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(file_path),
                    '..'
                )
            ),
            local_path
        )
