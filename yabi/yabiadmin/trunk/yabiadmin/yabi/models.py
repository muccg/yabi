# -*- coding: utf-8 -*-
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
from django.db import models
from django import forms
from django.contrib.auth.models import User as DjangoUser
from django.utils import simplejson as json
from django.core import urlresolvers
from django.conf import settings
from urlparse import urlparse, urlunparse
from crypto import aes_enc_hex, aes_dec_hex

from django.contrib.memcache import KeyspacedMemcacheClient

from constants import STATUS_BLOCKED, STATUS_RESUME, STATUS_READY, STATUS_REWALK

DEBUG = False

class DecryptedCredentialNotAvailable(Exception): pass

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
    pattern = models.CharField(max_length=64, unique=True)
    
    def __unicode__(self):
        return self.pattern
        
    def extension(self):
        """try and express _only_ the extension from this glob. This is very naive.
        """
        return self.pattern.rsplit(".")[-1]

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
    
    # OBSOLETE
    #batch_on_param = models.ForeignKey('ToolParameter', related_name='batch_tool', null=True, blank=True)
    #batch_on_param_bundle_files = models.NullBooleanField(null=True, blank=True)
    
    cpus = models.CharField(max_length=64, null=True, blank=True)
    walltime = models.CharField(max_length=64, null=True, blank=True)
    module = models.TextField(null=True, blank=True)
    queue = models.CharField(max_length=50, default='normal', null=True, blank=True)
    max_memory = models.PositiveIntegerField(null=True, blank=True)
    job_type = models.CharField(max_length=40, default='single', null=True, blank=True)
    lcopy_supported = models.BooleanField(default=True)
    link_supported = models.BooleanField(default=True)

    name.help_text="Unique toolname for internal use."
    display_name.help_text="Tool name visible to users."
    path.help_text="The path to the binary for this file. Will normally just be binary name."
    description.help_text="The description that will be sent to the frontend for the user."
    enabled.help_text="Enable tool in frontend."
    backend.help_text="The execution backend for this tool."
    fs_backend.help_text="The filesystem backend for this tool."
    accepts_input.help_text="If checked, this tool will accept inputs from prior tools rather than presenting file select widgets."
    #batch_on_param.help_text="Specify switch that will be fed files in batch mode. i.e. -i in blast."
    module.help_text="Comma separated list of modules to load."
    lcopy_supported.help_text="If this tool should use local copies on supported backends where appropriate."
    link_supported.help_text="If this tool should use symlinks on supported backends where appropriate."
    
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
        extensions = [ext.extension() for ext in reduce(lambda x,y: x+y, [list(ft.extensions.all()) for ft in filetypes],[])]           # HACK: make frontend see old nonglob
        return list(set(extensions)) # remove duplicates

    def input_filetype_extensions_for_batch_param(self):
        '''
        This is used by the builder to determine the extensions than the batch_on_param parameter uses.
        '''
        extensions = []
        if self.batch_on_param:
            filetypes = self.batch_on_param.accepted_filetypes.all()
            extensions = [ext.extension() for ext in reduce(lambda x,y: x+y, [list(ft.extensions.all()) for ft in filetypes],[])]       # HACK: make frontend see old nonglob
        return list(set(extensions)) # remove duplicates

    def output_filetype_extensions(self):
        '''Work out output file extensions for this tool and return a a list of them all'''
        extensions = [fe.file_extension.extension() for fe in self.tooloutputextension_set.all()]                                       # HACK: make frontend see old nonglob
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
            #'batch_on_param':self.batch_on_param.switch if self.batch_on_param else '',
            #'batch_on_param_bundle_files':self.batch_on_param_bundle_files,
            'cpus':self.cpus,
            'walltime':self.walltime,
            'module':self.module,
            'queue':self.queue,
            'max_memory':self.max_memory,
            'job_type': self.job_type,
            'inputExtensions':self.input_filetype_extensions(),                     
            'outputExtensions': list(self.tooloutputextension_set.values("must_exist", "must_be_larger_than", "file_extension__pattern")),            
            'parameter_list': list(self.toolparameter_set.order_by('id').values("id", "rank", "mandatory", "hidden", "input_file", "output_file",
                                                                                "switch", "switch_use__display_text", "switch_use__formatstring","switch_use__description",
                                                                                "possible_values","default_value","helptext","batch_param", "batch_bundle_files", "use_output_filename__switch"))
            }
            
        for index in range(len(tool_dict['outputExtensions'])):
            tool_dict['outputExtensions'][index]['file_extension__pattern']=tool_dict['outputExtensions'][index]['file_extension__pattern'].rsplit('.')[-1]    # HACK. munge the glob so it looks oldschool so we dont need to rewrite the frontend

        for p in tool_dict["parameter_list"]:
            tp = ToolParameter.objects.get(id=p["id"])
            p["acceptedExtensionList"] = tp.input_filetype_extensions()        # HACK. munge the glob so it looks oldschool so we dont need to rewrite the frontend
            if tp.extension_param:
                p["extension_param"] = tp.extension_param.extension()                           # HACK. munge the glob so it looks oldschool so we dont need to rewrite the frontend
                
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
    switch = models.CharField(max_length=64)
    switch_use = models.ForeignKey(ParameterSwitchUse)
    rank = models.IntegerField(null=True, blank=True)
    mandatory = models.BooleanField(blank=True, default=False)
    hidden = models.BooleanField(blank=True, default=False)
    input_file = models.BooleanField(blank=True, default=False)
    output_file = models.BooleanField(blank=True, default=False)
    accepted_filetypes = models.ManyToManyField(FileType, blank=True)
    #use_batch_filename = models.BooleanField(default=False)
    extension_param = models.ForeignKey(FileExtension, null=True, blank=True)
    possible_values = models.TextField(null=True, blank=True)
    default_value = models.TextField(null=True, blank=True)
    helptext = models.TextField(null=True, blank=True)
    
    # this replaces the Tool level batch_on_param and batch_on_param_bundle_files
    batch_param = models.BooleanField(blank=False, null=False, default=False)
    batch_bundle_files = models.BooleanField(blank=False, null=False, default=False)
    
    # this foreign key points to the tool parameter (that is a batch_on_param) that we will derive the output filename for this switch from
    use_output_filename = models.ForeignKey('ToolParameter', null=True, blank=True)
    

    switch.help_text="The actual command line switch that should be passed to the tool i.e. -i or --input-file"
    switch_use.help_text="The way the switch should be combined with the value."
    rank.help_text="The order in which the switches should appear. Leave blank if order is unimportant."
    mandatory.help_text="Select if the switch is required as input."
    hidden.help_text="Select if the switch should be hidden from users in the frontend."
    input_file.help_text="Select if the switch takes a file as input from another tool."
    output_file.help_text="Select if the switch is specifying an output file."
    accepted_filetypes.help_text="The extensions of accepted filetypes for this switch."
    #use_batch_filename.help_text="If selected the tool will use the batch parameter file name as the basename of the output"
    extension_param.help_text="If an extension is selected then this extension will be appended to the filename. This should only be set for specifying output files."
    possible_values.help_text="Json snippet for html select. See blast tool for examples."
    default_value.help_text="Value that will appear in field. If possible values is populated this should match one of the values so the select widget defaults to that option."
    helptext.help_text="Help text that is passed to the frontend for display to the user."
    
    def __unicode__(self):
        return self.switch or ''

    def input_filetype_patterns(self):
        '''Work out input file extensions for this toolparameter and return a a list of them all'''
        # empty list passed to reduce is initializer, see reduce docs
        filetypes = self.accepted_filetypes.all()
        extensions = [ext.pattern for ext in reduce(lambda x,y: x+y, [list(ft.extensions.all()) for ft in filetypes],[])]
        return list(set(extensions)) # remove duplicates

    def input_filetype_extensions(self):
        '''Work out input file extensions for this toolparameter and return a a list of them all'''
        # empty list passed to reduce is initializer, see reduce docs
        filetypes = self.accepted_filetypes.all()
        extensions = [ext.extension() for ext in reduce(lambda x,y: x+y, [list(ft.extensions.all()) for ft in filetypes],[])]
        return list(set(extensions)) # remove duplicates


class ToolOutputExtension(Base):
    tool = models.ForeignKey(Tool)
    file_extension = models.ForeignKey(FileExtension)
    must_exist = models.NullBooleanField(default=False) #TODO this field not currently in use
    must_be_larger_than = models.PositiveIntegerField(null=True, blank=True) #TODO this field not currently in use

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

    @property
    def default_stagein(self):
        return self.default_stageout + settings.DEFAULT_STAGEIN_DIRNAME

class Credential(Base):
    description = models.CharField(max_length=512, blank=True)
    username = models.CharField(max_length=512)
    password = models.CharField(max_length=512, blank=True)
    cert = models.TextField(blank=True)
    key = models.TextField(blank=True)
    user = models.ForeignKey(User)
    backends = models.ManyToManyField('Backend', through='BackendCredential', null=True, blank=True)

    expires_on = models.DateTimeField( null=True )                      # null mean never expire this
    encrypted = models.BooleanField( null=False )
    encrypt_on_login = models.BooleanField( null=False, default=True )
    
    username.help_text="The username on the backend this credential is for."
    user.help_text="Yabi username."

    def __unicode__(self):
        if DEBUG:
            return "Credential <id=%s description=%s username=%s user=%s backends=%s>" % (self.id, self.description if len(self.description)<20 else self.description[:20], self.username, self.user.name, self.backends.all())
        return "Credential %s username:%s for yabiuser:%s"%(self.description,self.username,self.user.name)
    
    def encrypt(self, key):
        """Turn this unencrypted cred into an encrypted one using the supplied password"""
        assert self.encrypted == False
        
        self.password = aes_enc_hex(self.password,key)
        self.cert = aes_enc_hex(self.cert,key,linelength=80)
        self.key = aes_enc_hex(self.key,key,linelength=80)
        
        self.encrypted = True
        
    def decrypt(self, key):
        assert self.encrypted == True
        
        self.password = aes_dec_hex(self.password,key)
        self.cert = aes_dec_hex(self.cert,key)
        self.key = aes_dec_hex(self.key,key)
        
        self.encrypted = False
        
    def recrypt(self,oldkey,newkey):
        self.decrypt(oldkey)
        self.encrypt(newkey)
        
    def memcache_keyname(self):
        """return the memcache key for this credential"""
        return "-cred-%s-%d"%(self.user.name.encode("utf-8"),self.id)              # TODO: memcache keys dont support unicode. user.name may contain unicode
        
    def send_to_memcache(self, key="encryption key", memcache=None, time_to_cache=None ):
        """This method temporarily decypts the key and stores the decrypted key in memcache"""
        # set up defaults if they aren't set
        memcache = memcache or "localhost.localdomain"
        time_to_cache = time_to_cache or settings.DEFAULT_CRED_CACHE_TIME
        
        # make sure this is an encrypted cred, otherwise theres no point
        assert self.encrypted == True
        
        # decrypt the credential using the passed in password
        credential = {
            'password': aes_dec_hex(self.password,key),
            'cert': aes_dec_hex(self.cert,key),
            'key': aes_dec_hex(self.key,key)
        }
        
        mckey = self.memcache_keyname()
        mcval = json.dumps(credential)
        
        # push the credential to memcache server
        ksc = KeyspacedMemcacheClient()
        ksc.add(key=mckey, val=mcval, time=time_to_cache)
        ksc.disconnect_all()
        
        # unblock our blocked tasks
        self.unblock_all_blocked_tasks()
        
        # rewalk any of this users workflows that are marked for rewalking
        from yabiadmin.yabiengine.tasks import walk
        wfs=self.rewalk_workflows()
        ids = [W.id for W in wfs]
        wfs.update(status=STATUS_READY)
        for id in ids:
            print "WALK----------->",id
            walk.delay(workflow_id=id)
       
    def get(self):
        """return the decrypted cert if available. Otherwise raise exception"""
        if not self.encrypted:
            return dict([('username', self.username),
                    ('password', self.password),
                    ('cert', self.cert),
                    ('key', self.key)])
        
        if self.is_memcached():
            result = self.get_memcache()
            result['username']=self.username
            return result
            
        # encrypted but not cached. ERROR!
        raise DecryptedCredentialNotAvailable("Credential for yabiuser: %s id: %d is not available in a decrypted form"%(self.user.name, self.id))
        
    def is_memcached(self):
        """return true if there is a decypted cert in memcache"""
        kmc = KeyspacedMemcacheClient()
        truth = bool(kmc.get(self.memcache_keyname()))
        kmc.disconnect_all()
        return truth
        
    def get_memcache_json(self):
        """return the memcached credential"""
        kmc = KeyspacedMemcacheClient()
        truth = kmc.get(self.memcache_keyname())
        kmc.disconnect_all()
        return truth
        
    def get_memcache(self):
        """return the decoded memcached credentials"""
        return json.loads(self.get_memcache_json())
        
    def refresh_memcache(self, time_to_cache=None):
        """refresh the memcache version with a new timeout"""
        time_to_cache = time_to_cache or settings.DEFAULT_CRED_CACHE_TIME
        mc = KeyspacedMemcacheClient()
        name = self.memcache_keyname()
        cred = mc.get( name )
        assert cred, "tried to refresh a non-cached credential"
        mc.set(name, cred, time=time_to_cache)
        mc.disconnect_all()
        
    def clear_memcache(self):
        mc = KeyspacedMemcacheClient()
        name = self.memcache_keyname()
        mc.delete( name )
        mc.disconnect_all()
        
    @property
    def is_cached(self):
        return self.is_memcached()
        
    def blocked_tasks(self):
        """This looks at all the blocked tasks for the user this credential belongs to
        and returns a queryset of all the tasks in a blocked status for that user"""
        from yabiengine.models import Task
        return Task.objects.filter(job__workflow__user=self.user).filter(status=STATUS_BLOCKED)
        
    def rewalk_workflows(self):
        from yabiengine.models import Workflow
        return Workflow.objects.filter(user=self.user).filter(status=STATUS_REWALK)
                
    def unblock_all_blocked_tasks(self):
        """Set the status on all tasks blocked for this user to 'resume' so they can resume"""
        self.blocked_tasks().update(status=STATUS_RESUME)     
        
class Backend(Base):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, blank=True)
    scheme = models.CharField(max_length=64)
    hostname = models.CharField(max_length=512)
    port = models.IntegerField(null=True, blank=True)
    path = models.CharField(max_length=512)
    max_connections = models.IntegerField(null=True, blank=True)
    lcopy_supported = models.BooleanField(default=True)
    link_supported = models.BooleanField(default=True)


    scheme.help_text="Must be one of %s." % ", ".join(settings.VALID_SCHEMES)
    hostname.help_text="Hostname must not end with a /."
    path.help_text="Path must start and end with a /.<br/>Execution backends must only have / in the path field."
    max_connections.help_text="Backend connection limit. Does not affect front end immediate mode requests. Blank means no limit on the number of connections. '0' means no connections allowed (frozen)."
    lcopy_supported.help_text="Backend supports 'cp' localised copies."
    link_supported.help_text="Backend supports 'ln' localised symlinking."

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
            }
        
        cred = self.credential                                  # TODO: check for expiry or non existence
        output.update( {
            'credential':cred.description,
            'username':cred.username,
        })
        if cred.encrypted:
            # encrypted credential. Lets try and get the cached decrypted version
            
            if cred.is_memcached():
                # there is a plain credential available
                parts = cred.get_memcache()
                
                # refresh its time stamp
                cred.refresh_memcache()
                
                # add in the decrypted cred parts
                output.update(parts)
                
            else:
                # there is no plain credential available!
                raise DecryptedCredentialNotAvailable("Credential for yabiuser: %s id: %d is not available in a decrypted form"%(cred.user.name, cred.id))
        else:
            # credential is decrypted already. we can just return it
            output.update( {
                'password':self.credential.password,
                'cert':self.credential.cert,
                'key':self.credential.key
            } )
            
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
