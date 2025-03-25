"""
server/auth.py

Server code for authentication with fixed UI and consistent navbar.
"""

import pyhtml as p
from flask import Blueprint, redirect, request

from first_mate.server.session import (
    clear_session,
    get_session,
    is_user_logged_in,
    set_session,
)

from .util import error_page, list_to_checkboxes, navbar
from ..consts import DEGREES_LIST
from first_mate.logic.user import login_user, logout_user, register_user


auth = Blueprint("/auth", __name__)


def enhanced_navbar(logged_in):
    """Custom enhanced navbar to match the homepage"""
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


@auth.get("/register")
def register_page():
    if is_user_logged_in():
        return redirect("/")
        
    # Define enhanced CSS for registration page
    enhanced_styles = p.style("""
        :root {
            --primary: #5e35b1;
            --primary-light: #7e57c2;
            --primary-dark: #4527a0;
            --accent: #2979ff;
            --text-light: #f5f5f5;
            --text-dark: #ddd;
            --dark-bg: #0f1729;
            --card-bg: #1a1f36;
            --input-bg: #10132c;
            --error: #ff5252;
            --success: #4caf50;
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
            line-height: 1.6;
            padding-top: var(--nav-height); /* Add padding for fixed navbar */
            min-height: 100vh;
            margin: 0;
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
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .form-header {
            text-align: center;
            margin-bottom: 30px;
            width: 100%;
            max-width: 800px;
        }
        
        h1 {
            font-size: 2.2rem;
            font-weight: 600;
            margin-bottom: 15px;
            background: linear-gradient(90deg, var(--primary-light), var(--accent));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            display: inline-block;
        }
        
        .form-subheader {
            color: var(--text-dark);
            font-size: 1.1rem;
            max-width: 600px;
            margin: 0 auto;
        }
        
        #registration-form {
            width: 100%;
            max-width: 550px;
            margin: 0 auto 60px;
            background-color: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            position: relative;
        }
        
        #registration-form::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-light), var(--accent));
        }
        
        .form-content {
            padding: 30px;
        }
        
        .form-section {
            margin-bottom: 30px;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .section-icon {
            font-size: 1.2rem;
            margin-right: 10px;
            color: var(--primary-light);
        }
        
        .section-title {
            font-size: 1.2rem;
            font-weight: 500;
            color: var(--text-light);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        input[type="text"],
        input[type="password"],
        input[type="url"] {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            background-color: var(--input-bg);
            color: white;
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        
        input[type="text"]:focus,
        input[type="password"]:focus,
        input[type="url"]:focus {
            border-color: var(--primary-light);
            box-shadow: 0 0 0 3px rgba(126, 87, 194, 0.2);
            outline: none;
        }
        
        .form-hint {
            font-size: 0.85rem;
            color: var(--text-dark);
            margin-top: 6px;
            font-style: italic;
        }
        
        .degrees-container {
            background-color: rgba(0, 0, 0, 0.15);
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .checkbox-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .checkbox-item input[type="checkbox"] {
            margin-right: 8px;
            width: 18px;
            height: 18px;
            accent-color: var(--primary);
        }
        
        .submit-button {
            display: block;
            width: 100%;
            padding: 14px;
            margin-top: 30px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .submit-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(94, 53, 177, 0.3);
        }
        
        .login-link {
            text-align: center;
            margin-top: 20px;
            font-size: 0.95rem;
        }
        
        .login-link a {
            color: var(--primary-light);
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .login-link a:hover {
            color: var(--accent);
            text-decoration: underline;
        }
        
        /* Reset server button */
        .reset-server {
            position: fixed;
            top: 15px;
            right: 15px;
            padding: 8px 16px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            z-index: 2000;
        }
        
        /* Responsive adjustments */
        @media (max-width: 600px) {
            .form-content {
                padding: 20px;
            }
            
            .checkbox-grid {
                grid-template-columns: 1fr;
            }
        }
    """)
    
    # Add JavaScript for navbar toggle
    navbar_script = p.script("""
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
    
    # Create checkbox items with better styling
    def create_checkbox_items(degrees_list):
        items = []
        for degree in degrees_list:
            items.append(
                p.div(class_="checkbox-item")(
                    p.input(type="checkbox", id=f"degree-{degree}", name="degrees", value=degree),
                    p.label(for_=f"degree-{degree}")(degree)
                )
            )
        return items
    
    return str(
        p.html(
            p.head(
                p.title("Register - First Mate"),
                p.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
                p.link(
                    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
                    rel="stylesheet"
                ),
                enhanced_styles,
                navbar_script
            ),
            p.body(
                # Use enhanced navbar instead of default
                enhanced_navbar(False),
                
                # Reset server button (positioned with CSS)
                p.button(class_="reset-server")("RESET SERVER"),
                
                p.div(class_="container")(
                    # Form header
                    p.div(class_="form-header")(
                        p.h1("Join First Mate"),
                        p.p(class_="form-subheader")(
                            "Create your account to find study partners and friends in your UNSW courses."
                        )
                    ),
                    
                    # Registration form
                    p.div(id="registration-form")(
                        p.div(class_="form-content")(
                            p.form(action="/auth/register", method="post")(
                                # Personal Information Section
                                p.div(class_="form-section")(
                                    p.div(class_="section-header")(
                                        p.i(class_="fas fa-user section-icon"),
                                        p.div(class_="section-title")("Personal Information")
                                    ),
                                    
                                    # zID field
                                    p.div(class_="form-group")(
                                        p.label(for_="zid")("Your zID"),
                                        p.input(
                                            type="text",
                                            name="zid",
                                            id="zid",
                                            placeholder="z1234567",
                                            value="z1234567",
                                            required=True
                                        ),
                                        p.div(class_="form-hint")("Enter your UNSW student ID")
                                    ),
                                    
                                    # Name field
                                    p.div(class_="form-group")(
                                        p.label(for_="name")("Your name"),
                                        p.input(
                                            type="text",
                                            name="name",
                                            id="name",
                                            placeholder="Robin Banks",
                                            value="Robin Banks",
                                            required=True
                                        )
                                    ),
                                    
                                    # Password field
                                    p.div(class_="form-group")(
                                        p.label(for_="password")("Your password"),
                                        p.input(
                                            type="password",
                                            name="password",
                                            id="password",
                                            placeholder="********",
                                            value="abc123ABC",
                                            required=True
                                        ),
                                        p.div(class_="form-hint")(
                                            "Choose a strong password with at least 8 characters"
                                        )
                                    )
                                ),
                                
                                # Calendar Information Section
                                p.div(class_="form-section")(
                                    p.div(class_="section-header")(
                                        p.i(class_="fas fa-calendar-alt section-icon"),
                                        p.div(class_="section-title")("Calendar Information")
                                    ),
                                    
                                    # iCal link field
                                    p.div(class_="form-group")(
                                        p.label(for_="ical")("Your UNSW calendar iCal link"),
                                        p.input(
                                            type="url",
                                            name="ical",
                                            id="ical",
                                            placeholder="webcal://my.unsw.edu.au/cal/pttd/...",
                                            value="webcal://my.unsw.edu.au/cal/pttd/ABCDEFGHIJ.ics",
                                            required=True
                                        ),
                                        p.div(class_="form-hint")(
                                            "Found in myUNSW → My Student Profile → My Timetable → Subscribe to timetable"
                                        )
                                    )
                                ),
                                
                                # Academic Information Section
                                p.div(class_="form-section")(
                                    p.div(class_="section-header")(
                                        p.i(class_="fas fa-graduation-cap section-icon"),
                                        p.div(class_="section-title")("Academic Information")
                                    ),
                                    
                                    # Degrees selection
                                    p.div(class_="form-group")(
                                        p.label("Select your degree(s)"),
                                        p.div(class_="degrees-container")(
                                            p.div(class_="checkbox-grid")(
                                                *create_checkbox_items(DEGREES_LIST)
                                            ),
                                            p.div(class_="form-hint")(
                                                "This helps us match you with students in similar courses"
                                            )
                                        )
                                    )
                                ),
                                
                                # Submit button
                                p.button(type="submit", class_="submit-button")(
                                    "Create Account"
                                ),
                                
                                # Login link
                                p.div(class_="login-link")(
                                    "Already have an account? ",
                                    p.a(href="/auth/login")("Log in instead")
                                )
                            )
                        )
                    )
                )
            )
        )
    )


@auth.post("/register")
def register_submit():
    if is_user_logged_in():
        return redirect("/")
    zid = request.form["zid"]
    name = request.form["name"]
    password = request.form["password"]
    ical = request.form["ical"]
    degrees = request.form.getlist("degrees")

    session_id = register_user(zid, name, password, ical, degrees)
    if session_id is None:
        return str(
            error_page(
                "Register - Error",
                "Unable to register",
                "Perhaps the account already exists?",
                False,
            )
        )

    set_session(session_id)

    return redirect("/")


@auth.get("/login")
def login():
    if is_user_logged_in():
        return redirect("/")
    
    # Define enhanced CSS for login page
    enhanced_styles = p.style("""
        :root {
            --primary: #5e35b1;
            --primary-light: #7e57c2;
            --primary-dark: #4527a0;
            --accent: #2979ff;
            --text-light: #f5f5f5;
            --text-dark: #ddd;
            --dark-bg: #0f1729;
            --card-bg: #1a1f36;
            --input-bg: #10132c;
            --error: #ff5252;
            --success: #4caf50;
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
            line-height: 1.6;
            padding-top: var(--nav-height); /* Add padding for fixed navbar */
            min-height: 100vh;
            margin: 0;
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
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            min-height: calc(100vh - var(--nav-height) - 40px); /* Center vertically */
        }
        
        .form-header {
            text-align: center;
            margin-bottom: 30px;
            width: 100%;
            max-width: 800px;
        }
        
        h1 {
            font-size: 2.2rem;
            font-weight: 600;
            margin-bottom: 15px;
            background: linear-gradient(90deg, var(--primary-light), var(--accent));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            display: inline-block;
        }
        
        .form-subheader {
            color: var(--text-dark);
            font-size: 1.1rem;
            max-width: 600px;
            margin: 0 auto;
        }
        
        #login-box {
            width: 100%;
            max-width: 400px;
            margin: 0 auto 40px;
            background-color: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            position: relative;
        }
        
        #login-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-light), var(--accent));
        }
        
        .form-content {
            padding: 30px;
        }
        
        .login-icon {
            font-size: 3rem;
            color: var(--primary-light);
            text-align: center;
            margin-bottom: 20px;
            display: block;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            background-color: var(--input-bg);
            color: white;
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: var(--primary-light);
            box-shadow: 0 0 0 3px rgba(126, 87, 194, 0.2);
            outline: none;
        }
        
        .submit-button {
            display: block;
            width: 100%;
            padding: 14px;
            margin-top: 30px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .submit-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(94, 53, 177, 0.3);
        }
        
        .register-link {
            text-align: center;
            margin-top: 20px;
            font-size: 0.95rem;
        }
        
        .register-link a {
            color: var(--primary-light);
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .register-link a:hover {
            color: var(--accent);
            text-decoration: underline;
        }
        
        /* Reset server button */
        .reset-server {
            position: fixed;
            top: 15px;
            right: 15px;
            padding: 8px 16px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            z-index: 2000;
        }
    """)
    
    # Add JavaScript for navbar toggle
    navbar_script = p.script("""
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
    
    return str(
        p.html(
            p.head(
                p.title("Login - First Mate"),
                p.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
                p.link(
                    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
                    rel="stylesheet"
                ),
                enhanced_styles,
                navbar_script
            ),
            p.body(
                # Use enhanced navbar instead of default
                enhanced_navbar(False),
                
                # Reset server button (positioned with CSS)
                p.button(class_="reset-server")("RESET SERVER"),
                
                p.div(class_="container")(
                    # Form header
                    p.div(class_="form-header")(
                        p.h1("Welcome Back"),
                        p.p(class_="form-subheader")(
                            "Sign in to continue connecting with your classmates"
                        )
                    ),
                    
                    # Login form
                    p.div(id="login-box")(
                        p.div(class_="form-content")(
                            p.i(class_="fas fa-anchor login-icon"),
                            p.form(action="/auth/login", method="post")(
                                # zID field
                                p.div(class_="form-group")(
                                    p.label(for_="zid")("Your zID"),
                                    p.input(
                                        type="text",
                                        name="zid",
                                        id="zid",
                                        placeholder="z1234567",
                                        value="z1234567"
                                    )
                                ),
                                
                                # Password field
                                p.div(class_="form-group")(
                                    p.label(for_="password")("Your password"),
                                    p.input(
                                        type="password",
                                        name="password",
                                        id="password",
                                        placeholder="********",
                                        value="abc123ABC"
                                    )
                                ),
                                
                                # Submit button
                                p.button(type="submit", class_="submit-button")(
                                    "Log in"
                                ),
                                
                                # Register link
                                p.div(class_="register-link")(
                                    "Don't have an account? ",
                                    p.a(href="/auth/register")("Sign up now")
                                )
                            )
                        )
                    )
                )
            )
        )
    )


@auth.post("/login")
def login_submit():
    if is_user_logged_in():
        return redirect("/")
    zid = request.form["zid"]
    password = request.form["password"]

    session_id = login_user(zid, password)
    if session_id is None:
        return str(
            error_page(
                "Register - Error",
                "Unable to log in",
                "zID or password is incorrect",
                False,
            )
        )

    set_session(session_id)

    return redirect("/")


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    session = get_session()
    if session is None:
        return redirect("/")
    logout_user(session)
    clear_session()
    return redirect("/")