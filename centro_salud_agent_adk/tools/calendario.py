from typing import Dict, List
from datetime import date, timedelta, datetime
import random

CALENDAR: Dict[str, List[str]] = {}


def generate_calendar() -> dict:
    today = date.today()
    possible_times = [f"{h:02}:00" for h in range(8, 16)]

    for i in range(10):
        current = today + timedelta(days=i)
        if current.weekday() < 5:
            date_str = current.strftime("%Y-%m-%d")
            CALENDAR[date_str] = sorted(random.sample(possible_times, 6))

    return CALENDAR


generate_calendar()


def disponibilidad(start_date: str, end_date: str) -> str:

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        today_date = date.today()
        current_time_str = datetime.now().strftime("%H:%M")

        results = []
        delta = end - start
        for i in range(delta.days + 1):
            day = start + timedelta(days=i)
            date_str = day.strftime("%Y-%m-%d")
            slots = CALENDAR.get(date_str, [])

            if slots:
                if day == today_date:
                    slots = [slot for slot in slots if slot > current_time_str]
                    
                if slots:
                    results.append(f"{date_str}: {', '.join(slots)}")
                else:
                    results.append(f"{date_str}: No hay turnos disponibles para el resto del día")
            else:
                results.append(f"{date_str}: No disponible")

        return "\n".join(results)
    except ValueError:
        return "Formato de fecha inválido. Use YYYY-MM-DD."
