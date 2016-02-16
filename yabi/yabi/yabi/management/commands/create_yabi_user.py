from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User as DjangoUser
from django.db import transaction
from mako.template import Template
from yabi.yabi.models import BackendCredential, Credential, User, ToolSet


class Command(BaseCommand):
    help = 'Creates a yabi user'

    def add_arguments(self, parser):
        parser.add_argument('username', help='The username of the new user')
        parser.add_argument('--email', help='The email address of the new user')
        parser.add_argument('--password', help='The password of the new user')
        parser.add_argument('--first-name', help='The first name of the new user')
        parser.add_argument('--last-name', help='The last name of the new user')
        parser.add_argument('--is-staff', default=None, action='store_true', help='Set if the new user should be a staff member')
        parser.add_argument('--is-superuser', default=None, action='store_true', help='Set if the new user should be a superuser')
        parser.add_argument('--is-active', default=None, action='store_true', help='Set if the new user should be active. Defaults to true.')
        parser.add_argument('--replicate-user', help="The username of an existing user who's tools and backnd credentials this user should also have")

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        if DjangoUser.objects.filter(username=username).exists():
            raise CommandError("Couldn't create user '%s'!\nUser with same username already exists." % username)
        skeleton_user = None
        if options['replicate_user']:
            try:
                skeleton_user = User.objects.get(name=options['replicate_user'])
            except User.DoesNotExist:
                raise CommandError("User '%s' doesn't exist" % options['replicate_user'])

        self.stdout.write("Creating user '%s'." % username)
        extra_arguments = {}
        for extra_arg in ('email', 'password', 'first_name', 'last_name'):
            if options[extra_arg]:
                extra_arguments[extra_arg] = options[extra_arg]

        try:
            new_user = DjangoUser.objects.create_user(username, **extra_arguments)
            handle_is_staff_and_is_superuser(new_user, options, skeleton_user)
            if skeleton_user is not None:
                replicate_other_user(skeleton_user, new_user.user)

        except Exception, e:
            raise CommandError("Couldn't create user '%s'!\n%s" % (username, e))

        self.stdout.write("Successfully created user '%s'." % username)


def handle_is_staff_and_is_superuser(new_user, options, skeleton_user):
    is_staff = options['is_staff']
    is_superuser = options['is_superuser']
    is_active = options['is_active']

    if skeleton_user is not None:
        if is_staff is None:
            is_staff = skeleton_user.user.is_staff
        if is_superuser is None:
            is_superuser = skeleton_user.user.is_superuser
        if is_active is None:
            is_active = skeleton_user.user.is_active

    if is_staff is not None:
        new_user.is_staff = is_staff
    if is_superuser is not None:
        new_user.is_superuser = is_superuser
    if is_active is not None:
        new_user.is_active = is_active
    if any((is_staff, is_superuser, is_active)):
        new_user.save()


def replicate_other_user(source_user, user):
    """Replicates toolsets and backends of the source_user into user.

    Passwords and keys of credentials are copied only if they are in the protected security
    state (encrypted with the SECRET_CODE).
    Most string fields can use the ${username} Mako variable to customise their value."""

    for toolset in ToolSet.objects.filter(users=source_user):
        toolset.users.add(user)
        toolset.save()

    def render(str):
        return Template(str).render(username=user.name)

    credentials = {}
    for cred in source_user.credential_set.all():
        new_user_cred = Credential.objects.create(
            description=render(cred.description),
            username=render(cred.username),
            user=user,
            expires_on=cred.expires_on)
        if cred.security_state == Credential.PROTECTED:
            new_user_cred.security_state = Credential.PROTECTED
            new_user_cred.password = cred.password
            new_user_cred.key = cred.key
            new_user_cred.save()
        credentials[cred.pk] = new_user_cred

    for bc in BackendCredential.objects.filter(credential__user=source_user):
        BackendCredential.objects.create(
            backend=bc.backend,
            credential=credentials[bc.credential.pk],
            homedir=render(bc.homedir),
            visible=bc.visible,
            default_stageout=bc.default_stageout,
            submission=render(bc.submission))
