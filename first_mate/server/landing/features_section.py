from pyhtml import div, section, p, img, h2, h3

def generate_features() -> section:
    return section(
        div(
            div(
                div("Features", Class="badge"),
                h2("Everything you need to build connections", Class="section-title"),
                p("Our platform makes it easy to find and connect with other students on your campus.", Class="section-description"),
                Class="section-header"
            ),
            div(
                div(
                    div(
                        img(src="/static/location-icon.svg", alt="Location pin icon", Class="feature-icon"),
                        Class="feature-icon-wrapper"
                        ),
                    h3("Location-Based", Class="feature-title"),
                    p("Find students nearby in your dorm, library, or favorite campus spots.", Class="feature-description"),
                    Class="feature-card"
                ),
                div(
                    div(
                        img(src="/static/people-icon.svg", alt="people together icon", Class="feature-icon"),
                        Class="feature-icon-wrapper"
                        ),
                    h3("Interest Matching", Class="feature-title"),
                    p("Connect with students who share your hobbies, major, or extracurricular interests.", Class="feature-description"),
                    Class="feature-card"
                ),
                div(
                    div(
                        img(src="/static/chat-bubble-icon.svg", alt="chat bubble icon", Class="feature-icon"),
                        Class="feature-icon-wrapper"
                        ),
                    h3("Safe Messaging", Class="feature-title"),
                    p("Chat securely with verified students from your campus.", Class="feature-description"),
                    Class="feature-card"
                ),
                Class="features-grid"
            ),
            Class="container"
        ),
        id="features", Class="features-section"
    )