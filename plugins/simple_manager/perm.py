from core import *
from core import _
import db
from .general_handler import *
import logging

logger = logging.getLogger('permission')

checkingset = set()

@cacheable
class Role:
    def __init__(self, name: str, param_names=None):
        assert_name(name)
        self.name = name
        if param_names is not None:
            self.config = {
                'param_names': param_names,
                'rules': []
            }
            self.persist()
        else:
            self.config = db.get_json(self.ident())
            assert(self.config is not None)
        self.num_params = len(self.config['param_names'])
    def ident(self):
        return join_ident([PermissionNS.name, self.name])
    def persist(self):
        db.put_json(self.ident(), self.config)
    def delete(self):
        self.config = None
        db.put(self.ident(), None)
        self.uncache()

    def assertion(self, ident, args=[]):        
        if not self.check(ident, args):
            raise PermissionError(f'{ident} ~ {self.name}{"<" + ", ".join(args) + ">" if len(args) > 0 else ""}')
    def check(self, ident, args=[]):
        assert_ident(ident)
        for arg in args:
            assert_ident(arg)
        assert(len(args) == self.num_params)

        logger.info(f'check {self.name} {args} {ident}')

        desc = f'{ident}~{self.name}<{",".join(args)}>'
        if desc in checkingset:
            return False
        checkingset.add(desc)
        try:
            for rule in self.config['rules']:
                passed = True
                entity = rule['entity']
                params = rule['params']
                constraints = rule['constraints']
                resolved = {}
                if entity.startswith('*'):
                    resolved[entity[1:]] = ident
                elif entity != ident:
                    continue
                for idx in range(0, len(params)):
                    if params[idx].startswith('*'):
                        k = params[idx][1:]
                        if k in resolved and resolved[k] != args[idx]:
                            passed = False
                            break
                        resolved[params[idx][1:]] = args[idx]
                    elif params[idx] != args[idx]:
                        passed = False
                        break
                if not passed:
                    continue
                for name in constraints:
                    if type(constraints[name]) is str:
                        if name in resolved and resolved[name] != constraints[name]:
                            passed = False
                            break
                        resolved[name] = constraints[name]
                if not passed:
                    continue
                for name in constraints:
                    if name not in resolved:
                        logger.warning(f'Unresolved name {name} in rule for role {self.name}')
                        passed = False
                        break
                if not passed:
                    continue
                for name in constraints:
                    rid = resolved[name]
                    con = constraints[name]
                    if type(con) is str:
                        passed = (con == rid)
                    else:
                        for role_info in con:
                            role_name, params1 = parse_role(role_info)
                            for i in range(len(params1)):
                                if params1[i].startswith('*'):
                                    params1[i] = resolved[params1[i][1:]]
                            role = query_object(f'permission:{role_name}')
                            if role is None or not role.check(rid, params1):
                                passed = False
                                break
                    if not passed:
                        break
                if passed:
                    logger.info(f'check passed {rule}')
                    return True
            return False
        finally:
            checkingset.remove(desc)

    # entity: ident or *name
    # params: [entity, ...]
    # constraints: {name: ident or [role, ...], ...}
    def assign(self, entity, params=[], constraints={}):
        assert(len(params) == self.num_params)
        def assert_entity(entity: str):
            if not entity.startswith('*'):
                assert_ident(entity)
        assert_entity(entity)
        for param in params:
            assert_entity(param)
        for con in constraints:
            if type(con) is str:
                assert_ident(con)
            else:
                for role_info in con:
                    role_name, ps = parse_role(role_info)
                    assert_name(role_name)
                    for param in ps:
                        assert_entity(param)
        self.config['rules'].append({
            'entity': entity,
            'params': params,
            'constraints': constraints
        })
        self.persist()
    def revoke(self, num):
        del(self.config['rules'][num])
        self.persist()
    def info(self):
        if type(self) is not Role:
            return 'Internal role'
        else:
            fname = self.name
            if self.num_params > 0:
                fname += f'<{", ".join(self.config["param_names"])}>'
            result = f'addrole {self.name}'
            num = 0
            for rule in self.config['rules']:
                sparams = f'<{", ".join(rule["params"])}>' if self.num_params > 0 else ""
                result += f'\n{num}: assign {self.name}{sparams} to {rule["entity"]}'
                if len(rule['constraints']) > 0:
                    result += ' where'
                    first = True
                    for name in rule['constraints']:
                        cons = rule['constraints'][name]
                        if not first:
                            result += ","
                        if type(cons) is str:
                            result += f' {name} = {cons}'
                        else:
                            result += f' {name} ~ {" + ".join(cons)}'
                        first = False
                num += 1
            return result

def parse_role(role_info: str):
    role_info = role_info.strip()
    ppos = role_info.find('<')
    if ppos != -1:
        assert(role_info[-1] == '>')
        role_name = role_info[:ppos].strip()
        params = [*map(str.strip, role_info[ppos+1:-1].split(','))]
    else:
        role_name = role_info
        params = []
    return role_name, params

class PermissionNS(GeneralHandler):
    name = 'permission'
    prompt = 'perm:'
    description = '''Permission Management
Part of Simple Manager (simple_manager)'''
    def instance():
        return _(PermissionNS.name)
    def query(self, ids):
        if len(ids) != 1:
            return None
        try:
            return Role(ids[0])
        except:
            return None
    def __init__(self):
        super().__init__()
        self.register(addrole, helpmsg='addrole Role<>')
        self.register(delrole, helpmsg='delrole Role')
        self.register(assign, helpmsg='assign Role<> to Entity [where Constraints]')
        self.register(revoke, helpmsg='revoke Role #')
        self.register(test, helpmsg='test Role<> to Entity')
        self.register(info, helpmsg='info Role')
    def exec(self, cmd: str):
        logger.info(f'execute: {cmd}')
        try:
            cmds = cmd.split(' ')
            if len(cmds) < 2:
                raise Exception('Bad command')
            if cmds[0] == 'addrole':
                role_info = ' '.join(cmds[1:])
                role_name, params = parse_role(role_info)
                assert_name(role_name)
                if query_object(join_ident([PermissionNS.name, role_name])) is not None:
                    raise Exception(f'Role {role_name} exists')
                Role(role_name, params)
                return True
            elif cmds[0] == 'delrole':
                assert_name(cmds[1])
                _(f'permission:{cmds[1]}').delete()
                return True
            elif cmds[0] == 'assign':
                crole = None
                centity = None
                ccons = None
                to_pos = cmds.index('to')
                where_pos = len(cmds)
                if 'where' in cmds:
                    where_pos = cmds.index('where')
                crole = ' '.join(cmds[1:to_pos]).strip()
                centity = ' '.join(cmds[to_pos+1:where_pos]).strip()
                ccons = ' '.join(cmds[where_pos+1:]).strip()
                role_name, params = parse_role(crole)
                entity = centity
                constraints = {}
                if len(ccons) > 0:
                    for cons in ccons.split(','):
                        if '=' in cons:
                            pos = cons.index('=')
                            name = cons[:pos].strip()
                            ident = cons[pos+1:].strip()
                            assert(name not in constraints)
                            constraints[name] = ident
                        elif '~' in cons:
                            pos = cons.index('~')
                            name = cons[:pos].strip()
                            roles = cons[pos+1:].split('+')
                            assert(name not in constraints)
                            constraints[name] = [*map(str.strip, roles)]
                        else:
                            raise Exception(f'Bad constraint {cons}')
                _(f'permission:{role_name}').assign(entity, params, constraints)
                return True
            elif cmds[0] == 'revoke':
                role = _(f'permission:{cmds[1]}').revoke(int(cmds[2]))
                return True
            elif cmds[0] == 'test':
                to_pos = cmds.index('to')
                crole = ' '.join(cmds[1:to_pos]).strip()
                centity = ' '.join(cmds[to_pos+1:]).strip()
                role_name, params = parse_role(crole)
                entity = centity
                return _(f'permission:{role_name}').check(entity, params)
            else:
                raise Exception('Bad command')
        except:
            logger.error(f'Fail to execute: {cmd}', exc_info=True)
            return False

def addrole(cmds, msg, chan):
    _('permission:SuperUser').assertion(msg['user'])
    cmd = 'addrole ' + ' '.join(cmds)
    return str(PermissionNS.instance().exec(cmd))

def delrole(cmds, msg, chan):
    _('permission:SuperUser').assertion(msg['user'])
    cmd = 'delrole ' + ' '.join(cmds)
    return str(PermissionNS.instance().exec(cmd))

def assign(cmds, msg, chan):
    _('permission:SuperUser').assertion(msg['user'])
    cmd = 'assign ' + ' '.join(cmds)
    return str(PermissionNS.instance().exec(cmd))

def revoke(cmds, msg, chan):
    _('permission:SuperUser').assertion(msg['user'])
    cmd = 'revoke ' + ' '.join(cmds)
    return str(PermissionNS.instance().exec(cmd))

def test(cmds, msg, chan):
    cmd = 'test ' + ' '.join(cmds)
    return str(PermissionNS.instance().exec(cmd))

def info(cmds, msg, chan):
    return _(f'permission:{cmds[0]}').info()

