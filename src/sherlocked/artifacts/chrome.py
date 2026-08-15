import sqlite3
import shutil
from pathlib import Path
from modules.browser.utils import chrome_time


class ChromeArtifacts:

    @staticmethod
    def extract(history_file):

        history_file = Path(history_file)

        if not history_file.exists():
            return []

        # Chrome locks the History DB while running.
        temp = history_file.parent / "History_Copy"

        shutil.copy2(history_file, temp)

        conn = sqlite3.connect(temp)

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                url,
                title,
                last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            LIMIT 100
        """)

        rows = cursor.fetchall()

        conn.close()

        temp.unlink()

        history = []

        for url, title, time in rows:

            history.append({
                "url": url,
                "title": title,
                "timestamp": chrome_time(time)
            })

        return history
    
        
    @staticmethod
    def extract_downloads(history_file):

        history_file = Path(history_file)

        if not history_file.exists():
            return []

        temp = history_file.parent / "History_Copy"

        shutil.copy2(history_file, temp)

        conn = sqlite3.connect(temp)

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                target_path,
                tab_url,
                total_bytes,
                start_time
            FROM downloads
            ORDER BY start_time DESC
            LIMIT 100
        """)

        rows = cursor.fetchall()

        conn.close()

        temp.unlink()

        downloads = []

        for path, url, size, time in rows:

            downloads.append({
                "path": path,
                "url": url,
                "size": size,
                "time": chrome_time(time)
            })

        return downloads