from pyhtml import div, section, p, img, h2, h3

def generate_features() -> section:
    return section(
        div(
            div(
                div("Features", _class="badge"),
                h2("Everything you need to build connections", _class="section-title"),
                p("Our platform makes it easy to find and connect with other students on your campus.", _class="section-description"),
                _class="section-header"
            ),
            div(
                div(
                    div(
                        img(src="/static/location-icon.svg", alt="Location pin icon", _class="feature-icon"),
                        _class="feature-icon-wrapper"
                        ),
                    h3("Location-Based", _class="feature-title"),
                    p("Find students nearby in your dorm, library, or favorite campus spots.", _class="feature-description"),
                    _class="feature-card"
                ),
                div(
                    div(
                        img(src="/static/people-icon.svg", alt="people together icon", _class="feature-icon"),
                        _class="feature-icon-wrapper"
                        ),
                    h3("Interest Matching", _class="feature-title"),
                    p("Connect with students who share your hobbies, major, or extracurricular interests.", _class="feature-description"),
                    _class="feature-card"
                ),
                div(
                    div(
                        img(src="/static/chat-bubble-icon.svg", alt="chat bubble icon", _class="feature-icon"),
                        _class="feature-icon-wrapper"
                        ),
                    h3("Safe Messaging", _class="feature-title"),
                    p("Chat securely with verified students from your campus.", _class="feature-description"),
                    _class="feature-card"
                ),
                _class="features-grid"
            ),
            _class="container"
        ),
        id="features", _class="features-section"
    )