"""
Авторский рисунок: «световое кольцо» — пересекающиеся дуги с градиентом по номеру шага.
Идея нашей группы для проекта Kiber One.
Запуск: python 02_svetloe_kruzho.py
"""
import math
import turtle


def hex_color(h: float) -> str:
    """h от 0 до 1 → цвет в формате #rrggbb (HSV-подобный оттенок)."""
    h = h % 1.0
    r = abs(h * 6 - 3) - 1
    g = 2 - abs(h * 6 - 2)
    b = 2 - abs(h * 6 - 4)
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def main() -> None:
    screen = turtle.Screen()
    screen.bgcolor("#0d1117")
    screen.title("Световое кольцо — проект Kiber One")
    screen.setup(width=900, height=700)

    t = turtle.Turtle()
    t.speed(0)
    t.width(2)

    count = 36
    for k in range(count):
        hue = k / count
        t.color(hex_color(hue))
        t.penup()
        t.goto(0, 0)
        t.setheading(k * (360 / count))
        t.pendown()
        for _ in range(80):
            t.forward(3)
            t.left(2 + math.sin(math.radians(k * 5)) * 0.5)

    t.hideturtle()
    screen.exitonclick()


if __name__ == "__main__":
    main()
