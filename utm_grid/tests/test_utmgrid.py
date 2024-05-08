import os, sys
import json
import pytest
from utm import UTMGrid, UTMZone
from utm import row2degLat, col2degLng

@pytest.fixture
def the_grid():
  return UTMGrid()

def test_primitives():
    assert row2degLat("M") == (-8, 0)
    assert row2degLat("N") == (0, 8)
    with pytest.raises(Exception) as e_info:
        row2degLat("O") # Row 'O','I' is not in the grid.
    assert row2degLat('P') == (8, 16)
    assert col2degLng(47) == (96, 102)
    assert col2degLng(48) == (102, 108)

def test_get_single_zone(the_grid):
    z1 = UTMZone(name='1C')
    assert z1.zone_code == '1C'
    z47N = the_grid['47N']
    z48P = the_grid.get_zone_obj('48P')
    z48Q = the_grid['48Q']
    assert z48P.zone_code == '48P', "Get UTM zone."
    n, n1, n2 = z47N, z47N.NE, z47N.NE.N
    assert n2 == z48Q, f'Check adjacent zones of 47N {n} NE : {n1} N : {n2}'
    assert z48P.top == 16, f'Top of zone {z48P} is {z48P.top}.'
    assert z48P.left == 102, f'Left of zone {z48P} is {z48P.left}.'
    with open("z.geojson","w") as f:
        f.write(json.dumps(z47N.as_geojson(), indent=4))
    assert "geometry" in str(z47N.as_geojson()), f'JSON of zone {z47N}'

def test_grid_class_enumerate_grid(the_grid):
  """The UTM grid class can enumerate 1C...60X"""
  z1 = UTMZone(name='1C')
  assert z1.zone_code == '1C'
  assert the_grid['1C'] == z1, "Access grid 1C from the UTM map."
  assert the_grid.zones[0] == '1C', "First zone is 1C"
  assert the_grid.zones[-1] == '60X', "Last zone is 60X"

  assert the_grid['60X'] == UTMZone(name='60X'), "Access grid 60X from the UTM map."
  assert the_grid['47N'] == UTMZone('47N'), "Access grid 47N from the UTM map."

def test_grid_class_has_60cols(the_grid):
  assert len(the_grid.cols) == 60, "UTM grid should have columns 1..60"
  assert the_grid.rows[0] == 'C'

def test_grid_zone_get_neighbors(the_grid):
    z1 = the_grid['4E']
    z2 = the_grid['4F']
    assert z1.N == z2, "North of 4E is 4F"
    assert z1.S == the_grid['4D'], "South of 4E is 4D"
    assert z1.E == the_grid['5E'], "East of 4E is 5E"
    assert z1.W == the_grid['3E'], "West of 4E is 3E"
    assert z1.NE == the_grid['5F'], "NE of 4E is 5F"

    n_list = z1.neighbors
    n_set = [z.zone_code for z in n_list]
    assert len(n_set) == 8, "Get neighbor cells for %s" % z1
    n_0 = n_set[0] # [z.zone_code for z in n_0.neighbors]
    for c in n_list[:3]:
        assert c.zone_code in n_set, "Check neighbor prop for %s" % c

def test_grid_thailand(the_grid):
    z1 = the_grid['47N']
    with open("out.txt", "w") as f:
        dat = [z1] + z1.neighbors
        f.write(str(dat))
