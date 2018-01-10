# -*- coding: utf-8 -*-
"""

Functions related to roller bearings.

"""

from math import tan

import numpy as np

from tribology.boundary_element import __secant


def fcylrolbear(ang_pos, comb_prof, ax_rol, f_rad, rad_clear=0, max_dif=0.0005):
    """

    Calculate the normal force distribution in a cylindrical roller bearing
    according to DIN 26281. For the calculation, each roller is modelled as a
    set of neighbouring spring slices with known stiffness. Applying an outer
    force :code:`f_rad` leads to an elastic displacement of the spring slices
    of each roller. To find the normal force on each roller, the spring slice
    displacement is varied systematically until the sum of the inner spring
    forces is (approximately) equal to the outer force :code:`f_rad`.

    Parameters
    ----------
    ang_pos: ndarray
        The angular positions of the rollers in angular coordinates. The length
        of the array determines the number of rollers.
    comb_prof: ndarray
        The combined 1D profile of the roller and the bearing inner/outer ring.
    ax_rol: ndarray
        The longitudinal axis of the roller with length :code:`len(comb_prof)`.
        The length of the axis determines the number of roller spring slices.
    f_rad: scalar
        The normal force acting on the inner ring of the bearing. The force acts
        from the center of the bearing in the direction of the origin of the
        polar axis.
    rad_clear: scalar, optional
        The radial clearance of the bearing. Default is 0.
    max_dif: scalar, optional
        The maximum allowed difference between the outer force :code:`f_rad` and
        the sum over all roller forces (in percent of :code:`f_rad`). Default
        is 0.05 %.

    Returns
    -------
    f_rols: ndarray
        The roller normal forces for each roller position in :code:`ang_pos`.
    disp_rols: ndarray
        The elastic normal displacement in the ring-roller contact for each
        roller position in :code:`ang_pos`.
    delta_f: scalar
        The difference between the outer force :code:`f_rad` and the sum over
        all roller forces in the direction of applied force (i.e., the
        difference between user input force and the force used for the numerical
        calculation).

    """

    if f_rad == 0:
        return np.zeros(len(ang_pos)), np.zeros(len(ang_pos)), 0

    x_axis = abs(ax_rol)
    len_roll = max(ax_rol) - min(ax_rol)
    res_x = len(x_axis)
    num_rols = len(ang_pos)
    cos_pos = np.cos(ang_pos)

    # stiffness constants according to DIN 26281
    stiff_rol = 35948 * len_roll**(8 / 9)
    stiff_slice = stiff_rol / res_x

    sum_re_ns = np.zeros(num_rols)
    psi_j = np.zeros(num_rols)
    delta_j = np.zeros(num_rols)
    sum_mns = np.zeros(num_rols)
    delta_jk = np.zeros((num_rols, res_x))
    disp_rols = np.zeros(num_rols)

    sec = [[], []]

    delta_r = rad_clear + rad_clear * 10**-6
    delta_f = 20

    while abs(delta_f) > max_dif * f_rad:
        sum_slice_disps = 0
        disp_rols = np.zeros(num_rols)

        for rol in range(num_rols):
            sum_re_ns[rol] = 0
            sum_mns[rol] = 0
            delta_j[rol] = delta_r * cos_pos[rol] - rad_clear / 2

            for idx in range(0, res_x):
                delta_jk[rol, idx] = max((delta_j[rol] - x_axis[idx] *
                                          tan(psi_j[rol]) -
                                          2 * comb_prof[idx]), 0)
                sum_re_ns[rol] += pow(delta_jk[rol, idx], (10 / 9))

            disp_rols[rol] = cos_pos[rol] * sum_re_ns[rol]
            sum_slice_disps += disp_rols[rol]

        delta_f = f_rad - stiff_slice * sum_slice_disps
        sec[0] = np.append(sec[0], [delta_r])
        sec[1] = np.append(sec[1], [delta_f])
        delta_r = __secant(sec[0], sec[1])

    f_rols = sum_re_ns * stiff_slice

    return f_rols, disp_rols, delta_f
