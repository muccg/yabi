# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User as DjangoUser
from django.utils import simplejson as json
from django.core import urlresolvers
from django.conf import settings
from urlparse import urlparse, urlunparse


DEBUG = False

import logging
logger = logging.getLogger('yabiadmin')

class ManyToManyField_NoSyncdb(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(ManyToManyField_NoSyncdb, self).__init__(*args, **kwargs)
        self.creates_table = False

class Base(models.Model):
    """
    comment
    """
    
    '''
    comment
    '''
    
    
    class Meta:
        abstract = True

        # now do this
        

    last_modified_by = models.ForeignKey(DjangoUser, editable=False, related_name="%(class)s_modifiers", null=True)
    last_modified_on = models.DateTimeField(null=True, auto_now=True, editable=False)
    created_by = models.ForeignKey(DjangoUser, editable=False, related_name="%(class)s_creators",null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)

class FileExtension(Base):
    extension = models.CharField(max_length=10, unique=True)
    
    def __unicode__(self):
        return self.extension

class FileType(Base):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    extensions = models.ManyToManyField(FileExtension, null=True, blank=True)

    def __unicode__(self):
        return self.name

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
    batch_on_param = models.ForeignKey('ToolParameter', related_name='batch_tool', null=True, blank=True)
    batch_on_param_bundle_files = models.NullBooleanField(null=True, blank=True)
    cpus = models.CharField(max_length=64, null=True, blank=True)
    walltime = models.CharField(max_length=64, null=True, blank=True)
    module = models.TextField(null=True, blank=True)
    queue = models.CharField(max_length=50, default='normal', null=True, blank=True)
    max_memory = models.PositiveIntegerField(null=True, blank=True)
    job_type = models.CharField(max_length=40, default='single', null=True, blank=True)


    name.help_text="Unique toolname for internal use."
    display_name.help_text="Tool name visible to users."
    path.help_text="The path to the binary for this file. Will normally just be binary name."
    description.help_text="The description that will be sent to the frontend for the user."
    enabled.help_text="Enable tool in frontend."
    backend.help_text="The execution backend for this tool."
    fs_backend.help_text="The filesystem backend for this tool."
    accepts_input.help_text="Check the effect of this."
    batch_on_param.help_text="Specify switch that will be fed files in batch mode. i.e. -i in blast."
    module.help_text="Comma separated list of modules to load."
    
    def tool_groups_str(self):
        return ",".join(
            ["%s (%s)" % (tg.tool_group,tg.tool_set) 
                for tg in self.toolgrouping_set.all()
            ]
        )
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
        filetypes = reduce(lambda x, y: x+y, [list(x.accepted_filetypes.all()) for x in self.toolparameter_set.all()],[])
        extensions = [ext.extension for ext in reduce(lambda x,y: x+y, [list(ft.extensions.all()) for ft in filetypes],[])]
        return list(set(extensions)) # remove duplicates

    def input_filetype_extensions_for_batch_param(self):
        '''
        This is used by the builder to determine the extensions than the batch_on_param parameter uses.
        '''
        extensions = []
        if self.batch_on_param:
            filetypes = self.batch_on_param.accepted_filetypes.all()
            extensions = [ext.extension for ext in reduce(lambda x,y: x+y, [list(ft.extensions.all()) for ft in filetypes],[])]
        return list(set(extensions)) # remove duplicates

    def output_filetype_extensions(self):
        '''Work out output file extensions for this tool and return a a list of them all'''
        extensions = [fe.file_extension.extension for fe in self.tooloutputextension_set.all()]
        return list(set(extensions)) # remove duplicates

    def tool_dict(self):
        '''Gathers tool details into convenient dict for use by json or other models json'''

        tool_dict = {
            'name':self.name,
            'display_name':self.display_name,
            'path':self.path,
            'description':self.description,
            'enabled':self.enabled,
            'backend':self.backend.name,
            'fs_backend':self.fs_backend.name,            
            'accepts_input':self.accepts_input,
            'batch_on_param':self.batch_on_param.switch if self.batch_on_param else '',
            'batch_on_param_bundle_files':self.batch_on_param_bundle_files,
            'cpus':self.cpus,
            'walltime':self.walltime,
            'module':self.module,
            'queue':self.queue,
            'max_memory':self.max_memory,
            'job_type': self.job_type,
            'inputExtensions': self.input_filetype_extensions(),
            'outputExtensions': list(self.tooloutputextension_set.values("must_exist", "must_be_larger_than", "file_extension__extension")),            
            'parameter_list': list(self.toolparameter_set.order_by('id').values("id", "rank", "mandatory", "input_file", "output_file",
                                                                                "switch", "switch_use__display_text", "switch_use__formatstring","switch_use__description",
                                                                                "possible_values","default_value","helptext"))
            }

        for p in tool_dict["parameter_list"]:
            tp = ToolParameter.objects.get(id=p["id"])
            p["acceptedExtensionList"] = tp.input_filetype_extensions()
            if tp.source_param:
                p["source_param"] = tp.source_param.switch
            if tp.extension_param:
                p["extension_param"] = tp.extension_param.switch
        return tool_dict
    
    def json(self):

        # the possible_values field has json in it so we need to make it decode
        # or it will be double encoded
        output = self.tool_dict()

        for plist in output["parameter_list"]:
            if "possible_values" in plist and plist["possible_values"]:
                plist["possible_values"] = json.loads(plist["possible_values"])

        return json.dumps({'tool':output})

    def json_pretty(self):

        # the possible_values field has json in it so we need to make it decode
        # or it will be double encoded
        output = self.tool_dict()

        for plist in output["parameter_list"]:
            if "possible_values" in plist and plist["possible_values"]:
                plist["possible_values"] = json.loads(plist["possible_values"])

        return json.dumps({'tool':output}, indent=4)


    def __unicode__(self):
        return self.name

class ParameterSwitchUse(Base):
    display_text = models.CharField(max_length=30)
    formatstring = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    formatstring.help_text="Example: %(switch)s %(value)s"

    def __unicode__(self):
        return self.display_text

class ToolParameter(Base):
    tool = models.ForeignKey(Tool)
    switch = models.CharField(max_length=64, null=True, blank=True)
    switch_use = models.ForeignKey(ParameterSwitchUse, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    mandatory = models.BooleanField(blank=True, default=False)
    input_file = models.BooleanField(blank=True, default=False)
    output_file = models.BooleanField(blank=True, default=False)
    accepted_filetypes = models.ManyToManyField(FileType, blank=True)
    source_param = models.ForeignKey('self', related_name='source_parent', null=True, blank=True)
    extension_param = models.ForeignKey('self', related_name='extension_parent', null=True, blank=True)
    possible_values = models.TextField(null=True, blank=True)
    default_value = models.TextField(null=True, blank=True)
    helptext = models.TextField(null=True, blank=True)    

    switch.help_text="The actual command line switch that should be passed to the tool i.e. -i or --input-file"
    switch_use.help_text="The way the switch should be combined with the value."
    rank.help_text="The order in which the switches should appear. Leave blank if order is unimportant."
    mandatory.help_text="Select if the switch is required as input."
    input_file.help_text="Select if the switch takes a file as input from another tool."
    output_file.help_text="Select if the switch is specifying an output file."
    accepted_filetypes.help_text="The extensions of accepted filetypes for this switch."
    source_param.help_text="Unused. Could be used again for appending and extension to the end of a input file. This switch would then refer to a file specified at another switch."
    extension_param.help_text="Unused. Need to find what this is for."
    possible_values.help_text="Json snippet for html select. See blast tool for examples."
    default_value.help_text="Value that will appear in field. If possible values is populated this should match one of the values so the select widget defaults to that option."
    helptext.help_text="Help text that is passed to the frontend for display to the user."
    
    def __unicode__(self):
        return self.switch or ''

    def input_filetype_extensions(self):
        '''Work out input file extensions for this toolparameter and return a a list of them all'''
        # empty list passed to reduce is initializer, see reduce docs
        filetypes = self.accepted_filetypes.all()
        extensions = [ext.extension for ext in reduce(lambda x,y: x+y, [list(ft.extensions.all()) for ft in filetypes],[])]
        return list(set(extensions)) # remove duplicates

class ToolOutputExtension(Base):
    tool = models.ForeignKey(Tool)
    file_extension = models.ForeignKey(FileExtension)
    must_exist = models.NullBooleanField(default=False)
    must_be_larger_than = models.PositiveIntegerField(null=True, blank=True)

class ToolGroup(Base):
    name = models.CharField(max_length=100, unique=True)

    def tools_str(self):
        tools_by_toolset = {}
        for tg in self.toolgrouping_set.all():
           tools = tools_by_toolset.setdefault(tg.tool_set, [])
           tools.append(tg.tool) 
        return "<br/>".join([
            "%s: (%s)" % (set, ",".join(str(t) for t in tools)) 
                                for (set, tools) in tools_by_toolset.iteritems() ]) 
    tools_str.short_description = 'Tools in toolgroup, by toolset'
    tools_str.allow_tags = True

    def __unicode__(self):
        return self.name

class ToolGrouping(Base):
    tool = models.ForeignKey(Tool)
    tool_set = models.ForeignKey('ToolSet')
    tool_group = models.ForeignKey(ToolGroup)

class ToolSet(Base):
    name = models.CharField(max_length=50, unique=True)
    users = ManyToManyField_NoSyncdb("User", related_name='users', db_table='yabi_user_toolsets', blank=True)

    def users_str(self):
        return ",".join([str(user) for user in self.users.all()])
    users_str.short_description = 'Users using toolset'

    def __unicode__(self):
        return self.name

class User(Base):
    name = models.CharField(max_length=50, unique=True)
    toolsets = models.ManyToManyField("ToolSet", related_name='toolsets', db_table='yabi_user_toolsets', blank=True)

    def toolsets_str(self):
        return ",".join([str(role) for role in self.toolsets.all()])
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


    def __unicode__(self):
        return self.name

    @property
    def default_stageout(self):
        bec = BackendCredential.objects.get(credential__user=self, default_stageout=True) # will raise a MultipleObjectsReturned exception if default_stageout not unique
        return bec.homedir_uri

class Credential(Base):
    description = models.CharField(max_length=512, blank=True)
    username = models.CharField(max_length=512)
    password = models.CharField(max_length=512, blank=True)
    cert = models.TextField(null=True, blank=True)
    key = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User)
    backends = models.ManyToManyField('Backend', through='BackendCredential', null=True, blank=True)

    username.help_text="The username on the backend this credential is for."
    user.help_text="Yabi username."

    def __unicode__(self):
        if DEBUG:
            return "Credential <id=%s description=%s username=%s user=%s backends=%s>" % (self.id, self.description if len(self.description)<20 else self.description[:20], self.username, self.user.name, self.backends.all())
        return "Credential %s username:%s for yabiuser:%s"%(self.description,self.username,self.user.name)

class Backend(Base):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, blank=True)
    scheme = models.CharField(max_length=64)
    hostname = models.CharField(max_length=512)
    port = models.IntegerField(null=True, blank=True)
    path = models.CharField(max_length=512)

    scheme.help_text="Must be one of %s." % ", ".join(settings.VALID_SCHEMES)
    hostname.help_text="Hostname must not end with a /."
    path.help_text="Path must start and end with a /.<br/>Execution backends must only have / in the path field."




    @property
    def uri(self):
        netloc = self.hostname
        if self.port:
            netloc += ':%d' % self.port

        return urlunparse((self.scheme, netloc, self.path, '', '', ''))

    def __unicode__(self):
        if DEBUG:
            return "Backend <%s name=%s scheme=%s hostname=%s port=%s path=%s>"%(self.id, self.name,self.scheme,self.hostname,self.port,self.path)
        return "Backend %s %s %s://%s:%s%s"%(self.name, self.description,self.scheme,self.hostname,self.port,self.path)


    @models.permalink
    def get_absolute_url(self):
        return ('backend_view', (), {'backend_id': str(self.id)})


    def backend_summary_link(self):
        return '<a href="%s">View</a>' % self.get_absolute_url()
    backend_summary_link.short_description = 'Summary'
    backend_summary_link.allow_tags = True



class BackendCredential(Base):
    class Meta:
        verbose_name_plural = "Backend Credentials"

    backend = models.ForeignKey(Backend)
    credential = models.ForeignKey(Credential)
    homedir = models.CharField(max_length=512, blank=True, null=True)
    visible = models.BooleanField()                                                         # ALTER TABLE "admin_backendcredential" ADD "visible" boolean NOT NULL default False;
    default_stageout = models.BooleanField()                                                         # ALTER TABLE "admin_backendcredential" ADD "visible" boolean NOT NULL default False;

    homedir.help_text="Homedir must not start with a / but must end with a /."
    default_stageout.help_text="There must be only one default_stageout per yabi user."
    
    def __unicode__(self):
        if DEBUG:
            return "BackendCredential <%s backend.id=%s credential.id=%s homedir=%s visbile=%s>"%(self.id,self.backend.id,self.credential.id,self.homedir,str(self.visible))
        return "BackendCredential %s"%(self.id)

    def json(self):
        output = {
            'name':self.backend.name,
            'scheme':self.backend.scheme,
            'homedir':self.homedir_uri,
            'credential':self.credential.description,
            'username':self.credential.username,
            'password':self.credential.password,
            'cert':self.credential.cert,
            'key':self.credential.key
            }
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
    backend_cred_test_link.short_description = 'Test Credential'
    backend_cred_test_link.allow_tags = True
