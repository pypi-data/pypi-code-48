import io
import itertools as it
from pathlib import Path
import re

import pandas as pd


class Convert:
    type_dict = {'s': str, 'd': int, 'le': float}

    @classmethod
    def by_file_name(cls, f_name, **kwargs):
        if isinstance(f_name, str):
            f_name = Path(f_name)
        if f_name.name.lower() == 'trackone':
            return cls.trackone(f_name)
        else:
            return cls.tfs(f_name, **kwargs)

    @classmethod
    def tfs(cls, f_name, return_meta=False):
        """
        Convert table in TFS (Table File System) format to pandas data frame.
        
        Parameters
        ----------
        f_name : str
            File name pointing to the TFS file.
        return_meta : bool, optional
            If `True`, return meta information prefixed by "@ " in form of a `dict`.
            
        Returns
        -------
        df : pd.DataFrame
            The corresponding data frame. If `return_meta` then a tuple containing the data frame and
            the meta data in form of a `dict` is returned.
            
        Raises
        ------
        ValueError
            If the given table is incomplete or if it's not presented in TFS format.
        """
        with open(f_name) as fp:
            content = fp.read().split('\n')

        csv_content = filter(lambda x: x and not x.startswith(('@', '#')), content)
        col_names_str = next(csv_content)
        col_types_str = next(csv_content)

        if not col_names_str.startswith('* '):
            raise ValueError('Column names not found (indicated by "* ")')
        if not col_types_str.startswith('$ '):
            raise ValueError('Column types not found (indicated by "$ ")')

        col_names = re.findall('[A-Z0-9_.]+', col_names_str)
        col_types = re.findall('%(s|d|le)', col_types_str)
        col_types_map = {'s': str, 'd': int, 'le': float}
        columns = {n: col_types_map[t] for n, t in zip(col_names, col_types)}

        csv_content = map(cls._replace_characters, csv_content)
        csv_content = ','.join(col_names) + '\n' + '\n'.join(csv_content)

        df = pd.read_csv(io.StringIO(csv_content), index_col=None, dtype=columns)
        if return_meta:
            return df, dict(map(cls._parse_meta, it.takewhile(lambda x: x.startswith('@'), iter(content))))
        return df

    @classmethod
    def trackone(cls, f_name):
        """
        Convert "trackone" table (generated by ``TRACK, onetable = true``) to pandas data frame.

        Parameters
        ----------
        f_name : str
            File name pointing to the "trackone" file.

        Returns
        -------
        df : pd.DataFrame
            The corresponding data frame, augmented by two columns "PLACE" and "LABEL" indicating
            the observation place *number* and *label* respectively. The columns
            `[PLACE, LABEL, NUMBER, TURN]` are set as the data frame's index.
        """
        df = cls.tfs(f_name)

        with open(f_name) as fp:
            content = fp.read().split('\n')

        content = filter(lambda x: x and not x.startswith('@'), content)
        next(content)  # Column names.
        next(content)  # Column types.
        place_nrs = []
        place_labels = []
        nr = None
        label = None
        for line in content:
            if line.startswith('#segment'):
                __, nr, __, __, __, label = cls._replace_characters(line).split(',')
                continue
            place_nrs.append(nr)
            place_labels.append(label)

        return df.assign(PLACE=pd.Series(place_nrs, dtype=int), LABEL=place_labels) \
                 .set_index(['PLACE', 'LABEL', 'NUMBER', 'TURN'])

    @classmethod
    def _parse_meta(cls, x):
        m = re.match(r'^@ ([A-Z0-9_.]+)\s+%(\d{2,})?(s|le)\s+(.+)$', x)
        key, __, dtype, value = m.groups()
        if dtype == 's':
            value = value.strip('"')
        return key, cls.type_dict[dtype](value)

    @staticmethod
    def _replace_characters(s):
        s = re.sub(r'^\s+', '', s)
        s = re.sub(r'\s+$', '', s)
        s = re.sub(r'\s+', ',', s)
        return s
