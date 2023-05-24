from py4web import action, request, abort, redirect, URL
from py4web.core import Fixture
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.auth import AuthAPI
from pydal import Field
from pydal.validators import IS_EMAIL

#Code based off unit 8 video
#This overrides the default authentication. As of right now we're not actually sending emails, so when you input an email
#check the console for a login link associated with that email
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
        f = action.uses(session, url_signer.verify())(self.logout)
        action("logout")(f)

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
           return dict(form=form, auth = self)

    def logout(self):
        #shamelessly taken from the original auth.py and modified to redirect users to the homepage upon logging out
        if AuthAPI.model_request("logout"):
            return AuthAPI.get_model(defaultAuthFunction=auth.form_source.logout)

        self.session.clear()
        redirect(URL("index"))

    def confirm(self, email=None):
        assert email is not None
        self.session["_user_email"] = email
        redirect(URL("index"))

    def wait(self):
        #this is the page where the user stays while awaiting the authentication email
        return dict(auth = self)

    def send_email(self, email, link):
        """Replace this with something that sends the link to the email."""
        print("Login Link Here:", "http://127.0.0.1:8000"+ link)
        '''def send_email(self, email, link):
        #this is potential stuff to be used in the future maybe
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

    #Imma be honest I'm not sure how transform works here
    def transform(self, output, shared_data):
        template_context = shared_data.get("template_context")
        template_context["user"] = self.current_user
        return output


class EmailAuthEnforcer(Fixture):
    #ensures that a user is logged in when trying to access restricted pages
    def __init__(self, auth):
        self.session = auth.session
        self.__prerequisites__ = [auth.session]
        self.auth = auth

    def on_request(self, context):
        #checks if the user is logged in or not, prompts them to sign if they aren't
        if self.session.get("_user_email"):
            print(self.session.get("_user_email"))
            return
        else:
            redirect(URL("sign_in"))
    
    def transform(self, output, shared_data):
        return self.auth.transform(output, shared_data)
