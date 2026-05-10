"""
Классический красивый пример Turtle: цветная спираль.
Такое часто показывают в уроках и туториалах — узор из линий с плавным сменом цвета.
Запуск: python 01_rainbow_spiral.py
"""
import turtle

COLORS = (
    "#e63946",
    "#f4a261",
    "#e9c46a",
    "#2a9d8f",
    "#264653",
    "#457b9d",
    "#a8dadc",
)


def _bring_tk_window_to_front(screen: turtle.Screen) -> None:
    """На macOS окно Turtle/Tk часто оказывается под IDE — поднимем на передний план."""
    try:
        root = screen._root  # тип: tkinter.Tk
        root.lift()
        root.after(50, lambda: root.focus_force())
    except Exception:
        pass


def main() -> None:
    screen = turtle.Screen()
    screen.bgcolor("#1a1a2e")
    screen.title("Радужная спираль (классика Turtle)")
    _bring_tk_window_to_front(screen)

    t = turtle.Turtle()
    t.speed(0)
    t.width(2)

    n = 200
    for i in range(n):
        t.color(COLORS[i % len(COLORS)])
        t.forward(i * 2)
        t.left(119)

    t.hideturtle()
    print("Спираль нарисована. Кликните по окну Turtle, чтобы выйти.", flush=True)
    screen.exitonclick()


if __name__ == "__main__":
    main()
