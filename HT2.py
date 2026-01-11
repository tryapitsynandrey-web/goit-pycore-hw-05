import re
from typing import Callable, Generator


def generator_numbers(text: str) -> Generator[float, None, None]:
    
    # Генерує всі дійсні числа з тексту, які відокремлені пробілами з обох боків.
    # Регулярний вираз для пошуку дійсних чисел, які мають пробіл зліва і справа
    pattern = r"(?<=\s)\d+\.\d+(?=\s)"

    for match in re.finditer(pattern, text):
        # Перетворюємо знайдений рядок у число з плаваючою комою
        yield float(match.group())


def sum_profit(text: str, func: Callable[[str], Generator[float, None, None]]) -> float:
    
    # Обчислює загальну суму всіх чисел, отриманих з генератора func.
    # Підсумовуємо всі значення, які повертає генератор чисел
    return sum(func(text))

text = (
    "Загальний дохід працівника складається з декількох частин: "
    "1000.01 як основний дохід, доповнений додатковими надходженнями "
    "27.45 і 324.00 доларів."
)

total_income = sum_profit(text, generator_numbers)
print(f"Загальний дохід: {total_income}")