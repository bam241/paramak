
import warnings

import paramak


class CenterColumnStudyReactor(paramak.Reactor):
    """Creates geometry for a simple reactor that is optimised for carrying
    out parametric studies on the center column shield. Several aspects
    such as outboard magnets are intentionally missing from this reactor
    so that the model runs quickly and only includes componets that have a
    significant impact on the center column shielding. This allows the
    neutronics simulations to run quickly the column design space to be
    explored efficiently.

    Arguments:
        inner_bore_radial_thickness (float): the radial thickness of the
            inner bore (m)
        inboard_tf_leg_radial_thickness (float): the radial thickness of
            the inner leg of the toroidal field coils (m)
        center_column_shield_radial_thickness_mid (float): the radial thickness
            of the center column shield at the mid point (m)
        center_column_shield_radial_thickness_upper (float): the radial
            thickness of the center column shield at the upper point (m)
        inboard_firstwall_radial_thickness (float): the radial thickness
            of the inboard firstwall (m)
        inner_plasma_gap_radial_thickness (float): the radial thickness of
            the inboard gap between the plasma and the center column shield (m)
        plasma_radial_thickness (float): the radial thickness of the plasma (m)
        outer_plasma_gap_radial_thickness (float): the radial thickness of
            the outboard gap between the plasma and the first wall (m)
        center_column_arc_vertical_thickness (float): height of the outer
            hyperbolic profile of the center column shield.
        plasma_high_point (tuple of 2 floats): the (x,z) coordinate value of
            the top of the plasma (m)
        plasma_gap_vertical_thickness (float): the vertical thickness of
            the upper gap between the plasma and the blanket (m)
        rotation_angle (float): the angle of the sector that is desired.
            Defaults to 360.0.

    Returns:
        a paramak shape object: a Reactor object that has generic functionality
    """

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness_mid,
        center_column_shield_radial_thickness_upper,
        inboard_firstwall_radial_thickness,
        divertor_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outer_plasma_gap_radial_thickness,
        center_column_arc_vertical_thickness,
        plasma_high_point,
        plasma_gap_vertical_thickness,
        rotation_angle=360.0,
    ):

        super().__init__([])

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness_mid = center_column_shield_radial_thickness_mid
        self.center_column_shield_radial_thickness_upper = center_column_shield_radial_thickness_upper
        self.inboard_firstwall_radial_thickness = inboard_firstwall_radial_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.plasma_high_point = plasma_high_point
        self.plasma_gap_vertical_thickness = plasma_gap_vertical_thickness
        self.center_column_arc_vertical_thickness = center_column_arc_vertical_thickness
        self.rotation_angle = rotation_angle

        # these are set later by the plasma when it is created
        self.major_radius = None
        self.minor_radius = None
        self.elongation = None
        self.triangularity = None

        shapes_or_components = []

        self.rotation_angle_check()
        self.make_radial_build()
        self.make_vertical_build()
        self.make_inboard_tf_coils(shapes_or_components)
        self.make_center_column_shield(shapes_or_components)
        self.make_inboard_firstwall(shapes_or_components)
        self.make_plasma(shapes_or_components)
        self.make_outboard_blanket(shapes_or_components)
        self.make_divertor(shapes_or_components)
        self.make_component_cuts(shapes_or_components)

        self.shapes_and_components = shapes_or_components

    def rotation_angle_check(self):

        if self.rotation_angle == 360:
            warnings.warn(
                "360 degree rotation may result in a Standard_ConstructionError or AttributeError",
                UserWarning)

    def make_radial_build(self):

        # this is the radial build sequence, where one component stops and
        # another starts

        self._inner_bore_start_radius = 0
        self._inner_bore_end_radius = self._inner_bore_start_radius + \
            self.inner_bore_radial_thickness

        self._inboard_tf_coils_start_radius = self._inner_bore_end_radius
        self._inboard_tf_coils_end_radius = self._inboard_tf_coils_start_radius + \
            self.inboard_tf_leg_radial_thickness

        self._center_column_shield_start_radius = self._inboard_tf_coils_end_radius
        self._center_column_shield_end_radius_upper = self._center_column_shield_start_radius + \
            self.center_column_shield_radial_thickness_upper
        self._center_column_shield_end_radius_mid = self._center_column_shield_start_radius + \
            self.center_column_shield_radial_thickness_mid

        self._inboard_firstwall_start_radius = self._center_column_shield_end_radius_upper
        self._inboard_firstwall_end_radius = self._inboard_firstwall_start_radius + \
            self.inboard_firstwall_radial_thickness

        self._divertor_start_radius = self._inboard_firstwall_end_radius
        self._divertor_end_radius = self._divertor_start_radius + \
            self.divertor_radial_thickness

        self._inner_plasma_gap_start_radius = self._center_column_shield_end_radius_mid + \
            self.inboard_firstwall_radial_thickness

        self._inner_plasma_gap_end_radius = self._inner_plasma_gap_start_radius + \
            self.inner_plasma_gap_radial_thickness

        self._plasma_start_radius = self._inner_plasma_gap_end_radius
        self._plasma_end_radius = self._plasma_start_radius + self.plasma_radial_thickness

        self._outer_plasma_gap_start_radius = self._plasma_end_radius
        self._outer_plasma_gap_end_radius = self._outer_plasma_gap_start_radius + \
            self.outer_plasma_gap_radial_thickness

        self._outboard_blanket_start_radius = self._outer_plasma_gap_end_radius
        self._outboard_blanket_end_radius = self._outboard_blanket_start_radius + 100.

    def make_vertical_build(self):

        # this is the vertical build sequence, componets build on each other in
        # a similar manner to the radial build

        self._plasma_start_height = 0
        self._plasma_end_height = self._plasma_start_height + \
            self.plasma_high_point[1]

        self._plasma_to_blanket_gap_start_height = self._plasma_end_height
        self._plasma_to_blanket_gap_end_height = self._plasma_to_blanket_gap_start_height + \
            self.plasma_gap_vertical_thickness

        self._blanket_start_height = self._plasma_to_blanket_gap_end_height
        self._blanket_end_height = self._blanket_start_height + 100.

        self._center_column_shield_end_height = self._blanket_end_height
        self._inboard_firstwall_end_height = self._blanket_end_height

        # raises an error if the plasma high point is not above part of the
        # plasma
        if self.plasma_high_point[0] < self._plasma_start_radius:
            raise ValueError(
                "The first value in plasma high_point is too small, it should be larger than",
                self._plasma_start_radius,
            )
        if self.plasma_high_point[0] > self._plasma_end_radius:
            raise ValueError(
                "The first value in plasma high_point is too large, it should be smaller than",
                self._plasma_end_radius,
            )

    def make_inboard_tf_coils(self, shapes_or_components):

        # shapes_or_components.append(inboard_tf_coils)
        self._inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=self._blanket_end_height * 2,
            inner_radius=self._inboard_tf_coils_start_radius,
            outer_radius=self._inboard_tf_coils_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="inboard_tf_coils.stp",
            stl_filename="inboard_tf_coils.stl",
            name="inboard_tf_coils",
            material_tag="inboard_tf_coils_mat",
        )
        shapes_or_components.append(self._inboard_tf_coils)

    def make_center_column_shield(self, shapes_or_components):

        self._center_column_shield = paramak.CenterColumnShieldFlatTopHyperbola(
            height=self._center_column_shield_end_height * 2.,
            arc_height=self.center_column_arc_vertical_thickness,
            inner_radius=self._center_column_shield_start_radius,
            mid_radius=self._center_column_shield_end_radius_mid,
            outer_radius=self._center_column_shield_end_radius_upper,
            rotation_angle=self.rotation_angle)
        shapes_or_components.append(self._center_column_shield)

    def make_inboard_firstwall(self, shapes_or_components):

        self._inboard_firstwall = paramak.InboardFirstwallFCCS(
            central_column_shield=self._center_column_shield,
            thickness=self.inboard_firstwall_radial_thickness,
            rotation_angle=self.rotation_angle)
        shapes_or_components.append(self._inboard_firstwall)

    def make_plasma(self, shapes_or_components):

        self._plasma = paramak.PlasmaFromPoints(
            outer_equatorial_x_point=self._plasma_end_radius,
            inner_equatorial_x_point=self._plasma_start_radius,
            high_point=self.plasma_high_point,
            rotation_angle=self.rotation_angle,
        )

        self.major_radius = self._plasma.major_radius
        self.minor_radius = self._plasma.minor_radius
        self.elongation = self._plasma.elongation
        self.triangularity = self._plasma.triangularity

        shapes_or_components.append(self._plasma)

    def make_outboard_blanket(self, shapes_or_components):

        center_column_cutter = paramak.CenterColumnShieldCylinder(
            height=self._inboard_firstwall_end_height * 2.5,  # extra 0.5 to ensure overlap,
            inner_radius=0,
            outer_radius=self._inboard_firstwall_end_radius,
            rotation_angle=self.rotation_angle
        )

        self._blanket = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=100.,
            offset_from_plasma=[
                self.inner_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                self.outer_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                self.inner_plasma_gap_radial_thickness],
            start_angle=-179,
            stop_angle=179,
            rotation_angle=self.rotation_angle,
            cut=center_column_cutter
        )

    def make_divertor(self, shapes_or_components):

        self._divertor = paramak.CenterColumnShieldCylinder(
            height=self._center_column_shield_end_height *
            2.5,  # extra 0.5 to ensure overlap
            inner_radius=self._divertor_start_radius,
            outer_radius=self._divertor_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat",
            intersect=self._blanket,
        )
        shapes_or_components.append(self._divertor)

    def make_component_cuts(self, shapes_or_components):

        # the divertor is cut away then the blanket can be added to the
        self._blanket.solid = self._blanket.solid.cut(self._divertor.solid)
        shapes_or_components.append(self._blanket)
