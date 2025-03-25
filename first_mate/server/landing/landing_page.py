from pyhtml import footer, form, html, head, body, meta, script, title, link, div, header, nav, a, span, main, section, h1, p, img, h2, h3, input

from first_mate.server.landing.features_section import generate_features
from first_mate.server.landing.how_it_works_testimonials_section import generate_how_it_works, generate_testimonials
from first_mate.server.util import navbar

def generate_head() -> head:
    return head(
        meta(charset="UTF-8"),
        meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        title("FirstMate - Find Friends on Campus"),
        link(rel="stylesheet", href="/static/styles.css")
    )
    
def generate_cta() -> section:
    return section(
        div(
            div(
                h2("Ready to make new friends on campus?", Class="section-title"),
                p("Join thousands of students who are already connecting and building friendships.", Class="section-description"),
                Class="section-header"
            ),
            div(
                a("Sign Up Now", href="/auth/register", Class="btn btn-primary btn-lg"),
                Class="cta-buttons"
            ),
            Class="container"
        ),
        Class="cta-section"
)

def generate_footer() -> footer:
    return footer(
        div(
            div(
                a(div(
                    img(src="/static/firstmate-logo.png", alt="FirstMate logo", Class="logo-icon-small"),
                    span("FirstMate", Class="logo-text-small"),
                    Class="footer-logo"
                ),
                href="/",
                title="Return to Homepage"),
                p(
                    "© ",
                    script("document.write(new Date().getFullYear())"),
                    "-FirstMate. All rights reserved.",
                    Class="copyright"
                ),
                div(
                    a("Terms", href="/terms", Class="footer-link"),
                    a("Privacy", href="/privacy", Class="footer-link"),
                    a("Contact", href="/contact", Class="footer-link"),
                    Class="footer-links"
                ),
                Class="footer-content"
            ),
            Class="container"
        ),
        Class="site-footer"
    )


def generate_header(logged_in: bool) -> header:
    return header(
        div(
            navbar(logged_in),
            Class="container"
        ),
        Class="sticky-header"
    )

def generate_hero() -> section:
    return section(
        div(
            div(
                h1("Find Friends on Campus", Class="hero-title"),
                p("Connect with students who share your interests, classes, and hangout spots.", Class="hero-description"),
                div(
                    a("Get Started", href="/auth/register", Class="btn btn-primary btn-lg"),
                    a("Learn More", href="#how-it-works", Class="btn btn-outline btn-lg"),
                    Class="hero-buttons"
                ),
                Class="hero-content"
            ),
            div(
                img(src="/static/friends.webp", alt="Students connecting on campus", Class="rounded-image"),
                Class="hero-image"
            ),
            Class="hero-grid"
        ),
        Class="hero-section"
    )

def generate_body(logged_in: bool) -> body:
    return body(
        div(
            generate_header(logged_in),
            main(
                generate_hero(),
                generate_features(),
                generate_how_it_works(),
                generate_testimonials(),
                generate_cta(),
                Class="flex-1"
            ),
            generate_footer(),
            Class="flex min-h-screen flex-col"
        )
    )
    

    
def render_page(logged_in: bool) -> str:
    return str(html(
        generate_head(),
        generate_body(logged_in),
    ))

# if __name__ == "__main__":
#     print(render_page())
