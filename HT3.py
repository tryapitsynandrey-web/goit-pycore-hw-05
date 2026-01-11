import sys
from typing import Dict, List, Optional


def parse_log_line(line: str) -> Optional[Dict[str, str]]:
    # Парсить один рядок логу у словник з датою, часом, рівнем та повідомленням
    line = line.strip()
    if not line:
        return None

    parts = line.split(maxsplit=3)
    if len(parts) < 4:
        # Якщо формат рядка некоректний — пропускаємо його
        return None

    date, time, level, message = parts
    return {
        "date": date,
        "time": time,
        "level": level.upper(),
        "message": message
    }


def load_logs(file_path: str) -> List[Dict[str, str]]:
    # Завантажує лог-файл і повертає список розпарсених записів
    logs: List[Dict[str, str]] = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                parsed = parse_log_line(line)
                if parsed is not None:
                    logs.append(parsed)
    except FileNotFoundError:
        print(f"Помилка: файл не знайдено: {file_path}")
        sys.exit(1)
    except PermissionError:
        print(f"Помилка: немає прав доступу до файлу: {file_path}")
        sys.exit(1)
    except OSError as exc:
        print(f"Помилка читання файлу: {exc}")
        sys.exit(1)

    return logs


def filter_logs_by_level(
    logs: List[Dict[str, str]],
    level: str
) -> List[Dict[str, str]]:
    # Фільтрує логи за заданим рівнем логування
    # Використано елемент функціонального програмування: filter + lambda
    level = level.upper()
    return list(filter(lambda item: item.get("level") == level, logs))


def count_logs_by_level(logs: List[Dict[str, str]]) -> Dict[str, int]:
    # Підраховує кількість записів для кожного рівня логування
    counts: Dict[str, int] = {}

    for item in logs:
        level = item.get("level", "UNKNOWN")
        counts[level] = counts.get(level, 0) + 1

    return counts


def display_log_counts(counts: Dict[str, int]) -> None:
    # Форматує та виводить таблицю з кількістю записів по рівнях логування
    print("Рівень логування | Кількість")
    print("-----------------|----------")

    preferred_order = ["INFO", "DEBUG", "ERROR", "WARNING"]
    printed = set()

    for level in preferred_order:
        if level in counts:
            print(f"{level:<15} | {counts[level]}")
            printed.add(level)

    for level in sorted(counts.keys()):
        if level not in printed:
            print(f"{level:<15} | {counts[level]}")


def display_log_details(logs: List[Dict[str, str]], level: str) -> None:
    # Виводить деталі логів для заданого рівня
    level = level.upper()
    print(f"\nДеталі логів для рівня '{level}':")

    if not logs:
        print("(Немає записів для цього рівня.)")
        return

    for item in logs:
        # Формат виводу: YYYY-MM-DD HH:MM:SS - message
        print(f"{item['date']} {item['time']} - {item['message']}")


def main() -> None:
    # Точка входу для запуску скрипта з командного рядка
    if len(sys.argv) < 2:
        print("Використання: python main.py /path/to/logfile.log [level]")
        sys.exit(1)

    file_path = sys.argv[1]
    level_arg = sys.argv[2] if len(sys.argv) >= 3 else None

    logs = load_logs(file_path)
    counts = count_logs_by_level(logs)
    display_log_counts(counts)

    if level_arg:
        filtered = filter_logs_by_level(logs, level_arg)
        display_log_details(filtered, level_arg)


if __name__ == "__main__":
    main()
