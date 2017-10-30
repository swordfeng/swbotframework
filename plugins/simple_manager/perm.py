from core import *

def initialize():
    pass
def finalize():
    pass

class PermissionNS:
    pass

@cacheable
class Role:
    def query(ids):
        pass
    def __init__(self, role_name: str, num_params=0):
        assert_name(role_name)
        self.role_name = role_name
        self.num_params = num_params
    def ident(self):
        return join_ident(['perm', self.role_name])

'''
Generic (Parameterized) Roles
Users and usergroups
perm.check(userId, perm.role('channeladmin', chanId))
perm.check(chanId, perm.role('trustedchannel'))

Entity = Type
Role = Trait

role ChannelAdmin<C: Channel>
def_role(SuperUser) -> perm:SuperUser
def_role(Channel) -> perm:Channel
def_role(ChannelAdmin, role(Channel)) -> perm:ChannelAdmin
ChannelAdmin<c> -> perm:ChannelAdmin:1:c
assign ChannelAdmin<*c> to *swordfeng, swordfeng='', c: Channel
assign(c, role(Channel))
assign(u, role(SuperUser))
assign(*0, role(ChannelAdmin, *1), role(SuperUser), role(Channel))
assign<U: SuperUser, C: Channel> U to ChannelAdmin<C>

assign<U, C> ChannelUser<C> to U where U: ChannelAdmin<C>

assign PermissionEditor<P> to U

perm: assign ChannelAdmin<*xxx> to *yyy where *xxx=

'''

