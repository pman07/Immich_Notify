import threading
import subprocess


def start_flask():
    subprocess.run(["python", "flask_app.py"])


def start_scheduler():
    subprocess.run(["python", "notify.py"])


if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    scheduler_thread = threading.Thread(target=start_scheduler)

    flask_thread.start()
    scheduler_thread.start()

    flask_thread.join()
    scheduler_thread.join()

