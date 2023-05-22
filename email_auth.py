from py4web import action, request, abort, redirect, URL
from py4web.core import Fixture
from py4web.utils.form import Form, FormStyleBulma
from pydal import Field
from pydal.validators import IS_EMAIL

#Code based off unit 8 video
EMAIL_KEY = "_user_email"

class EmailAuth(Fixture):
    def __init__(self, session, url_signer, emailer=None):
        self.session = session
        self.url_signer = url_signer
        self.emailer = emailer
        self.__prerequisites__ = [session]
        f = action.uses("sign_in.html", session)(self.login)
        action("sign_in", method=["GET", "POST"])(f)
        f = action.uses("sign_in_wait.html", session)(self.wait)
        action("sign_in_wait", method=["GET"])(f)
        f = action.uses("sign_in_wait.html", session, url_signer.verify())(self.confirm)
        action("sign_in_confirm" + "/<email>", method=["GET"])(f)


    def enforce(self):
        #requires a user to be logged in
        return EmailAuthEnforcer(self)
   
    @property
    def current_user(self):
        """Current_user is None if the user is not logged in,
        else it is a dictionary containing the email (and only the email)."""
        if self.session.get(EMAIL_KEY):
            return dict(email=self.session.get(EMAIL_KEY))
        else:
            return None


    def login(self):
        if self.session.get("_user_email"):
            #redirects a user if they're already signed in
            print(self.session.get("_user_email"))
            redirect(URL("index"))
        else:
           form = Form([Field('email', requires=IS_EMAIL())], csrf_session=self.session, formstyle=FormStyleBulma)
           if form.accepted:
               link = URL("sign_in_confirm", form.vars['email'], signer=self.url_signer)
               self.send_email(form.vars['email'], link)
               redirect(URL("sign_in_wait"))
               #redirect(URL(link))
           return dict(form=form)

    def confirm(self, email=None):
        assert email is not None
        self.session["_user_email"] = email
        redirect(URL("index"))

    def wait(self):
        return dict()

    def send_email(self, email, link):
        """Replace this with something that sends the link to the email."""
        print("Login Link Here:", "http://127.0.0.1:8000"+ link)
    '''def send_email(self, email, link):
    #email sending format based off 2fa documentation
        try:
            auth.sender.send(
                to=[email],
                subject=f"Bloombase Verification Email",
                body=f"Your verification link is {link}",
                sender="Verification@Bloombase.com",
            )
        except Exception as e:
            print(e)
        return link'''
    def transform(self, output, shared_data):
        template_context = shared_data.get("template_context")
        template_context["user"] = self.current_user
        return output


class EmailAuthEnforcer(Fixture):
    def __init__(self, auth):
        self.session = auth.session
        self.__prerequisites__ = [auth.session]
        self.auth = auth

    def on_request(self, context):
        if self.session.get("_user_email"):
            print(self.session.get("_user_email"))
            return
        else:
            redirect(URL("sign_in"))
    
    def transform(self, output, shared_data):
        return self.auth.transform(output, shared_data)
