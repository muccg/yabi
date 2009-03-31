from django.db import models

class ManyToManyField_NoSyncdb(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(ManyToManyField_NoSyncdb, self).__init__(*args, **kwargs)
        self.creates_table = False

class Base(models.Model):
    class Meta:
        abstract = True

    last_modified_by = models.CharField(blank=True, max_length=50, editable=False)
    last_modified_on = models.DateTimeField(blank=True, auto_now=True, editable=False)
    created_by = models.CharField(max_length=50, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)

class FileExtension(Base):
    name = models.CharField(max_length=10, unique=True)
    
    def __unicode__(self):
        return self.name

class FileType(Base):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    extensions = models.ManyToManyField(FileExtension)

    def __unicode__(self):
        return self.name

class ToolType(Base):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name

class Tool(Base):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    path = models.CharField(max_length=512, blank=True)
    description = models.TextField()
    enabled = models.BooleanField(default=True)
    type = models.ForeignKey(ToolType)
    groups = models.ManyToManyField("ToolGroup", through='ToolGrouping')
    output_filetypes = models.ManyToManyField(FileType, blank=True)
    output_must_exist = models.BooleanField(default=False)
    # I don't think this is required, it can be deduced from parameters
    # revise
    #input_required = models.BooleanField(default=False)

    def tool_groups_str(self):
        return ",".join(
            ["%s (%s)" % (tg.tool_group,tg.tool_set) 
                for tg in self.toolgrouping_set.all()
            ]
        )
    tool_groups_str.short_description = 'Belongs to Tool Groups'

    def __unicode__(self):
        return self.name

SWITCH_USE_CHOICES = (
    ('switchOnly', 'switch only'),
    ('valueOnly', 'value only'),
    ('both', 'both'),
    ('combined', 'combined'),
    ('none', 'none'),
)

class ToolParameter(Base):
    tool = models.ForeignKey(Tool)
    rank = models.IntegerField(blank=True)
    mandatory = models.BooleanField(blank=True, default=False)
    input_file = models.BooleanField(blank=True, default=False)
    output_file = models.BooleanField(blank=True, default=False)
    switch = models.CharField(blank=True, max_length=5, unique=True)
    switch_use = models.CharField(blank=True, max_length=20, choices=SWITCH_USE_CHOICES)
    accepted_filetypes = models.ManyToManyField(FileType, blank=True)
    input_extensions = models.ManyToManyField(FileExtension, blank=True, related_name='input_params')
    append_string = models.CharField(max_length=255, blank=True)
    source_param = models.ForeignKey('self', blank=True)

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

