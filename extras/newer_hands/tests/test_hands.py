import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import importlib.util
spec = importlib.util.spec_from_file_location("hand_pose", pathlib.Path(__file__).resolve().parents[1] / "app/ui/widgets/hand_pose.py")
hp = importlib.util.module_from_spec(spec); spec.loader.exec_module(hp)


def test_rest_pose_on_home_row():
    pose, _ = hp.compute_pose()
    assert pose["L"]["L2"][1] == (5.25, 2.5) and pose["R"]["R2"][1] == (8.25, 2.5)
    assert abs(pose["L"]["L5"][1][0] + pose["R"]["R5"][1][0] - 13.5) < 1e-9  # mirrored


def test_active_finger_reaches_key_within_limits():
    for fid, target in (("L2", (4.5, 0.5)), ("R5", (12.5, 0.5)), ("L3", (2.5, 3.5)), ("TR", (6.5, 4.5))):
        pose, _ = hp.compute_pose(fid, target)
        base, tip, _w = pose[fid[0] if fid[0] in "LR" else "R"][fid] if fid != "TR" else pose["R"]["TR"]
        assert math.dist(base, tip) <= 6.0
        assert math.dist(tip, target) < 0.6, (fid, tip, target)


def test_shift_pinky_goes_to_shift_key():
    pose, _ = hp.compute_pose("R2", (7.5, 3.5), shift_fid="L5")
    assert math.dist(pose["L"]["L5"][1], hp.SHIFT_CENTER["L5"]) < 1.0


def test_perspective_keeps_bottom_and_shrinks_top():
    spec2 = importlib.util.spec_from_file_location("perspective", pathlib.Path(__file__).resolve().parents[1] / "app/ui/widgets/perspective.py")
    pm = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(pm)
    m = pm.perspective_matrix(800, 400)
    bl, br = pm.project(m, 0, 400), pm.project(m, 800, 400)
    tl, tr = pm.project(m, 0, 0), pm.project(m, 800, 0)
    assert abs(bl[0]) < 1e-6 and abs(bl[1] - 400) < 1e-6 and abs(br[0] - 800) < 1e-6   # bottom edge fixed
    assert (tr[0] - tl[0]) < 800 * 0.95 and tl[1] > 0                                    # top narrower, pushed down
    assert abs((tl[0] + tr[0]) / 2 - 400) < 1e-6                                         # stays centred


def test_finger_outline_is_closed_and_reaches_tip():
    sp = importlib.util.spec_from_file_location("hand_shapes", pathlib.Path(__file__).resolve().parents[1] / "app/ui/widgets/hand_shapes.py")
    hs = importlib.util.module_from_spec(sp); sp.loader.exec_module(hs)
    cmds = hs.finger_cmds("L3", (4.35, 6.3), (4.25, 2.5), 0.9)
    pts = hs.sample(cmds)
    assert cmds[-1] == ("Z",) and min(y for _, y in pts) < 2.5          # fingertip cap extends past the tip point
    palm = hs.sample(hs.smooth_closed([(0, 0), (4, 0), (4, 4), (0, 4)]))
    assert len(palm) > 8


def test_hands_stay_anchored_on_home_row_only_active_finger_reaches():
    rest, rest_palms = hp.compute_pose()
    for fid, target in (("L2", (4.5, 0.5)), ("R5", (14.0, 1.5)), ("L3", (2.5, 3.5)), ("R2", (7.5, 0.5))):
        pose, palms = hp.compute_pose(fid, target)
        hand = fid[0]
        for f, (b, t, _w) in pose[hand].items():
            b0, t0, _ = rest[hand][f]
            assert math.dist(b, b0) <= 0.5                       # knuckles stay put (tiny sway only)
            if f != fid:
                assert math.dist(t, t0) <= 0.5, (fid, f)           # other fingers stay on the home row
        assert math.dist(pose[hand][fid][1], target) < 0.6         # the active finger reaches the key
        other = "R" if hand == "L" else "L"
        assert pose[other] == rest[other]                          # the other hand does not move at all


def test_blend_pose_endpoints():
    a, b = hp.compute_pose(), hp.compute_pose("L2", (4.5, 0.5))
    assert hp.blend_pose(a, b, 0.0)[0] == a[0] and hp.blend_pose(a, b, 1.0)[0]["L"]["L2"][1] == b[0]["L"]["L2"][1]


def test_finger_point_endpoints():
    sp = importlib.util.spec_from_file_location("hand_shapes2", pathlib.Path(__file__).resolve().parents[1] / "app/ui/widgets/hand_shapes.py")
    hs = importlib.util.module_from_spec(sp); sp.loader.exec_module(hs)
    b, t = (4.35, 6.3), (4.25, 2.5)
    assert hs.finger_point("L3", b, t, 0.9, 0.0) == b
    x, y = hs.finger_point("L3", b, t, 0.9, 1.0)
    assert abs(y - 2.5) < 0.1                      # tip lands on the target (curve only shifts sideways)
