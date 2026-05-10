"""
Надпись для школы: «Kiber one я люблю тебя!»
Можно поменять шрифт в tuple font, если на Mac отобразится не так.
Запуск: python 04_kiber_one_lyublyu.py
"""
import turtle


def main() -> None:
    screen = turtle.Screen()
    screen.bgcolor("#16213e")
    screen.title("Kiber One")
    screen.setup(width=800, height=400)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)

    # Декоративная рамка-сердечко из двух дуг (упрощённо)
    pen.penup()
    pen.goto(-280, 40)
    pen.color("#e94560")
    pen.pensize(3)
    pen.pendown()
    pen.setheading(140)
    pen.circle(50, 200)
    pen.setheading(40)
    pen.circle(50, 200)

    pen.penup()
    pen.goto(0, 20)
    pen.color("#e94560")

    title_font = ("Arial", 28, "bold")
    subtitle_font = ("Arial", 22, "normal")

    pen.write("Kiber one", align="center", font=title_font)

    pen.goto(0, -25)
    pen.color("#eaeaea")
    pen.write("я люблю тебя!", align="center", font=subtitle_font)

    pen.penup()
    pen.goto(0, -80)
    pen.color("#8b949e")
    pen.write("(черепашка Turtle ♥)", align="center", font=("Arial", 14, "italic"))

    screen.exitonclick()


if __name__ == "__main__":
    main()
