from pyhtml import (
    footer,
    html,
    head,
    body,
    meta,
    script,
    title,
    link,
    div,
    header,
    a,
    span,
    main,
    section,
    h1,
    p,
    img,
    h2,
)

from first_mate.server.landing.features_section import generate_features
from first_mate.server.landing.how_it_works_testimonials_section import (
    generate_how_it_works,
    generate_testimonials,
)
from first_mate.server.util import navbar


def generate_head() -> head:
    return head(
        meta(charset="UTF-8"),
        meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        title("FirstMate - Find Friends on Campus"),
        link(rel="stylesheet", href="/static/root.css"),
        link(rel="stylesheet", href="/static/landing.css"),
    )


def generate_cta(logged_in: bool) -> section:
    return section(
        div(
            div(
                h2("Ready to make new friends on campus?", _class="section-title"),
                p(
                    "Join thousands of students who are already connecting and building friendships.",
                    _class="section-description",
                ),
                _class="section-header",
            ),
            div(
                (
                    a(
                        "Sign Up Now",
                        href="/auth/register",
                        _class="btn btn-primary btn-lg",
                    )
                    if not logged_in
                    else a(
                        "Look for mates",
                        href="/mates",
                        _class="btn btn-primary btn-lg",
                    )
                ),
                _class="cta-buttons",
            ),
            _class="container",
        ),
        _class="cta-section",
    )


def generate_footer() -> footer:
    return footer(
        div(
            div(
                a(
                    div(
                        img(
                            src="/static/firstmate-logo.png",
                            alt="FirstMate logo",
                            _class="logo-icon-small",
                        ),
                        span("FirstMate", _class="logo-text-small"),
                        _class="footer-logo",
                    ),
                    href="/",
                    title="Return to Homepage",
                ),
                p(
                    "© ",
                    script("document.write(new Date().getFullYear())"),
                    "-FirstMate. All rights reserved.",
                    _class="copyright",
                ),
                div(
                    a("Terms", href="/terms", _class="footer-link"),
                    a("Privacy", href="/privacy", _class="footer-link"),
                    a("Contact", href="/contact", _class="footer-link"),
                    _class="footer-links",
                ),
                _class="footer-content",
            ),
            _class="container",
        ),
        _class="site-footer",
    )


def generate_header(logged_in: bool) -> header:
    return header(div(navbar(logged_in), _class="container"), _class="sticky-header")


def generate_hero(logged_in: bool) -> section:
    return section(
        div(
            div(
                h1("Find Friends on Campus", _class="hero-title"),
                p(
                    "Connect with students who share your interests, classes, and hangout spots.",
                    _class="hero-description",
                ),
                div(
                    (
                        a(
                            "Get Started",
                            href="/auth/register",
                            _class="btn btn-primary btn-lg",
                        )
                        if not logged_in
                        else a(
                            "Look for mates",
                            href="/mates",
                            _class="btn btn-primary btn-lg",
                        )
                    ),
                    a("Learn More", href="#features", _class="btn btn-outline btn-lg"),
                    _class="hero-buttons",
                ),
                _class="hero-content",
            ),
            div(
                img(
                    src="/static/friends.webp",
                    alt="Students connecting on campus",
                    _class="rounded-image",
                ),
                _class="hero-image",
            ),
            _class="hero-grid",
        ),
        _class="hero-section",
    )


def generate_body(logged_in: bool) -> body:
    return body(
        div(
            generate_header(logged_in),
            main(
                generate_hero(logged_in),
                generate_features(),
                generate_how_it_works(),
                generate_testimonials(),
                generate_cta(logged_in),
                _class="flex-1",
            ),
            generate_footer(),
            _class="flex min-h-screen flex-col",
        )
    )


def render_page(logged_in: bool) -> str:
    return str(
        html(
            generate_head(),
            generate_body(logged_in),
        )
    )


# if __name__ == "__main__":
#     print(render_page())
