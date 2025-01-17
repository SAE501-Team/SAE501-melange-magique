import time
from threading import Lock
from flask import abort
from app_generate_text import generate_cereal_info

class APILimiter:
    def __init__(self, max_per_minute=14, max_per_day=998):
        self.max_per_minute = max_per_minute
        self.max_per_day = max_per_day

        # Compteurs
        self.minute_count = 0
        self.day_count = 0

        # Horodatages
        self.minute_start_time = time.time()
        self.day_start_time = time.time()

        # Verrou pour les accès concurrents
        self.lock = Lock()

    def reset_counters(self):
        """
        Réinitialise les compteurs si les délais sont atteints.
        """
        current_time = time.time()

        # Réinitialiser le compteur minute
        if current_time - self.minute_start_time >= 60:
            self.minute_count = 0
            self.minute_start_time = current_time

        # Réinitialiser le compteur jour
        if current_time - self.day_start_time >= 86400:
            self.day_count = 0
            self.day_start_time = current_time

    def can_make_request(self):
        """
        Vérifie si une requête peut être effectuée.
        :return: True si possible, False sinon.
        """
        with self.lock:
            self.reset_counters()

            if self.minute_count < self.max_per_minute and self.day_count < self.max_per_day:
                return True
            return False

    def wait_if_needed(self):
        """
        Attend jusqu'à ce qu'une requête puisse être effectuée, ou lève une erreur si la limite journalière est atteinte.
        """
        while True:
            with self.lock:
                self.reset_counters()

                # Limite journalière atteinte
                if self.day_count >= self.max_per_day:
                    remaining_time = 86400 - (time.time() - self.day_start_time)
                    raise RuntimeError(
                        f"Limite journalière atteinte. Réessayez dans {int(remaining_time // 3600)} heures et {int((remaining_time % 3600) // 60)} minutes."
                    )

                # Limite par minute atteinte
                if self.minute_count >= self.max_per_minute:
                    time_to_wait = 60 - (time.time() - self.minute_start_time)
                    print(f"Limite par minute atteinte. Attente de {int(time_to_wait)} secondes.")
                    time.sleep(time_to_wait)
                    continue

                # Une requête peut être effectuée
                self.minute_count += 1
                self.day_count += 1
                break
