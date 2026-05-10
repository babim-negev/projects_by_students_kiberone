"""
Второй авторский рисунок: силуэт города на закате + «звёздное» небо из точек.
Подходит для презентации темы черепашки как «рисунок с настроением».
Запуск: python 03_gorod_gorizont.py
"""
import random
import turtle


def main() -> None:
    screen = turtle.Screen()
    screen.setup(width=900, height=600)
    screen.bgcolor("#1e3a5f")
    screen.title("Город на горизонте — Kiber One")

    # Небо: градиент полосами (упрощённый закат)
    sky = turtle.Turtle()
    sky.hideturtle()
    sky.speed(0)
    palette = ["#ffd89b", "#ffb347", "#ff6b6b", "#c44569", "#303952"]
    y_base = -300
    band = 600 / len(palette)
    for i, color in enumerate(palette):
        sky.penup()
        sky.goto(-450, y_base + i * band)
        sky.color(color)
        sky.pendown()
        sky.begin_fill()
        for _ in range(2):
            sky.forward(900)
            sky.left(90)
            sky.forward(band + 2)
            sky.left(90)
        sky.end_fill()

    # Звёзды
    star = turtle.Turtle()
    star.hideturtle()
    star.speed(0)
    star.color("white")
    random.seed(42)
    for _ in range(80):
        star.penup()
        star.goto(random.randint(-400, 400), random.randint(50, 250))
        star.dot(random.randint(1, 3))

    # Силуэт зданий
    buildings = turtle.Turtle()
    buildings.hideturtle()
    buildings.speed(0)
    buildings.color("#0a0e17")
    buildings.penup()
    buildings.goto(-450, -80)
    buildings.pendown()
    buildings.begin_fill()
    x = -450
    while x < 450:
        w = random.randint(40, 90)
        h = random.randint(80, 220)
        buildings.goto(x, -80)
        buildings.goto(x, -80 + h)
        buildings.goto(x + w, -80 + h)
        buildings.goto(x + w, -80)
        x += w + random.randint(-5, 15)
    buildings.goto(450, -80)
    buildings.goto(-450, -80)
    buildings.end_fill()

    # Окошки-жёлтые точки
    win_t = turtle.Turtle()
    win_t.hideturtle()
    win_t.speed(0)
    random.seed(7)
    for _ in range(120):
        win_t.penup()
        win_t.goto(random.randint(-420, 420), random.randint(-60, 120))
        if abs(win_t.xcor()) > 440:
            continue
        win_t.color("#feca57")
        win_t.dot(2)

    screen.exitonclick()


if __name__ == "__main__":
    main()
