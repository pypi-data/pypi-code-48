# coding: utf-8
"""Dragonfly Building."""
from ._base import _BaseGeometry
from .properties import BuildingProperties
from .story import Story
from .room2d import Room2D

from honeybee.model import Model
from honeybee.shade import Shade
from honeybee.boundarycondition import Surface

from ladybug_geometry.geometry2d.pointvector import Point2D
from ladybug_geometry.geometry3d.pointvector import Vector3D
from ladybug_geometry.geometry3d.face import Face3D

try:
    from itertools import izip as zip  # python 2
except ImportError:
    xrange = range  # python 3


class Building(_BaseGeometry):
    """A complete Building defined by Stories.

    Properties:
        * name
        * display_name
        * unique_stories
        * unique_room_2ds
        * height
        * height_from_first_floor
        * volume
        * floor_area
        * exterior_wall_area
        * exterior_aperture_area
        * min
        * max
    """
    __slots__ = ('_unique_stories',)

    def __init__(self, name, unique_stories):
        """A complete Building defined by Stories.

        Args:
            name: Building name. Must be < 100 characters.
            unique_stories: An array of unique Dragonfly Story objects that
                together form the entire building. Stories should be ordered
                from lowest floor to highest floor and they will be automatically
                sorted besed on floor height when they are added to a Building.
                Note that, if a given Story is repeated several times over the
                height of the Building, the unique Story included in this list
                should be the first (lowest) Story of the repeated floors.
        """
        _BaseGeometry.__init__(self, name)  # process the name

        # process the story geometry
        assert len(unique_stories) > 0, 'Building must have at least one Story.'
        for story in unique_stories:
            assert isinstance(story, Story), \
                'Expected dragonfly Story. Got {}'.format(type(story))
            story._parent = self
        flr_hgts = (story.floor_height for story in unique_stories)
        unique_stories = tuple(x for h, x in sorted(zip(flr_hgts, unique_stories)))
        self._unique_stories = unique_stories

        self._properties = BuildingProperties(self)  # properties for extensions

    @classmethod
    def from_footprint(cls, name, footprint, floor_to_floor_heights, tolerance=None):
        """Initialize a Building from an array of Face3Ds representing a footprint.

        All of the resulting Room2Ds will have a floor-to-ceiling height equal to the
        Story floor-to-floor height. Also, none of the Room2Ds will have contact
        with the ground or top exposure but the separate_top_bottom_floors method
        can be used to automatically break these floors out from the multiplier
        representation and assign these proeprties.

        Args:
            name: Building name. Must be < 100 characters.
            footprint: An array of horizontal ladybug-geometry Face3Ds that together
                represent the the footprint of the Building.
            floor_to_floor_heights: An array of float values with a length equal
                to the number of stories in the Building. Each value in the list
                represents the floor_to_floor height of the Story starting from
                the first floor and then moving to the top floor.
            tolerance: The maximum difference between z values at which point vertices
                are considered to be in the same horizontal plane. This is used to check
                that all vertices of the input floor_geometry lie in the same horizontal
                floor plane. Default is None, which will not perform any check.
        """
        # generate the unique Room2Ds from the footprint
        room_2ds = cls._generate_room_2ds(footprint, floor_to_floor_heights[0],
                                          name, 1, tolerance)

        # generate the unique stories from the floor_to_floor_heights
        # TODO: Add an input for core_perimeter_offsets once we have straight skeletons
        stories = []
        total_height = 0
        prev_flr_to_flr = None
        for i, flr_hgt in enumerate(floor_to_floor_heights):
            if flr_hgt != prev_flr_to_flr:
                if i != 0:
                    rooms = [room.duplicate() for room in room_2ds]
                    move_vec = Vector3D(0, 0, total_height)
                    for j, room in enumerate(rooms):
                        room.move(move_vec)
                        room.floor_to_ceiling_height = flr_hgt
                        room.name = '{}_Floor{}_Room{}'.format(name, i + 1, j + 1)
                else:
                    rooms = room_2ds
                stories.append(Story('{}_Floor{}'.format(name, i + 1), rooms, flr_hgt))
            else:
                stories[-1].multiplier += 1
            total_height += flr_hgt
            prev_flr_to_flr = flr_hgt

        return cls(name, stories)

    @classmethod
    def from_all_story_geometry(cls, name, all_story_geometry, floor_to_floor_heights,
                                tolerance):
        """Initialize a Building from an array of Face3Ds arrays representing all floors.

        This method will test to see which of the stories are geometrically unique
        (accouting for both the floor plate geometry and the floor_to_floor_heights).
        It will only include the unique floor geometries in the resulting Building.

        All of the resulting Room2Ds will have a floor-to-ceiling height equal to the
        Story floor-to-floor height.

        Args:
            name: Building name. Must be < 100 characters.
            all_story_geometry: An array of arrays with each sub-array possessing
                horizontal ladybug-geometry Face3Ds that representing the floor
                plates of the building. Together, these Face3Ds should represent
                all Stories of a building and each array of Face3Ds should together
                represent one Story.
            floor_to_floor_heights: An array of float values with a length equal
                to the number of stories in the Building. Each value in the list
                represents the floor_to_floor height of the Story starting from
                the first floor and then moving to the top floor.
            tolerance: The maximum difference between x, y, and z values at which
                point vertices are considered to be the same. This is required as
                a means to determine which floor geometries are equivalent to one
                another.
        """
        # generate the first story of the building
        room_2ds = cls._generate_room_2ds(
            all_story_geometry[0], floor_to_floor_heights[0], name, 1, tolerance)
        stories = [Story('{}_Floor1'.format(name), room_2ds, floor_to_floor_heights[0])]

        # generate the remaining unique stories from the floor_to_floor_heights
        # TODO: Add an input for core_perimeter_offsets once we have straight skeletons
        remaining_geo = all_story_geometry[1:]
        remaining_flr_hgts = floor_to_floor_heights[1:]
        prev_geo = all_story_geometry[0]
        prev_flr_to_flr = floor_to_floor_heights[0]
        for i, (room_geo, flr_hgt) in enumerate(zip(remaining_geo, remaining_flr_hgts)):
            # test is anything is geometrically different
            if flr_hgt != prev_flr_to_flr or len(room_geo) != len(prev_geo) or \
                    not all(cls._is_story_equivalent(rm1, rm2, tolerance)
                            for rm1, rm2 in zip(room_geo, prev_geo)):
                room_2ds = cls._generate_room_2ds(
                    room_geo, flr_hgt, name, i + 2, tolerance)
                stories.append(Story('{}_Floor{}'.format(name, i + 2), room_2ds, flr_hgt))
            else:  # geometry is the same as the floor below
                stories[-1].multiplier += 1
            prev_geo = room_geo
            prev_flr_to_flr = flr_hgt

        return cls(name, stories)

    @classmethod
    def from_dict(cls, data):
        """Initialize an Building from a dictionary.

        Args:
            data: A dictionary representation of a Building object.
        """
        # check the type of dictionary
        assert data['type'] == 'Building', 'Expected Building dictionary. ' \
            'Got {}.'.format(data['type'])

        stories = [Story.from_dict(s_dict) for s_dict in data['unique_stories']]

        building = Building(data['name'], stories)
        if 'display_name' in data and data['display_name'] is not None:
            building._display_name = data['display_name']

        if data['properties']['type'] == 'BuildingProperties':
            building.properties._load_extension_attr_from_dict(data['properties'])
        return building

    @property
    def unique_stories(self):
        """Get a tuple of only unique Story objects that form the Building.

        Repeated stories are represented only once but will have a non-unity multiplier.
        """
        return self._unique_stories

    @property
    def unique_room_2ds(self):
        """Get a list of the unique Room2D objects that form the Building."""
        rooms = []
        for story in self._unique_stories:
            rooms.extend(story.room_2ds)
        return rooms

    @property
    def height(self):
        """Get a number for the height of the top ceiling of the Building."""
        last_flr = self._unique_stories[-1]
        return last_flr.floor_height + \
            (last_flr.floor_to_floor_height * last_flr.multiplier)

    @property
    def height_from_first_floor(self):
        """Get a the height difference between the top ceiling and bottom floor."""
        return self.height - self._unique_stories[0].floor_height

    @property
    def volume(self):
        """Get a number for the volume of all the Rooms in the Building.

        Note that this property uses the story multipliers.
        """
        return sum([story.volume * story.multiplier
                    for story in self._unique_stories])

    @property
    def floor_area(self):
        """Get a number for the total floor area in the Building.

        Note that this property uses the story multipliers.
        """
        return sum([story.floor_area * story.multiplier
                    for story in self._unique_stories])

    @property
    def exterior_wall_area(self):
        """Get a number for the total exterior wall area in the Building.

        Note that this property uses the story multipliers.
        """
        return sum([story.exterior_wall_area * story.multiplier
                    for story in self._unique_stories])

    @property
    def exterior_aperture_area(self):
        """Get a number for the total exterior aperture area in the Building.

        Note that this property uses the story multipliers.
        """
        return sum([story.exterior_aperture_area * story.multiplier
                    for story in self._unique_stories])
    
    @property
    def min(self):
        """Get a Point2D for the min bounding rectangle vertex in the XY plane.
        
        This is useful in calculations to determine if this Building is in proximity
        to other objects.
        """
        return self._calculate_min(self._unique_stories)
    
    @property
    def max(self):
        """Get a Point2D for the max bounding rectangle vertex in the XY plane.
        
        This is useful in calculations to determine if this Building is in proximity
        to other objects.
        """
        return self._calculate_max(self._unique_stories)

    def all_stories(self):
        """Get a list of all Story objects that form the Building.

        The Story objects returned here each have a multiplier of 1 and repeated
        stories are represented will their own Story object.
        """
        all_stories = []
        for story in self._unique_stories:
            new_story = story.duplicate()
            new_story.add_prefix('Flr1')
            new_story.multiplier = 1
            all_stories.append(new_story)

            if story.multiplier != 1:
                for i in range(story.multiplier - 1):
                    new_story = story.duplicate()
                    new_story.add_prefix('Flr{}'.format(i + 2))
                    new_story.multiplier = 1
                    m_vec = Vector3D(0, 0, story.floor_to_floor_height * (i + 1))
                    new_story.move(m_vec)
                    all_stories.append(new_story)
        return all_stories

    def all_room_2ds(self):
        """Get a list of all Room2D objects that form the Building."""
        rooms = []
        for story in self.all_stories():
            rooms.extend(story.room_2ds)
        return rooms

    def shade_representation(self, tolerance):
        """A list of honeybee Shade objects representing the building geometry.

        These can be used to account for this Building's shade in the simulation of
        another nearby Building.

        Args:
            tolerance: The minimum distance between points at which they are
                not considered touching.
        """
        context_shades = []
        for story in self.unique_stories:
            extru_vec = Vector3D(0, 0, story.floor_to_floor_height * story.multiplier)
            for i, seg in enumerate(story.outline_segments(tolerance)):
                extru_geo = Face3D.from_extrusion(seg, extru_vec)
                shd_name = '{}_{}_{}'.format(self.name, story.name, i)
                context_shades.append(Shade(shd_name, extru_geo))
            # TODO: add a Shade object to cap the extrusion once lb_geometry has polyline
        return context_shades

    def add_prefix(self, prefix):
        """Change the name of this object and all child objects by inserting a prefix.
        
        This is particularly useful in workflows where you duplicate and edit
        a starting object and then want to combine it with the original object
        into one Model (like making a model of repeating buildings) since all objects
        within a Model must have unique names.

        Args:
            prefix: Text that will be inserted at the start of this object's
                (and child segments') name and display_name. It is recommended
                that this name be short to avoid maxing out the 100 allowable
                characters for honeybee names.
        """
        self.name = '{}_{}'.format(prefix, self.display_name)
        self.properties.add_prefix(prefix)
        for story in self.unique_stories:
            story.add_prefix(prefix)

    def separate_top_bottom_floors(self):
        """Separate top/bottom Stories with non-unity multipliers into their own Stories.

        The resulting first and last Stories will each have a multiplier of 1 and
        duplicated middle Stories will be added as needed. This method also
        automatically assigns the first story Room2Ds to have a ground contact
        floor and the top story Room2Ds to have an outdoor-exposed roof.

        This is particularly helpful when using to_honeybee workflows with
        multipliers but one wants to account for the heat exchange of the top
        or bottom floors with the gound or outdoors.
        """
        new_ground_floor = ()
        new_top_floor = ()

        # ensure that the bottom floor is unique
        if self._unique_stories[0].multiplier != 1:
            story = self._unique_stories[0]
            new_ground_floor = (self._separated_ground_floor(story),)
            story.multiplier = story.multiplier - 1
            story.move(Vector3D(0, 0, story.floor_to_floor_height))  # 2nd floor
        
        # ensure that the top floor is unique
        if self._unique_stories[-1].multiplier != 1:
            new_top_floor = (self._separated_top_floor(story),)
            story.multiplier = story.multiplier - 1

        # set the unique stories to include any new top and bottom floors
        self._unique_stories = new_ground_floor + self._unique_stories + new_top_floor

        # assign the is_ground_contact and is_top_exposed properties
        self._unique_stories[0].set_ground_contact()
        self._unique_stories[-1].set_top_exposed()

    def set_outdoor_window_parameters(self, window_parameter):
        """Set all of the outdoor walls to have the same window parameters."""
        for story in self._unique_stories:
            story.set_outdoor_window_parameters(window_parameter)

    def set_outdoor_shading_parameters(self, shading_parameter):
        """Set all of the outdoor walls to have the same shading parameters."""
        for story in self._unique_stories:
            story.set_outdoor_shading_parameters(shading_parameter)

    def move(self, moving_vec):
        """Move this Building along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the object.
        """
        for story in self._unique_stories:
            story.move(moving_vec)

    def rotate_xy(self, angle, origin):
        """Rotate this Building counterclockwise in the XY plane by a certain angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for story in self._unique_stories:
            story.rotate_xy(angle, origin)

    def reflect(self, plane):
        """Reflect this Building across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will be reflected.
        """
        for story in self._unique_stories:
            story.reflect(plane)

    def scale(self, factor, origin=None):
        """Scale this Building by a factor from an origin point.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        for story in self._unique_stories:
            story.scale(factor, origin)

    def to_honeybee(self, use_multiplier=True, tolerance=None):
        """Convert Dragonfly Building to a Honeybee Model.

        Args:
            use_multiplier: If True, the multipliers on this Building's Stories will be
                passed along to the generated Honeybee Room objects, indicating the
                simulation will be run once for each unique room and then results
                will be multiplied. If False, full geometry objects will be written
                for each and every floor in the building that are represented through
                multipliers and all resulting multipliers will be 1. Default: True
            tolerance: The minimum distance in z values of floor_height and
                floor_to_ceiling_height at which adjacent Faces will be split.
                If None, no splitting will occur. Default: None.
        """
        if use_multiplier:
            hb_rooms = [room.to_honeybee(story.multiplier, tolerance)
                        for story in self._unique_stories for room in story]
        else:
            hb_rooms = [room.to_honeybee(1, tolerance) for room in self.all_room_2ds()]
        return Model(self.display_name, hb_rooms)

    def to_dict(self, abridged=False, included_prop=None):
        """Return Building as a dictionary.

        Args:
            abridged: Boolean to note whether the extension properties of the
                object (ie. construciton sets) should be included in detail
                (False) or just referenced by name (True). Default: False.
            included_prop: List of properties to filter keys that must be included in
                output dictionary. For example ['energy'] will include 'energy' key if
                available in properties to_dict. By default all the keys will be
                included. To exclude all the keys from extensions use an empty list.
        """
        base = {'type': 'Building'}
        base['name'] = self.name
        base['display_name'] = self.display_name
        base['unique_stories'] = [s.to_dict(abridged, included_prop)
                                  for s in self._unique_stories]
        base['properties'] = self.properties.to_dict(abridged, included_prop)
        return base
    
    @staticmethod
    def buildings_to_honeybee(buildings, use_multiplier, tolerance):
        """Convert an array of Building objects into a single honeybee Model.
        
        Args:
            buildings: An array of Building objects to be converted into a
                honeybee Model.
            use_multiplier: If True, the multipliers on this Building's Stories will be
                passed along to the generated Honeybee Room objects, indicating the
                simulation will be run once for each unique room and then results
                will be multiplied. If False, full geometry objects will be written
                for each and every floor in the building that are represented through
                multipliers and all resulting multipliers will be 1.
            tolerance: The minimum distance in z values of floor_height and
                floor_to_ceiling_height at which adjacent Faces will be split.
                If None, no splitting will occur.
        """
        # create a base model to which everything will be added
        base_model = buildings[0].to_honeybee(use_multiplier, tolerance)
        # loop through each Building, create a model, and add it to the base one
        for bldg in buildings[1:]:
            base_model.add_model(bldg.to_honeybee(use_multiplier, tolerance))
        return base_model
    
    @staticmethod
    def buildings_to_honeybee_self_shade(
            buildings, context_shades=None, shade_distance=None, use_multiplier=True,
            tolerance=None):
        """Convert an array of Buildings into several honeybee Models with self-shading.

        Each input Building will be exported into its own Model. For each Model,
        the other input Buildings will appear as context shade geometry. Thus,
        each Model is its own simulate-able unit accounting for the total
        self-shading of the input Buildings.
        
        Args:
            buildings: An array of Building objects to be converted into honeybee
                Models that account for their own shading of one another.
            context_shades: An optional array of ContextShade objects that will be
                added to the honeybee Models if their bounding box overlaps with a
                given building within the shade_distance.
            shade_distance: An optional number to note the distance beyond which other
                objects' shade should not be exported into a given Model. This is
                helpful for reducing the simulation run time of each Model when other
                connected buildings are too far away to have a meaningful impact on
                the results. If None, all other buildings will be included as context
                shade in each and every Model. Set to 0 to exclude all neighboring
                buildings from the resulting models. Default: None.
            use_multiplier: If True, the multipliers on this Building's Stories will be
                passed along to the generated Honeybee Room objects, indicating the
                simulation will be run once for each unique room and then results
                will be multiplied. If False, full geometry objects will be written
                for each and every floor in the building that are represented through
                multipliers and all resulting multipliers will be 1. Default: True
            tolerance: The minimum distance in z values of floor_height and
                floor_to_ceiling_height at which adjacent Faces will be split.
                If None, no splitting will occur. Default: None.
        """
        models = []  # list to be filled with Honeybee Models

        # create lists with all context representations of the buildings + shade
        bldg_shades = []
        bldg_pts = []
        con_shades = []
        con_pts = []
        if shade_distance is None or shade_distance > 0:
            for bldg in buildings:
                bldg_shades.append(bldg.shade_representation(tolerance))
                b_min, b_max = bldg.min, bldg.max
                center = Point2D((b_min.x + b_max.x) / 2, (b_min.y + b_max.y) / 2)
                bldg_pts.append((b_min, center, b_max))
            if context_shades is not None:
                for con in context_shades:
                    con_shades.append(con.to_honeybee())
                    c_min, c_max = con.min, con.max
                    center = Point2D((c_min.x + c_max.x) / 2, (c_min.y + c_max.y) / 2)
                    con_pts.append((c_min, center, c_max))
        
        # loop through each Building and create a model
        num_bldg = len(buildings)
        for i, bldg in enumerate(buildings):
            model = bldg.to_honeybee(use_multiplier, tolerance)
            
            if shade_distance is None:  # add all other bldg shades to the model
                for j in xrange(i + 1, num_bldg):  # buildings before this one
                    for shd in bldg_shades[j]:
                        model.add_shade(shd)
                for k in xrange(i):  # buildings after this one
                    for shd in bldg_shades[k]:
                        model.add_shade(shd)
                for c_shade in con_shades:  # context shades
                    for shd in c_shade:
                        model.add_shade(shd)
            elif shade_distance > 0:  # add only shade within the distance
                for j in xrange(i + 1, num_bldg):  # buildings before this one
                    if Building._bound_rect_in_dist(bldg_pts[i], bldg_pts[j],
                                                    shade_distance):
                        for shd in bldg_shades[j]:
                            model.add_shade(shd)
                for k in xrange(i):  # buildings after this one
                    if Building._bound_rect_in_dist(bldg_pts[i], bldg_pts[k],
                                                    shade_distance):
                        for shd in bldg_shades[k]:
                            model.add_shade(shd)
                for s in xrange(len(con_shades)):  # context shades
                    if Building._bound_rect_in_dist(bldg_pts[i], con_pts[s],
                                                    shade_distance):
                        for shd in con_shades[s]:
                            model.add_shade(shd)
            models.append(model)  # apend to the final list of Models
        return models

    @staticmethod
    def _generate_room_2ds(face3d_array, flr_to_flr, bldg_name, flr_count, tolerance):
        """Generate Room2D objects given geometry and information about their parent."""
        room_2ds = []
        for i, room_geo in enumerate(face3d_array):
            room = Room2D('{}_Floor{}_Room{}'.format(bldg_name, flr_count, i + 1),
                          room_geo, flr_to_flr, tolerance=tolerance)
            room_2ds.append(room)
        return room_2ds

    @staticmethod
    def _is_story_equivalent(face1, face2, tolerance):
        """Check whether the area, XY centerpoint and XY first point match between Face3D.

        Args:
            face1: First Face3D to check.
            face2: Second Face3D to check.
            tolerance: The maximum difference between x, y, and z values at which
                point vertices are considered to be the same.

        Returns:
            True if face1 is geometrically equivalent to face 2 else False.
        """
        # check wether the center points match within tolerance.
        cent1 = face1.center
        cent2 = face2.center
        if abs(cent1.x - cent2.x) > tolerance or abs(cent1.y - cent2.y) > tolerance:
            return False

        # check wether the point at start matches within tolerance
        start1 = face1[0]
        start2 = face2[0]
        if abs(start1.x - start2.x) > tolerance or abs(start1.y - start2.y) > tolerance:
            return False

        # check whether areas match within tolerance
        area_tol = tolerance ** 2
        if abs(face1.area - face2.area) > area_tol:
            return False

        return True
    
    @staticmethod
    def _bound_rect_in_dist(bound_pts1, bound_pts2, distance):
        """Check if the bounding rectangles of two footprints overlap within a distance.

        Checking the overlap of the bounding rectangels is extremely quick given this
        method's use of the Separating Axis Theorem.

        Args:
            bound_pts1: An array of Point2Ds (min, center, max) for the first footprint.
            bound_pts2: An array of Point2Ds (min, center, max) for the second footprint.
            distance: Acceptable distance between the two bounding rectangles.
        """
        # Bounding rectangle check using the Separating Axis Theorem
        polygon1_width = bound_pts1[2].x - bound_pts1[0].x
        polygon2_width = bound_pts2[2].x - bound_pts2[0].x
        dist_btwn_x = abs(bound_pts1[1].x - bound_pts2[1].x)
        x_gap_btwn_rect = dist_btwn_x - (0.5 * polygon1_width) - (0.5 * polygon2_width)

        polygon1_height = bound_pts1[2].y - bound_pts1[0].y
        polygon2_height = bound_pts2[2].y - bound_pts2[0].y
        dist_btwn_y = abs(bound_pts1[1].y - bound_pts2[1].y)
        y_gap_btwn_rect = dist_btwn_y - (0.5 * polygon1_height) - (0.5 * polygon2_height)

        if x_gap_btwn_rect > distance or y_gap_btwn_rect > distance:
            return False  # no overlap
        return True  # overlap exists

    @staticmethod
    def _separated_ground_floor(base_story):
        """Get a separated ground floor from a base_story."""
        bottom = base_story.duplicate()  # generate a new bottom floor
        bottom.multiplier = 1
        bottom.add_prefix('Ground')
        return bottom

    @staticmethod
    def _separated_top_floor(base_story):
        """Get a separated top floor from a base_story."""
        top = base_story.duplicate()  # generate a new top floor
        move_vec = Vector3D(0, 0, top.floor_to_floor_height * (top.multiplier - 1))
        top.move(move_vec)
        top.multiplier = 1
        top.add_prefix('Top')
        return top

    def __copy__(self):
        new_b = Building(self.name,
                         tuple(story.duplicate() for story in self._unique_stories))
        new_b._display_name = self.display_name
        new_b._properties._duplicate_extension_attr(self._properties)
        return new_b

    def __len__(self):
        return len(self._unique_stories)

    def __getitem__(self, key):
        return self._unique_stories[key]

    def __iter__(self):
        return iter(self._unique_stories)

    def __repr__(self):
        return 'Building: %s' % self.display_name
