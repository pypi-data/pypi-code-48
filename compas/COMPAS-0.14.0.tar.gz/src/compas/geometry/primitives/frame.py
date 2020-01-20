from __future__ import print_function

import math

from compas.geometry.basic import cross_vectors
from compas.geometry.basic import subtract_vectors

from compas.geometry.transformations import Transformation

from compas.geometry.transformations import matrix_from_basis_vectors
from compas.geometry.transformations import basis_vectors_from_matrix
from compas.geometry.transformations import quaternion_from_matrix
from compas.geometry.transformations import matrix_from_quaternion
from compas.geometry.transformations import axis_angle_vector_from_matrix
from compas.geometry.transformations import matrix_from_axis_angle_vector
from compas.geometry.transformations import euler_angles_from_matrix
from compas.geometry.transformations import matrix_from_euler_angles
from compas.geometry.transformations import decompose_matrix

from compas.geometry.primitives import Primitive
from compas.geometry.primitives import Point
from compas.geometry.primitives import Vector
from compas.geometry.primitives import Quaternion

__all__ = ['Frame']


class Frame(Primitive):
    """A frame is defined by a base point and two orthonormal base vectors.

    Parameters
    ----------
    point : point
        The origin of the frame.
    xaxis : vector
        The x-axis of the frame.
    yaxis : vector
        The y-axis of the frame.

    Attributes
    ----------
    axis_angle_vector
    data
    point
    normal
    xaxis
    yaxis
    zaxis
    quaternion

    Notes
    -----
    All input vectors are orthonormalized when creating a frame, with the first
    vector as starting point.

    Examples
    --------
    >>> from compas.geometry import Point
    >>> from compas.geometry import Vector
    >>> f = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
    >>> f = Frame(Point(0, 0, 0), Vector(1, 0, 0), Point(0, 1, 0))
    """

    def __init__(self, point, xaxis, yaxis):
        self._point = None
        self._xaxis = None
        self._yaxis = None
        self.point = point
        self.xaxis = xaxis
        self.yaxis = yaxis

    # ==========================================================================
    # factory
    # ==========================================================================

    @classmethod
    def worldXY(cls):
        """Construct the world XY frame.

        Returns
        -------
        Frame
            The world XY frame.

        Examples
        --------
        >>> frame = Frame.worldXY()
        >>> frame.point
        Point(0.000, 0.000, 0.000)
        >>> frame.xaxis
        Vector(1.000, 0.000, 0.000)
        >>> frame.yaxis
        Vector(0.000, 1.000, 0.000)
        """
        return cls([0, 0, 0], [1, 0, 0], [0, 1, 0])

    @classmethod
    def worldZX(cls):
        """Construct the world ZX frame.

        Returns
        -------
        Frame
            The world ZX frame.

        Examples
        --------
        >>> frame = Frame.worldZX()
        >>> frame.point
        Point(0.000, 0.000, 0.000)
        >>> frame.xaxis
        Vector(0.000, 0.000, 1.000)
        >>> frame.yaxis
        Vector(1.000, 0.000, 0.000)
        """
        return cls([0, 0, 0], [0, 0, 1], [1, 0, 0])

    @classmethod
    def worldYZ(cls):
        """Construct the world YZ frame.

        Returns
        -------
        Frame
            The world YZ frame.

        Examples
        --------
        >>> frame = Frame.worldYZ()
        >>> frame.point
        Point(0.000, 0.000, 0.000)
        >>> frame.xaxis
        Vector(0.000, 1.000, 0.000)
        >>> frame.yaxis
        Vector(0.000, 0.000, 1.000)
        """
        return cls([0, 0, 0], [0, 1, 0], [0, 0, 1])

    @classmethod
    def from_points(cls, point, point_xaxis, point_xyplane):
        """Constructs a frame from 3 points.

        Parameters
        ----------
        point : point
            The origin of the frame.
        point_xaxis : point
            A point on the x-axis of the frame.
        point_xyplane : point
            A point within the xy-plane of the frame.

        Returns
        -------
        Frame
            The constructed frame.

        Examples
        --------
        >>> frame = Frame.from_points([0, 0, 0], [1, 0, 0], [0, 1, 0])
        >>> frame.point
        Point(0.000, 0.000, 0.000)
        >>> frame.xaxis
        Vector(1.000, 0.000, 0.000)
        >>> frame.yaxis
        Vector(0.000, 1.000, 0.000)
        """
        xaxis = subtract_vectors(point_xaxis, point)
        xyvec = subtract_vectors(point_xyplane, point)
        yaxis = cross_vectors(cross_vectors(xaxis, xyvec), xaxis)
        return cls(point, xaxis, yaxis)

    @classmethod
    def from_rotation(cls, rotation, point=[0, 0, 0]):
        """Constructs a frame from a ``Rotation``.

        Parameters
        ----------
        rotation : :class:`Rotation`
            The rotation defines the orientation of the frame.
        point : :obj:`list` of :obj:`float`, optional
            The origin of the frame.
            Defaults to [0, 0, 0].

        Returns
        -------
        Frame
            The constructed frame.

        Examples
        --------
        >>> from compas.geometry import Rotation
        >>> f1 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> R = Rotation.from_frame(f1)
        >>> f2 = Frame.from_rotation(R, point=f1.point)
        >>> f1 == f2
        True
        """
        xaxis, yaxis = rotation.basis_vectors
        return cls(point, xaxis, yaxis)

    @classmethod
    def from_transformation(cls, transformation):
        """Constructs a frame from a ``Transformation``.

        Parameters
        ----------
        transformation : :class:`Transformation`
            The transformation defines the orientation of the frame through the
            rotation and the origin through the translation.

        Returns
        -------
        Frame
            The constructed frame.

        Examples
        --------
        >>> from compas.geometry import Rotation
        >>> f1 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> T = Transformation.from_frame(f1)
        >>> f2 = Frame.from_transformation(T)
        >>> f1 == f2
        True
        """
        xaxis, yaxis = transformation.basis_vectors
        point = transformation.translation
        return cls(point, xaxis, yaxis)

    @classmethod
    def from_matrix(cls, matrix):
        """Construct a frame from a matrix.

        Parameters
        ----------
        matrix : :obj:`list` of :obj:`list` of :obj:`float`
            The 4x4 transformation matrix in row-major order.

        Returns
        -------
        Frame
            The constructed frame.

        Examples
        --------
        >>> from compas.geometry import matrix_from_euler_angles
        >>> ea1 = [0.5, 0.4, 0.8]
        >>> M = matrix_from_euler_angles(ea1)
        >>> f = Frame.from_matrix(M)
        >>> ea2 = f.euler_angles()
        >>> allclose(ea1, ea2)
        True
        """
        sc, sh, a, point, p = decompose_matrix(matrix)
        R = matrix_from_euler_angles(a, static=True, axes='xyz')
        xaxis, yaxis = basis_vectors_from_matrix(R)
        return cls(point, xaxis, yaxis)

    @classmethod
    def from_list(cls, values):
        """Construct a frame from a list of 12 or 16 :obj:`float` values.

        Parameters
        ----------
        values : :obj:`list` of :obj:`float`
            The list of 12 or 16 values representing a 4x4 matrix.

        Returns
        -------
        Frame
            The constructed frame.

        Raises
        ------
        ValueError
            If the length of the list is neither 12 nor 16.

        Notes
        -----
        Since the transformation matrix follows the row-major order, the
        translational components must be at the list's indices 3, 7, 11.

        Examples
        --------
        >>> l = [-1.0,  0.0,  0.0, 8110, 0.0,  0.0, -1.0, 7020, 0.0, -1.0,  0.0, 1810]
        >>> f = Frame.from_list(l)
        """
        if len(values) == 12:
            values.extend([0., 0., 0., 1.])
        if len(values) != 16:
            raise ValueError(
                'Expected 12 or 16 floats but got %d' %
                len(values))

        matrix = [[0. for i in range(4)] for j in range(4)]
        for i in range(4):
            for j in range(4):
                matrix[i][j] = float(values[i * 4 + j])

        return cls.from_matrix(matrix)

    @classmethod
    def from_quaternion(cls, quaternion, point=[0, 0, 0]):
        """Construct a frame from a rotation represented by quaternion coefficients.

        Parameters
        ----------
        quaternion : :obj:`list` of :obj:`float`
            Four numbers that represent the four coefficient values of a quaternion.
        point : :obj:`list` of :obj:`float`, optional
            The point of the frame.
            Defaults to [0, 0, 0].

        Returns
        -------
        Frame
            The constructed frame.

        Examples
        --------
        >>> q1 = [0.945, -0.021, -0.125, 0.303]
        >>> f = Frame.from_quaternion(q1, point = [1., 1., 1.])
        >>> q2 = f.quaternion
        >>> allclose(q1, q2, tol=1e-03)
        True
        """
        R = matrix_from_quaternion(quaternion)
        xaxis, yaxis = basis_vectors_from_matrix(R)
        return cls(point, xaxis, yaxis)

    @classmethod
    def from_axis_angle_vector(cls, axis_angle_vector, point=[0, 0, 0]):
        """Construct a frame from an axis-angle vector representing the rotation.

        Parameters
        ----------
        axis_angle_vector : :obj:`list` of :obj:`float`
            Three numbers that represent the axis of rotation and angle of
            rotation by its magnitude.
        point : :obj:`list` of :obj:`float`, optional
            The point of the frame.
            Defaults to [0, 0, 0].

        Returns
        -------
        Frame
            The constructed frame.

        Examples
        --------
        >>> aav1 = [-0.043, -0.254, 0.617]
        >>> f = Frame.from_axis_angle_vector(aav1, point=[0, 0, 0])
        >>> aav2 = f.axis_angle_vector
        >>> allclose(aav1, aav2)
        True
        """
        R = matrix_from_axis_angle_vector(axis_angle_vector)
        xaxis, yaxis = basis_vectors_from_matrix(R)
        return cls(point, xaxis, yaxis)

    @classmethod
    def from_euler_angles(cls, euler_angles, static=True,
                          axes='xyz', point=[0, 0, 0]):
        """Construct a frame from a rotation represented by Euler angles.

        Parameters
        ----------
        euler_angles : :obj:`list` of :obj:`float`
            Three numbers that represent the angles of rotations about the defined axes.
        static : :obj:`bool`, optional
            If true the rotations are applied to a static frame.
            If not, to a rotational.
            Defaults to true.
        axes : :obj:`str`, optional
            A 3 character string specifying the order of the axes.
            Defaults to 'xyz'.
        point : :obj:`list` of :obj:`float`, optional
            The point of the frame.
            Defaults to [0, 0, 0].

        Returns
        -------
        Frame
            The constructed frame.

        Examples
        --------
        >>> ea1 = 1.4, 0.5, 2.3
        >>> f = Frame.from_euler_angles(ea1, static=True, axes='xyz')
        >>> ea2 = f.euler_angles(static=True, axes='xyz')
        >>> allclose(ea1, ea2)
        True
        """
        R = matrix_from_euler_angles(euler_angles, static, axes)
        xaxis, yaxis = basis_vectors_from_matrix(R)
        return cls(point, xaxis, yaxis)

    @classmethod
    def from_data(cls, data):
        """Construct a frame from its data representation.

        Parameters
        ----------
        data : :obj:`dict`
            The data dictionary.

        Returns
        -------
        Frame
            The constructed frame.

        Examples
        --------
        >>> data = {'point': [0.0, 0.0, 0.0], 'xaxis': [1.0, 0.0, 0.0], 'yaxis': [0.0, 1.0, 0.0]}
        >>> frame = Frame.from_data(data)
        >>> frame.point
        Point(0.000, 0.000, 0.000)
        >>> frame.xaxis
        Vector(1.000, 0.000, 0.000)
        >>> frame.yaxis
        Vector(0.000, 1.000, 0.000)
        """
        frame = cls.worldXY()
        frame.data = data
        return frame

    @classmethod
    def from_plane(cls, plane):
        """Constructs a frame from a plane.

        Xaxis and yaxis are arbitrarily selected based on the plane's normal.

        Parameters
        ----------
        plane : :class:`compas.geometry.Plane`
            A plane.

        Returns
        -------
        :class:`compas.geometry.Frame`
            The constructed frame.

        Examples
        --------
        >>> from compas.geometry import Plane
        >>> plane = Plane([0,0,0], [0,0,1])
        >>> frame = Frame.from_plane(plane)
        >>> allclose(frame.normal, plane.normal)
        True
        """
        # plane equation: a*x + b*y + c*z = d
        d = Vector(*plane.point).dot(plane.normal)
        # select 2 arbitrary points in the plane from which we create the xaxis
        coeffs = list(plane.normal)  # a, b, c
        # select a coeff with a value != 0
        coeffs_abs = [math.fabs(x) for x in coeffs]
        idx = coeffs_abs.index(max(coeffs_abs))
        # first point
        coords = [0, 0, 0]  # x, y, z
        # z = (d - a*0 + b*0)/c, if idx == 2
        v = d/coeffs[idx]
        coords[idx] = v
        pt1_in_plane = Point(*coords)
        # second point
        coords = [1, 1, 1]  # x, y, z
        coords[idx] = 0
        # z = (d - a*1 + b*1)/c, if idx == 2
        v = (d - sum([a*x for a, x in zip(coeffs, coords)]))/coeffs[idx]
        coords[idx] = v
        pt2_in_plane = Point(*coords)
        xaxis = pt2_in_plane - pt1_in_plane
        yaxis = plane.normal.cross(xaxis)
        return cls(plane.point, xaxis, yaxis)

    # ==========================================================================
    # descriptors
    # ==========================================================================

    @property
    def point(self):
        return self._point

    @point.setter
    def point(self, point):
        self._point = Point(*point)

    @property
    def xaxis(self):
        return self._xaxis

    @xaxis.setter
    def xaxis(self, vector):
        xaxis = Vector(*vector)
        xaxis.unitize()
        self._xaxis = xaxis

    @property
    def yaxis(self):
        return self._yaxis

    @yaxis.setter
    def yaxis(self, vector):
        yaxis = Vector(*vector)
        yaxis.unitize()
        zaxis = Vector.cross(self.xaxis, yaxis)
        zaxis.unitize()
        self._yaxis = Vector.cross(zaxis, self.xaxis)

    @property
    def data(self):
        """Returns the data dictionary that represents the frame.

        Returns
        -------
        dict
            The frame data.
        """
        return {'point': list(self.point),
                'xaxis': list(self.xaxis),
                'yaxis': list(self.yaxis)}

    @data.setter
    def data(self, data):
        self.point = data['point']
        self.xaxis = data['xaxis']
        self.yaxis = data['yaxis']

    @property
    def normal(self):
        """:class:`Vector` : The frame's normal (z-axis)."""
        return Vector(*cross_vectors(self.xaxis, self.yaxis))

    @property
    def zaxis(self):
        """:class:`Vector` : The frame's z-axis (normal)."""
        return self.normal

    @property
    def quaternion(self):
        """:class:`Quaternion` : The quaternion from the rotation given by the frame.
        """
        rotation = matrix_from_basis_vectors(self.xaxis, self.yaxis)
        return Quaternion(*quaternion_from_matrix(rotation))

    @property
    def axis_angle_vector(self):
        """vector : The axis-angle vector from the rotation given by the frame."""
        R = matrix_from_basis_vectors(self.xaxis, self.yaxis)
        return Vector(*axis_angle_vector_from_matrix(R))

    # ==========================================================================
    # representation
    # ==========================================================================

    def __repr__(self):
        return "Frame({0}, {1}, {2})".format(self.point, self.xaxis, self.yaxis)

    def __len__(self):
        return 3

    # ==========================================================================
    # access
    # ==========================================================================

    def __getitem__(self, key):
        if key == 0:
            return self.point
        if key == 1:
            return self.xaxis
        if key == 2:
            return self.yaxis
        raise KeyError

    def __setitem__(self, key, value):
        if key == 0:
            self.point = value
            return
        if key == 1:
            self.xaxis = value
            return
        if key == 2:
            self.yaxis = value
        raise KeyError

    def __iter__(self):
        return iter([self.point, self.xaxis, self.yaxis])

    # ==========================================================================
    # comparison
    # ==========================================================================

    def __eq__(self, other, tol=1e-05):
        for v1, v2 in zip(self, other):
            for a, b in zip(v1, v2):
                if math.fabs(a - b) > tol:
                    return False
        return True

    # ==========================================================================
    # operators
    # ==========================================================================

    # ==========================================================================
    # inplace operators
    # ==========================================================================

    # ==========================================================================
    # helpers
    # ==========================================================================

    def copy(self):
        """Make a copy of this ``Frame``.

        Returns
        -------
        Frame
            The copy.

        Examples
        --------
        >>> f1 = Frame.worldXY()
        >>> f2 = f1.copy()
        >>> f2.point
        Point(0.000, 0.000, 0.000)
        """
        cls = type(self)
        return cls(self.point.copy(), self.xaxis.copy(), self.yaxis.copy())

    # ==========================================================================
    # methods
    # ==========================================================================

    def euler_angles(self, static=True, axes='xyz'):
        """The Euler angles from the rotation given by the frame.

        Parameters
        ----------
        static : :obj:`bool`, optional
            If true the rotations are applied to a static frame.
            If not, to a rotational.
            Defaults to True.
        axes : :obj:`str`, optional
            A 3 character string specifying the order of the axes.
            Defaults to 'xyz'.

        Returns
        -------
        :obj:`list` of :obj:`float`
            Three numbers that represent the angles of rotations about the defined axes.

        Examples
        --------
        >>> from compas.geometry import Frame
        >>> ea1 = 1.4, 0.5, 2.3
        >>> f = Frame.from_euler_angles(ea1, static = True, axes = 'xyz')
        >>> ea2 = f.euler_angles(static = True, axes = 'xyz')
        >>> allclose(ea1, ea2)
        True
        """
        R = matrix_from_basis_vectors(self.xaxis, self.yaxis)
        return euler_angles_from_matrix(R, static, axes)

    # ==========================================================================
    # coordinate frames
    # ==========================================================================

    def to_local_coords(self, object_in_wcf):
        """Returns the object's coordinates in the local coordinate system of the frame.

        Parameters
        ----------
        object_in_wcf : :class:`Point` or :class:`Vector` or :class:`Frame` or list of float
            An object in the world coordinate frame.

        Returns
        -------
        :class:`Point` or :class:`Vector` or :class:`Frame`
            The object in the local coordinate system of the frame.

        Notes
        -----
        If you pass a list of float, it is assumed to represent a point.

        Examples
        --------
        >>> from compas.geometry import Point, Frame
        >>> frame = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> pw = Point(2, 2, 2) # point in wcf
        >>> pl = frame.to_local_coords(pw) # point in frame
        >>> frame.to_world_coords(pl)
        Point(2.000, 2.000, 2.000)
        """
        T = Transformation.change_basis(Frame.worldXY(), self)
        if isinstance(object_in_wcf, list):
            return Point(*object_in_wcf).transformed(T)
        else:
            return object_in_wcf.transformed(T)

    def to_world_coords(self, object_in_lcs):
        """Returns the object's coordinates in the global coordinate frame.

        Parameters
        ----------
        object_in_lcs : :class:`Point` or :class:`Vector` or :class:`Frame` or list of float
            An object in local coordinate system of the frame.

        Returns
        -------
        :class:`Point` or :class:`Vector` or :class:`Frame`
            The object in the world coordinate frame.

        Notes
        -----
        If you pass a list of float, it is assumed to represent a point.

        Examples
        --------
        >>> from compas.geometry import Frame
        >>> frame = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> pl = Point(1.632, -0.090, 0.573) # point in frame
        >>> pw = frame.to_world_coords(pl) # point in wcf
        >>> frame.to_local_coords(pw)
        Point(1.632, -0.090, 0.573)
        """
        T = Transformation.change_basis(self, Frame.worldXY())
        if isinstance(object_in_lcs, list):
            return Point(*object_in_lcs).transformed(T)
        else:
            return object_in_lcs.transformed(T)

    @staticmethod
    def local_to_local_coords(frame1, frame2, object_in_frame1):
        """Returns the object's coordinates in frame1 in the local coordinates of frame2.

        Parameters
        ----------
        frame1 : :class:`Frame`
            A frame representing one local coordinate system.
        frame2 : :class:`Frame`
            A frame representing another local coordinate system.
        object_in_frame1 : :class:`Point` or :class:`Vector` or :class:`Frame` or list of float
            An object in the coordinate frame1. If you pass a list of float, it is assumed to represent a point.

        Returns
        -------
        :class:`Point` or :class:`Vector` or :class:`Frame`
            The object in the local coordinate system of frame2.

        Examples
        --------
        >>> from compas.geometry import Point, Frame
        >>> frame1 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> frame2 = Frame([2, 1, 3], [1., 0., 0.], [0., 1., 0.])
        >>> p1 = Point(2, 2, 2) # point in frame1
        >>> p2 = Frame.local_to_local_coords(frame1, frame2, p1) # point in frame2
        >>> Frame.local_to_local_coords(frame2, frame1, p2)
        Point(2.000, 2.000, 2.000)
        """
        T = Transformation.change_basis(frame1, frame2)
        if isinstance(object_in_frame1, list):
            return Point(*object_in_frame1).transformed(T)
        else:
            return object_in_frame1.transformed(T)

    # ==========================================================================
    # transformations
    # ==========================================================================

    def transform(self, transformation):
        """Transform the frame.

        Parameters
        ----------
        transformation : :class:`Transformation`
            The transformation used to transform the Frame.

        Examples
        --------
        >>> from compas.geometry import Frame
        >>> from compas.geometry import Transformation
        >>> f1 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> T = Transformation.from_frame(f1)
        >>> f2 = Frame.worldXY()
        >>> f2.transform(T)
        >>> f1 == f2
        True
        """
        T = transformation * Transformation.from_frame(self)
        point = T.translation
        xaxis, yaxis = T.basis_vectors
        self.point = point
        self.xaxis = xaxis
        self.yaxis = yaxis

    def transformed(self, transformation):
        """Returns a transformed copy of the current frame.

        Parameters
        ----------
        transformation : :class:`Transformation`
            The transformation used to transform the Frame.

        Returns
        -------
        :class:`Frame`
            The transformed frame.

        Examples
        --------
        >>> from compas.geometry import Frame
        >>> from compas.geometry import Transformation
        >>> f1 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> T = Transformation.from_frame(f1)
        >>> f2 = Frame.worldXY()
        >>> f1 == f2.transformed(T)
        True
        """
        frame = self.copy()
        frame.transform(transformation)
        return frame


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import doctest
    from compas.geometry import allclose  # noqa: F401
    doctest.testmod(globs=globals())
