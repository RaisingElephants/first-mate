from pyhtml import div, h2, h3, p, section


def generate_how_it_works() -> section:
    return section(
        div(
            div(
                div("How It Works", Class="badge"),
                h2("Start making friends in 3 simple steps", Class="section-title"),
                Class="section-header"
            ),
            div(
                div(
                    div("1", Class="step-number"),
                    h3("Create Your Profile", Class="step-title"),
                    p("Sign up with your school email and create a profile with your interests and classes.", Class="step-description"),
                    Class="step-card"
                ),
                div(
                    div("2", Class="step-number"),
                    h3("Discover Students", Class="step-title"),
                    p("Browse profiles of students nearby who share your interests and schedule.", Class="step-description"),
                    Class="step-card"
                ),
                div(
                    div("3", Class="step-number"),
                    h3("Connect & Meet", Class="step-title"),
                    p("Send a message, plan a meetup, and make new friends on campus.", Class="step-description"),
                    Class="step-card"
                ),
                Class="steps-grid"
            ),
            Class="container"
        ),
        id="how-it-works", Class="how-it-works-section"
    )
    

def generate_testimonials() -> section:
    return section(
        div(
            div(
                div("Testimonials", Class="badge"),
                h2("Hear from students who found friends", Class="section-title"),
                Class="section-header"
            ),
            div(
                div(
                    p("I was new to campus and didn't know anyone. FirstMate helped me find students in my dorm who shared my love for gaming. Now we have weekly game nights!", Class="testimonial-text"),
                    div(
                        div(Class="author-avatar"),
                        div(
                            p("Alex J.", Class="author-name"),
                            p("Freshman, Computer Science", Class="author-details"),
                            Class="author-info"
                        ),
                        Class="testimonial-author"
                    ),
                    Class="testimonial-card"
                ),
                div(
                    p("As a transfer student, it was hard to break into established friend groups. This app helped me connect with other transfer students and now I have an amazing circle of friends.", Class="testimonial-text"),
                    div(
                        div(Class="author-avatar"),
                        div(
                            p("Taylor M.", Class="author-name"),
                            p("Junior, Psychology", Class="author-details"),
                            Class="author-info"
                        ),
                        Class="testimonial-author"
                    ),
                    Class="testimonial-card"
                ),
                Class="testimonials-grid"
            ),
            Class="container"
        ),
        id="testimonials", Class="testimonials-section"
    )

    