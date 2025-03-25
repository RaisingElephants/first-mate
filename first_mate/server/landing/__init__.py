from datetime import datetime
import pyhtml as p

from first_mate.server.landing.features_section import generate_features
from first_mate.server.landing.how_it_works_testimonials_section import (
    generate_how_it_works,
    generate_testimonials,
)
from first_mate.server.util import navbar


def generate_head() -> p.head:
    return p.head(
        p.meta(charset="UTF-8"),
        p.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        p.title("FirstMate - Find Friends on Campus"),
        p.link(rel="stylesheet", href="/static/root.css"),
        p.link(rel="stylesheet", href="/static/landing.css"),
    )


def generate_cta(logged_in: bool) -> p.section:
    return p.section(_class="cta-section")(
        p.div(_class="container")(
            p.div(_class="section-header")(
                p.h2(_class="section-title")("Ready to make new friends on campus?"),
                p.p(_class="section-description")(
                    "Join thousands of students who are already connecting and building friendships.",
                ),
            ),
            p.div(_class="cta-buttons")(
                (
                    p.a(href="/auth/register", _class="btn btn-primary btn-lg")(
                        "Sign Up Now",
                    )
                    if not logged_in
                    else p.a(href="/mates", _class="btn btn-primary btn-lg")(
                        "Look for mates",
                    )
                ),
            ),
        ),
    )


def generate_footer() -> p.footer:
    return p.footer(_class="site-footer")(
        p.div(_class="container")(
            p.div(_class="footer-content")(
                p.a(href="/", title="Return to homepage")(
                    p.div(_class="footer-logo")(
                        p.img(
                            src="/static/firstmate-logo.png",
                            alt="FirstMate logo",
                            _class="logo-icon-small",
                        ),
                        p.span(_class="logo-text-small")("FirstMate"),
                    ),
                ),
                p.p(_class="copyright")(
                    f"© {datetime.now().year} FirstMate. All rights reserved.",
                ),
                p.div(_class="footer-links")(
                    p.a(href="/terms", _class="footer-link")("Terms"),
                    p.a(href="/privacy", _class="footer-link")("Privacy"),
                    p.a(href="/contact", _class="footer-link")("Contact"),
                ),
            ),
        ),
    )


def generate_hero(logged_in: bool) -> p.section:
    return p.section(_class="hero-section")(
        p.div(_class="hero-grid")(
            p.div(_class="hero-content")(
                p.h1(_class="hero-title")("Find Friends on Campus"),
                p.p(_class="hero-description")(
                    "Connect with students who share your interests, classes, and hangout spots.",
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
                        )("Look for mates")
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
        )
    )


def render_page(logged_in: bool) -> str:
    return str(
        p.html(
            generate_head(),
            generate_body(logged_in),
        )
    )


# if __name__ == "__main__":
#     print(render_page())
