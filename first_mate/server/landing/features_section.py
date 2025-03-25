import pyhtml as p


def generate_features() -> p.section:
    return p.section(id="features", _class="features-section")(
        p.div(_class="container")(
            p.div(_class="section-header")(
                p.div(_class="badge")("Features"),
                p.h2(_class="section-title")(
                    "Everything you need to build connections"
                ),
                p.p(_class="section-description")(
                    "Our platform makes it easy to find and connect with other students on your campus."
                ),
            ),
            p.div(_class="features-grid")(
                p.div(_class="feature-card")(
                    p.div(_class="feature-icon-wrapper")(
                        p.img(
                            src="/static/location-icon.svg",
                            alt="Location pin icon",
                            _class="feature-icon",
                        ),
                    ),
                    p.h3(_class="feature-title")("Location-Based"),
                    p.p(_class="feature-description")(
                        "Find students nearby in your dorm, library, or favorite campus spots.",
                    ),
                ),
                p.div(_class="feature-card")(
                    p.div(_class="feature-icon-wrapper")(
                        p.img(
                            src="/static/people-icon.svg",
                            alt="people together icon",
                            _class="feature-icon",
                        ),
                    ),
                    p.h3(_class="feature-title")("Interest Matching"),
                    p.p(_class="feature-description")(
                        "Connect with students who share your hobbies, major, or extracurricular interests.",
                    ),
                ),
                p.div(_class="feature-card")(
                    p.div(_class="feature-icon-wrapper")(
                        p.img(
                            src="/static/chat-bubble-icon.svg",
                            alt="chat bubble icon",
                            _class="feature-icon",
                        ),
                    ),
                    p.h3(_class="feature-title")("Safe Messaging"),
                    p.p(_class="feature-description")(
                        "Chat securely with verified students from your campus.",
                    ),
                ),
            ),
        ),
    )
