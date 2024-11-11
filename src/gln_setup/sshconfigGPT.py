from collections.abc import MutableMapping
from collections import OrderedDict
import re

class Line:
    def __init__(self, text):
        self.text = text

class CommentLine(Line):
    pass

class BlankLine(Line):
    pass

class HostLine(Line):
    def __init__(self, text, hosts):
        super().__init__(text)
        self.hosts = hosts  # List of host names

class OptionLine(Line):
    def __init__(self, text, key, value):
        super().__init__(text)
        self.key = key
        self.value = value

class Section:
    def __init__(self):
        self.lines = []

class HostSection(Section):
    def __init__(self, hosts):
        super().__init__()
        self.hosts = hosts  # List of host names

class GlobalSection(Section):
    pass

class SSHConfig(MutableMapping):
    def __init__(self, filename=None):
        self.sections = []
        self.host_map = OrderedDict()  # Map host names to HostSection objects
        if filename:
            self.read(filename)

    def __getitem__(self, key):
        section = self.host_map.get(key)
        if section:
            # Return options as a dictionary
            return self._get_options_from_section(section)
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if key in self.host_map:
            # Update existing host
            section = self.host_map[key]
            self._set_options_in_section(section, value)
        else:
            # Add new host
            self.add_host(key, value)

    def __delitem__(self, key):
        section = self.host_map.get(key)
        if section:
            self.sections.remove(section)
            # Remove host from host_map and other sections that share the same hosts
            for host in section.hosts:
                del self.host_map[host]
        else:
            raise KeyError(key)

    def __iter__(self):
        return iter(self.host_map)

    def __len__(self):
        return len(self.host_map)

    def _get_options_from_section(self, section):
        options = OrderedDict()
        for line in section.lines:
            if isinstance(line, OptionLine):
                options[line.key] = line.value
        return options

    def _set_options_in_section(self, section, options):
        # Remove existing OptionLines
        section.lines = [line for line in section.lines if not isinstance(line, OptionLine)]
        # Add new OptionLines
        for key, value in options.items():
            option_text = f'    {key} {value}'
            line = OptionLine(option_text, key, value)
            section.lines.append(line)

    def read(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

        host_pattern = re.compile(r'^\s*Host\s+(.*)$', re.IGNORECASE)
        option_pattern = re.compile(r'^\s*(\S+)\s+(.*)$')
        current_section = GlobalSection()
        self.sections.append(current_section)

        for line_text in lines:
            stripped_line = line_text.strip('\n')
            if not stripped_line.strip():
                line = BlankLine(stripped_line)
                current_section.lines.append(line)
                continue
            if stripped_line.strip().startswith('#'):
                line = CommentLine(stripped_line)
                current_section.lines.append(line)
                continue
            host_match = host_pattern.match(stripped_line)
            if host_match:
                host_line_text = stripped_line
                host_line_hosts = host_match.group(1).strip().split()
                host_line = HostLine(host_line_text, host_line_hosts)
                current_section = HostSection(host_line_hosts)
                current_section.lines.append(host_line)
                self.sections.append(current_section)
                for host in host_line_hosts:
                    self.host_map[host] = current_section
                continue
            option_match = option_pattern.match(stripped_line)
            if option_match:
                key, value = option_match.groups()
                option_line = OptionLine(stripped_line, key, value)
                current_section.lines.append(option_line)
            else:
                # Unrecognized line
                line = Line(stripped_line)
                current_section.lines.append(line)

    def write(self, filename):
        with open(filename, 'w') as f:
            for section in self.sections:
                for line in section.lines:
                    f.write(line.text + '\n')

    def add_host(self, host_name, options=None):
        """Add a new host configuration."""
        if options is None:
            options = OrderedDict()
        host_line_text = f'Host {host_name}'
        host_line = HostLine(host_line_text, [host_name])
        section = HostSection([host_name])
        section.lines.append(host_line)
        for key, value in options.items():
            option_text = f'    {key} {value}'
            option_line = OptionLine(option_text, key, value)
            section.lines.append(option_line)
        self.sections.append(section)
        self.host_map[host_name] = section

    def set_option(self, host_name, option_key, option_value):
        """Set an option for a given host."""
        if host_name not in self.host_map:
            # Host does not exist, create it
            self.add_host(host_name)
        section = self.host_map[host_name]
        # Check if the option already exists
        for line in section.lines:
            if isinstance(line, OptionLine) and line.key == option_key:
                # Update existing option
                line.value = option_value
                line.text = f'    {option_key} {option_value}'
                return
        # Add new option
        option_text = f'    {option_key} {option_value}'
        option_line = OptionLine(option_text, option_key, option_value)
        section.lines.append(option_line)

    def get_option(self, host_name, option_key):
        """Get an option value for a given host."""
        section = self.host_map.get(host_name)
        if section:
            for line in section.lines:
                if isinstance(line, OptionLine) and line.key == option_key:
                    return line.value
        return None

    def remove_option(self, host_name, option_key):
        """Remove an option from a given host."""
        section = self.host_map.get(host_name)
        if section:
            section.lines = [line for line in section.lines if not (isinstance(line, OptionLine) and line.key == option_key)]

    def remove_host(self, host_name):
        """Remove a host configuration."""
        section = self.host_map.get(host_name)
        if section:
            self.sections.remove(section)
            for host in section.hosts:
                del self.host_map[host]

