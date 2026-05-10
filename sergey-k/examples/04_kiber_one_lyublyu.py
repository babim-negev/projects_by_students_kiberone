"""
Надпись для школы: «Kiber one я люблю тебя!»
С анимацией: пульсирующее сердце, перелив текста и мерцающие блёстки.
Запуск из папки sergey-k: python examples/04_kiber_one_lyublyu.py
"""
import math
import random
import turtle


def hex_color(h: float) -> str:
    """Оттенок h ∈ [0, 1) → #rrggbb (как в примере про «световое кольцо»)."""
    h %= 1.0
    r = abs(h * 6 - 3) - 1
    g = 2 - abs(h * 6 - 2)
    b = 2 - abs(h * 6 - 4)
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def _bring_window_forward(screen: turtle.Screen) -> None:
    try:
        root = screen._root
        root.lift()
        root.after(50, lambda: root.focus_force())
    except Exception:
        pass


def main() -> None:
    screen = turtle.Screen()
    screen.bgcolor("#16213e")
    screen.title("Kiber One — я люблю тебя ♥")
    screen.setup(width=800, height=420)
    screen.tracer(0)

    artist = turtle.Turtle()
    artist.hideturtle()
    artist.speed(0)

    subtitle_font = ("Arial", 22, "normal")

    rnd = random.Random(202)
    sparks = [(rnd.randint(-340, 340), rnd.randint(-150, 150), rnd.random()) for _ in range(28)]

    frame = {"n": 0}

    def draw_heart(px: float, py: float, scale: float, width: float) -> None:
        artist.penup()
        artist.goto(px, py)
        artist.color("#e94560")
        artist.pensize(width)
        artist.pendown()
        artist.setheading(140)
        artist.circle(50 * scale, 200)
        artist.setheading(40)
        artist.circle(50 * scale, 200)

    def tick() -> None:
        artist.clear()
        n = frame["n"]
        t = n / 40.0
        pulse = 1.0 + 0.07 * math.sin(t * math.pi)

        pen_w = 2.5 + 1.8 * pulse
        draw_heart(-280, 40, pulse, pen_w)

        artist.penup()
        artist.goto(0, 24)
        glow = hex_color((n * 0.012) % 1.0)
        artist.color(glow)
        artist.write(
            "Kiber one",
            align="center",
            font=("Arial", 28, "bold"),
        )

        subtitle_hue = (n * 0.019) % 1.0
        artist.goto(0, -22)
        artist.color(hex_color(subtitle_hue))
        artist.write("я люблю тебя!", align="center", font=subtitle_font)

        artist.goto(0, -78)
        artist.color("#8b949e")
        artist.write("(анимация Turtle ♥)", align="center", font=("Arial", 14, "italic"))

        artist.pensize(1)
        for sx, sy, phase in sparks:
            br = (math.sin((n + phase * 360) * 0.09) + 1) / 2
            sz = 1 + br * 2.8
            artist.penup()
            artist.goto(sx, sy)
            artist.color(hex_color(((n * 0.02 + phase) % 1.0)))
            artist.dot(sz)

        screen.update()
        frame["n"] = n + 1
        screen.ontimer(tick, 48)

    _bring_window_forward(screen)
    tick()
    screen.exitonclick()


if __name__ == "__main__":
    main()
