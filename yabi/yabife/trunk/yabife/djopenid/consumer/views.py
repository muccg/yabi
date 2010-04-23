
from django import http
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.utils import webhelpers

from django.shortcuts import render_to_response, get_object_or_404, render_mako

from django import forms

from openid.consumer import consumer
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import ax, pape, sreg
from openid.yadis.constants import YADIS_HEADER_NAME, YADIS_CONTENT_TYPE
from openid.server.trustroot import RP_RETURN_TO_URL_TYPE

from yabifeapp.views import LoginForm

from djopenid import util

PAPE_POLICIES = [
    'AUTH_PHISHING_RESISTANT',
    'AUTH_MULTI_FACTOR',
    'AUTH_MULTI_FACTOR_PHYSICAL',
    ]

# List of (name, uri) for use in generating the request form.
POLICY_PAIRS = [(p, getattr(pape, p))
                for p in PAPE_POLICIES]

def getOpenIDStore():
    """
    Return an OpenID store object fit for the currently-chosen
    database backend, if any.
    """
    return util.getOpenIDStore('/tmp/djopenid_c_store', 'c_')

def getConsumer(request):
    """
    Get a Consumer object to perform OpenID authentication.
    """
    return consumer.Consumer(request.session, getOpenIDStore())

def renderIndexPage(request, **template_args):
    template_args['consumer_url'] = util.getViewURL(request, startOpenID)
    template_args['pape_policies'] = POLICY_PAIRS

    template_args['h'] = webhelpers
    template_args['request'] = request

    response = render_to_response('consumer/index.html', template_args)

    response[YADIS_HEADER_NAME] = siteurl(request) . webhelpers.url('/openid/consumer/') #util.getViewURL(request, rpXRDS)
    return response


def startOpenID(request):
    """
    Start the OpenID authentication process.  Renders an
    authentication form and accepts its POST.

    * Renders an error message if OpenID cannot be initiated

    * Requests some Simple Registration data using the OpenID
      library's Simple Registration machinery

    * Generates the appropriate trust root and return URL values for
      this application (tweak where appropriate)

    * Generates the appropriate redirect based on the OpenID protocol
      version.
    """
    if request.POST:
        # Start OpenID authentication.
        openid_url = request.POST['openid_identifier']
        c = getConsumer(request)
        error = None

        try:
            auth_request = c.begin(openid_url)
        except DiscoveryFailure, e:
            # Some other protocol-level failure occurred.
            error = "OpenID discovery error: %s" % (str(e),)

        if error:
            # Render the page with an error.
            form = LoginForm()
            result = {}
            result['h'] = webhelpers
            result['form'] = form
            result['error'] = error

            return render_to_response('login.html', result)


        # Add Simple Registration request information.  Some fields
        # are optional, some are required.  It's possible that the
        # server doesn't support sreg or won't return any of the
        # fields.
        sreg_request = sreg.SRegRequest(optional=['email', 'nickname'],
                                        required=['dob'])
        auth_request.addExtension(sreg_request)

        # Add Attribute Exchange request information.
        ax_request = ax.FetchRequest()
        # XXX - uses myOpenID-compatible schema values, which are
        # not those listed at axschema.org.
        ax_request.add(
            ax.AttrInfo('http://axschema.org/namePerson',
                        required=True))
        ax_request.add(
            ax.AttrInfo('http://axschema.org/namePerson/friendly',
                        required=True))
        ax_request.add(
            ax.AttrInfo('http://axschema.org/contact/email',
                        required=False, count=ax.UNLIMITED_VALUES))
        auth_request.addExtension(ax_request)

        # Add PAPE request information.  We'll ask for
        # phishing-resistant auth and display any policies we get in
        # the response.
        requested_policies = []
        policy_prefix = 'policy_'
        for k, v in request.POST.iteritems():
            if k.startswith(policy_prefix):
                policy_attr = k[len(policy_prefix):]
                if policy_attr in PAPE_POLICIES:
                    requested_policies.append(getattr(pape, policy_attr))

        if requested_policies:
            pape_request = pape.Request(requested_policies)
            auth_request.addExtension(pape_request)

        # Compute the trust root and return URL values to build the
        # redirect information.
        trust_root = util.getViewURL(request, startOpenID)
        return_to = siteurl(request) + 'openid/finish/'

        # Send the browser to the server either by sending a redirect
        # URL or by generating a POST form.
        if auth_request.shouldSendRedirect():
            url = auth_request.redirectURL(trust_root, return_to)
            return HttpResponseRedirect(url)
        else:
            # Beware: this renders a template whose content is a form
            # and some javascript to submit it upon page load.  Non-JS
            # users will have to click the form submit button to
            # initiate OpenID authentication.
            form_id = 'openid_message'
            auth_request.addExtensionArg('','type.email','http://axschema.org/contact/email')
            form_html = auth_request.formMarkup(trust_root, return_to,
                                                False, {'id': form_id})
            #if openid_url.find('google') >= 0:
            #    return direct_to_template(
            #        request, 'consumer/request_form.html', {'html': form_html, 'is_google': True, 'h':webhelpers, 'return_to':return_to, 'realm':trust_root})
            #else:
            return direct_to_template(
                    request, 'consumer/request_form.html', {'html': form_html, 'h':webhelpers, 'return_to':return_to})

    form = LoginForm()
    result = {}
    result['h'] = webhelpers
    result['form'] = form

    return render_to_response('login.html', result)


def finishOpenID(request):
    """
    Finish the OpenID authentication process.  Invoke the OpenID
    library with the response from the OpenID server and render a page
    detailing the result.
    """
    result = {}

    # Because the object containing the query parameters is a
    # MultiValueDict and the OpenID library doesn't allow that, we'll
    # convert it to a normal dict.

    # OpenID 2 can send arguments as either POST body or GET query
    # parameters.
    request_args = util.normalDict(request.GET)
    if request.method == 'POST':
        request_args.update(util.normalDict(request.POST))

    request_args = request.GET

    if request_args:
        c = getConsumer(request)

        # Get a response object indicating the result of the OpenID
        # protocol.
        return_to = util.getViewURL(request, finishOpenID)
        response = c.complete(request_args, return_to)

        # Get a Simple Registration response object if response
        # information was included in the OpenID response.
        sreg_response = {}
        ax_items = {}
        if response.status == consumer.SUCCESS:
            sreg_response = sreg.SRegResponse.fromSuccessResponse(response)

            ax_response = ax.FetchResponse.fromSuccessResponse(response, False)
            if ax_response:
                ax_items = {
                    'fullname': ax_response.get(
                        'http://axschema.org/namePerson'),
                    'email': ax_response.get(
                        'http://axschema.org/contact/email'),
                    'username': ax_response.get(
                        'http://axschema.org/namePerson/friendly')
                    }

        # Get a PAPE response object if response information was
        # included in the OpenID response.
        pape_response = None
        if response.status == consumer.SUCCESS:
            pape_response = pape.Response.fromSuccessResponse(response)

            if not pape_response.auth_policies:
                pape_response = None

        # Map different consumer status codes to template contexts.
        results = {
            consumer.CANCEL:
            {'message': 'OpenID authentication cancelled.'},

            consumer.FAILURE:
            {'error': 'OpenID authentication failed.'},

            consumer.SUCCESS:
            {'url': response.getDisplayIdentifier(),
             'sreg': sreg_response and sreg_response.items(),
             'ax': ax_items.items(),
             'pape': pape_response}
            }

        result = results[response.status]

        if isinstance(response, consumer.FailureResponse):
            # In a real application, this information should be
            # written to a log for debugging/tracking OpenID
            # authentication failures. In general, the messages are
            # not user-friendly, but intended for developers.
            result['failure_reason'] = response.message

    form = LoginForm()
    result['h'] = webhelpers
    result['form'] = form

    if response.status == consumer.SUCCESS:
        from django.contrib.auth import authenticate, login

        user = authenticate(openid_url = response.getDisplayIdentifier())

        if user is None:
            return render_to_response('consumer/registration.html', result)
        else:
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        return render_to_response('login.html', result)

def rpXRDS(request):
    """
    Return a relying party verification XRDS document
    """
    return util.renderXRDS(
        request,
        [RP_RETURN_TO_URL_TYPE],
        [util.getViewURL(request, finishOpenID)])

# forms
class RegistrationForm(forms.Form):
    name = forms.CharField()
    openid_url = forms.CharField()
    organisation = forms.CharField()
    faculty = forms.CharField()
    user_type = forms.CharField()
    org_user_id = forms.CharField()
    email = forms.CharField()
    contact_number = forms.CharField()
    supervisor_name = forms.CharField()
    supervisor_number = forms.CharField()
    supervisor_email = forms.CharField()
    project_title = forms.CharField()
    project_description = forms.CharField()
    rfcd_code_1 = forms.CharField()
    rfcd_code_1_weight = forms.CharField()
    rfcd_code_2 = forms.CharField()
    rfcd_code_2_weight = forms.CharField()
    rfcd_code_3 = forms.CharField()
    rfcd_code_3_weight = forms.CharField()
    resources_compute = forms.CharField()
    resources_data = forms.CharField()
    resources_network = forms.CharField()
    estimate = forms.CharField()
    describe = forms.CharField()
    software_needs = forms.CharField()
    agreement = forms.CharField()
    
def registration(request):
    result = {}
    result['h'] = webhelpers
    
    form = RegistrationForm(request)
    
    name = form.cleaned_data['name']
    openid_url = form.cleaned_data['openid_url']
    organisation = form.cleaned_data['organisation']
    faculty = form.cleaned_data['faculty']
    user_type = form.cleaned_data['user_type']
    org_user_id = form.cleaned_data['org_user_id']
    email = form.cleaned_data['email']
    contact_number = form.cleaned_data['contact_number']
    supervisor_name = form.cleaned_data['supervisor_name']
    supervisor_number = form.cleaned_data['supervisor_number']
    supervisor_email = form.cleaned_data['supervisor_email']
    project_title = form.cleaned_data['project_title']
    project_description = form.cleaned_data['project_description']
    rfcd_code_1 = form.cleaned_data['rfcd_code_1']
    rfcd_code_1_weight = form.cleaned_data['rfcd_code_1_weight']
    rfcd_code_2 = form.cleaned_data['rfcd_code_2']
    rfcd_code_2_weight = form.cleaned_data['rfcd_code_2_weight']
    rfcd_code_3 = form.cleaned_data['rfcd_code_3']
    rfcd_code_3_weight = form.cleaned_data['rfcd_code_3_weight']
    resources_compute = form.cleaned_data['resources_compute']
    resources_data = form.cleaned_data['resources_data']
    resources_network = form.cleaned_data['resources_network']
    estimate = form.cleaned_data['estimate']
    describe = form.cleaned_data['describe']
    software_needs = form.cleaned_data['software_needs']
    agreement = form.cleaned_data['agreement']
    
    form.save()
    

    response = render_to_response('consumer/registration_complete.html',result)
    return response

def siteurl(request):
    import os
    wsgibase=os.environ['SCRIPT_NAME']

    d = request.__dict__
    if d['META'].has_key('HTTP_X_FORWARDED_HOST'):
        #The request has come from outside, so respect X_FORWARDED_HOST
        u = d['META']['wsgi.url_scheme'] + '://' + d['META']['HTTP_X_FORWARDED_HOST'] + wsgibase
    else:
        #Otherwise, its an internal request
        host = d['META'].get('HTTP_HOST')
        if not host:
            host = d['META'].get('SERVER_NAME')
        u = d['META']['wsgi.url_scheme'] + '://' + host + wsgibase + '/' 

    return u

