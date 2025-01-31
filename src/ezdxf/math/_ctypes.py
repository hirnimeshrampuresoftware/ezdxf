#  Copyright (c) 2020-2021, Manfred Moitzi
#  License: MIT License
from ezdxf.acc import USE_C_EXT

__all__ = [
    "Vec3",
    "Vec2",
    "X_AXIS",
    "Y_AXIS",
    "Z_AXIS",
    "NULLVEC",
    "distance",
    "lerp",
    "Matrix44",
    "Bezier4P",
    "Bezier3P",
    "Basis",
    "Evaluator",
    "cubic_bezier_arc_parameters",
    "cubic_bezier_from_arc",
    "cubic_bezier_from_ellipse",
    "has_clockwise_orientation",
    "intersection_line_line_2d",
    "intersection_ray_ray_3d",
    "arc_angle_span_deg",
    "arc_angle_span_rad",
]
# Import of Python or Cython implementations:
if USE_C_EXT:
    from ezdxf.acc.vector import (
        Vec3,
        Vec2,
        X_AXIS,
        Y_AXIS,
        Z_AXIS,
        NULLVEC,
        distance,
        lerp,
    )
    from ezdxf.acc.matrix44 import Matrix44
    from ezdxf.acc.bezier4p import (
        Bezier4P,
        cubic_bezier_arc_parameters,
        cubic_bezier_from_arc,
        cubic_bezier_from_ellipse,
    )
    from ezdxf.acc.bezier3p import Bezier3P
    from ezdxf.acc.bspline import Basis, Evaluator
    from ezdxf.acc.construct import (
        has_clockwise_orientation,
        intersection_line_line_2d,
        intersection_ray_ray_3d,
        arc_angle_span_deg,
        arc_angle_span_rad,
    )
else:
    from ._vector import (
        Vec3,
        Vec2,
        X_AXIS,
        Y_AXIS,
        Z_AXIS,
        NULLVEC,
        distance,
        lerp,
    )
    from ._matrix44 import Matrix44
    from ._bezier4p import (
        Bezier4P,
        cubic_bezier_arc_parameters,
        cubic_bezier_from_arc,
        cubic_bezier_from_ellipse,
    )
    from ._bezier3p import Bezier3P
    from ._bspline import Basis, Evaluator
    from ._construct import (
        has_clockwise_orientation,
        intersection_line_line_2d,
        intersection_ray_ray_3d,
        arc_angle_span_deg,
        arc_angle_span_rad,
    )
