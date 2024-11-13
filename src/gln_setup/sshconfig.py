from collections.abc import MutableMapping
from itertools import takewhile
from dataclasses import dataclass, field

@dataclass
class Line:
    """User responsiblity to strip whitespace, replaces '=' with ' ' and converts single quotes to double.

    This simplifies parsing and allows formatting decisions to be made of write.
    """
    text: str = ""

    @property
    def key(self) -> str:
        if self.__is_comment_or_blank:
            return None
        return text[:find(" ")]

    @property
    def value(self) -> str: #TODO: or list[str] for lists??
        if self.__is_comment_or_blank:
            return text
        return text[find(" "):]

    def __is_comment_or_blank(self) -> bool:
        return len(text) == 0 or text.starts_with("#")

    def __repr__(self):
        return text

        
@dataclass
class Section(MutableMapping):
    #The first line in the "host" line
    lines: list[Line] = field(default_factory = list)

    def __getitem__(self, key):
        for line in lines:
            if line.key == key:
                return line.value
        raise KeyError(key)
            
    def __setitem__(self, key, value):
        for i, line in enumerate(lines):
            if line.key == key:
                lines[i] = Line(f"{key} {value}")
                return
        lines.append(Line(f"{key} {value}"))

    def __delitem__(self, key):
        for i, line in enumerate(lines):
            if line.key == key:
                lines = lines[:i] + lines[i+1:]
                return
        raise KeyError(key)

    def __iter__(self):
        keys = set()
        for line in lines:
            if line.key:
                keys.add(line.key)
        return iter(keys)

    def __len__(self):
        return len(list(self.__iter__()))

    @property
    def host(self):
        return lines[0].value

    def __repr__(self):
        if len(lines) == 1:
            return str(lines[0])
        return '\n'.join(lines[0:1] + ["    " + str(line) for line in lines])
        

@dataclass
class SSHConfig(MutableMapping):
    sections: list[Section] = field(default_factory = list)
    preamble: list[Line] = field(default_factory = list)
    __keys: set[str] = field(default_factory = set, init = False)

    def __post_init__(self):
        for section in self.sections:
            self.__keys.add(section.host)

    def __getitem__(self, key) -> Section:
        if key not in self.__keys:
            raise KeyError(key)
        for section in self.sections:
            if section.host == key:
                return section
        raise KeyError(key)

    def __setitem__(self, key: str, value: Section) -> None:
        if key not in self.__keys:
            self.prepend(key, value)
            return
        self.replace(key, value)

    def __delitem__(self, key):
        if key not in self.__keys:
            raise KeyError(key)
        self.__keys.remove(key)
        self.sections = list(filter(lambda s:s.host != key, self.sections))

    def __iter__(self):
        return iter(self.__keys)

    def __len__(self) -> int:
        return len(self.__keys)

    def prepend(self, key:str, value: Section) -> None:
        self.sections = [value] + self.sections
        self.__keys.add(value.host)

    def append(self, key: str, value: Section) -> None:
        self.sections.append(value)
        self.__keys.add(value.host)

    def replace(self, key: str, value: Section) -> None:
        for i, section in enumerate(self.sections):
            if section.host == key:
                self.sections[i] == value
                return
        raise KeyError(key)

    def __repr__(self) -> str:
        return "\n".join([preamble] + [str(section) for section in sections])

def load(path: str) -> SSHConfig:
    if not path.expanduser().exists():
        return ""
    return loads(path.expanduser().read_text())

def loads(text: str) -> SSHConfig:
    sections = []
    lines = text.splitlines()
    preamble = list(takewhile(lambda x: __clean_line(x)[:5].lower() != "host ", lines))
    lines = lines[len(preamble):]
    current = []
    for line in lines:
        line = __clean_line(line)
        if line[:5].lower() == 'host ' and len(current) > 0:
            sections.append(Section(current))
            current = []
        current.append(line)
    return SSHConfig(sections, preamble)

def dump(config: SSHConfig, path: str) -> None:
    path.expanduser().write_text(dumps(config))

def dumps(config: SSHConfig) -> str:
    return str(config)
                
def __clean_line(text: str) -> str:
    return text.strip().replace("=", " ").replace("'", '"')
