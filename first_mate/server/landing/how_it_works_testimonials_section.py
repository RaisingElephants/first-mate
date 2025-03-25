from pyhtml import div, h2, h3, p, section


def generate_how_it_works() -> section:
    return section(
        div(
            div(
                div("How It Works", _class="badge"),
                h2("Start making friends in 3 simple steps", _class="section-title"),
                _class="section-header"
            ),
            div(
                div(
                    div("1", _class="step-number"),
                    h3("Create Your Profile", _class="step-title"),
                    p("Sign up with your school email and create a profile with your interests and classes.", _class="step-description"),
                    _class="step-card"
                ),
                div(
                    div("2", _class="step-number"),
                    h3("Discover Students", _class="step-title"),
                    p("Browse profiles of students nearby who share your interests and schedule.", _class="step-description"),
                    _class="step-card"
                ),
                div(
                    div("3", _class="step-number"),
                    h3("Connect & Meet", _class="step-title"),
                    p("Send a message, plan a meetup, and make new friends on campus.", _class="step-description"),
                    _class="step-card"
                ),
                _class="steps-grid"
            ),
            _class="container"
        ),
        id="how-it-works", _class="how-it-works-section"
    )
    

def generate_testimonials() -> section:
    return section(
        div(
            div(
                div("Testimonials", _class="badge"),
                h2("Hear from students who found friends", _class="section-title"),
                _class="section-header"
            ),
            div(
                div(
                    p("I was new to campus and didn't know anyone. FirstMate helped me find students in my dorm who shared my love for gaming. Now we have weekly game nights!", _class="testimonial-text"),
                    div(
                        div(_class="author-avatar"),
                        div(
                            p("Alex J.", _class="author-name"),
                            p("Freshman, Computer Science", _class="author-details"),
                            _class="author-info"
                        ),
                        _class="testimonial-author"
                    ),
                    _class="testimonial-card"
                ),
                div(
                    p("As a transfer student, it was hard to break into established friend groups. This app helped me connect with other transfer students and now I have an amazing circle of friends.", _class="testimonial-text"),
                    div(
                        div(_class="author-avatar"),
                        div(
                            p("Taylor M.", _class="author-name"),
                            p("Junior, Psychology", _class="author-details"),
                            _class="author-info"
                        ),
                        _class="testimonial-author"
                    ),
                    _class="testimonial-card"
                ),
                _class="testimonials-grid"
            ),
            _class="container"
        ),
        id="testimonials", _class="testimonials-section"
    )

    