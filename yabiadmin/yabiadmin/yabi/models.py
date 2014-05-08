#-*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics
# (http://ccg.murdoch.edu.au/).
#
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS,"
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS.
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
#
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
### END COPYRIGHT ###
# -*- coding: utf-8 -*-
import traceback
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate
from django.utils import simplejson as json
from django.conf import settings
from django.core.cache import cache
from urlparse import urlunparse
from yabiadmin.crypto_utils import encrypt_to_annotated_block, decrypt_annotated_block, \
    encrypted_block_is_legacy, any_unencrypted, any_annotated_block, DecryptException
from yabiadmin.utils import cache_keyname
from collections import namedtuple

import logging
from functools import reduce
import six
logger = logging.getLogger(__name__)

try:
    from yabiadmin import ldaputils
    LDAP_IN_USE = True
except ImportError as e:
    LDAP_IN_USE = False
    logger.info("LDAP modules not imported. If you are not using LDAP this is not a problem.")


class DecryptedCredentialNotAvailable(Exception):
    pass


class Base(models.Model):

    class Meta:
        abstract = True

    last_modified_by = models.ForeignKey(DjangoUser, editable=False, related_name="%(class)s_modifiers", null=True, on_delete=models.SET_NULL)
    last_modified_on = models.DateTimeField(null=True, auto_now=True, editable=False)
    created_by = models.ForeignKey(DjangoUser, editable=False, related_name="%(class)s_creators", null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)


class FileExtension(Base):
    pattern = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ('pattern',)

    def __unicode__(self):
        return self.pattern

    def extension(self):
        """Try and express _only_ the extension from this glob. This is very naive."""
        return self.pattern.rsplit(".")[-1]


class FileType(Base):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    extensions = models.ManyToManyField(FileExtension, null=True, blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.file_extensions_text())

    def file_extensions_list(self):
        extensions = [ext.pattern for ext in self.extensions.all()]
        return extensions

    def file_extensions_text(self):
        return ", ".join(self.file_extensions_list())

    file_extensions_text.short_description = 'File Extensions'


class Tool(Base):

    class Meta:
        ordering = ("name",)

    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    path = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    enabled = models.BooleanField(default=True)
    backend = models.ForeignKey('Backend')
    fs_backend = models.ForeignKey('Backend', related_name="fs_backends")
    groups = models.ManyToManyField('ToolGroup', through='ToolGrouping', null=True, blank=True)
    output_filetypes = models.ManyToManyField(FileExtension, through='ToolOutputExtension', null=True, blank=True)
    accepts_input = models.BooleanField(default=False)
    cpus = models.CharField(max_length=64, null=True, blank=True)
    walltime = models.CharField(max_length=64, null=True, blank=True)
    module = models.TextField(null=True, blank=True)
    queue = models.CharField(max_length=50, default='normal', null=True, blank=True)
    max_memory = models.CharField(max_length=64, null=True, blank=True)
    job_type = models.CharField(max_length=40, default='single', null=True, blank=True)
    submission = models.TextField(blank=True)
    lcopy_supported = models.BooleanField(default=True)
    link_supported = models.BooleanField(default=True)

    name.help_text = "Unique toolname for internal use."
    display_name.help_text = "Tool name visible to users."
    path.help_text = "The path to the binary for this file. Will normally just be binary name."
    description.help_text = "The description that will be sent to the frontend for the user."
    enabled.help_text = "Enable tool in frontend."
    backend.help_text = "The execution backend for this tool."
    fs_backend.help_text = "The filesystem backend for this tool."
    accepts_input.help_text = "If checked, this tool will accept inputs from prior tools rather than presenting file select widgets."
    module.help_text = "Comma separated list of modules to load."
    submission.help_text = "Mako script to be used to generate the submission script. (Variables: walltime, memory, cpus, working, modules, command, etc.)"
    lcopy_supported.help_text = "If this tool should use local copies on supported backends where appropriate."
    link_supported.help_text = "If this tool should use symlinks on supported backends where appropriate."

    def tool_groups_str(self):
        return ",".join(["%s (%s)" % (tg.tool_group, tg.tool_set) for tg in self.toolgrouping_set.all()])

    tool_groups_str.short_description = 'Belongs to Tool Groups'

    @models.permalink
    def view_url(self):
        return ('tool_view', (), {'tool_id': self.id})

    def tool_link(self):
        return '<a href="%s">View</a>' % self.view_url()

    tool_link.short_description = 'View'
    tool_link.allow_tags = True

    def input_filetype_extensions(self):
        '''
        Work out input file extensions for this tool and return a a list of them all.
        This is used by the front end to determine all input types a tool will accept.
        '''
        # empty list passed to reduce is initializer, see reduce docs
        filetypes = reduce(lambda x, y: x + y, [list(x.accepted_filetypes.all()) for x in self.toolparameter_set.all()], [])
        extensions = [ext.pattern for ext in reduce(lambda x, y: x + y, [list(ft.extensions.all()) for ft in filetypes], [])]
        return list(set(extensions))  # remove duplicates

    def input_filetype_extensions_for_batch_param(self):
        '''
        This is used by the builder to determine the extensions than the batch_on_param parameter uses.
        '''
        extensions = []
        if self.batch_on_param:
            filetypes = self.batch_on_param.accepted_filetypes.all()
            extensions = [ext.pattern for ext in reduce(lambda x, y: x + y, [list(ft.extensions.all()) for ft in filetypes], [])]
        return list(set(extensions))  # remove duplicates

    def output_filetype_extensions(self):
        '''Work out output file extensions for this tool and return a a list of them all'''
        extensions = [fe.file_extension.pattern for fe in self.tooloutputextension_set.all()]
        return list(set(extensions))  # remove duplicates

    def tool_dict(self):
        '''Gathers tool details into convenient dict for use by json or other models json'''

        tool_dict = {
            'name': self.name,
            'display_name': self.display_name,
            'path': self.path,
            'description': self.description,
            'enabled': self.enabled,
            'backend': self.backend.name,
            'fs_backend': self.fs_backend.name,
            'accepts_input': self.accepts_input,
            'cpus': self.cpus,
            'walltime': self.walltime,
            'module': self.module,
            'queue': self.queue,
            'max_memory': self.max_memory,
            'job_type': self.job_type,
            'inputExtensions': self.input_filetype_extensions(),
            'outputExtensions': list(self.tooloutputextension_set.values("must_exist", "must_be_larger_than", "file_extension__pattern")),
            'parameter_list': list(self.toolparameter_set.order_by('fe_rank', 'id').values("id", "rank", "mandatory", "common", "hidden", "file_assignment", "output_file",
                                                                                "switch", "switch_use__display_text", "switch_use__formatstring", "switch_use__description",
                                                                                "possible_values", "default_value", "helptext", "batch_bundle_files", "use_output_filename__switch"))
        }

        for p in tool_dict["parameter_list"]:
            tp = ToolParameter.objects.get(id=p["id"])
            p["acceptedExtensionList"] = tp.input_filetype_extensions()
            if tp.extension_param:
                p["extension_param"] = tp.extension_param.pattern

        return tool_dict

    def decode_embedded_json(self):
        # the possible_values field has json in it so we need to make it decode
        # or it will be double encoded
        output = self.tool_dict()

        for plist in output["parameter_list"]:
            if "possible_values" in plist and plist["possible_values"]:
                plist["possible_values"] = json.loads(plist["possible_values"])

        return output

    def json(self):
        output = self.decode_embedded_json()
        return json.dumps({'tool': output})

    def json_pretty(self):
        output = self.decode_embedded_json()
        return json.dumps({'tool': output}, indent=4)

    def purge_from_cache(self):
        """Purge this tools entry description from cache"""
        cache.delete(cache_keyname(self.name))

    def __unicode__(self):
        return self.name


class ParameterSwitchUse(Base):
    display_text = models.CharField(max_length=30)
    formatstring = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    formatstring.help_text = "Example: %(switch)s %(value)s"

    def __unicode__(self):
        return self.display_text

FILE_ASSIGNMENT_CHOICES = (
    ('none', 'No input files'),
    ('batch', 'Single input file'),
    ('all', 'Multiple input files'),
)


class ToolParameter(Base):
    tool = models.ForeignKey(Tool)
    switch = models.CharField(max_length=64)
    switch_use = models.ForeignKey(ParameterSwitchUse)
    rank = models.IntegerField(null=True, blank=True)
    fe_rank = models.IntegerField(null=True, blank=True, verbose_name="Frontend rank")
    mandatory = models.BooleanField(blank=True, default=False)
    common = models.BooleanField(blank=True, default=False, verbose_name="Commonly used")
    hidden = models.BooleanField(blank=True, default=False)
    output_file = models.BooleanField(blank=True, default=False)
    accepted_filetypes = models.ManyToManyField(FileType, blank=True)
    extension_param = models.ForeignKey(FileExtension, null=True, blank=True)
    possible_values = models.TextField(null=True, blank=True)
    default_value = models.TextField(null=True, blank=True)
    helptext = models.TextField(null=True, blank=True)

    batch_bundle_files = models.BooleanField(blank=False, null=False, default=False)

    file_assignment = models.CharField(max_length=5, null=False, choices=FILE_ASSIGNMENT_CHOICES)

    # this foreign key points to the tool parameter (that is a batch_on_param) that we will derive the output filename for this switch from
    use_output_filename = models.ForeignKey('ToolParameter', null=True, blank=True)
    switch.help_text = "The actual command line switch that should be passed to the tool i.e. -i or --input-file"
    switch_use.help_text = "The way the switch should be combined with the value."
    rank.help_text = "The order in which the switches should appear on the command line. Leave blank if order is unimportant."
    fe_rank.help_text = "The order in which the switches should appear in the frontend. Leave blank if order is unimportant."
    mandatory.help_text = "Select if the switch is required as input."
    common.help_text = "Commonly used parameters will not hidden by default in the frontend."
    hidden.help_text = "Select if the switch should be hidden from users in the frontend."
    output_file.help_text = "Select if the switch is specifying an output file."
    accepted_filetypes.help_text = "The extensions of accepted filetypes for this switch."
    extension_param.help_text = "If an extension is selected then this extension will be appended to the filename. This should only be set for specifying output files."
    possible_values.help_text = "Json snippet for html select. See blast tool for examples."
    default_value.help_text = "Value that will appear in field. If possible values is populated this should match one of the values so the select widget defaults to that option."
    helptext.help_text = "Help text that is passed to the frontend for display to the user."
    batch_bundle_files.help_text = "When staging in files, stage in every file that is in the same source location as this file. Useful for bringing along other files that are associated, but not specified."
    file_assignment.help_text = """Specifies how to deal with files that match the accepted filetypes setting...<br/><br/>
        <i>No input files:</i> This parameter does not take any input files as an argument<br/>
        <i>Single input file:</i> This parameter can only take a single input file, and batch jobs will need to be created for multiple files if the user passes them in<br/>
        <i>Multiple input file:</i> This parameter can take a whole string of input files, one after the other. All matching filetypes will be passed into it"""

    def __unicode__(self):
        return self.switch or ''

    def input_filetype_patterns(self):
        '''Work out input file extensions for this toolparameter and return a a list of them all'''
        # empty list passed to reduce is initializer, see reduce docs
        filetypes = self.accepted_filetypes.all()
        extensions = [ext.pattern for ext in reduce(lambda x, y: x + y, [list(ft.extensions.all()) for ft in filetypes], [])]
        return list(set(extensions))  # remove duplicates

    def input_filetype_extensions(self):
        '''Work out input file extensions for this toolparameter and return a a list of them all'''
        # empty list passed to reduce is initializer, see reduce docs
        filetypes = self.accepted_filetypes.all()
        extensions = [ext.pattern for ext in reduce(lambda x, y: x + y, [list(ft.extensions.all()) for ft in filetypes], [])]
        return list(set(extensions))  # remove duplicates

    @property
    def input_file(self):
        return self.file_assignment == 'batch' or self.file_assignment == 'all'


class ToolOutputExtension(Base):
    tool = models.ForeignKey(Tool)
    file_extension = models.ForeignKey(FileExtension)
    must_exist = models.NullBooleanField(default=False)  # TODO this field not currently in use
    must_be_larger_than = models.PositiveIntegerField(null=True, blank=True)  # TODO this field not currently in use

    def __unicode__(self):
        return "%s" % self.file_extension


class ToolGroup(Base):
    name = models.CharField(max_length=100, unique=True)

    def tools_str(self):
        tools_by_toolset = {}
        for tg in self.toolgrouping_set.all():
            tools = tools_by_toolset.setdefault(tg.tool_set, [])
            tools.append(tg.tool)
        return "<br/>".join([
            "%s: (%s)" % (set, ",".join(str(t) for t in tools))
            for (set, tools) in six.iteritems(tools_by_toolset)])

    tools_str.short_description = 'Tools in toolgroup, by toolset'
    tools_str.allow_tags = True

    def __unicode__(self):
        return self.name


class ToolGrouping(Base):
    tool = models.ForeignKey(Tool)
    tool_set = models.ForeignKey('ToolSet')
    tool_group = models.ForeignKey(ToolGroup)

    def __unicode__(self):
        return "Tool: %s, Toolset: %s and Toolgroup: %s" % (self.tool, self.tool_set, self.tool_set)


class ToolSet(Base):
    name = models.CharField(max_length=50, unique=True)
    users = models.ManyToManyField("User", related_name='users', db_table='yabi_user_toolsets', blank=True)

    def users_str(self):
        return ",".join([str(user) for user in self.users.all()])

    users_str.short_description = 'Users using toolset'

    def __unicode__(self):
        return self.name


class User(Base):

    class Meta:
        ordering = ("name",)

    name = models.CharField(max_length=50, unique=True)
    user = models.OneToOneField(DjangoUser, null=False)
    user_option_access = models.BooleanField(default=True)
    credential_access = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % self.user.username

    def reencrypt_user_credentials(self, request):
        logger.debug("")
        yabiuser = User.objects.get(name=request.user.username)

        currentPassword = request.POST['currentPassword']
        newPassword = request.POST['newPassword']

        # get all creds for this user that are encrypted
        creds = Credential.objects.filter(user=yabiuser)
        for cred in creds:
            cred.recrypt(currentPassword, newPassword)
            cred.save()

    def has_account_tab(self):
        logger.debug('')
        return self.user_option_access or self.credential_access

    def validate(self, request):
        logger.debug('')

        currentPassword = request.POST.get("currentPassword", None)
        newPassword = request.POST.get("newPassword", None)
        confirmPassword = request.POST.get("confirmPassword", None)

        # check the user is allowed to change password
        if not self.user_option_access:
            return (False, "You do not have permission to change the password.")

        # check we have everything
        if not currentPassword or not newPassword or not confirmPassword:
            return (False, "Either the current, new or confirmation password is missing from request.")

        # check the current password
        if not authenticate(username=request.user.username, password=currentPassword):
            return (False, "Current password is incorrect")

        # the new passwords should at least match and meet whatever rules we decide
        # to impose (currently a minimum six character length)
        if newPassword != confirmPassword:
            return (False, "The new passwords must match")

        if len(newPassword) < 6:
            return (False, "The new password must be at least 6 characters in length")

        return (True, "Password valid.")

    def toolsets_str(self):
        return ",".join([str(role) for role in self.users.all()])
    toolsets_str.short_description = 'Toolsets'

    @models.permalink
    def tools_url(self):
        return ('user_tools_view', (), {'user_id': self.id})

    @models.permalink
    def backends_url(self):
        return ('user_backends_view', (), {'user_id': self.id})

    def tools_link(self):
        return '<a href="%s">Tools</a>' % self.tools_url()
    tools_link.short_description = 'Tools'
    tools_link.allow_tags = True

    def backends_link(self):
        return '<a href="%s">Backends</a>' % self.backends_url()
    backends_link.short_description = 'Backends'
    backends_link.allow_tags = True

    @property
    def default_stageout(self):
        bec = BackendCredential.objects.get(credential__user=self, default_stageout=True)  # will raise a MultipleObjectsReturned exception if default_stageout not unique
        return bec.homedir_uri

    @property
    def default_stagein(self):
        return self.default_stageout + settings.DEFAULT_STAGEIN_DIRNAME


class CredentialAccess:
    """
    manage storage of protected credentials in the cache so they can be
    accessed by tasks
    """

    def __init__(self, credential):
        self.credential = credential

    @property
    def keyname(self):
        return cache_keyname("-cred-%s-%d" % (self.credential.user.name, self.credential.id))

    @property
    def in_cache(self):
        return self.keyname in cache

    def cache_protected_creds(self, protected_password, protected_cert, protected_key):
        key = self.keyname
        val = json.dumps({
            'password': protected_password,
            'cert': protected_cert,
            'key': protected_key
        })
        cache.set(key, val, settings.DEFAULT_CRED_CACHE_TIME)

    def get(self):
        """return the decrypted cert if available. Otherwise raise exception"""
        protected_creds_str = cache.get(self.keyname)
        if protected_creds_str is None:
            raise DecryptedCredentialNotAvailable("Credential for yabiuser: %s id: %s is not available in a decrypted form" % (self.credential.user.name, self.credential.id))
        protected_creds = json.loads(protected_creds_str)
        decrypt = lambda v: decrypt_annotated_block(v, settings.SECRET_KEY)
        return dict((t, decrypt(protected_creds[t])) for t in protected_creds)

    def clear_cache(self):
        cache.delete(self.keyname)


class Credential(Base):
    PLAINTEXT = 0
    PROTECTED = 1
    ENCRYPTED = 2
    SECURITYSTATE_CHOICES = (
        (PLAINTEXT, 'Plaintext'),
        (PROTECTED, 'Protected with secret key'),
        (ENCRYPTED, 'Encrypted with user password')
    )

    description = models.CharField(max_length=512, blank=True)
    # blank=True is set here because we infer the value on form submit in the admin
    security_state = models.PositiveSmallIntegerField(choices=SECURITYSTATE_CHOICES, default=0, blank=True)
    username = models.CharField(max_length=512)
    password = models.CharField(max_length=512, blank=True)
    cert = models.TextField(blank=True)
    key = models.TextField(blank=True)
    user = models.ForeignKey(User)
    backends = models.ManyToManyField('Backend', through='BackendCredential', null=True, blank=True)
    expires_on = models.DateTimeField(null=True)   # null mean never expire this

    username.help_text = "The username on the backend this credential is for."
    password.help_text = "Password for backend auth. Doesn't apply to all backends."
    cert.help_text = "Certificate for backend auth, if required."
    key.help_text = "Key for backend auth, if required."
    user.help_text = "Yabi username."

    def __unicode__(self):
        return "%s username:%s for yabiuser:%s" % (self.description, self.username, self.user.name)

    def on_pre_save(self):
        # security state is read-only in the admin; we validate the form to
        # make sure the data is consistent, but cross-check here and throw an
        # exception just in case
        #
        # we can't rewrite security_state in the form's clean method, as the
        # field is marked readonly, and so django discards any changes made to it
        crypto_values = [self.key, self.password, self.cert]
        # are any of the crypto_fields set to a non-empty, non-annotated-block value?
        have_unencrypted_field = any_unencrypted(*crypto_values)
        # are any of the crypto_fields set to a non-empty, annotated-block value?
        have_annotated_field = any_annotated_block(*crypto_values)
        assert(not (have_unencrypted_field and have_annotated_field),
               'Internal YABI error - unencrypted and annotated data mixed in Credential object %s' % str(self))
        # we never allow plaintext credentials to make it into the database
        if have_unencrypted_field:
            protect = lambda v: encrypt_to_annotated_block(v, settings.SECRET_KEY)
            self.password, self.cert, self.key = protect(self.password), protect(self.cert), protect(self.key)
            self.security_state = Credential.PROTECTED

    def on_post_save(self):
        if self.security_state == Credential.PROTECTED:
            # put these updated protected credentials into the cache
            access = self.get_credential_access()
            access.cache_protected_creds(self.password, self.cert, self.key)

    def encrypt_if_protected(self, username, password):
        "if we have are in protected credential state, move to encrypted state while we have username and password"
        if self.security_state == Credential.PROTECTED:
            protect_to_encrypt = lambda v: encrypt_to_annotated_block(decrypt_annotated_block(v, settings.SECRET_KEY), password)
            self.password, self.cert, self.key = protect_to_encrypt(self.password), protect_to_encrypt(self.cert), protect_to_encrypt(self.key)
            self.security_state = Credential.ENCRYPTED
            self.save()

    def on_login(self, username, password):
        """When a user logs in, convert protected credentials to encrypted credentials"""
        # reject plaintext creds (shouldn't be possible), encrypt protected creds
        if self.security_state == Credential.PLAINTEXT:
            raise DecryptException("credential is plaintext, should be unreachable")
        self.encrypt_if_protected(username, password)
        # we are now guaranteed to be encrypted; but we need to make sure there's protected creds in the cache
        encrypted_to_protected = lambda v: encrypt_to_annotated_block(decrypt_annotated_block(v, password), settings.SECRET_KEY)
        access = self.get_credential_access()
        access.cache_protected_creds(
            encrypted_to_protected(self.password),
            encrypted_to_protected(self.cert),
            encrypted_to_protected(self.key))
        # if the encrypted token is in legacy crypto, migrate it
        if any(encrypted_block_is_legacy(t) for t in (self.password, self.cert, self.key)):
            self.recrypt(password, password)

    def recrypt(self, oldkey, newkey):
        if self.security_state != Credential.ENCRYPTED:
            return
        recrypted = lambda v: encrypt_to_annotated_block(decrypt_annotated_block(v, oldkey), newkey)
        self.password, self.cert, self.key = recrypted(self.password), recrypted(self.cert), recrypted(self.key)
        self.save()

    def get_credential_access(self):
        access = CredentialAccess(self)
        if self.security_state == Credential.PROTECTED:
            access.cache_protected_creds(self.password, self.cert, self.key)
        return access

    CredentialData = namedtuple("CredentialData", "username, password, key")
    def get_decrypted(self):
        decrypted = self.get_credential_access().get()
        return self.CredentialData(self.username, decrypted['password'], decrypted['key'])

    def guess_backend_auth_class(self):
        """
        Return a probable backend auth type based on the backends
        associated with this credential.
        """
        backends = self.backends.annotate(scount=Count("scheme"))
        backends = backends.order_by("-scount", "created_on")[:1]
        scheme = backends[0].scheme if backends else ""

        # lookup scheme, return auth class
        from ..backend import BaseBackend
        cls = BaseBackend.get_backend_cls_for_scheme(scheme)
        return getattr(cls, "backend_auth", {}).get("class", "") if cls else ""

class Backend(Base):
    def __init__(self, *args, **kwargs):
        super(Backend, self).__init__(*args, **kwargs)
        scheme = self._meta.get_field_by_name("scheme")[0]
        from ..backend import BaseBackend
        scheme._choices = BaseBackend.get_scheme_choices()

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, blank=True)
    scheme = models.CharField(max_length=64)
    hostname = models.CharField(max_length=512)
    port = models.IntegerField(null=True, blank=True)
    path = models.CharField(max_length=512)
    lcopy_supported = models.BooleanField(default=True)
    link_supported = models.BooleanField(default=True)
    submission = models.TextField(blank=True)
    temporary_directory = models.CharField(max_length=512, blank=True)
    hostname.help_text = "Hostname must not end with a /."
    path.help_text = """Path must start and end with a /.<br/><br/>Execution backends must only have / in the path field.<br/><br/>
    For filesystem backends, Yabi will take the value in path and combine it with any path snippet in Backend Credential to form a URI. <br/>
    i.e. http://myserver.mydomain/home/ would be entered here and then on the Backend Credential for UserX you would enter <br/>
    their home directory in the User Directory field i.e. UserX/. This would then combine to form a valid URI: http://myserver.mydomain/home/UserX/"""
    lcopy_supported.help_text = "Backend supports 'cp' localised copies."
    link_supported.help_text = "Backend supports 'ln' localised symlinking."
    submission.help_text = "Mako script to be used to generate the submission script. (Variables: walltime, memory, cpus, working, modules, command, etc.)"
    temporary_directory.help_text = 'Only to be set on execution backends. Temporary directory used for temporary execution scripts. Blank means "/tmp".'

    @property
    def uri(self):
        netloc = self.hostname
        if self.port:
            netloc += ':%d' % self.port

        return urlunparse((self.scheme, netloc, self.path, '', '', ''))

    def __unicode__(self):
        return "%s - %s://%s:%s%s" % (self.name, self.scheme, self.hostname, self.port, self.path)

    @models.permalink
    def get_absolute_url(self):
        return ('backend_view', (), {'backend_id': str(self.id)})

class HostKey(Base):
    hostname = models.CharField(max_length=512)
    key_type = models.CharField(max_length=32, blank=False, null=False)
    fingerprint = models.CharField(max_length=64, blank=False, null=False)                # some SSH handshakes send a SSH "message" associated with the key
    data = models.TextField(max_length=16384, blank=False, null=False)
    allowed = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s hostkey for %s" % (self.key_type, self.hostname)

    def make_hash(self):
        """return the contents of this hostkey as a python dictionary"""
        return {
            'hostname': self.hostname,
            'key_type': self.key_type,
            'fingerprint': self.fingerprint,
            'data': self.data,
            'allowed': self.allowed
        }


class BackendCredential(Base):

    class Meta:
        verbose_name_plural = "Backend Credentials"

    backend = models.ForeignKey(Backend)
    credential = models.ForeignKey(Credential)
    homedir = models.CharField(max_length=512, blank=True, null=True, verbose_name="User Directory")
    visible = models.BooleanField()
    default_stageout = models.BooleanField()
    submission = models.TextField(blank=True)

    homedir.help_text = "This must not start with a / but must end with a /.<br/>This value will be combined with the Backend path field to create a valid URI."
    default_stageout.help_text = "There must be only one default_stageout per yabi user."
    submission.help_text = "Mako script to be used to generate a custom submission script. (Variables: walltime, memory, cpus, working, modules, command, etc.)"

    def __unicode__(self):
        return "BackendCredential %s %s" % (self.id, self.backend)

    def json(self):
        output = {
            'name': self.backend.name,
            'scheme': self.backend.scheme,
            'homedir': self.homedir_uri,
        }

        cred = self.credential                                  # TODO: check for expiry or non existence
        output.update({
            'credential': cred.description,
            'username': cred.username,
        })

        parts = cred.get()

        # refresh its time stamp
        cred.refresh_cache()

        # add in the decrypted cred parts
        output.update(parts)

        return json.dumps(output)

    @property
    def homedir_uri(self):
        """
        Returns full uri to the user's homedir
        """
        netloc = '%s@%s' % (self.credential.username, self.backend.hostname)
        if self.backend.port:
            netloc += ':%d' % self.backend.port

        uri = urlunparse((self.backend.scheme, netloc, self.backend.path, '', '', ''))

        if uri.endswith('/') and self.homedir.startswith('/'):
            uri = uri[:-1]

        return uri + self.homedir

    @property
    def uri(self):
        """
        Returns full uri
        """
        netloc = '%s@%s' % (self.credential.username, self.backend.hostname)
        if self.backend.port:
            netloc += ':%d' % self.backend.port

        uri = urlunparse((self.backend.scheme, netloc, self.backend.path, '', '', ''))

        return uri

    @models.permalink
    def test_url(self):
        return ('backend_cred_test_view', (), {'backend_cred_id': self.id})

    @models.permalink
    def edit_url(self):
        return ('admin:yabi_credential_change', (self.credential.id,))

    def backend_cred_test_link(self):
        return '<a href="%s">Test</a>' % self.test_url()

    backend_cred_test_link.short_description = 'Test Credential'
    backend_cred_test_link.allow_tags = True

    def backend_cred_edit_link(self):
        return '<a href="%s">Edit</a>' % self.edit_url()


class ModelBackendUserProfile(User):

    class Meta:
        proxy = True

    def change_password(self, request):
        logger.debug("passchange in ModelBackendUserProfile")
        currentPassword = request.POST.get("currentPassword", None)
        newPassword = request.POST.get("newPassword", None)

        assert currentPassword, "No currentPassword was found in the request."
        assert newPassword, "No newPassword was found in the request."

        (valid, message) = self.validate(request)
        if not valid:
            return (valid, message)

        try:
            self.user.set_password(newPassword)
            self.reencrypt_user_credentials(request)
            self.user.save()
            return (True, "Password successfully changed")
        except AttributeError as e:
            # Send back something fairly generic.
            logger.debug("Error changing password in database server: %s" % str(e))
            return (False, "Error changing password")


class LDAPBackendUserProfile(User):

    class Meta:
        proxy = True

    def change_password(self, request):
        logger.debug("passchange in LDAPBackendUserProfile")
        currentPassword = request.POST.get("currentPassword", None)
        newPassword = request.POST.get("newPassword", None)

        (valid, message) = self.validate(request)
        if not valid:
            return (valid, message)

        # if we manage to change the userpassword, then reencrypt the creds
        if ldaputils.set_ldap_password(self.user, currentPassword, newPassword):
            self.reencrypt_user_credentials(request)
            (status, message) = (True, 'Password successfully changed.')
        else:
            (status, message) = (False, 'Error changing password on LDAP server.')

        return (status, message)


class YabiCache(models.Model):
    """
    This model is here to make explicit the table created by running the command python manage.py createcachetable.
    It is used by django caching mechanism.
    """
    class Meta:
        db_table = 'yabi_cache'

    cache_key = models.CharField(max_length=255, unique=True, primary_key=True)
    value = models.TextField()
    expires = models.DateTimeField(db_index=True)


##
## Django Signals
##


def signal_credential_pre_save(sender, instance, **kwargs):
    instance.on_pre_save()


def signal_credential_post_save(sender, instance, **kwargs):
    instance.on_post_save()


def signal_tool_post_save(sender, **kwargs):
    try:
        tool = kwargs['instance']
        logger.debug("purging tool %s from cache" % str(tool))
        tool.purge_from_cache()
    except Exception as e:
        logger.critical(e)
        logger.critical(traceback.format_exc())
        raise


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        logger.debug('Creating user profile for %s' % instance.username)
        User.objects.create(user=instance, name=instance.username)


# connect up signals
from django.db.models.signals import post_save, pre_save
post_save.connect(signal_tool_post_save, sender=Tool, dispatch_uid="signal_tool_post_save")
post_save.connect(create_user_profile, sender=DjangoUser, dispatch_uid="create_user_profile")
pre_save.connect(signal_credential_pre_save, sender=Credential, dispatch_uid="signal_credential_pre_save")
post_save.connect(signal_credential_post_save, sender=Credential, dispatch_uid="signal_credential_post_save")
