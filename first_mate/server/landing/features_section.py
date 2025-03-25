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
                    "Make friends with your peers on-campus at UNSW"
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
                    p.h3(_class="feature-title")("Timetable-Based"),
                    p.p(_class="feature-description")(
                        "Find friends who are on-campus at the same time as you. Just upload your calendar and we'll handle the rest!",
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
                        "Explore profiles to find people in your niche",
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
                    p.h3(_class="feature-title")("Privacy Comes First"),
                    p.p(_class="feature-description")(
                        "Your calendar is only visible to you. Control what is shown to your matches, and everyone else.",
                    ),
                ),
            ),
        ),
    )
