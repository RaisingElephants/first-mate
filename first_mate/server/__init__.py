"""
server.py

Entrypoint to the first-mate server with enhanced navbar.
"""

import os
import pyhtml as p
from flask import Flask, send_file

from .session import is_user_logged_in
from .util import navbar
from .auth import auth
from .calendar import calendar
from .debug import debug
from .mates import mates


app = Flask(__name__)


# FIXME: Load from .env
app.secret_key = "top secret key"

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(calendar, url_prefix="/calendar")
app.register_blueprint(debug, url_prefix="/debug")
app.register_blueprint(mates, url_prefix="/mates")


@app.get("/")
def root():
    logged_in = is_user_logged_in()

    # Define navbar links based on login status
    navbar_links = []
    if logged_in:
        navbar_links = [
            {"title": "My Calendar", "url": "/calendar", "icon": "fa-calendar-alt"},
            {"title": "Find Mates", "url": "/mates", "icon": "fa-users"},
            {"title": "Log Out", "url": "/auth/logout", "icon": "fa-sign-out-alt"}
        ]
    else:
        navbar_links = [
            {"title": "Register", "url": "/auth/register", "icon": "fa-user-plus"},
            {"title": "Login", "url": "/auth/login", "icon": "fa-sign-in-alt"}
        ]
    
    # Custom navbar implementation
    def enhanced_navbar():
        links = []
        for link in navbar_links:
            links.append(
                p.a(href=link["url"], class_="nav-link")(
                    p.i(class_=f"fas {link['icon']}"),
                    p.span(link["title"])
                )
            )
        
        return p.nav(class_="main-nav")(
            p.div(class_="nav-container")(
                p.div(class_="nav-logo")(
                    p.a(href="/")(
                        p.i(class_="fas fa-anchor nav-logo-icon"),
                        "First Mate"
                    )
                ),
                p.div(class_="nav-links")(
                    *links
                ),
                p.div(class_="nav-toggle")(
                    p.i(class_="fas fa-bars")
                )
            )
        )

    # Since p.raw is not available, we'll create a head element with style tag the standard way
    head_element = p.head(
        p.title("First Mate - Connect with Your Classmates"),
        p.link(href="/static/root.css", rel="stylesheet"),
        p.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        p.link(
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
            rel="stylesheet"
        ),
        # Add style tag
        p.style("""
            :root {
                --primary: #5e35b1;
                --primary-light: #7e57c2;
                --primary-dark: #4527a0;
                --accent: #2979ff;
                --text-light: #f5f5f5;
                --text-dark: #ddd;
                --dark-bg: #0f1729;
                --card-bg: #1a1f36;
                --nav-height: 70px;
            }
            
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body {
                font-family: 'Segoe UI', Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: var(--dark-bg);
                color: var(--text-light);
                margin: 0;
                padding: 0;
                line-height: 1.6;
                padding-top: var(--nav-height); /* Add padding for fixed navbar */
            }
            
            /* Enhanced Navbar Styles */
            .main-nav {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: var(--nav-height);
                background-color: rgba(13, 17, 31, 0.95);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
                z-index: 1000;
            }
            
            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                height: 100%;
                padding: 0 20px;
            }
            
            .nav-logo {
                font-size: 1.5rem;
                font-weight: 700;
            }
            
            .nav-logo a {
                color: white;
                text-decoration: none;
                display: flex;
                align-items: center;
                transition: color 0.2s ease;
            }
            
            .nav-logo a:hover {
                color: var(--accent);
            }
            
            .nav-logo-icon {
                margin-right: 10px;
                color: var(--primary-light);
            }
            
            .nav-links {
                display: flex;
                gap: 8px;
            }
            
            .nav-link {
                padding: 8px 16px;
                color: var(--text-light);
                text-decoration: none;
                font-weight: 500;
                border-radius: 6px;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                position: relative;
                overflow: hidden;
            }
            
            .nav-link:before {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 0;
                height: 3px;
                background: linear-gradient(90deg, var(--primary-light), var(--accent));
                transition: width 0.3s ease;
            }
            
            .nav-link:hover {
                background-color: rgba(255, 255, 255, 0.1);
                transform: translateY(-2px);
            }
            
            .nav-link:hover:before {
                width: 100%;
            }
            
            .nav-link i {
                margin-right: 8px;
                font-size: 16px;
            }
            
            .nav-toggle {
                display: none;
                cursor: pointer;
                font-size: 1.5rem;
                color: var(--text-light);
            }
            
            /* Media query for responsive navbar */
            @media (max-width: 768px) {
                .nav-links {
                    display: none;
                    position: absolute;
                    top: var(--nav-height);
                    left: 0;
                    right: 0;
                    flex-direction: column;
                    background-color: var(--dark-bg);
                    padding: 20px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    z-index: 999;
                }
                
                .nav-links.show {
                    display: flex;
                }
                
                .nav-link {
                    padding: 12px 16px;
                }
                
                .nav-toggle {
                    display: block;
                }
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            .hero-section {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                padding: 60px 20px;
                position: relative;
                overflow: hidden;
            }
            
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary), var(--accent));
                z-index: 1;
            }
            
            .hero-title {
                font-size: 2.8rem;
                font-weight: 700;
                margin-bottom: 24px;
                color: var(--primary-light);
                background: linear-gradient(90deg, var(--primary-light), var(--accent));
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }
            
            .hero-subtitle {
                font-size: 1.5rem;
                max-width: 800px;
                margin: 0 auto 40px;
                color: var(--text-dark);
            }
            
            .features-section {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 40px 20px;
                background-color: rgba(0, 0, 0, 0.2);
            }
            
            .features-title {
                font-size: 2rem;
                margin-bottom: 40px;
                text-align: center;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                width: 100%;
                max-width: 1200px;
            }
            
            .feature-card {
                background-color: var(--card-bg);
                border-radius: 8px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            }
            
            .feature-icon {
                font-size: 36px;
                margin-bottom: 20px;
                color: var(--primary-light);
            }
            
            .feature-title {
                font-size: 1.4rem;
                margin-bottom: 15px;
                color: white;
            }
            
            .feature-description {
                font-size: 1rem;
                color: var(--text-dark);
            }
            
            .showcase-section {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 60px 20px;
                background-color: rgba(94, 53, 177, 0.05);
            }
            
            .showcase-content {
                display: flex;
                flex-direction: row;
                align-items: center;
                max-width: 1200px;
                gap: 40px;
            }
            
            @media (max-width: 900px) {
                .showcase-content {
                    flex-direction: column;
                    text-align: center;
                }
            }
            
            .showcase-image {
                flex: 1;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                max-width: 500px;
            }
            
            .showcase-image img {
                width: 100%;
                height: auto;
                display: block;
            }
            
            .showcase-text {
                flex: 1;
                padding: 20px;
            }
            
            .showcase-title {
                font-size: 2rem;
                margin-bottom: 20px;
                color: white;
            }
            
            .showcase-description {
                font-size: 1.1rem;
                margin-bottom: 30px;
                color: var(--text-dark);
            }
            
            .cta-section {
                text-align: center;
                padding: 60px 20px;
                background-color: rgba(94, 53, 177, 0.1);
            }
            
            .cta-title {
                font-size: 2.2rem;
                margin-bottom: 20px;
            }
            
            .cta-description {
                font-size: 1.2rem;
                max-width: 700px;
                margin: 0 auto 30px;
                color: var(--text-dark);
            }
            
            .cta-button {
                display: inline-block;
                background: linear-gradient(90deg, var(--primary), var(--accent));
                color: white;
                padding: 14px 32px;
                border-radius: 30px;
                font-size: 1.1rem;
                font-weight: 600;
                text-decoration: none;
                box-shadow: 0 4px 15px rgba(94, 53, 177, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: none;
                cursor: pointer;
            }
            
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(94, 53, 177, 0.4);
            }
            
            .footer {
                padding: 30px 20px;
                text-align: center;
                color: var(--text-dark);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .footer-text {
                font-size: 0.9rem;
            }
        """),
        p.script("""
            // Add event listener to toggle navbar on mobile
            document.addEventListener('DOMContentLoaded', function() {
                const navToggle = document.querySelector('.nav-toggle');
                const navLinks = document.querySelector('.nav-links');
                
                if (navToggle) {
                    navToggle.addEventListener('click', function() {
                        navLinks.classList.toggle('show');
                    });
                }
            });
        """)
    )
    
    return str(
        p.html(
            head_element,
            p.body(
                # Use our enhanced navbar instead of the default one
                enhanced_navbar(),
                
                # Hero Section
                p.section(class_="hero-section")(
                    p.div(class_="container")(
                        p.h1(class_="hero-title")("First Mate - Making UNSW Connections"),
                        p.p(class_="hero-subtitle")(
                            "Find and connect with fellow students in your courses. "
                            "Turn your class schedule into meaningful friendships."
                        ),
                    )
                ),
                
                # Features Section
                p.section(class_="features-section")(
                    p.div(class_="container")(
                        p.h2(class_="features-title")("How First Mate Works"),
                        p.div(class_="features-grid")(
                            p.div(class_="feature-card")(
                                p.i(class_="fas fa-calendar feature-icon"),
                                p.h3(class_="feature-title")("Sync Your Schedule"),
                                p.p(class_="feature-description")(
                                    "Connect your UNSW timetable with our platform "
                                    "to find students who share your classes."
                                )
                            ),
                            p.div(class_="feature-card")(
                                p.i(class_="fas fa-users feature-icon"),
                                p.h3(class_="feature-title")("Match With Classmates"),
                                p.p(class_="feature-description")(
                                    "Our algorithm matches you with students in your courses "
                                    "who have similar schedules."
                                )
                            ),
                            p.div(class_="feature-card")(
                                p.i(class_="fas fa-comments feature-icon"),
                                p.h3(class_="feature-title")("Connect & Collaborate"),
                                p.p(class_="feature-description")(
                                    "Message your matches, form study groups, and make "
                                    "the most of your university experience."
                                )
                            )
                        )
                    )
                ),
                
                # Showcase Section with Elephant
                p.section(class_="showcase-section")(
                    p.div(class_="showcase-content")(
                        p.div(class_="showcase-image")(
                            p.img(
                                src="https://cdn.britannica.com/02/152302-050-1A984FCB/African-savanna-elephant.jpg",
                                alt="Happy elephant who found friends using First Mate"
                            )
                        ),
                        p.div(class_="showcase-text")(
                            p.h2(class_="showcase-title")("Success Stories"),
                            p.p(class_="showcase-description")(
                                "This elephant used First Mate to find a friend in COMP1511. "
                                "Now it's happy and thriving in its courses! Our platform has "
                                "helped thousands of students build meaningful connections "
                                "that enhance their university experience."
                            ),
                            p.p(class_="showcase-description")(
                                "Even shy students find it easy to connect with others who "
                                "share their interests and academic goals."
                            )
                        )
                    )
                ),
                
                # Call to Action
                p.section(class_="cta-section")(
                    p.div(class_="container")(
                        p.h2(class_="cta-title")("Ready to Find Your Study Mates?"),
                        p.p(class_="cta-description")(
                            "Join First Mate today and start connecting with fellow UNSW students in your courses."
                        ),
                        p.a(href="/auth/register", class_="cta-button")(
                            "Get Started Now"
                        )
                    )
                ),
                
                # Footer
                p.footer(class_="footer")(
                    p.div(class_="container")(
                        p.p(class_="footer-text")(
                            "Created by UNSW students, for UNSW students. © 2025 First Mate"
                        )
                    )
                )
            )
        )
    )


@app.get("/static/<filename>")
def serve_static(filename):
    """
    Manually implement static directory because we couldn't convince Flask to
    actually load the data no matter what we tried :(

    Seriously I do not know why it was broken no matter what we did

    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    """
    file_path = os.path.join(os.getcwd(), "first_mate", "static", filename)
    return send_file(file_path)