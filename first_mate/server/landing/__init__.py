import pyhtml as p

from first_mate.server.landing.bg_animation import generate_bg_animation
from first_mate.server.landing.features_section import generate_features
from first_mate.server.landing.how_it_works_testimonials_section import (
    generate_how_it_works,
    generate_testimonials,
)
from first_mate.server.util import generate_footer, generate_head, navbar


# def generate_head() -> p.head:
#     return p.head(
#         p.meta(charset="UTF-8"),
#         p.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
#         p.title("FirstMate - Find Friends on Campus"),
#         p.link(rel="stylesheet", href="/static/root.css"),
#         p.link(rel="stylesheet", href="/static/landing.css"),
#         p.link(rel="stylesheet", href="/static/animation.css"),
#     )


def generate_cta(logged_in: bool) -> p.section:
    return p.section(_class="cta-section")(
        p.div(_class="container")(
            p.div(_class="section-header")(
                p.h2(_class="section-title")("Ready to make new friends on campus?"),
                p.p(_class="section-description")(
                    "Join hundreds, if not, tens of students who are already connecting and building friendships.",
                ),
            ),
            p.div(_class="cta-buttons")(
                (
                    p.a(href="/auth/register", _class="btn btn-primary btn-lg")(
                        "Sign Up Now",
                    )
                    if not logged_in
                    else p.a(href="/mates", _class="btn btn-primary btn-lg")(
                        "Find your mates",
                    )
                ),
            ),
        ),
    )


def generate_hero(logged_in: bool) -> p.section:
    return p.section(_class="hero-section")(
        p.div(_class="hero-grid")(
            p.div(_class="hero-content")(
                p.h1(_class="hero-title")("Find your crowd"),
                p.p(_class="hero-description")(
                    "FirstMate helps you make friends that work with your schedule",
                ),
                p.div(_class="hero-buttons")(
                    (
                        p.a(
                            href="/auth/register",
                            _class="btn btn-primary btn-lg",
                        )("Get Started")
                        if not logged_in
                        else p.a(
                            href="/mates",
                            _class="btn btn-primary btn-lg",
                        )("Find your mates")
                    ),
                    p.a(
                        href="#features",
                        _class="btn btn-outline btn-lg",
                    )("Learn More"),
                ),
            ),
            p.div(
                p.img(
                    src="/static/friends.webp",
                    alt="Students connecting on campus",
                    _class="rounded-image",
                ),
                _class="hero-image",
            ),
        ),
    )


def generate_body(logged_in: bool) -> p.body:
    return p.body(
        p.canvas(id="animation-canvas", _class="background-animation"),
        generate_bg_animation(),
        p.div(_class="flex min-h-screen flex-col")(
            navbar(logged_in),
            p.main(_class="flex-1")(
                generate_hero(logged_in),
                generate_features(),
                generate_how_it_works(),
                generate_testimonials(),
                generate_cta(logged_in),
            ),
            generate_footer(),
        ),
    )


def render_page(logged_in: bool) -> str:
    return str(
        p.html(
            generate_head(
                "Find Friends on Campus",
                ["/static/landing.css", "/static/animation.css"],
            ),
            generate_body(logged_in),
        )
    )
