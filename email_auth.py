from py4web.core import Fixture
from py4web import action, request, abort, redirect, URL
from py4web.utils.form import Form, FormStyleBulma
from pydal import Field
from pydal.validators import IS_EMAIL

# Key to access email in the session
EMAIL_KEY = "_user_email"
LOGIN_PATH = "auth_by_email/login"
CONFIRMATION_PATH = "auth_by_email/confirm"
WAITING_PATH = "auth_by_email/waiting"


class TestEmailer(object):
    """Dummy class for sending emails; all it does is prints the link."""

    def send_email(self, email, link):
        """Replace this with something that sends the link to the email."""
        print("Please click here:", link)


class AuthByEmail(Fixture):

    def __init__(self, session, url_signer, emailer=None, default_path='index'):
        """Store the session."""
        self.session = session
        self.url_signer = url_signer
        self.emailer = emailer or TestEmailer()
        self.__prerequisites__ = [session]
        self.default_path = default_path
        # Register path to login
        f = action.uses("auth_by_email_login.html", session)(self.login)
        action(LOGIN_PATH, method=["GET", "POST"])(f)
        # Register path to waiting
        f = action.uses("auth_by_email_wait.html", session)(self.wait)
        action(WAITING_PATH, method=["GET"])(f)
        # Register path to confirmation
        f = action.uses("auth_by_email_wait.html", session, url_signer.verify())(self.confirm)
        action(CONFIRMATION_PATH + "/<email>", method=["GET"])(f)

    @property
    def current_user(self):
        """Current_user is None if the user is not logged in,
        else it is a dictionary containing the email (and only the email)."""
        if self.session.get(EMAIL_KEY):
            return dict(email=self.session.get(EMAIL_KEY))
        else:
            return None

    def enforce(self):
        """This returns a fixture that enforces log-in via email."""
        return AuthByEmailEnforcer(self)

    @property
    def login_url(self):
        return URL(LOGIN_PATH)

    def login(self):
        """This is the controller that allows a user to login."""
        if self.session.get(EMAIL_KEY):
            redirect(URL(self.default_path))
        # The user is not logged in.  I provide a form to log in.
        form = Form([Field('email', requires=IS_EMAIL())],
                    csrf_session=self.session, formstyle=FormStyleBulma)
        if form.accepted:
            # At this point, in reality, I want to send an email to the user asking to confirm the email
            # by clicking on a link.  The link will cause the user to be logged in.
            link = URL(CONFIRMATION_PATH, form.vars['email'], signer=self.url_signer)
            self.emailer.send_email(form.vars['email'], link)
            redirect(URL(WAITING_PATH))
        return dict(form=form)

    def wait(self):
        """Controller for waiting page."""
        return dict()

    def confirm(self, email=None):
        """Controller for the confirmation page.  IF the link the valid, writes
        that the user is now logged in into the session."""
        assert email is not None
        self.session[EMAIL_KEY] = email
        redirect(URL(self.default_path))

    def transform(self, output, shared_data):
        """Injects user in the template, so that I can refer to it
        from layout.html"""
        template_context = shared_data.get("template_context")
        template_context["user"] = self.current_user
        return output


class AuthByEmailEnforcer(Fixture):

    def __init__(self, auth):
        """Initializes the enforcer."""
        self.session = auth.session
        self.__prerequisites__ = [auth.session]
        self.auth = auth

    def on_request(self):
        if self.session.get(EMAIL_KEY):
            return # The user is logged in
        else:
            redirect(URL(LOGIN_PATH))

    def transform(self, output, shared_data):
        """Injects user in the template, so that I can refer to it
        from layout.html"""
        return self.auth.transform(output, shared_data)
