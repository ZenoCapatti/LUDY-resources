import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import json

    import marimo as mo
    from wigglystuff import ManimWeb

    return ManimWeb, json, mo


@app.cell(hide_code=True)
def _(mo):
    get_collinear_e2, set_collinear_e2 = mo.state(2.0)
    return get_collinear_e2, set_collinear_e2


@app.cell(hide_code=True)
def _(mo):
    q1_energy = mo.ui.slider(
        start=0.25,
        stop=4.0,
        step=0.05,
        value=1.0,
        label=r"$E_1$",
        show_value=True,
        include_input=True,
        debounce=True,
    )

    mass_squared = mo.ui.slider(
        start=0.0,
        stop=16.0,
        step=0.05,
        value=4.0,
        label=r"$M_0^2$",
        show_value=True,
        include_input=True,
        debounce=True,
    )

    soft_start_angle = mo.ui.slider(
        start=5.0,
        stop=175.0,
        step=1.0,
        value=90.0,
        label=r"Soft starting angle $\theta_s$",
        show_value=True,
        include_input=True,
        debounce=True,
    )

    show_full_cones = mo.ui.checkbox(
        value=False,
        label="Show full cones",
    )
    return mass_squared, q1_energy, show_full_cones, soft_start_angle


@app.cell(hide_code=True)
def _(
    get_collinear_e2,
    mass_squared,
    mo,
    q1_energy,
    set_collinear_e2,
):
    _e1 = float(q1_energy.value)
    _m2 = float(mass_squared.value)

    # This is the minimum allowed E2, not the maximum.
    _e2_min = _m2 / (4.0 * _e1)
    _e2_stop = max(4.0, _e2_min + 0.05)

    # Preserve the user's absolute E2 choice across temporary clamps.
    _e2_requested = float(get_collinear_e2())
    _e2_displayed = min(
        _e2_stop,
        max(_e2_min, _e2_requested),
    )

    if _e2_requested < _e2_min:
        _collinear_label = (
            f"Collinear E2: requested {_e2_requested:.3f}, "
            f"temporarily using {_e2_displayed:.3f}"
        )
    else:
        _collinear_label = (
            f"Collinear starting E2 "
            f"(minimum {_e2_min:.3f})"
        )

    collinear_start_e2 = mo.ui.slider(
        start=_e2_min,
        stop=_e2_stop,
        step=0.05,
        value=_e2_displayed,
        on_change=set_collinear_e2,
        label=_collinear_label,
        show_value=True,
        include_input=True,
        debounce=True,
    )
    return (collinear_start_e2,)


@app.cell(hide_code=True)
def _(
    collinear_start_e2,
    mass_squared,
    mo,
    q1_energy,
    show_full_cones,
    soft_start_angle,
):
    mo.vstack([
        mo.hstack([
            q1_energy,
            mass_squared,
            show_full_cones,
        ]),
        collinear_start_e2,
        soft_start_angle,
    ])
    return


@app.cell(hide_code=True)
def _(
    ManimWeb,
    collinear_start_e2,
    json,
    mass_squared,
    mo,
    q1_energy,
    show_full_cones,
    soft_start_angle,
):
    _params = json.dumps(
        {
            "E1": float(q1_energy.value),
            "M20": float(mass_squared.value),
            "E20": float(collinear_start_e2.value),
            "theta0Deg": float(soft_start_angle.value),
            "fullCones": bool(show_full_cones.value),
        }
    )

    _scene_code = r"""
    const params = __PARAMS__;

    const E1 = params.E1;
    const M20 = params.M20;
    const E20 = params.E20;
    const theta0 = params.theta0Deg * Math.PI / 180;
    const fullCones = params.fullCones;

    const EPS = 1e-10;
    const TAU = 2 * Math.PI;
    const N = 80;

    const angularExtent = fullCones ? TAU : Math.PI;
    const angularResolution = fullCones ? 40 : 20;

    const softStartE2 = M20 <= EPS
        ? 0
        : M20 / (2 * E1 * (1 - Math.cos(theta0)));

    const startingEnergy = Math.max(
        E1 + E20,
        E1 + softStartE2,
        E1,
        0.25
    );
    const originConeExtent = 1.30 * startingEnergy;

    const shiftedConeExtent = Math.max(
        1.35 * E20,
        1.35 * softStartE2,
        0.20 * startingEnergy
    );

    const displayEnergyMax = Math.max(
        originConeExtent,
        E1 + shiftedConeExtent
    );

    const scale = 4.3 / displayEnergyMax;

    const W = (pz, px, energy) => [
        scale * pz,
        scale * px,
        scale * energy,
    ];

    const origin = W(0, 0, 0);
    const q1Point = W(E1, 0, E1);

    const clamp = (x, lo, hi) =>
        Math.max(lo, Math.min(hi, x));

    const distance = (a, b) => Math.sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    );

    const scene = new manim.ThreeDScene(container, {
        width,
        height,
        backgroundColor: "#07090d",
        phi: 68 * Math.PI / 180,
        theta: -42 * Math.PI / 180,
        distance: 14,
        fov: 31,
        enableOrbitControls: true,
        orbitControlsUp: "z",
    });

    scene.lighting.removeAll();
    scene.lighting.addAmbient({ intensity: 0.9 });
    scene.lighting.addPoint({
        position: [3, 5, 8],
        intensity: 1.5,
        decay: 0,
    });

    const axes = new manim.ThreeDAxes({
        xRange: [-4.7, 4.7, 1],
        yRange: [-4.7, 4.7, 1],
        zRange: [0, 4.7, 1],
        axisColor: "#343943",
        tipLength: 0.19,
        tipRadius: 0.07,
        shaftRadius: 0.004,
    });

    function addSegment(group, start, end, color) {
        if (distance(start, end) > 1e-7) {
            group.add(new manim.Line3D({
                start,
                end,
                color,
            }));
        }
    }

    function polyline(points, color) {
        const group = new manim.VGroup();

        for (let i = 0; i < points.length - 1; ++i) {
            addSegment(
                group,
                points[i],
                points[i + 1],
                color
            );
        }

        return group;
    }

    function appendGroup(target, source) {
        for (const item of source.submobjects) {
            target.add(item);
        }
    }

    function ringPoints(
        centerPz,
        centerPx,
        energy,
        radius,
        count = angularResolution
    ) {
        const points = [];

        for (let i = 0; i <= count; ++i) {
            const phi = angularExtent * i / count;

            points.push(W(
                centerPz + radius * Math.cos(phi),
                centerPx + radius * Math.sin(phi),
                energy
            ));
        }

        return points;
    }

    function makeConeWireframe(
        apexPz,
        apexPx,
        apexEnergy,
        maxRadius,
        color
    ) {
        const group = new manim.VGroup();

        for (let ring = 1; ring <= 3; ++ring) {
            const radius = maxRadius * ring / 3;

            appendGroup(
                group,
                polyline(
                    ringPoints(
                        apexPz,
                        apexPx,
                        apexEnergy + radius,
                        radius
                    ),
                    color
                )
            );
        }

        const meridians = fullCones ? 12 : 6;

        for (let i = 0; i <= meridians; ++i) {
            const phi = angularExtent * i / meridians;

            addSegment(
                group,
                W(apexPz, apexPx, apexEnergy),
                W(
                    apexPz + maxRadius * Math.cos(phi),
                    apexPx + maxRadius * Math.sin(phi),
                    apexEnergy + maxRadius
                ),
                color
            );
        }

        return group;
    }

    const finalCone = new manim.Surface3D({
        func: (r, phi) => W(
            r * Math.cos(phi),
            r * Math.sin(phi),
            r
        ),
        uRange: [0, originConeExtent],
        vRange: [0, angularExtent],
        uResolution: 13,
        vResolution: angularResolution,
        checkerboardColors: ["#24558f", "#3274b8"],
        opacity: 0.22,
    });

    const shiftedCone = new manim.Surface3D({
        func: (r, phi) => W(
            E1 + r * Math.cos(phi),
            r * Math.sin(phi),
            E1 + r
        ),
        uRange: [0, shiftedConeExtent],
        vRange: [0, angularExtent],
        uResolution: 13,
        vResolution: angularResolution,
        checkerboardColors: ["#9a5f24", "#c77c2d"],
        opacity: 0.22,
    });

    const finalConeWireframe = makeConeWireframe(
        0,
        0,
        0,
        originConeExtent,
        "#30435c"
    );

    const shiftedConeWireframe = makeConeWireframe(
        E1,
        0,
        E1,
        shiftedConeExtent,
        "#584834"
    );

    const tracker = new manim.ValueTracker(M20);

    const shellRadiusMax = Math.sqrt(
        Math.max(
            displayEnergyMax * displayEnergyMax - M20,
            0
        )
    );

    function shellPoint(radius, phi, mu2) {
        return W(
            radius * Math.cos(phi),
            radius * Math.sin(phi),
            Math.sqrt(radius * radius + mu2)
        );
    }

    const movingMassWireframe = new manim.VGroup();

    function addMovingShellSegment(
        radius0,
        phi0,
        radius1,
        phi1
    ) {
        const line = new manim.Line3D({
            start: shellPoint(radius0, phi0, M20),
            end: shellPoint(radius1, phi1, M20),
            color: "#607779",
        });

        line.addUpdater((mob) => {
            const mu2 = tracker.getValue();

            mob.setStart(
                shellPoint(radius0, phi0, mu2)
            );

            mob.setEnd(
                shellPoint(radius1, phi1, mu2)
            );
        });

        movingMassWireframe.add(line);
    }

    const meridianCount = fullCones ? 10 : 5;
    const radialSegments = 18;

    for (let i = 0; i < meridianCount; ++i) {
        const meridianDivisor = fullCones
            ? meridianCount
            : meridianCount - 1;
        const phi = angularExtent * i / meridianDivisor;

        for (let j = 0; j < radialSegments; ++j) {
            const radius0 =
                shellRadiusMax * j / radialSegments;

            const radius1 =
                shellRadiusMax * (j + 1) / radialSegments;

            addMovingShellSegment(
                radius0,
                phi,
                radius1,
                phi
            );
        }
    }

    const ringCount = 3;
    const angularSegments = fullCones ? 48 : 24;

    for (let ring = 1; ring <= ringCount; ++ring) {
        const radius =
            shellRadiusMax * ring / ringCount;

        for (let j = 0; j < angularSegments; ++j) {
            const phi0 =
                angularExtent * j / angularSegments;

            const phi1 =
                angularExtent * (j + 1) / angularSegments;

            addMovingShellSegment(
                radius,
                phi0,
                radius,
                phi1
            );
        }
    }

    const shellConeIntersection = new manim.VGroup();
    const intersectionSegments = 64;

    function intersectionPoint(index, mu2) {
        if (mu2 <= EPS) {
            return q1Point;
        }

        const minimumCosine = clamp(
            1 - mu2 / (2 * E1 * shiftedConeExtent),
            -1,
            1
        );
        const minimumAngle = Math.acos(minimumCosine);
        const maximumAngle = fullCones
            ? TAU - minimumAngle
            : Math.PI;
        const angle = minimumAngle
            + (maximumAngle - minimumAngle)
            * index / intersectionSegments;
        const energy2 = mu2
            / (2 * E1 * (1 - Math.cos(angle)));

        return W(
            E1 + energy2 * Math.cos(angle),
            energy2 * Math.sin(angle),
            E1 + energy2
        );
    }

    for (let i = 0; i < intersectionSegments; ++i) {
        const segment = new manim.Line3D({
            start: intersectionPoint(i, M20),
            end: intersectionPoint(i + 1, M20),
            color: "#ffd166",
        });

        segment.addUpdater((mob) => {
            const mu2 = tracker.getValue();

            mob.setStart(intersectionPoint(i, mu2));
            mob.setEnd(intersectionPoint(i + 1, mu2));
        });

        shellConeIntersection.add(segment);
    }

    function markerAt(point, color, radius = 0.11) {
        const marker = new manim.Surface3D({
            func: (u, v) => [
                radius * Math.cos(u) * Math.cos(v),
                radius * Math.cos(u) * Math.sin(v),
                radius * Math.sin(u),
            ],
            uRange: [-Math.PI / 2, Math.PI / 2],
            vRange: [0, TAU],
            uResolution: 8,
            vResolution: 12,
            checkerboardColors: [color, color],
            opacity: 1,
        });

        marker.moveTo(point);
        return marker;
    }

    const shellApex = markerAt(
        W(0, 0, Math.sqrt(M20)),
        "#82a9aa",
        0.065
    );

    shellApex.addUpdater((mob) => {
        mob.moveTo(
            W(
                0,
                0,
                Math.sqrt(
                    Math.max(tracker.getValue(), 0)
                )
            )
        );
    });

    function collinearPosition(mu2) {
        if (E20 <= EPS) {
            return q1Point;
        }

        const cosine = clamp(
            1 - mu2 / (2 * E1 * E20),
            -1,
            1
        );

        const sine = Math.sqrt(
            Math.max(0, 1 - cosine * cosine)
        );

        return W(
            E1 + E20 * cosine,
            E20 * sine,
            E1 + E20
        );
    }

    function softPosition(mu2) {
        if (M20 <= EPS) {
            return q1Point;
        }

        const E2 = softStartE2 * mu2 / M20;

        return W(
            E1 + E2 * Math.cos(theta0),
            E2 * Math.sin(theta0),
            E1 + E2
        );
    }

    const collinearStartPoint = collinearPosition(M20);
    const softStartPoint = softPosition(M20);
    const collinearEndpoint = collinearPosition(0);
    const softEndpoint = softPosition(0);

    const collinearPoints = [];
    const softPoints = [];

    for (let i = 0; i < N; ++i) {
        const mu2 = M20 * (1 - i / (N - 1));

        collinearPoints.push(collinearPosition(mu2));
        softPoints.push(softPosition(mu2));
    }

    const collinearTrace = polyline(
        collinearPoints,
        "#4ade80"
    );

    const softTrace = polyline(
        softPoints,
        "#d879ed"
    );

    const q1Line = new manim.Line3D({
        start: origin,
        end: q1Point,
        color: "#729cff",
    });

    const safeEnd = (start, end) => {
        if (distance(start, end) > 1e-6) {
            return end;
        }

        return [end[0], end[1], end[2] + 1e-6];
    };

    const collinearQ2 = new manim.Line3D({
        start: q1Point,
        end: safeEnd(q1Point, collinearStartPoint),
        color: "#4ade80",
    });

    const softQ2 = new manim.Line3D({
        start: q1Point,
        end: safeEnd(q1Point, softStartPoint),
        color: "#d879ed",
    });

    const collinearMarker = markerAt(
        collinearStartPoint,
        "#4ade80",
        0.115
    );

    const softMarker = markerAt(
        softStartPoint,
        "#d879ed",
        0.08
    );

    const collinearStartMarker = markerAt(
        collinearStartPoint,
        "#a7f3c2",
        0.052
    );

    const softStartMarker = markerAt(
        softStartPoint,
        "#efb4fa",
        0.052
    );

    const collinearLimitMarker = markerAt(
        collinearEndpoint,
        "#a7f3c2",
        0.073
    );

    const softLimitMarker = markerAt(
        softEndpoint,
        "#efb4fa",
        0.073
    );

    collinearQ2.addUpdater((mob) => {
        mob.setEnd(safeEnd(
            q1Point,
            collinearPosition(tracker.getValue())
        ));
    });

    softQ2.addUpdater((mob) => {
        mob.setEnd(safeEnd(
            q1Point,
            softPosition(tracker.getValue())
        ));
    });

    collinearMarker.addUpdater((mob) => {
        mob.moveTo(
            collinearPosition(tracker.getValue())
        );
    });

    softMarker.addUpdater((mob) => {
        mob.moveTo(
            softPosition(tracker.getValue())
        );
    });

    const title = new manim.MathTexImage({
        latex:
            `M_0^2=${M20.toFixed(3)},\\qquad`
            + `p^2=\\mu^2:\\ M_0^2\\to0`,
        color: "#ffffff",
    });

    const collinearLabel = new manim.MathTexImage({
        latex:
            String.raw`\text{collinear:}\quad`
            + `E_2=${E20.toFixed(3)},\ \\theta\\to0`,
        color: "#4ade80",
    });

    const softLabel = new manim.MathTexImage({
        latex:
            String.raw`\text{soft:}\quad`
            + `\\theta=${params.theta0Deg.toFixed(1)}^\\circ,`
            + String.raw`\ E_2\to0`,
        color: "#d879ed",
    });

    const finalConeLabel = new manim.MathTexImage({
        latex: String.raw`p^2=0`,
        color: "#6688b8",
    });

    const shiftedConeLabel = new manim.MathTexImage({
        latex: String.raw`(p-q_1)^2=0`,
        color: "#a48562",
    });

    const shellLabel = new manim.MathTexImage({
        latex: String.raw`p^2=\mu^2`,
        color: "#71898a",
    });

    for (const label of [
        title,
        collinearLabel,
        softLabel,
        finalConeLabel,
        shiftedConeLabel,
        shellLabel,
    ]) {
        await label.waitForRender();
    }

    title.scale(0.54);
    collinearLabel.scale(0.42);
    softLabel.scale(0.42);
    finalConeLabel.scale(0.37);
    shiftedConeLabel.scale(0.37);
    shellLabel.scale(0.37);

    title.toCorner(manim.UL);

    collinearLabel.nextTo(title, manim.DOWN, 0.12);
    collinearLabel.alignTo(title, manim.LEFT);

    softLabel.nextTo(collinearLabel, manim.DOWN, 0.09);
    softLabel.alignTo(title, manim.LEFT);

    finalConeLabel.toCorner(manim.UR);

    shiftedConeLabel.nextTo(
        finalConeLabel,
        manim.DOWN,
        0.09
    );
    shiftedConeLabel.alignTo(
        finalConeLabel,
        manim.RIGHT
    );

    shellLabel.nextTo(
        shiftedConeLabel,
        manim.DOWN,
        0.09
    );
    shellLabel.alignTo(
        finalConeLabel,
        manim.RIGHT
    );

    const pzLabel = new manim.MathTexImage({
        latex: "p_z",
        color: "#929aa7",
    });

    const pxLabel = new manim.MathTexImage({
        latex: "p_x",
        color: "#929aa7",
    });

    const energyLabel = new manim.MathTexImage({
        latex: "E",
        color: "#929aa7",
    });

    for (const label of [
        pzLabel,
        pxLabel,
        energyLabel,
    ]) {
        await label.waitForRender();
        label.scale(0.4);
    }

    pzLabel.moveTo([4.62, 0, 0.1]);
    pxLabel.moveTo([0, 4.62, 0.1]);
    energyLabel.moveTo([0, 0, 4.62]);

    scene.add(
        axes,

        finalCone,
        shiftedCone,

        finalConeWireframe,
        shiftedConeWireframe,
        movingMassWireframe,
        shellConeIntersection,
        shellApex,

        collinearTrace,
        softTrace,

        q1Line,
        collinearQ2,
        softQ2,

        collinearStartMarker,
        softStartMarker,
        collinearLimitMarker,
        softLimitMarker,
        collinearMarker,
        softMarker,

        pzLabel,
        pxLabel,
        energyLabel,
    );

    scene.addFixedInFrameMobjects(
        title,
        collinearLabel,
        softLabel,
        finalConeLabel,
        shiftedConeLabel,
        shellLabel,
    );

    scene.addFixedOrientationMobjects(
        pzLabel,
        pxLabel,
        energyLabel,
    );

    await scene.wait(0.8);

    if (M20 > EPS) {
        while (true) {
            await scene.play(
                tracker.animateTo(0, {
                    duration: 7,
                    rateFunc: manim.linear,
                })
            );

            await scene.wait(1.2);

            await scene.play(
                tracker.animateTo(M20, {
                    duration: 3,
                    rateFunc: manim.linear,
                })
            );

            await scene.wait(0.8);
        }
    } else {
        await scene.wait(Infinity);
    }
    """.replace("__PARAMS__", _params)

    manim_view = mo.ui.anywidget(
        ManimWeb(
            code=_scene_code,
            width=1060,
            height=650,
            version="0.3.24",
        )
    )

    manim_view
    return


if __name__ == "__main__":
    app.run()
