"""Module to prepare initial poses for docking"""

import os
import operator
import numpy as np
from lightdock.pdbutil.PDBIO import create_pdb_from_points
from lightdock.prep.starting_points import calculate_surface_points
from lightdock.prep.ftdock import FTDockCoordinatesParser, classify_ftdock_poses
from lightdock.mathutil.lrandom import MTGenerator, NormalGenerator
from lightdock.mathutil.cython.quaternion import Quaternion
from lightdock.mathutil.cython.cutil import distance as cdistance
from lightdock.mathutil.cython.cutil import norm
from lightdock.constants import CLUSTERS_CENTERS_FILE,\
    DEFAULT_PDB_STARTING_PREFIX, DEFAULT_STARTING_PREFIX, DEFAULT_BILD_STARTING_PREFIX, DEFAULT_EXTENT_MU, \
    DEFAULT_EXTENT_SIGMA
from lightdock.prep.geometry import create_bild_file
from lightdock.structure.residue import Residue
from lightdock.error.lightdock_errors import LightDockWarning


def get_random_point_within_sphere(number_generator, radius):
    """Generates a random point within a sphere of given radius"""
    r2 = radius**2
    while True:
        x = (2 * number_generator() - 1) * radius
        y = (2 * number_generator() - 1) * radius
        z = (2 * number_generator() - 1) * radius
        if x**2 + y**2 + z**2 <= r2:
            return x, y, z


def normalize_vector(v):
    """Normalizes a given vector"""
    norm = np.linalg.norm(v)
    if norm < 0.00001: 
       return v
    return v / norm


def quaternion_from_vectors(a, b):
    """Calculate quaternion between two vectors a and b. 

    Code source: http://lolengine.net/blog/2014/02/24/quaternion-from-two-vectors-final
    """
    u = normalize_vector(a)
    v = normalize_vector(b)
    norm_u_norm_v = np.sqrt( np.dot(u, u) * np.dot(v, v))
    real_part = norm_u_norm_v + np.dot(u, v)

    if real_part < 1.e-6 * norm_u_norm_v:
        # If u and v are exactly opposite, rotate 180 degrees
        # around an arbitrary orthogonal axis. Axis normalisation
        # can happen later, when we normalise the quaternion.
        real_part = 0.0
        if abs(u[0]) > abs(u[2]):
            w = [-u[1], u[0], 0.]
        else:
            w = [0., -u[2], u[1]]
    else:
        # Otherwise, build quaternion the standard way
        w = np.cross(u, v)

    return Quaternion(real_part, w[0], w[1], w[2]).normalize()


def get_quaternion_for_restraint(rec_residue, lig_residue, tx, ty, tz, rt, lt):
    """Calculates the quaternion required for orienting the ligand towards the restraint"""
    r_ca = rec_residue.get_calpha()
    # Deal with possible DNA nucleotides
    if not r_ca:
        r_ca = rec_residue.get_atom('P')
    l_ca = lig_residue.get_calpha()
    # Deal with possible DNA nucleotides
    if not l_ca:
        l_ca = lig_residue.get_atom('P')

    rx = r_ca.x + rt[0]
    ry = r_ca.y + rt[1]
    rz = r_ca.z + rt[2]

    lx = l_ca.x + lt[0]
    ly = l_ca.y + lt[1]
    lz = l_ca.z + lt[2]

    # Define restraints vectors
    a = np.array([lx, ly, lz])
    b = np.array([rx - tx, ry - ty, rz - tz])
    
    q = quaternion_from_vectors(a, b)

    return q


def populate_poses(to_generate, center, radius, number_generator, rec_translation, lig_translation,
                    rng_nm=None, rec_nm=0, lig_nm=0, receptor_restraints=None, ligand_restraints=None,
                    ligand_diameter=1.):
    """Creates new poses around a given center and a given radius"""
    new_poses = []

    # Calculate closest residue restraints
    closest_residues = []
    if receptor_restraints:
        distances = []
        for i, residue in enumerate(receptor_restraints):
            ca = residue.get_calpha()
            if not ca:
                ca = residue.get_atom('P')
            distances.append((i, cdistance(ca.x , ca.y , ca.z ,
                                            center[0], center[1], center[2])))
        distances.sort(key=lambda tup: tup[1])
        closest_residues = [x[0] for x in distances[:10]]

    for _ in range(to_generate):
        # First calculate a random translation within the swarm sphere
        x, y, z = get_random_point_within_sphere(number_generator, radius)
        tx = center[0] + x
        ty = center[1] + y
        tz = center[2] + z

        # Restraints in both partners
        if receptor_restraints and ligand_restraints:
            # We select one of the closest residue restraints to point the quaternion
            rec_residue = receptor_restraints[closest_residues[number_generator.randint(0, len(closest_residues)-1)]]
            # Random restraint on the ligand to use for pre-orientation
            lig_residue = ligand_restraints[number_generator.randint(0, len(ligand_restraints)-1)]
            # Calculate the quaternion which rotates the ligand to point to the given receptor restraint
            q = get_quaternion_for_restraint(rec_residue, lig_residue, tx, ty, tz,
                                             rec_translation, lig_translation)

        # Only restraints in the ligand partner
        elif ligand_restraints and not receptor_restraints:
            # The strategy is similar to previous but for the receptor side we will use a simulated point
            # over the receptor surface to point out the quaternion
            coef = norm(center) / ligand_diameter
            if coef > 1.0:
                raise LightDockWarning('Found wrong coefficient on calculating poses with restraints')
            # It is important to keep the coordinates as in the original complex without
            # moving to the center of coordinates (applying translation)
            rec_residue = Residue.dummy(center[0]*coef - rec_translation[0], 
                                        center[1]*coef - rec_translation[1], 
                                        center[2]*coef - rec_translation[2])

            lig_residue = ligand_restraints[number_generator.randint(0, len(ligand_restraints)-1)]
            q = get_quaternion_for_restraint(rec_residue, lig_residue, tx, ty, tz,
                                             rec_translation, lig_translation)
        # No restraints at all
        else:
            q = Quaternion.random(number_generator)

        # Glowworm's optimization vector
        op_vector = [tx, ty, tz, q.w, q.x, q.y, q.z]

        # If ANM is enabled, we need to create random components for the extents
        if rng_nm:
            if rec_nm > 0:
                op_vector.extend([rng_nm() for _ in range(rec_nm)])
            if lig_nm > 0:
                op_vector.extend([rng_nm() for _ in range(lig_nm)])

        new_poses.append(op_vector)

    return new_poses


def create_file_from_poses(pos_file_name, poses):
    """Writes to file the initial poses"""
    positions_file = open(pos_file_name, 'w')
    for pose in poses:
        position = ' '.join(["{:.9f}".format(coord) for coord in pose])
        positions_file.write(position + os.linesep)
    positions_file.close()


def apply_restraints(swarm_centers, receptor_restraints, distance_cutoff, translation, 
                     swarms_per_restraint=10):
    """Filter out swarm centers which are not close to the given restraints"""
    closer_swarms = []
    for i, residue in enumerate(receptor_restraints):
        distances = {}
        # We will use CA in case of protein, P in case of DNA
        ca = residue.get_calpha()
        if not ca:
            ca = residue.get_atom('P')
        # Calculate the euclidean distance between swarm center and given atom/bead
        for swarm_id, center in enumerate(swarm_centers):
            distances[swarm_id] = cdistance(ca.x + translation[0], ca.y + translation[1], ca.z + translation[2],
                                            center[0], center[1], center[2])
        sorted_distances = sorted(list(distances.items()), key=operator.itemgetter(1))
        swarms_considered = 0
        for swarm in sorted_distances:
            swarm_id, distance = swarm[0], swarm[1]
            if distance <= distance_cutoff:
                closer_swarms.append(swarm_id)
                swarms_considered += 1
            if swarms_considered == swarms_per_restraint:
                break

    # Unique swarm ids
    closer_swarm_ids = sorted(list(set(closer_swarms)))

    # Final filtered list of swarms
    new_swarm_centers = [swarm_centers[i] for i in closer_swarm_ids]
    return new_swarm_centers


def estimate_membrane(z_coordinates, cutoff=10.0):
    """Given a 1D array with Z-axis coordinates, estimate the number of groups, which
    will correspond to the number of membrane layers."""
    sorted_data = sorted(z_coordinates)
    data_length = len(sorted_data)
    diffs = [abs(sorted_data[i]-sorted_data[i-1]) for i in range(1, data_length)]
    points = [i+1 for i, x in enumerate(diffs) if x > cutoff]
    if not points:
        return [sorted_data]
    indices = [0] + points + [data_length]
    layers = [sorted_data[v:indices[k+1]] for k, v in enumerate(indices[:-1])]
    return layers


def upper_layer(layers):
    """Calculates which is the upper membrane layer"""
    avgs = [np.mean(layer) for layer in layers]
    upper = layers[np.argmax(avgs)]
    return upper


def apply_membrane(swarm_centers, membrane_beads, translation):
    """Applies membrane restraints to the given swarm centers
    
    Requires membrane beads to be orthogal to Z-axis.
    """
    bead_z_coordinates = [residue.get_atom('BJ').z for residue in membrane_beads]
    layers = estimate_membrane(bead_z_coordinates)
    layer = upper_layer(layers)
    min_z = max(layer) + translation[2]
    compatible = []
    for swarm_id, center in enumerate(swarm_centers):
        if center[2] >= min_z:
            compatible.append(center)
    return compatible


def calculate_initial_poses(receptor, ligand, num_clusters, num_glowworms,
                            seed, receptor_restraints, ligand_restraints, 
                            rec_translation, lig_translation,
                            dest_folder, ftdock_file='', nm_mode=False, nm_seed=0, rec_nm=0, lig_nm=0,
                            is_membrane=False):
    """Calculates the starting points for each of the glowworms using the center of swarms
    and FTDock poses.
    """
    # Random number generator for poses
    rng = MTGenerator(seed)

    # Random number generator for NM
    if nm_mode:
        rng_nm = NormalGenerator(nm_seed, mu=DEFAULT_EXTENT_MU, sigma=DEFAULT_EXTENT_SIGMA)
    else:
        rng_nm = None
    
    # Calculate swarm centers
    swarm_centers, receptor_diameter, ligand_diameter = calculate_surface_points(receptor, 
                                                                                 ligand, 
                                                                                 num_clusters,
                                                                                 distance_step=1.0,
                                                                                 is_membrane=is_membrane)
    # Filter swarms far from the restraints
    if receptor_restraints:
        swarm_centers = apply_restraints(swarm_centers, receptor_restraints, 
                                         ligand_diameter / 2., rec_translation)

    # Filter out swarms which are not compatible with the explicit membrane
    if is_membrane:
        membrane_beads = [residue for residue in receptor.residues if residue.name == 'MMB']
        swarm_centers = apply_membrane(swarm_centers, membrane_beads, rec_translation)

    pdb_file_name = os.path.join(dest_folder, CLUSTERS_CENTERS_FILE)
    create_pdb_from_points(pdb_file_name, swarm_centers)

    ligand_center = ligand.center_of_coordinates()
    radius = 10.    # ligand_diameter / 2.
    positions_files = []

    # Populate the clusters using the FTDock poses
    if ftdock_file:
        if nm_mode:
            raise NotImplementedError('Using FTDock poses with NM is not supported')

        poses = FTDockCoordinatesParser.get_list_of_poses(ftdock_file, ligand_center)
        clusters = classify_ftdock_poses(poses, swarm_centers, radius)

        for cluster_id, ftdock_poses in clusters.items():
            # Translate FTDock poses into lightdock poses
            poses = []
            for pose in ftdock_poses:
                poses.append([pose.translation[0],
                              pose.translation[1],
                              pose.translation[2],
                              pose.q.w,
                              pose.q.x,
                              pose.q.y,
                              pose.q.z])

            # Populate new poses if needed
            if len(poses) < num_glowworms:
                needed = num_glowworms - len(poses)
                poses.extend(populate_poses(needed, swarm_centers[cluster_id], radius, rng, rec_translation, lig_translation))

            # Save poses as pdb file
            pdb_file_name = os.path.join(dest_folder, '%s_%s.pdb' % (DEFAULT_PDB_STARTING_PREFIX, cluster_id))
            create_pdb_from_points(pdb_file_name, [[pose[0], pose[1], pose[2]] for pose in poses[:num_glowworms]])

            # Save poses as initial_positions file
            pos_file_name = os.path.join(dest_folder, '%s_%s.dat' % (DEFAULT_STARTING_PREFIX, cluster_id))
            bild_file_name = os.path.join(dest_folder, '%s_%s.bild' % (DEFAULT_BILD_STARTING_PREFIX, cluster_id))
            create_file_from_poses(pos_file_name, poses[:num_glowworms])
            positions_files.append(pos_file_name)
            create_bild_file(bild_file_name, poses)
    else:
        for swarm_id, swarm_center in enumerate(swarm_centers):
            poses = populate_poses(num_glowworms, swarm_center, radius, rng, rec_translation, lig_translation,
                                    rng_nm, rec_nm, lig_nm, receptor_restraints, ligand_restraints, ligand_diameter)
            # Save poses as pdb file
            pdb_file_name = os.path.join(dest_folder, '%s_%s.pdb' % (DEFAULT_PDB_STARTING_PREFIX, swarm_id))
            create_pdb_from_points(pdb_file_name, [[pose[0], pose[1], pose[2]] for pose in poses[:num_glowworms]])

            # Save poses as initial_positions file
            pos_file_name = os.path.join(dest_folder, '%s_%s.dat' % (DEFAULT_STARTING_PREFIX, swarm_id))
            bild_file_name = os.path.join(dest_folder, '%s_%s.bild' % (DEFAULT_BILD_STARTING_PREFIX, swarm_id))
            create_file_from_poses(pos_file_name, poses[:num_glowworms])
            positions_files.append(pos_file_name)
            create_bild_file(bild_file_name, poses)

    return positions_files
