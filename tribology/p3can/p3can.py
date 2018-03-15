"""

**Note: The P3CAN project is currently not maintained!**

The P3CAN project aimed to develop a Python 3 implementation of an open source
multi-purpose (tribology) contact analyzer, both for research and higher level
educational purposes. However, due to its monolithic structure it proved hard
to maintain, and it can be hard for new users to understand the code in its
entirety.

**The P3CAN project precedes the** :code:`tribology` **package and many of its
functions and functionalities have since been integrated into the package. This
work will be continued in the future.**

Simply put, P3CAN can be used to calculate parameters such
as contact pressure, load distribution and friction energy for various
tribological systems.

P3can currently provides implementations of the following tribological systems:
- radial roller bearings
- axial thrust roller bearings
- pin-on-disk
- 4-ball
- ball-on-3-plates
- ring-on-ring

You can run P3CAN by calling it with a program specific input file. Templates
for user input files can be generated using the `generate_input_file`
function below.

For more information on the P3CAN project, please refer to its GitHub page:
https://github.com/moritzploss/p3can

"""

import os
import shutil

from BluPrintSim import Sim
from Constants import SimType
from generate_latex_output import generate_latex_output
from influ_matrix_management import make_infl_mat_db, manage_influ_mat_cache
from setup_tribosystem import setup_cyl_rol_bearing, \
    setup_deep_gro_ball_bearing, setup_cyl_rol_thrust_bearing, \
    setup_ball_on_disk, setup_pin_on_disk, setup_four_ball, \
    setup_ball_on_three_plates, setup_ring_on_ring
from system_functions import exit_program, print_it, in_d


def p3can(in_file='USER_INPUT.py', out_dir=None):
    """

    Start a P3CAN simulation run.

    Parameters
    ----------
    in_file: str, optional
        The file path of the P3CAN input file. The default value is
        `USER_INPUT.py`. You can generate `in_file` templates for different
        tribological systems using the `generate_input_file` function.
    out_dir: str
        The directory in which output files will be stored. A folder named
        `results` will be created in `out_dir`. The `results` folder then
        contains a simulation-specific folder containing all outputs. Default
        is the current working directory.

    Returns
    -------
    sim.res_dir: str
        The path to the simulation-specific results folder. The path is:

        `out_dir`/results/<unique simulation name>

        The unique simulation name is automatically generated by P3CAN.

    """

    if not out_dir:
        out_dir = os.getcwd()

    # set-up a simulation
    sim = Sim(in_file, out_dir)
    sim.mk_uniq_parameter_id()
    sim.infl_db_file_hand = make_infl_mat_db(os.path.dirname(sim.res_dir))
    tribo_system = None

    # generate a tribosystem based on user input
    print_it('initialising contact bodies')
    if sim.simulation_type == SimType.cyl_rol_bearing.value:
        roller, ring1, ring2, tribo_system = setup_cyl_rol_bearing(sim.ui)
    elif sim.simulation_type == SimType.deep_gro_ball_bearing.value:
        setup_deep_gro_ball_bearing(sim.ui)
    elif sim.simulation_type == SimType.cyl_rol_thrust_bearing.value:
        roller, ring1, ring2, tribo_system = setup_cyl_rol_thrust_bearing(
            sim.ui)
    elif sim.simulation_type == SimType.ball_on_disk.value:
        ball, disk, tribo_system = setup_ball_on_disk(sim.ui)
    elif sim.simulation_type == SimType.pin_on_disk.value:
        pin, disk, tribo_system = setup_pin_on_disk(sim.ui)
    elif sim.simulation_type == SimType.four_ball.value:
        rot_ball, stat_ball, tribo_system = setup_four_ball(sim.ui)
    elif sim.simulation_type == SimType.ball_on_three_plates.value:
        ball, plate, tribo_system = setup_ball_on_three_plates(sim.ui)
    elif sim.simulation_type == SimType.ring_on_ring.value:
        sun, planet, tribo_system = setup_ring_on_ring(sim.ui)
    else:
        exit_program("'simulation_type' option '{}'not defined".format(
            sim.simulation_type))

    # simulate tribosystem
    tribo_system.calc_load_distribution(sim.ui, sim.res_dir)
    tribo_system.calc_contact_pressure(sim.ui, sim.res_dir)
    tribo_system.calc_kinematics(in_d('rot_velocity1', sim.ui, 0),
                                 in_d('rot_velocity2', sim.ui, 0),
                                 sim.ui, sim.res_dir)
    tribo_system.calc_pv(sim.ui, sim.res_dir)
    tribo_system.calc_e_akin(sim.ui, sim.res_dir)

    # generate output plots and pdf report
    if sim.auto_plot is True:
        tribo_system.plot_it(sim.ui, sim.res_dir)
    if sim.auto_report is True:
        generate_latex_output(sim, tribo_system, sim.ui, sim.res_dir)

    # manage the influence matrix cache
    manage_influ_mat_cache(sim.res_dir)

    # finish simulation
    sim.finished()
    return sim.res_dir


def generate_input_file(temp_type, out_file):
    """

    Generate a P3CAN input file based on a user input template.

    Parameters
    ----------
    temp_type: int
        Specifies which type of user input template will be generated:

        0:  complete set of available parameters

        1:  template for single row cylindrical roller bearings

        3:  template for cylindrical roller thrust bearings

        4:  template for ball-on-disk setup

        5:  template for pin-on-disk setup

        6:  template for 4-ball setup

        7:  template for ball-on-3-plates setup

        8:  template for ring-on-ring setup

    out_file: str
        The complete file path of the output file.

    Returns
    -------
    out_file: str
        The complete file path of the output file.

    """

    file_path = os.path.realpath(__file__)
    dir_path = os.sep.join(file_path.split(os.sep)[:-1])

    if temp_type == 0:
        template = 'Template00_CompleteParameters.py'
    elif temp_type == 1:
        template = 'Template01_SingleRowCylindricalRollerBearing.py'
    elif temp_type == 3:
        template = 'Template03_CylindricalRollerThustBearing.py'
    elif temp_type == 4:
        template = 'Template04_BallOnDisk.py'
    elif temp_type == 5:
        template = 'Template05_PinOnDisk.py'
    elif temp_type == 6:
        template = 'Template06_4Ball.py'
    elif temp_type == 7:
        template = 'Template07_BallOn3Plates.py'
    elif temp_type == 8:
        template = 'Template08_RingOnRing.py'
    else:
        raise ValueError("temp_type value '{}' undefined".format(temp_type))

    shutil.copy(os.sep.join([dir_path, 'UserInputTemplates', template]),
                out_file)
    return out_file


if __name__ == "__main__":
    pass