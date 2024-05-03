from utm_conversion import to_latlon, from_latlon, latlon_to_zone_number, latitude_to_zone_letter, check_valid_zone



cols = range(1,61) # C...X is 66 ...
# I not in the list
rows = [chr(c) for c in range(ord('C'),ord('X')+1) if chr(c) not in ['I','O']]
# 1C...60X
utm_zones = [f'{col}{row}' for row in rows for col in cols]
_utm_zones = {} # Cache objects

# lat,lng for bottom left, top left
Zone47N = ((96,0), (96,8), (102,0), (102,8))

# 47_ -> 96-102
col2degLng = lambda c: (cols.index(int(c)) * 6 -180, cols.index(int(c)) * 6 -180+6)
# __P -> 8-16
row2degLat = lambda r: (rows.index(r) * 8 -80, rows.index(r) * 8 -72)

class UTMZone:
    """Individual UTM zone. Each zone is 6 deg."""
    direction = ['N','E','S','W','NE','NW','SE','SW']
    def __init__(self, name='47N'):
        self.zone_code = name
        self._row, self._col = name[-1:], name[:-1] # N , # 47
        self.neighbor = {}
    def __repr__(self):
        return """UTMZone(%s)""" % self.zone_code
    def __eq__(self, other):
        # print("compare %s %s" % (self, other))
        return self.zone_code == other.zone_code and type(self) == type(other)
    def __getattr__(self, key):
        r, c = self._row, self._col
        # Direction -> (Row,Col)
        ngbr_cell = {
            'N': (rows[rows.index(r) + 1], self._col),
            'S': (rows[rows.index(r) - 1], self._col),
            'E': (self._row, cols[cols.index(int(c)) + 1]),
            'W': (self._row, cols[cols.index(int(c)) - 1]),
            'NE': (rows[rows.index(r) + 1], cols[cols.index(int(c)) + 1]),
            'NW': (rows[rows.index(r) + 1], cols[cols.index(int(c)) - 1]),
            'SE': (rows[rows.index(r) - 1], cols[cols.index(int(c)) + 1]),
            'SW': (rows[rows.index(r) - 1], cols[cols.index(int(c)) - 1])
        }
        if key in self.direction:
            row, col = ngbr_cell[key]
            print("Return %s of %s : %s%s" % (key, self.zone_code, row, col))
            return grid[f'{col}{row}']
        south, north = row2degLat(self._row)
        west, east = col2degLng(self._col)
        bounds = { 'top': north, 'bottom': south, 'left': west, 'right': east }
        if key in bounds.keys():
            return bounds[key]
    @property
    def neighbors(self) -> []:
        """Returns neighbor to this zone as a list.
            Key are N,E,S,W,NE,NW,SE,SW
        """
        neighbor = []
        for d in self.direction:
            n = getattr(self, d)
            neighbor.append(n)
        return neighbor
    def as_geojson(self):
        neighbors = {}
        for k in self.direction:
            n = getattr(self, k)
            neighbors[k] = n.zone_code
        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                  [
                    [self.left, self.top],
                    [self.right, self.top],
                    [self.right, self.bottom],
                    [self.left, self.bottom]
                  ]
                ]
              },
              "properties": {
                "type": self.__class__.__name__,
                "zone": self.zone_code,
                "neighbors": neighbors
              }
            }
        return geojson

class UTMGrid:
    """The whole world coverage using UTM coordinate system."""
    zones = utm_zones
    def get_zone_obj(self, code):
        """Get the zone, i.e. 1C or 47N."""
        if not code in self.zones:
            raise Exception(f'{code} not in utm_zones')
        return self[code]

    def __getitem__(self, key):
        """Example: the_grid['60X']"""
        # print(utm_zones)
        # print(key in self.zones)
        print("Getting item %s " % key)
        if key in self.zones:
            # print("Returning the zone %s." % key)
            if not key in _utm_zones:
                _utm_zones[key] = UTMZone(key)
            return _utm_zones[key]
        raise Exception("UTM zone %s does not exists in the coordinate system." % key)

    def __getattr__(self, key):
        if key == 'rows':  # utm.rows -> 60
            return rows # C..X
        if key == 'cols':
            return cols # 1..60
        print("Getting attribute %s " % key)

grid = UTMGrid()
