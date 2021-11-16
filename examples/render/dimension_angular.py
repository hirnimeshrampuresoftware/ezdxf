# Purpose: using angular DIMENSION
# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Optional
import pathlib
import math
import ezdxf
from ezdxf.math import Vec3, UCS, NULLVEC
import logging

# ========================================
# Setup logging
# ========================================
logging.basicConfig(level="WARNING")

# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

# ========================================
# Default text attributes
# ========================================
TEXT_ATTRIBS = {
    "height": 0.25,
    "style": ezdxf.options.default_dimension_text_style,
}
DIM_TEXT_STYLE = ezdxf.options.default_dimension_text_style

# =======================================================
# Discarding dimension rendering is possible
# for BricsCAD, but is incompatible to AutoCAD -> error
# =======================================================
BRICSCAD = False


def locations():
    def location(offset: Vec3, flip: float):
        base = Vec3(0, 5) + offset
        p1 = Vec3(-4, 3 * flip) + offset
        p2 = Vec3(-1, 0) + offset
        p4 = Vec3(4, 3 * flip) + offset
        p3 = Vec3(1, 0) + offset
        return base, (p1, p2), (p3, p4)

    return [
        location(NULLVEC, +1),
        location(Vec3(10, 0), -1),
    ]


def angular_cra_default(dxfversion="R2013"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    radius = 5
    distance = 2
    data = [
        [Vec3(0, 0), 60, 120],
        [Vec3(10, 0), 300, 240],
        [Vec3(20, 0), 240, 300],
        [Vec3(30, 0), 300, 30],
    ]
    for name, dimtad, offset in [
        ["above", 1, Vec3(0, 20)],
        ["center", 0, Vec3(0, 0)],
        ["below", 4, Vec3(0, -20)],
    ]:
        for center, start_angle, end_angle in data:
            center += offset
            add_lines(msp, center, radius, start_angle, end_angle)
            # Default DimStyle EZ_CURVED:
            # - angle units = degree
            # - scale 1: 100
            # - closed filled arrow, size = 0.25
            # - text location above dimension line
            #
            # center:
            #   center of angle
            # radius:
            #   distance from center to the start of the extension lines
            # distance:
            #   distance from start of the extension lines to the dimension line
            # start_angle:
            #   start angle in degrees
            # end_angle:
            #   end angle in degrees
            # The measurement is always done from start_angle to end_angle in
            # counter clockwise orientation. This does not always match the result
            # in CAD applications!
            dim = msp.add_angular_dim_cra(
                center,
                radius,
                start_angle,
                end_angle,
                distance,
                override={"dimtad": dimtad},
            )
            # Necessary second step, to create the BLOCK entity with the DIMENSION
            # geometry. Ezdxf supports DXF R2000 attributes for DXF R12 rendering,
            # but they have to be applied by the DIMSTYLE override feature, this
            # additional attributes are not stored in the XDATA section of the
            # DIMENSION entity, they are just used to render the DIMENSION entity.
            # The return value `dim` is not a DIMENSION entity, instead a
            # DimStyleOverride object is returned, the DIMENSION entity is stored
            # as dim.dimension, see also ezdxf.override.DimStyleOverride class.
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"dim_angular_cra_{dxfversion}_default.dxf")


def angular_3p_default(dxfversion="R2013"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    radius = 5
    distance = 2
    data = [
        [Vec3(0, 0), 60, 120],
        [Vec3(10, 0), 300, 240],
        [Vec3(20, 0), 240, 300],
    ]
    for name, dimtad, offset in [
        ["above", 1, Vec3(0, 20)],
        ["center", 0, Vec3(0, 0)],
        ["below", 4, Vec3(0, -20)],
    ]:
        for center, start_angle, end_angle in data:
            center += offset
            dir1 = Vec3.from_deg_angle(start_angle)
            dir2 = Vec3.from_deg_angle(end_angle)

            # calculate defpoints from parameters of the "cra" example:
            p1 = center + dir1 * radius
            p2 = center + dir2 * radius
            base = center + dir1.lerp(dir2) * (radius + distance)

            add_lines(msp, center, radius, start_angle, end_angle)
            msp.add_angular_dim_3p(
                base,
                center,
                p1,
                p2,
                override={"dimtad": dimtad},
            ).render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"dim_angular_3p_{dxfversion}_default.dxf")


def angular_2l_default(dxfversion="R2013"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for base, line1, line2 in locations():
        msp.add_line(line1[0], line1[1])
        msp.add_line(line2[0], line2[1])
        msp.add_angular_dim_2l(
            base=base, line1=line1, line2=line2, dimstyle="EZ_CURVED"
        ).render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=30)
    doc.saveas(OUTDIR / f"dim_angular_2l_{dxfversion}_default.dxf")


def add_lines(
    msp, center: Vec3, radius: float, start_angle: float, end_angle: float
):
    attribs = {"color": 1}
    start_point = center + Vec3.from_deg_angle(start_angle) * radius
    end_point = center + Vec3.from_deg_angle(end_angle) * radius
    msp.add_line(center, start_point, dxfattribs=attribs)
    msp.add_line(center, end_point, dxfattribs=attribs)


def angular_3d(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()

    for base, line1, line2 in locations():
        ucs = UCS(origin=(base.x, base.y, 0)).rotate_local_x(math.radians(45))

        msp.add_line(line1[0], line1[1]).transform(ucs.matrix)
        msp.add_line(line2[0], line2[1]).transform(ucs.matrix)

        dim = msp.add_angular_dim_2l(
            base=base, line1=line1, line2=line2, dimstyle="EZ_CURVED"
        )
        dim.render(discard=BRICSCAD, ucs=ucs)

    doc.set_modelspace_vport(height=30)
    doc.saveas(OUTDIR / f"dim_angular_{dxfversion}_3d.dxf")


def angular_units_tol_limits(dxfversion="R2013"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    radius = 5
    distance = 2
    data = [
        [Vec3(0, 0), 60, 120, 0, 0],
        [Vec3(10, 0), 300, 240, 0, 0],
        [Vec3(20, 0), 240, 300, 1, 0],  # tolerance
        [Vec3(30, 0), 300, 30, 0, 1],  # limits
    ]
    for dimaunit, offset in [
        [0, Vec3(0, 0)],
        [1, Vec3(0, 20)],
        [2, Vec3(0, 40)],
        [3, Vec3(0, 60)],
    ]:
        for center, start_angle, end_angle, dimtol, dimlim in data:
            center += offset
            add_lines(msp, center, radius, start_angle, end_angle)
            dim = msp.add_angular_dim_cra(
                center,
                radius,
                start_angle,
                end_angle,
                distance,
                override={
                    "dimaunit": dimaunit,
                    "dimtol": dimtol,
                    "dimtp": 1.0,
                    "dimtm": 2.0,
                    "dimlim": dimlim,
                },
            )
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"dim_angular_units_tol_limits_{dxfversion}.dxf")


def add_angle_dim(
    msp,
    center: Vec3,
    angle: float,
    delta: float,
    radius: float,
    distance: float,
    text_rotation: Optional[float],
    override: dict,
):
    start_angle = angle - delta
    end_angle = angle + delta
    add_lines(msp, center, radius, start_angle, end_angle)
    dim = msp.add_angular_dim_cra(
        center,
        radius,
        start_angle,
        end_angle,
        distance,
        text_rotation=text_rotation,
        override=override,
    )
    return dim


def measure_fixed_angle(angle: float, dxfversion="R2013"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    x_dist = 15
    for dimtad, y_dist in [[0, 0], [1, 20], [4, 40]]:
        for count in range(8):
            dim = add_angle_dim(
                msp,
                center=Vec3(x_dist * count, y_dist),
                angle=45.0 * count,
                delta=angle / 2.0,
                radius=3.0,
                distance=1.0,
                text_rotation=None,
                override={"dimtad": dimtad},
            )
            dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=100, center=(x_dist * 4, 20))
    doc.saveas(OUTDIR / f"dim_angular_{angle:.0f}_deg_{dxfversion}.dxf")


def usr_location_absolute(
    angle: float, rotation: float = None, dxfversion="R2013"
):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    x_dist = 15
    radius = 3.0
    distance = 1.0
    for dimtad, y_dist, leader in [
        [0, 0, False],
        [0, 20, True],
        [4, 40, True],
    ]:
        for count in range(8):
            center = Vec3(x_dist * count, y_dist)
            main_angle = 45.0 * count
            dim = add_angle_dim(
                msp,
                center=center,
                angle=main_angle,
                delta=angle / 2.0,
                radius=radius,
                distance=distance,
                text_rotation=rotation,
                override={"dimtad": dimtad},
            )
            # user location in WCS coordinates, absolut location:
            usr_location = center + Vec3.from_deg_angle(
                main_angle, radius + distance * 2.0
            )
            dim.set_location(usr_location, leader=leader)
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=100, center=(x_dist * 4, 40))
    rstr = ""
    if rotation is not None:
        rstr = f"rot_{rotation}_"
    doc.saveas(OUTDIR / f"dim_angular_usr_loc_absolute_{rstr}{dxfversion}.dxf")


def usr_location_relative(
    angle: float, rotation: float = None, dxfversion="R2013"
):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    x_dist = 15
    radius = 3.0
    distance = 1.0
    for dimtad, y_dist, leader in [
        [0, 0, False],
        [0, 20, True],
        [4, 40, True],
    ]:
        for count in range(8):
            center = Vec3(x_dist * count, y_dist)
            main_angle = 45.0 * count
            dim = add_angle_dim(
                msp,
                center=center,
                angle=main_angle,
                delta=angle / 2.0,
                radius=radius,
                distance=distance,
                text_rotation=rotation,
                override={"dimtad": dimtad},
            )
            # user location relative to center of dimension line:
            usr_location = Vec3.from_deg_angle(main_angle, 2.0)
            dim.set_location(usr_location, leader=leader, relative=True)
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=100, center=(x_dist * 4, 40))
    rstr = ""
    if rotation is not None:
        rstr = f"rot_{rotation}_"
    doc.saveas(OUTDIR / f"dim_angular_usr_loc_relative_{rstr}{dxfversion}.dxf")


def show_all_arrow_heads(dxfversion="R2013"):
    # The ezdxf arrow head blocks were designed for linear dimensions and do not
    # work well with curved dimension lines.
    # This are the arrow heads which look correct for arrows placed inside and
    # outside for curved dimension lines:
    # - closed_filled
    # - closed_filled
    # - closed_black
    # - architectural_tick
    # - dot_small
    # - dot_small_blank
    # - integral
    # - none
    # - oblique

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    x_dist = 15.0
    y_dist = 6.0
    for x, arrow_name in enumerate(sorted(ezdxf.ARROWS.__all_arrows__)):
        for y, angle in enumerate((3.0, 30.0)):
            center = Vec3(x * x_dist, y * y_dist)
            dim = add_angle_dim(
                msp,
                center=center,
                angle=90.0,
                delta=angle / 2.0,
                radius=3.0,
                distance=1.0,
                text_rotation=None,
                override={"dimblk": arrow_name},
            )
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=100, center=(50, 5))
    doc.saveas(OUTDIR / f"dim_angular_all_arrows_{dxfversion}.dxf")


if __name__ == "__main__":
    angular_cra_default()
    angular_3p_default()
    angular_2l_default()
    angular_3d()
    angular_units_tol_limits()
    measure_fixed_angle(3.0)
    measure_fixed_angle(6.0)
    measure_fixed_angle(9.0)
    usr_location_absolute(6)
    usr_location_absolute(6, rotation=15)
    usr_location_relative(30)
    usr_location_relative(30, rotation=345)
    show_all_arrow_heads()
