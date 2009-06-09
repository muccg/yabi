from django.db import models
from django import forms
from django.contrib.auth.models import User as DjangoUser

class ManyToManyField_NoSyncdb(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(ManyToManyField_NoSyncdb, self).__init__(*args, **kwargs)
        self.creates_table = False

class Base(models.Model):
    class Meta:
        abstract = True

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

class ToolType(Base):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

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
    type = models.ForeignKey(ToolType)
    groups = models.ManyToManyField('ToolGroup', through='ToolGrouping', null=True, blank=True)
    output_filetypes = models.ManyToManyField(FileExtension, through='ToolOutputExtension', null=True, blank=True)
    file_pass_thru = models.BooleanField(default=False)
    batch_on_param = models.ForeignKey('ToolParameter', related_name='batch_tool', null=True, blank=True)
    batch_on_param_bundle_files = models.NullBooleanField(null=True, blank=True)

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


    def tool_dict(self):
        '''Gathers tool details into convenient dict for use by json or other models json'''
        return {
            'name':self.name,
            'display_name':self.display_name,
            'path':self.path,
            'description':self.description,
            'enabled':self.enabled,
            'file_pass_thru':self.file_pass_thru,
            'batch_on_param':self.batch_on_param.switch,
            'job_type': self.type.name,
            'output_filetypes': list(self.tooloutputextension_set.values("must_exist", "must_be_larger_than", "file_extension__extension")),
            'parameter_list': list(self.toolparameter_set.order_by('id').values("rank", "mandatory", "input_file", "output_file",
                                                                                "switch", "switch_use__display_text", "switch_use__value","switch_use__description",
                                                                                "filter_value", "filter__display_text", "filter__value","filter__description"))
            }

    def json(self):
        from django.utils import simplejson as json
        return json.dumps({'tool':self.tool_dict()})

    def __unicode__(self):
        return self.name

class ParameterSwitchUse(Base):
    display_text = models.CharField(max_length=30)
    value = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.display_text

class ParameterFilter(Base):
    display_text = models.CharField(max_length=30)
    value = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.display_text

class ToolParameter(Base):
    tool = models.ForeignKey(Tool)
    rank = models.IntegerField(null=True, blank=True)
    mandatory = models.BooleanField(blank=True, default=False)
    input_file = models.BooleanField(blank=True, default=False)
    output_file = models.BooleanField(blank=True, default=False)
    switch = models.CharField(max_length=25, null=True, blank=True)
    switch_use = models.ForeignKey(ParameterSwitchUse, null=True, blank=True)
    accepted_filetypes = models.ManyToManyField(FileType, blank=True)
    input_extensions = models.ManyToManyField(FileExtension, blank=True, related_name='input_params')
    filter = models.ForeignKey(ParameterFilter, null=True, blank=True)
    filter_value = models.CharField(max_length=50, null=True, blank=True)
    source_param = models.ForeignKey('self', related_name='source_parent', null=True, blank=True)
    extension_param = models.ForeignKey('self', related_name='extension_parent', null=True, blank=True)

    def __unicode__(self):
        return self.switch or ''

class ToolRslInfo(Base):
    executable = models.CharField(max_length=50)
    count = models.PositiveIntegerField()
    queue = models.CharField(max_length=50, default='normal')
    max_wall_time = models.PositiveIntegerField()
    max_memory = models.PositiveIntegerField()
    job_type = models.CharField(max_length=40, default='single')
    tool = models.OneToOneField(Tool)

    def tool_name(self):
        return self.tool.name

class ToolRslExtensionModule(Base):
    tool_rsl = models.ForeignKey(ToolRslInfo)
    name = models.CharField(max_length=50)

class ToolRslArgumentOrder(Base):
    tool_rsl = models.ForeignKey(ToolRslInfo)
    name = models.CharField(max_length=50)
    rank = models.PositiveIntegerField(null=True, blank=True)

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
    users = ManyToManyField_NoSyncdb("User", related_name='users', db_table='yabmin_user_toolsets', blank=True)

    def users_str(self):
        return ",".join([str(user) for user in self.users.all()])
    users_str.short_description = 'Users using toolset'

    def __unicode__(self):
        return self.name

class User(Base):
    name = models.CharField(max_length=50, unique=True)
    toolsets = models.ManyToManyField("ToolSet", related_name='toolsets', db_table='yabmin_user_toolsets', blank=True)

    def toolsets_str(self):
        return ",".join([str(role) for role in self.toolsets.all()])
    toolsets_str.short_description = 'Toolsets'

    @models.permalink
    def tools_url(self):
        return ('user_tools_view', (), {'user_id': self.id})

    def tools_link(self):
        return '<a href="%s">See tools</a>' % self.tools_url()
    tools_link.short_description = 'See tools'
    tools_link.allow_tags = True

    def __unicode__(self):
        return self.name

class Credential(Base):
    description = models.CharField(max_length=512, blank=True)
    username = models.CharField(max_length=512, blank=True)
    password = models.CharField(max_length=512, blank=True)
    cert = models.TextField(null=True, blank=True)
    key = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return "%s %s" % (self.description, self.user)

class Backend(Base):
    name = models.CharField(max_length=255)
    credential = models.ForeignKey(Credential)

    def __unicode__(self):
        return self.name

    def json(self):

        from django.utils import simplejson as json

        output = {
            'backend':self.name,
            'credential':self.credential.description,
            'username':self.credential.username,
            'password':self.credential.password,
            'cert':self.credential.cert,
            'key':self.credential.key
            }
        
        return json.dumps(output)

        
class Status(models.Model):
    class Meta:
        db_table = 'status'

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True)

class Workflow(models.Model):
    class Meta:
        db_table = 'workflow'

    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    status = models.ForeignKey(Status)
    log_file_path = models.CharField(max_length=1000,null=True)
    last_modified_on = models.DateTimeField(null=True, auto_now=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return self.name

class Job(models.Model):
    class Meta:
        db_table = 'job'

    workflow = models.ForeignKey(Workflow)
    order = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    status = models.ForeignKey(Status)
    work_dir = models.CharField(max_length=1000)

class Subjob(models.Model):
    class Meta:
        db_table = 'subjob'

    job = models.ForeignKey(Job)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    status = models.ForeignKey(Status)
    job_identifier = models.TextField()
    error_msg = models.CharField(max_length=1000, null=True)

class SubjobParameter(models.Model):
    class Meta:
        db_table = 'subjob_parameter'

    subjob = models.ForeignKey(Subjob)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=512)

class JobParameter(models.Model):
    class Meta:
        db_table = 'job_parameter'

    job = models.ForeignKey(Job, related_name='parameters')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=512, null=True)
    source_job = models.ForeignKey(Job, related_name='ref_params', null=True) 

class QueueBase(models.Model):
    class Meta:
        abstract = True

    workflow = models.ForeignKey(Workflow) 
    created_on = models.DateTimeField(auto_now_add=True)

    def name(self):
        return self.workflow.name

    def user_name(self):
        return self.workflow.user.name

class QueuedWorkflow(QueueBase):
    class Meta:
        db_table = 'queue'

class InProgressWorkflow(QueueBase):
    class Meta:
        db_table = 'in_progress'

