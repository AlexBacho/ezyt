class BaseConfig:
    def __init__(self):
        pass

    def __str__(self):
        return str(self.__dict__)
    
    def __repr_(self):
        return str(self)


class Config(BaseConfig):
    def __init__(self, config_path):
        self.common = BaseConfig()
        self._init_from_file(config_path)
    
    def __str__(self):
        cfg = [ f'{str(k)}: {str(v)}' for k, v in self.__dict__.items() ]
        return '{'  + ', '.join(cfg) + '}'

    def _init_from_file(self, config_path):
        with open(config_path) as f:
            submodule = 'common'
            for line in f:
                if sub := _submodule_in_line(line):
                    self.__dict__[sub] = BaseConfig()
                    submodule = sub
                elif _valid_cfg_line(line):
                    key, value = line.split('=', maxsplit=1)
                    self.__dict__[submodule].__dict__[key] = value.strip()

def _submodule_in_line(line):
    line = line.strip()
    if line.startswith('[[') and line.endswith(']]'):
        submodule = line[2:-2]
        if not submodule:
            raise('Empty submodule in config file.')
        return submodule
    return False


def _valid_cfg_line(line):
    return '=' in line and line.index('=') not in (0, len(line)-1)
