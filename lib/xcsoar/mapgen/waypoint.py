from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.geopoint import GeoPoint

class Waypoint(GeoPoint):
    def __init__(self):
        self.altitude = 0
        self.name = ''

    def __str__(self):
        return '{}, {}, {}'.format(self.name, super(), self.altitude)

class WaypointList:
    def __init__(self):
        self.__list = []

    def __len__(self):
        return len(self.__list)

    def __getitem__(self, i):
        if i < 0 or i > len(self):
            return None
        return self.__list[i]

    def __iter__(self):
        return iter(self.__list)

    def append(self, wp):
        self.__list.append(wp)

    def get_bounds(self):
        rc = GeoRect(180, -180, -90, 90)
        for wp in self.__list:
            rc.left = min(rc.left, wp.lon)
            rc.right = max(rc.right, wp.lon)
            rc.top = max(rc.top, wp.lat)
            rc.bottom = min(rc.bottom, wp.lat)
        return rc

    def parse_file(self, filename):
        f = open(filename, 'r')
        try:
            return self.parse(f, filename)
        finally:
            f.close()

    def parse(self, lines, filename = 'unknown.dat'):
        if filename.lower().endswith('.xcw') or filename.lower().endswith('.dat'):
            self.__parse_winpilot(lines)
        elif filename.lower().endswith('.cup'):
            self.__parse_seeyou(lines)
        else:
            raise RuntimeError('Waypoint file {} has an unsupported format.'.format(filename))
        return self

    def __parse_seeyou(self, lines):
        first = True
        for line in lines:
            if first:
                first = False
                continue
            
            line = line.strip()
            if line == '' or line.startswith('*'):
                continue
            
            if line == '-----Related Tasks-----':
                break

            fields = line.split(',')
            if len(fields) < 6:
                continue

            wp = Waypoint()
            wp.lat = self.__parse_seeyou_coordinate(fields[3]);
            wp.lon = self.__parse_seeyou_coordinate(fields[4]);
            wp.altitude = self.__parse_seeyou_altitude(fields[5]);
            wp.name = fields[0].strip();
            self.append(wp)

    def __parse_seeyou_altitude(self, str):
        str = str.lower()
        if str.endswith('ft') or str.endswith('f'):
            str = str.rstrip('ft')
            return int(float(str) * 0.3048)
        else:
            str = str.rstrip('m')
            return int(float(str))

    def __parse_seeyou_coordinate(self, str):
        str = str.lower()
        negative = str.endswith('s') or str.endswith('w')
        is_lon = str.endswith('e') or str.endswith('w')
        str = str.rstrip('sw') if negative else str.rstrip('ne')

        # degrees + minutes / 60
        if is_lon:
            a = int(str[:3]) + float(str[3:]) / 60
        else:
            a = int(str[:2]) + float(str[2:]) / 60
            
        if (negative):
            a *= -1
        return a
    
    def __parse_winpilot(self, lines):
        for line in lines:
            line = line.strip()
            if line == '' or line.startswith('*'):
                continue

            fields = line.split(',')
            if len(fields) < 6:
                continue

            wp = Waypoint()
            wp.lat = self.__parse_winpilot_coordinate(fields[1]);
            wp.lon = self.__parse_winpilot_coordinate(fields[2]);
            wp.altitude = self.__parse_winpilot_altitude(fields[3]);
            wp.name = fields[5].strip();
            self.append(wp)

    def __parse_winpilot_altitude(self, str):
        str = str.lower()
        if str.endswith('ft') or str.endswith('f'):
            str = str.rstrip('ft')
            return int(str) * 0.3048
        else:
            str = str.rstrip('m')
            return int(str)

    def __parse_winpilot_coordinate(self, str):
        str = str.lower()
        negative = str.endswith('s') or str.endswith('w')
        str = str.rstrip('sw') if negative else str.rstrip('ne')

        str = str.split(':')
        if len(str) < 2:
            return None

        # degrees + minutes / 60
        a = int(str[0]) + float(str[1]) / 60
        if (negative):
            a *= -1
        return a
