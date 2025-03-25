import pyhtml as p


def generate_how_it_works() -> p.section:
    return p.section(id="how-it-works", _class="how-it-works-section")(
        p.div(_class="container")(
            p.div(_class="section-header")(
                p.div(_class="badge")("How It Works"),
                p.h2(_class="section-title")("Start making friends in 3 simple steps"),
            ),
            p.div(_class="steps-grid")(
                p.div(_class="step-card")(
                    p.div(_class="step-number")("1"),
                    p.h3(_class="step-title")("Create your profile"),
                    p.p(_class="step-description")(
                        "Sign up with your zID and create your profile.",
                    ),
                ),
                p.div(_class="step-card")(
                    p.div(_class="step-number")("2"),
                    p.h3("Sync your schedule", _class="step-title"),
                    p.p(_class="step-description")(
                        "Upload your UNSW calendar, and we'll analyse it to find people on-campus at the same time as you.",
                    ),
                ),
                p.div(_class="step-card")(
                    p.div(_class="step-number")("3"),
                    p.h3(_class="step-title")("Find your new besties"),
                    p.p(_class="step-description")(
                        "Add friends, and share details with your mates!",
                    ),
                ),
            ),
        ),
    )


def generate_testimonials() -> p.section:
    return p.section(id="testimonials", _class="testimonials-section")(
        p.div(_class="container")(
            p.div(_class="section-header")(
                p.div(_class="badge")("Testimonials"),
                p.h2(_class="section-title")("Hear from students who found friends"),
            ),
            p.div(_class="testimonials-grid")(
                p.div(_class="testimonial-card")(
                    p.p(_class="testimonial-text")(
                        "I was new to campus and didn't know anyone. FirstMate helped me meet people on my own terms, allowing our friendships to grow naturally.",
                    ),
                    p.div(_class="testimonial-author")(
                        p.div(_class="author-avatar"),
                        p.div(_class="author-info")(
                            p.p(_class="author-name")("Alex J."),
                            p.p(_class="author-details")("1st Year, Computer Science"),
                        ),
                    ),
                ),
                p.div(_class="testimonial-card")(
                    p.p(_class="testimonial-text")(
                        "As a transfer student, it was hard to break into established friend groups. FirstMate helped me connect with other transfer students and now I have an amazing circle of friends.",
                    ),
                    p.div(_class="testimonial-author")(
                        p.div(_class="author-avatar"),
                        p.div(_class="author-info")(
                            p.p(_class="author-name")("Taylor M."),
                            p.p(_class="author-details")("2nd Year, Psychology"),
                        ),
                    ),
                ),
            ),
        ),
    )
