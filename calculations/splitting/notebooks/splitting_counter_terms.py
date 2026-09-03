import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.Html(
        r"""
        <span aria-hidden="true" style="display: none">
          <marimo-tex>||(\gdef\slashed#1{\cancel{#1}}||)</marimo-tex>
        </span>
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Splitting counter terms

    A Symbolica-only reconstruction of the real collinear counter terms
    derived in the "Splitting counter-term calculation" end matter of
    [`paper/main.tex`](../../../paper/main.tex).

    The hard Born contribution is opaque. The calculation manipulates only
    its external spin or polarization connector and replaces a recognized
    contraction by the scalar functions $\sigma(q)$ or $\sigma(g)$.
    """)
    return


@app.cell
def _():
    import os

    from symbolica import Expression, get_version, set_license_key

    symbolica_license_key = os.environ.get("SYMBOLICA_LICENSE_KEY") or os.environ.get(
        "SYMBOLICA_LICENSE"
    )
    if symbolica_license_key:
        set_license_key(symbolica_license_key)

    from splitting_kernels.assembly import assemble_nlo_counterterm
    from splitting_kernels.channels import (
        build_gq_channel,
        build_gg_channel,
        build_qg_channel,
        build_qq_channel,
        derive_channel,
        kernel_qg,
    )
    from splitting_kernels.colors import make_color_context
    from splitting_kernels.kinematics import (
        assert_symbolic_equal,
        canonical,
        joint_collinear_scale,
        make_kinematics,
        set_dimension,
    )
    from splitting_kernels.kernels import (
        ap_gq_cdr,
        ap_gg_cdr,
        ap_kernel_symbol,
        ap_qg_cdr,
        ap_qq_cdr,
        cdr_kernel_symbol,
        expand_ap_kernel,
        expand_cdr_kernel,
    )
    from splitting_kernels.phase_space import integrate_channel_phase_space
    from splitting_kernels.tensors import (
        gluon_parent_quark_born_numerator,
        gluon_self_splitting_numerator,
        gluon_virtual_self_energy_numerator,
        make_tensor_context,
        quark_born_reduced_numerator,
    )
    from splitting_kernels.virtual import (
        integrate_gluon_virtual_self_energy,
        integrate_virtual_self_energy,
    )

    def latex_body(expression):
        source = expression.to_latex()
        if source.startswith("$$") and source.endswith("$$"):
            source = source[2:-2]
        elif source.startswith("$") and source.endswith("$"):
            source = source[1:-1]
        return source

    return (
        Expression,
        ap_gg_cdr,
        ap_gq_cdr,
        ap_qg_cdr,
        ap_qq_cdr,
        assemble_nlo_counterterm,
        assert_symbolic_equal,
        build_gg_channel,
        build_gq_channel,
        build_qg_channel,
        build_qq_channel,
        cdr_kernel_symbol,
        derive_channel,
        expand_ap_kernel,
        expand_cdr_kernel,
        get_version,
        gluon_parent_quark_born_numerator,
        gluon_self_splitting_numerator,
        gluon_virtual_self_energy_numerator,
        integrate_channel_phase_space,
        integrate_gluon_virtual_self_energy,
        integrate_virtual_self_energy,
        joint_collinear_scale,
        kernel_qg,
        latex_body,
        make_color_context,
        make_kinematics,
        make_tensor_context,
        quark_born_reduced_numerator,
        set_dimension,
    )


@app.cell
def _(make_color_context, make_kinematics, make_tensor_context):
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    colors = make_color_context()
    d = kinematics.d
    epsilon = kinematics.epsilon
    x = kinematics.x
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    Lambda2 = kinematics.cutoff2
    mu2 = kinematics.renormalization_scale2
    return Lambda2, colors, d, epsilon, kinematics, mu2, p2, tensors, transverse2, x


@app.cell
def _(latex_body):
    def manuscript_latex(expression, momentum="p"):
        latex_source = latex_body(expression)
        momentum_squared = r"p_1^{2}" if momentum == "p_1" else r"p^{2}"
        for internal_name, manuscript_name in (
            ("PggCDR", r"P_{gg}^{\mathrm{CDR}}"),
            ("PqqCDR", r"P_{qq}^{\mathrm{CDR}}"),
            ("PgqCDR", r"P_{gq}^{\mathrm{CDR}}"),
            ("PqgCDR", r"P_{qg}^{\mathrm{CDR}}"),
            ("pggCDR", r"p_{gg}^{\mathrm{CDR}}"),
            ("pqqCDR", r"p_{qq}^{\mathrm{CDR}}"),
            ("pgqCDR", r"p_{gq}^{\mathrm{CDR}}"),
            ("pqgCDR", r"p_{qg}^{\mathrm{CDR}}"),
            (r"sigma\!", r"\sigma\!"),
            ("epsilon", r"\epsilon"),
            ("n_f", r"n_f"),
            ("Lambda2", r"\Lambda^{2}"),
            ("mu2", r"\mu^{2}"),
            ("pplusdotpminus", r"\frac{s}{2}"),
            ("kperp2", r"|k_\perp|^{2}"),
            ("p2", momentum_squared),
            (r"Theta\!", r"\Theta\!"),
            (r"Delta\!", r"\delta\!"),
            (r"gamma\!", r"\Gamma\!"),
            (r"Beta\!", r"\mathrm{B}\!"),
        ):
            latex_source = latex_source.replace(internal_name, manuscript_name)
        return latex_source

    return (manuscript_latex,)


@app.cell
def _(get_version, mo):
    mo.callout(
        mo.md(
            f"""
            **Reproducibility.** Symbolica reports version `{get_version()}`.
            Mathematical expressions are manipulated only by Symbolica,
            Spenso, and Idenso. The notebook does not use SymPy, regular
            expressions, or string-based algebra.
            """
        ),
        kind="info",
    )
    return


@app.cell
def _(
    ap_gg_cdr,
    ap_gq_cdr,
    ap_qg_cdr,
    ap_qq_cdr,
    assert_symbolic_equal,
    colors,
    d,
    epsilon,
    kinematics,
    manuscript_latex,
    mo,
    x,
):
    cdr_definitions = (
        colors.cf * (2 * x / (1 - x) + (1 - epsilon) * (1 - x)),
        colors.cf * (2 * (1 - x) / x + (1 - epsilon) * x),
        colors.tr * (1 - 2 * x * (1 - x) / (1 - epsilon)),
        2
        * colors.ca
        * (x / (1 - x) + (1 - x) / x + x * (1 - x)),
    )
    for _definition, _internal_kernel, _label in zip(
        cdr_definitions,
        (
            colors.cf * ap_qq_cdr(x, epsilon),
            colors.cf * ap_gq_cdr(x, epsilon),
            colors.tr * ap_qg_cdr(x, epsilon),
            colors.ca * ap_gg_cdr(x, epsilon),
        ),
        ("P_qq", "P_gq", "P_qg", "P_gg"),
        strict=True,
    ):
        assert_symbolic_equal(
            _definition,
            _internal_kernel,
            f"{_label} CDR definition",
        )
    convention_rows = [
        {
            "Object": mo.md("$d$"),
            "Definition": mo.md(
                f"${manuscript_latex(d)}=4-2{manuscript_latex(epsilon)}$"
            ),
        },
        {
            "Object": mo.md(r"$|k_\perp|^2$"),
            "Definition": mo.md(r"$|k_\perp|^2=-k_\perp^2\geq0$"),
        },
        {
            "Object": mo.md(r"$p\cdot k$"),
            "Definition": mo.md(f"${manuscript_latex(kinematics.p_dot_k)}$"),
        },
        {
            "Object": mo.md(r"$(p-k)^2$"),
            "Definition": mo.md(
                f"${manuscript_latex(kinematics.reduced_virtuality)}$"
            ),
        },
        {
            "Object": mo.md("$p_0^2$"),
            "Definition": mo.md(
                f"${manuscript_latex(kinematics.virtuality_root)}$"
            ),
        },
        {
            "Object": mo.md(r"$|k_\perp|^2_{\max}$"),
            "Definition": mo.md(
                f"${manuscript_latex(kinematics.transverse_cutoff)}$"
            ),
        },
    ]
    ap_rows = [
        {
            "Kernel": mo.md(r"$P_{qq}^{\mathrm{CDR}}(x,\epsilon)$"),
            "Definition": mo.md(
                f"${manuscript_latex(cdr_definitions[0])}$"
            ),
        },
        {
            "Kernel": mo.md(r"$P_{gq}^{\mathrm{CDR}}(x,\epsilon)$"),
            "Definition": mo.md(
                f"${manuscript_latex(cdr_definitions[1])}$"
            ),
        },
        {
            "Kernel": mo.md(r"$P_{qg}^{\mathrm{CDR}}(x,\epsilon)$"),
            "Definition": mo.md(
                f"${manuscript_latex(cdr_definitions[2])}$"
            ),
        },
        {
            "Kernel": mo.md(r"$P_{gg}^{\mathrm{CDR}}(x,\epsilon)$"),
            "Definition": mo.md(
                f"${manuscript_latex(cdr_definitions[3])}$"
            ),
        },
    ]
    color_rows = [
        {
            "Splitting": mo.md(r"$q\to qg$"),
            "Idenso contraction": mo.md(r"$T^a_{ij}T^a_{jk}$"),
            "Reduction": mo.md(r"$C_F\,\delta_{ik}$"),
            "$SU(N_c)$ value": mo.md(
                f"${manuscript_latex(colors.cf_su_n)}$"
            ),
        },
        {
            "Splitting": mo.md(r"$g\to q\bar q$"),
            "Idenso contraction": mo.md(r"$T^a_{ij}T^b_{ji}$"),
            "Reduction": mo.md(r"$T_R\,\delta^{ab}$"),
            "$SU(N_c)$ value": mo.md(
                f"${manuscript_latex(colors.tr_su_n)}$"
            ),
        },
        {
            "Splitting": mo.md(r"$g\to gg$"),
            "Idenso contraction": mo.md(r"$f^{abc}f^{dbc}$"),
            "Reduction": mo.md(r"$C_A\,\delta^{ad}$"),
            "$SU(N_c)$ value": mo.md(
                f"${manuscript_latex(colors.ca_su_n)}$"
            ),
        },
    ]
    mo.vstack(
        [
            mo.md(
                r"""
                ## 1. Kinematics and conventions

                The momentum fraction $x$ labels the daughter entering the hard
                interaction. The cut daughter carries $1-x$. With
                $s=2p_+\!\cdot p_-$, the coordinates are

                $$
                p=p_++\frac{p^2}{s}p_-,\qquad
                k=(1-x)p_++k_\perp+
                \frac{|k_\perp|^2}{(1-x)s}p_-,
                $$

                $$
                p-k=xp_+-k_\perp+
                \left(\frac{p^2}{s}
                -\frac{|k_\perp|^2}{(1-x)s}\right)p_-.
                $$

                Equivalently, the momentum fraction used as the argument of
                every splitting kernel is defined by

                $$
                x=\frac{(p-k)\cdot p_-}{p\cdot p_-},\qquad
                1-x=\frac{k\cdot p_-}{p\cdot p_-}.
                $$

                Thus the hard momentum is $xp_+$ at leading collinear power,
                and the final kernels are already in the canonical form
                $P_{ij}^{\mathrm{CDR}}(x,\epsilon)$; no final
                $x\leftrightarrow1-x$ relabelling is made.
                The virtualities $p^2$ and $|k_\perp|^2$ have the same
                collinear weight.
                """
            ),
            mo.ui.table(convention_rows, pagination=False),
            mo.md(
                r"""
                ### Color algebra

                The contractions below are constructed with Spenso color
                representations and reduced by Idenso. The conventional
                labels are applied only after the reductions return the
                fundamental Casimir, generator index, or adjoint Casimir.
                Relative to the color-averaged Born identities, the relevant
                averages are

                $$
                \frac{1}{N_c}\sum_{i,j,a}T^a_{ij}T^a_{ji}=C_F,
                \qquad
                \frac{1}{N_A}\sum_{a,i,j}T^a_{ij}T^a_{ji}=T_R.
                $$

                Thus the parent color averages are already contained in the
                conventional $C_F$ and $T_R$ coefficients shown below.
                """
            ),
            mo.ui.table(color_rows, pagination=False),
            mo.md(
                r"""
                We use the unregularized, azimuthally averaged CDR
                Altarelli--Parisi kernels of Eqs. (32)--(35) of
                [Catani, Seymour and Trocsanyi](https://arxiv.org/abs/hep-ph/9610553),
                with $h_g=d-2=2(1-\epsilon)$ and $h_q=2$. Our labels use
                standard DGLAP ordering: the second index is the parent.
                Consequently the off-diagonal indices are transposed relative
                to that paper. Every $P_{ab}^{\mathrm{CDR}}$ below includes
                its color factor.
                """
            ),
            mo.ui.table(ap_rows, pagination=False),
        ]
    )
    return


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md(
                r"""
                ## 2. Black-box Born factorization

                Here $k$ is the on-shell cut daughter, carrying longitudinal
                fraction $1-x$, while the daughter entering the Born black box
                has momentum $p-k$ and tends to $xp_+$ in the collinear limit.
                The tensors below are coupling-stripped, and every
                $\mathcal I^{R,V}$ denotes the coefficient of
                $a_s=\alpha_s/(2\pi)$. With two Cutkosky deltas and the
                dispersive virtuality measure, define

                $$
                \begin{aligned}
                \mathcal C_\epsilon
                &\equiv
                \frac{g_s^2}{a_s}
                \left(\frac{e^{\gamma_E}\mu^2}{4\pi}\right)^\epsilon
                \frac{(2\pi)^2}{2\pi}\\
                &=16\pi^3
                \left(\frac{e^{\gamma_E}\mu^2}{4\pi}\right)^\epsilon,
                \qquad \frac{g_s^2}{a_s}=8\pi^2.
                \end{aligned}
                $$

                Every real contribution then starts from the normalized cut
                form

                $$
                \begin{aligned}
                \mathcal I_{ij}^{R}
                &={}
                \frac{g_s^2}{a_s}
                \left(\frac{e^{\gamma_E}\mu^2}{4\pi}\right)^\epsilon
                \int_0^{\Lambda^2}\frac{\mathrm dp^2}{2\pi p^2}
                \int\frac{\mathrm d^dk}{(2\pi)^d}\,
                \big[\mathcal T_{ij}\circ H_j\big](p,k)\,
                [2\pi\delta^+(k^2)]\,
                [2\pi\delta^{+\prime}((p-k)^2)]\\
                &={}\mathcal C_\epsilon
                \int_0^{\Lambda^2}\frac{\mathrm dp^2}{p^2}
                \int\frac{\mathrm d^dk}{(2\pi)^d}\,
                \big[\mathcal T_{ij}\circ H_j\big](p,k)\,
                \delta^+(k^2)\,\delta^{+\prime}((p-k)^2).
                \end{aligned}
                $$

                The virtual contribution is the two-particle cut of the
                external self-energy:

                $$
                \mathcal I_{ii}^{V}=
                \frac{\mathcal C_\epsilon}{2}
                \int_0^{\Lambda^2}\frac{\mathrm dp_1^2}{(p_1^2)^2}
                \int\frac{\mathrm d^dk}{(2\pi)^d}\,
                \big[\mathcal T_{ii}^{V}\circ H_i\big](p_1,k)\,
                \delta^+(k^2)\,
                \delta^+\!\left((p_1-k)^2\right).
                $$

                Here $1/2$ is the one-external-leg factor and
                $\mathcal T_{ii}^V$ is the cut self-energy numerator. Its quark
                and gluon components are given in Section 4; the corresponding
                symmetry and flavor weights are applied in Section 6.

                For a gluon Born,
                $\mathcal T\circ H=\mathcal T^{\rho\sigma}H^g_{\rho\sigma}$;
                for a quark Born it denotes the corresponding Dirac trace.
                Thus $\delta^+(k^2)$ puts the emitted cut daughter on shell,
                whereas the differentiated cut
                $\delta^{+\prime}((p-k)^2)$
                represents the squared propagator of the line entering the
                hard interaction.

                The black-box Born functions include their incoming color and
                spin averages. With $N_A=N_c^2-1$,

                $$
                \sigma(q)=\frac{1}{2N_c}
                \operatorname{Tr}_{s,c}[H_q\,x\slashed p_+],
                $$

                $$
                \sigma(g)=\frac{1}{(d-2)N_A}
                \Pi^{\mu\nu}H^g_{\mu\nu}.
                $$

                For the hard daughter momentum $p-k$ and a lightlike reference
                $n$, the tensor

                $$
                \Pi^{\mu\nu}(p-k;n)=-g^{\mu\nu}
                +\frac{(p-k)^\mu n^\nu+n^\mu(p-k)^\nu}{(p-k)\cdot n}
                -(p-k)^2\frac{n^\mu n^\nu}{((p-k)\cdot n)^2}
                $$

                is transverse to $p-k$ and is used to extract the scalar gluon
                Born; it is not an internal propagator.

                The spin factors multiplying the tensor reductions are
                $2/(d-2)$ for $D_{gq}$, $1/2$ for $D_{qg}$, and $1$ for
                $D_{qq}$ and $D_{gg}$; they include the conversion of the
                external spin sums to the averaged Born functions.

                The color averages are already included when the Idenso color
                contractions are reduced relative to the corresponding Born
                identity. Their remaining coefficients are $T_R$, $C_F$,
                and $C_A$;
                no additional $N_c$ or $N_A$ factor is applied.

                No expression inside $H_q$ or $H_g$ is constructed or inspected.
                The next section specifies the leading-power replacement under
                which $\mathcal T_{ij}\circ H_j$ becomes a scalar numerator multiplying
                $\sigma(q)$ or $\sigma(g)$.
                """
            ),
        ]
    )
    return


@app.cell
def _(
    build_gq_channel,
    colors,
    gluon_parent_quark_born_numerator,
    kinematics,
    tensors,
):
    gq_polarization_report = gluon_parent_quark_born_numerator(
        tensors,
        kinematics,
    )
    assert gq_polarization_report.massless_residual == 0
    assert gq_polarization_report.p_transverse_residual == 0
    gq_spec = build_gq_channel(kinematics, tensors, colors)
    return (gq_spec,)


@app.cell
def _(build_qg_channel, colors, kinematics, tensors):
    qg_spec = build_qg_channel(kinematics, tensors, colors)
    return (qg_spec,)


@app.cell
def _(
    build_qq_channel,
    colors,
    kinematics,
    quark_born_reduced_numerator,
    tensors,
):
    qq_tensor_report = quark_born_reduced_numerator(tensors, kinematics)
    assert qq_tensor_report.residual == 0
    qq_spec = build_qq_channel(kinematics, tensors, colors)
    return (qq_spec,)


@app.cell
def _(
    build_gg_channel,
    colors,
    gluon_self_splitting_numerator,
    kinematics,
    tensors,
):
    gg_tensor_report = gluon_self_splitting_numerator(tensors, kinematics)
    assert gg_tensor_report.residual == 0
    gg_spec = build_gg_channel(kinematics, tensors, colors)
    return gg_spec, gg_tensor_report


@app.cell
def _(gg_spec, gq_spec, qg_spec, qq_spec):
    channel_specs = (gq_spec, qg_spec, qq_spec, gg_spec)
    return (channel_specs,)


@app.cell
def _(
    assert_symbolic_equal,
    channel_specs,
    derive_channel,
    joint_collinear_scale,
    kinematics,
):
    channel_results = tuple(
        derive_channel(channel_spec, kinematics)
        for channel_spec in channel_specs
    )
    for _result in channel_results:
        assert_symbolic_equal(
            joint_collinear_scale(
                _result.normalized_ap_numerator,
                kinematics,
            ),
            kinematics.collinear_parameter**2
            * _result.ap_collinear_coefficient,
            f"{_result.spec.name} homogeneous joint-collinear numerator",
        )
    return (channel_results,)


@app.cell
def _(
    assert_symbolic_equal,
    channel_specs,
    expand_ap_kernel,
    kinematics,
    set_dimension,
):
    for channel_spec in channel_specs:
        expanded_ap_numerator = expand_ap_kernel(
            channel_spec.ap_numerator,
            channel_spec.ap_kernel_name,
            kinematics.x,
            kinematics.epsilon,
        )
        assert_symbolic_equal(
            set_dimension(
                channel_spec.spin_factorization_factor
                * channel_spec.color_factor
                * expanded_ap_numerator,
                kinematics,
            ),
            set_dimension(
                channel_spec.spin_factorization_factor
                * channel_spec.color_factor
                * channel_spec.raw_numerator,
                kinematics,
            ),
            f"{channel_spec.name} CDR AP representation",
        )
    return


@app.cell
def _(
    assert_symbolic_equal,
    d,
    kernel_qg,
    kinematics,
    p2,
    qg_spec,
    transverse2,
    x,
):
    qg_trace_target = (
        2 * (d - 2) * (1 - x) * p2
        + 4 * transverse2 * kernel_qg(kinematics) / (x * (1 - x))
    )
    assert_symbolic_equal(
        qg_spec.raw_numerator,
        qg_trace_target,
        "D_qg tensor trace",
    )
    return


@app.cell
def _(channel_results, manuscript_latex, mo):
    numerator_rows = [
        {
            "Channel": result.spec.name,
            "Born": mo.md(f"${manuscript_latex(result.spec.born)}$"),
            "Color": mo.md(
                f"${manuscript_latex(result.spec.color_factor)}$"
            ),
            "Spin/Born factor": mo.md(
                f"${manuscript_latex(result.spec.spin_factorization_factor)}$"
            ),
            "LP numerator": mo.md(
                f"${manuscript_latex(result.normalized_ap_numerator)}$"
            ),
        }
        for result in channel_results
    ]
    mo.vstack(
        [
            mo.md(
                r"""
                ## 3. Joint collinear approximation

                Apply the joint scaling

                $$
                p^2\mapsto\lambda^2p^2,\qquad
                |k_\perp|^2\mapsto\lambda^2|k_\perp|^2,\qquad
                H_j(p-k)\mapsto H_j(xp_+).
                $$

                Keeping the coefficient of $\lambda^2$ gives

                $$
                \big[\mathcal T_{ij}\circ H_j\big]_{\mathrm{LP}}
                =N_{ij}^{\mathrm{LP}}(x,p^2,|k_\perp|^2)\,\sigma(j).
                $$

                The Symbolica audit finds that all four reduced real
                numerators are homogeneous in $p^2$ and $|k_\perp|^2$ and
                contain only this $\lambda^2$ term. Thus every result displayed
                below is already the joint collinear approximation.

                ## 4. Numerators

                ### Real contributions

                The four structures contracted with the black-box hard part in
                the master integral are

                $$
                \begin{aligned}
                \mathcal T_{gq}&=(\slashed p-\slashed k)\gamma^\mu\slashed k
                \gamma^\nu(\slashed p-\slashed k)d_{\mu\nu}(p;n),\\
                \mathcal T_{qg}^{\rho\sigma}
                &=d^{\rho\mu}(p-k;n)d^{\sigma\nu}(p-k;n)
                \operatorname{Tr}\!\left[
                \slashed p\gamma_\mu\slashed k\gamma_\nu\right],\\
                \mathcal T_{qq}&=(\slashed k-\slashed p)\gamma^\mu\slashed p
                \gamma^\nu(\slashed k-\slashed p)d_{\mu\nu}(k;n),\\
                \mathcal T_{gg}^{\rho\sigma}
                &=\frac{1}{d-2}
                d^{\rho r}(p-k;n)d^{\sigma s}(p-k;n)
                V_{\alpha r\mu}(p,-(p-k),-k)
                V_{\beta s\nu}(p,-(p-k),-k)
                \Pi^{\alpha\beta}(p;n)
                \Pi^{\mu\nu}(k;n).
                \end{aligned}
                $$

                Here $d_{\mu\nu}$ is the ordinary axial-gauge propagator
                numerator. The quark structures enter as
                $\operatorname{Tr}(H_q\mathcal T_{ij})$, while the gluon
                structures enter as
                $\mathcal T_{ij}^{\rho\sigma}H^g_{\rho\sigma}$.
                Spenso applies the Born projection of Section 2 without
                constructing either hard function. The table gives
                $N_{ij}^{\mathrm{LP}}$, including the displayed color and spin/Born
                factors.

                After the longitudinal on-shell integration, define
                $\mathcal J_{ij}$ as the remaining scalar prefactor from the
                original $\mathrm dp^2/p^2$ measure, the rescaling of
                $\delta^{+\prime}((p-k)^2)$, and the Born flux normalization:

                $$
                \mathcal J_{gq}=\mathcal J_{qq}
                =\frac{1}{2x^2(1-x)p^2},\qquad
                \mathcal J_{qg}=\mathcal J_{gg}
                =\frac{1}{2x(1-x)p^2}.
                $$

                Thus the original cut integral becomes, at leading power,

                $$
                \begin{aligned}
                \left.\mathcal I_{ij}^{R}\right|_{\mathrm{LP}}
                &=\mathcal C_\epsilon
                \int_0^{\Lambda^2}\frac{\mathrm dp^2}{p^2}
                \int\frac{\mathrm d^dk}{(2\pi)^d}\,
                N_{ij}^{\mathrm{LP}}\,\sigma(j)\,
                \delta^+(k^2)\,\delta^{+\prime}\!\left((p-k)^2\right)\\
                &=\mathcal C_\epsilon
                \int_0^{\Lambda^2}\mathrm dp^2
                \int\frac{\mathrm dx\,\mathrm d^{d-2}k_\perp}{(2\pi)^d}\,
                \underbrace{\mathcal J_{ij}N_{ij}^{\mathrm{LP}}}_{
                \mathcal W_{ij}}
                \delta'\!\left(
                p^2-\frac{|k_\perp|^2}{x(1-x)}
                \right)\sigma(j).
                \end{aligned}
                $$

                Hence $\mathcal W_{ij}$ is the complete scalar coefficient of
                the remaining differentiated on-shell constraint; it is not an
                additional numerator.
                """
            ),
            mo.ui.table(numerator_rows, pagination=False),
        ]
    )
    return


@app.cell
def _(
    assert_symbolic_equal,
    cdr_kernel_symbol,
    epsilon,
    expand_cdr_kernel,
    gg_spec,
    gg_tensor_report,
    transverse2,
    x,
):
    gg_normalized_numerator = (
        2
        * transverse2
        * cdr_kernel_symbol("gg", x, epsilon)
        / (x * (1 - x))
    )
    assert_symbolic_equal(
        expand_cdr_kernel(
            gg_normalized_numerator,
            "gg",
            x,
            epsilon,
            gg_spec.color_factor,
        ),
        gg_spec.color_factor * gg_tensor_report.reduced_numerator,
        "D_gg color-dressed three-gluon numerator",
    )
    return


@app.cell
def _(
    assert_symbolic_equal,
    cdr_kernel_symbol,
    colors,
    epsilon,
    expand_cdr_kernel,
    gluon_virtual_tensor_report,
    kinematics,
    manuscript_latex,
    mo,
    p2,
    set_dimension,
    virtual_result,
    x,
):
    _virtual_computed = (
        set_dimension(
            colors.cf * virtual_result.numerator.leading_coefficient,
            kinematics,
        ),
        set_dimension(
            colors.ca * gluon_virtual_tensor_report.gluon_loop_coefficient,
            kinematics,
        ),
        set_dimension(
            colors.tr * gluon_virtual_tensor_report.quark_loop_coefficient,
            kinematics,
        ),
    )
    _virtual_cdr = (
        2 * p2 * cdr_kernel_symbol("qq", x, epsilon),
        2 * p2 * cdr_kernel_symbol("gg", x, epsilon),
        2 * p2 * cdr_kernel_symbol("qg", x, epsilon),
    )
    for _label, _name, _color, _computed, _compact in zip(
        ("D_qq quark-gluon cut", "D_gg gluon cut", "D_gg quark cut"),
        ("qq", "gg", "qg"),
        (colors.cf, colors.ca, colors.tr),
        _virtual_computed,
        _virtual_cdr,
        strict=True,
    ):
        assert_symbolic_equal(
            _computed,
            expand_cdr_kernel(
                _compact,
                _name,
                x,
                epsilon,
                _color,
            ),
            f"{_label} compact CDR representation",
        )

    def _virtual_row(_cut, _computed, _compact):
        return {
            "Cut": mo.md(_cut),
            "Spenso/Symbolica LP scalar": mo.md(
                f"${manuscript_latex(_computed, momentum='p_1')}$"
            ),
            "Equivalent CDR form": mo.md(
                f"${manuscript_latex(_compact, momentum='p_1')}$"
            ),
        }

    _qq_virtual_rows = [
        _virtual_row(
            r"$qg$",
            _virtual_computed[0],
            _virtual_cdr[0],
        )
    ]
    _gg_virtual_rows = [
        _virtual_row(_cut, _computed, _compact)
        for _cut, _computed, _compact in zip(
            (r"$gg$", r"$q\bar q$"),
            _virtual_computed[1:],
            _virtual_cdr[1:],
            strict=True,
        )
    ]

    mo.vstack(
        [
            mo.md(
                r"""
    ### Virtual contributions

    For $\eta=p_1+p_2$, every cut-gluon line uses

    $$
    d_{\mu\nu}(\ell;\eta)=-g_{\mu\nu}
    +\frac{\ell_\mu\eta_\nu+\eta_\mu\ell_\nu}{\ell\cdot\eta}
    -\eta^2\frac{\ell_\mu\ell_\nu}{(\ell\cdot\eta)^2}.
    $$

    The tables below are live outputs of the Spenso/Idenso contractions and
    the Symbolica leading-power expansion. Define the scalar virtual numerator
    by

    $$
    \big[\mathcal T_{ii}^{V}\circ H_i\big]_{\mathrm{LP}}
    =N_{ii}^{V,\mathrm{LP}}(x,p_1^2)\,\sigma(i).
    $$

    After Born projection, the virtual master integral of Section 2 is

    $$
    \begin{aligned}
    \left.\mathcal I_{ii}^{V}\right|_{\mathrm{LP}}=
    {}&\frac{\mathcal C_\epsilon}{2}
    \int_0^{\Lambda^2}\frac{\mathrm dp_1^2}{(p_1^2)^2}
    \int\frac{\mathrm d^dk}{(2\pi)^d}\,
    N_{ii}^{V,\mathrm{LP}}(x,p_1^2)\,\sigma(i)\,
    \delta^+(k^2)\,
    \delta^+\!\left((p_1-k)^2\right)\\
    ={}&\frac{\mathcal C_\epsilon}{2}
    \int_0^{\Lambda^2}\mathrm dp_1^2
    \int\frac{\mathrm dx\,\mathrm d^{d-2}k_\perp}{(2\pi)^d}\,
    \frac{N_{ii}^{V,\mathrm{LP}}(x,p_1^2)}
    {2x(1-x)(p_1^2)^2}\,
    \delta\!\left(
    p_1^2-\frac{|k_\perp|^2}{x(1-x)}
    \right)\sigma(i).
    \end{aligned}
    $$

    In the second line, $\delta^+(k^2)$ has fixed the longitudinal component
    of $k$, and the remaining delta has been rescaled with

    $$
    \delta^+\!\left((p_1-k)^2\right)
    =\frac{1}{x}\delta\!\left(
    p_1^2-\frac{|k_\perp|^2}{x(1-x)}
    \right).
    $$

    Here
    $N_{ii}^{V,\mathrm{LP}}$ denotes the relevant component, or their weighted
    sum when several cuts contribute.

    #### $D_{qq}$
    """
            ),
            mo.md(
                r"""

    The open quark self-energy tensor is

    $$
    \mathcal T_{qq}^{V}=\slashed p_1\gamma^\mu
    (\slashed p_1-\slashed k)\gamma^\nu\slashed p_1
    d_{\mu\nu}(k;\eta).
    $$

    Projecting its open Dirac chain onto $\slashed p_1$ with the
    complementary vector $p_2$ gives, at leading power in $p_1^2$,

    $$
    N_{qq}^{V,\mathrm{LP}}(x,p_1^2)
    =2p_1^2P_{qq}^{\mathrm{CDR}}(x,\epsilon).
    $$

    The table displays this computed scalar numerator.
    """
            ),
            mo.ui.table(_qq_virtual_rows, pagination=False),
            mo.md(
                r"""

    #### $D_{gg}$

    Before Born projection, the cut gluon- and quark-loop tensors are

    $$
    \begin{aligned}
    \mathcal T_{gg,\alpha\beta}^{V,(gg)}={}&
    V_{\alpha\rho\mu}(p_1,-(p_1-k),-k)
    V_{\beta\sigma\nu}(p_1,-(p_1-k),-k)
    d^{\rho\sigma}(p_1-k;\eta)d^{\mu\nu}(k;\eta),\\
    \mathcal T_{gg,\alpha\beta}^{V,(q\bar q)}={}&
    \operatorname{Tr}\!\left[
    \slashed k\gamma_\alpha(\slashed p_1-\slashed k)\gamma_\beta\right].
    \end{aligned}
    $$

    For $c\in\{gg,q\bar q\}$, define the exact Born-projected scalar
    numerator by

    $$
    N_{gg}^{V,(c)}(p_1,k;\eta)
    \equiv\frac{1}{d-2}\Pi^{\alpha\beta}(p_1;\eta)
    \mathcal T_{gg,\alpha\beta}^{V,(c)}.
    $$

    The corresponding leading-power reductions are

    $$
    \begin{aligned}
    N_{gg}^{V,\mathrm{LP},(gg)}(x,p_1^2)
    &=2p_1^2P_{gg}^{\mathrm{CDR}}(x,\epsilon),\\
    N_{gg}^{V,\mathrm{LP},(q\bar q)}(x,p_1^2)
    &=2p_1^2P_{qg}^{\mathrm{CDR}}(x,\epsilon).
    \end{aligned}
    $$

    The second equation is for one quark flavor. Axial-gauge ghosts
    decouple, and the four-gluon tadpole has no two-particle collinear cut.

    The identical-particle and flavor weights are applied in Section 6.
    """
            ),
            mo.ui.table(_gg_virtual_rows, pagination=False),
        ]
    )
    return


@app.cell
def _(
    assert_symbolic_equal,
    cdr_kernel_symbol,
    epsilon,
    expand_cdr_kernel,
    gq_spec,
    kinematics,
    p2,
    set_dimension,
    transverse2,
    x,
):
    _gq_fully_normalized_numerator = (
        4 * gq_spec.color_factor * (1 - x) * x**2 * p2 / (1 - epsilon)
        + 2
        * transverse2
        * cdr_kernel_symbol("qg", x, epsilon)
        / (1 - x)
    )
    assert_symbolic_equal(
        expand_cdr_kernel(
            _gq_fully_normalized_numerator,
            gq_spec.ap_kernel_name,
            x,
            epsilon,
            gq_spec.color_factor,
        ),
        set_dimension(gq_spec.raw_numerator, kinematics)
        * set_dimension(gq_spec.spin_factorization_factor, kinematics)
        * gq_spec.color_factor,
        "D_gq color- and spin-averaged Born normalization",
    )
    return


@app.cell
def _(channel_results, integrate_channel_phase_space, kinematics):
    phase_space_results = tuple(
        integrate_channel_phase_space(channel_result, kinematics)
        for channel_result in channel_results
    )
    return (phase_space_results,)


@app.cell
def _(
    assert_symbolic_equal,
    cdr_kernel_symbol,
    kinematics,
    manuscript_latex,
    mo,
    phase_space_results,
):
    for _result in phase_space_results:
        assert_symbolic_equal(
            _result.ap_bulk_coefficient,
            cdr_kernel_symbol(
                _result.channel.spec.ap_kernel_name,
                kinematics.x,
                kinematics.epsilon,
            ),
            f"{_result.channel.spec.name} compact CDR bulk coefficient",
        )
    phase_space_rows = [
        {
            "Channel": _result.channel.spec.name,
            "Bulk coefficient": mo.md(
                f"${manuscript_latex(_result.ap_bulk_coefficient)}$"
            ),
            "Integrated bulk": mo.md(
                rf"$-\dfrac{{\mathcal R_\epsilon(x)}}{{\epsilon}}"
                rf"\left[{manuscript_latex(_result.ap_bulk_coefficient)}\right]"
                rf"{manuscript_latex(_result.channel.spec.born)}$"
            ),
        }
        for _result in phase_space_results
    ]
    mo.vstack(
        [
            mo.md(
                r"""
                ## 5. Integrated real contributions

                The $\delta^+(k^2)$ integration fixes the longitudinal component
                of $k$. With

                $$
                (p-k)^2=x(p^2-p_0^2),\qquad
                p_0^2=\frac{|k_\perp|^2}{x(1-x)},\qquad
                \mathcal W_{ij}=\mathcal J_{ij}N_{ij}^{\mathrm{LP}},
                $$

                $p_0^2$ is therefore the value of the parent virtuality $p^2$
                selected by the on-shell condition $(p-k)^2=0$.

                The master integral of Section 2 becomes

                $$
                \mathcal I_{ij}^{R}=
                \mathcal C_\epsilon
                \int_0^{\Lambda^2}\mathrm dp^2
                \int\frac{\mathrm dx\,\mathrm d^{d-2}k_\perp}{(2\pi)^d}
                \mathcal W_{ij}(x,p^2,|k_\perp|^2)
                \delta'(p^2-p_0^2)\,\sigma(j).
                $$

                The $p^2$ integration is the equality

                $$
                \begin{aligned}
                \mathcal I_{ij}^{R}
                =\mathcal C_\epsilon
                \int\frac{\mathrm dx\,\mathrm d^{d-2}k_\perp}{(2\pi)^d}
                \Big[&-\left.\partial_{p^2}\mathcal W_{ij}\right|_{p^2=p_0^2}
                \Theta(\Lambda^2-p_0^2)\\
                &+\mathcal W_{ij}(x,\Lambda^2,|k_\perp|^2)
                \delta(\Lambda^2-p_0^2)\Big]\sigma(j).
                \end{aligned}
                $$

                The first line is the bulk contribution and the second is the
                cutoff boundary. Set $K=|k_\perp|^2$ and $d=4-2\epsilon$.
                Applying the angular measure and the Section 2 identity

                $$
                \mathcal C_\epsilon
                \frac{\pi^{1-\epsilon}}{(2\pi)^{4-2\epsilon}
                \Gamma(1-\epsilon)}
                =\frac{e^{\gamma_E\epsilon}(\mu^2)^\epsilon}
                {\Gamma(1-\epsilon)}
                $$

                directly to the preceding equality gives

                $$
                \begin{aligned}
                \mathcal I_{ij}^{R}={}&
                \frac{e^{\gamma_E\epsilon}(\mu^2)^\epsilon}
                {\Gamma(1-\epsilon)}
                \int_0^1\mathrm dx\int_0^\infty\mathrm dK\,K^{-\epsilon}
                \Bigg[-\left.\partial_{p^2}\mathcal W_{ij}
                \right|_{p^2=K/[x(1-x)]}
                \Theta\!\left(\Lambda^2-\frac{K}{x(1-x)}\right)\\
                &\hspace{4.8cm}+\mathcal W_{ij}(x,\Lambda^2,K)
                \delta\!\left(\Lambda^2-\frac{K}{x(1-x)}\right)
                \Bigg]\sigma(j).
                \end{aligned}
                $$

                The theta function fixes the bulk range, while the radial
                delta fixes $K=\Lambda^2x(1-x)$ with Jacobian $x(1-x)$.
                Performing both operations gives the next equality,

                $$
                \begin{aligned}
                \mathcal I_{ij}^{R}={}&
                \frac{e^{\gamma_E\epsilon}(\mu^2)^\epsilon}
                {\Gamma(1-\epsilon)}
                \int_0^1\mathrm dx\,\Bigg[
                -\int_0^{\Lambda^2x(1-x)}\mathrm dK\,K^{-\epsilon}
                \left.\partial_{p^2}\mathcal W_{ij}
                \right|_{p^2=K/[x(1-x)]}\\
                &\hspace{2.2cm}+x(1-x)
                [\Lambda^2x(1-x)]^{-\epsilon}
                \mathcal W_{ij}\!\left(
                x,\Lambda^2,\Lambda^2x(1-x)\right)
                \Bigg]\sigma(j).
                \end{aligned}
                $$

                The delta has now disappeared. Define the common radial factor
                by the equality

                $$
                \mathcal R_\epsilon(x)=
                \frac{1}{\Gamma(1-\epsilon)}
                \left(
                \frac{\Lambda^2x(1-x)}{e^{\gamma_E}\mu^2}
                \right)^{-\epsilon}.
                $$

                For every channel, the Symbolica reduction extracts the
                remaining power of $K$ as

                $$
                -\left.\partial_{p^2}\mathcal W_{ij}(x,p^2,K)
                \right|_{p^2=K/[x(1-x)]}
                =\frac{\widetilde{\mathcal W}_{ij}(x,\epsilon)}{K}.
                $$

                Since $\widetilde{\mathcal W}_{ij}$ is independent of $K$,
                the radial integral can now be performed. The preceding
                equality becomes

                $$
                \begin{aligned}
                \mathcal I_{ij}^{R}={}&\int_0^1\mathrm dx\,
                \mathcal R_\epsilon(x)
                \Bigg[-\frac{\widetilde{\mathcal W}_{ij}(x,\epsilon)}
                {\epsilon}
                +x(1-x)\mathcal W_{ij}\!\left(
                x,\Lambda^2,\Lambda^2x(1-x)\right)
                \Bigg]\sigma(j).
                \end{aligned}
                $$

                ### Bulk terms

                The coefficients $\widetilde{\mathcal W}_{ij}$ and the
                integrated terms
                $-\widetilde{\mathcal W}_{ij}\mathcal R_\epsilon(x)
                \sigma(j)/\epsilon$ are given by:
                """
            ),
            mo.ui.table(phase_space_rows, pagination=False),
        ]
    )
    return


@app.cell
def _(
    assert_symbolic_equal,
    colors,
    epsilon,
    manuscript_latex,
    mo,
    phase_space_results,
):
    compact_boundary_coefficients = (
        colors.tr,
        colors.cf * (1 - epsilon),
        colors.cf * (1 - epsilon),
        -3 * colors.ca * (3 - 2 * epsilon) / (4 * (1 - epsilon)),
    )
    for _result, _compact_coefficient in zip(
        phase_space_results,
        compact_boundary_coefficients,
        strict=True,
    ):
        assert_symbolic_equal(
            _result.boundary_coefficient,
            _compact_coefficient,
            f"{_result.channel.spec.name} compact metric boundary",
        )
    boundary_rows = [
        {
            "Channel": _result.channel.spec.name,
            "Projector retained": mo.md(r"$-g_{\mu\nu}$"),
            "Boundary coefficient": mo.md(
                f"${manuscript_latex(_compact_coefficient)}$"
            ),
            "Integrated boundary": mo.md(
                rf"$\mathcal R_\epsilon(x)"
                rf"\left[{manuscript_latex(_compact_coefficient)}\right]"
                rf"{manuscript_latex(_result.channel.spec.born)}$"
            ),
        }
        for _result, _compact_coefficient in zip(
            phase_space_results,
            compact_boundary_coefficients,
            strict=True,
        )
    ]
    mo.vstack(
        [
            mo.md(
                r"""
                ### Cutoff-boundary terms

                The cutoff term is evaluated in Feynman gauge: in the second
                term of the preceding $\mathcal I_{ij}^{R}$ equality, every
                axial-gauge projector numerator is replaced by its metric part
                $-g_{\mu\nu}$ before imposing
                $K=\Lambda^2x(1-x)$. Denote the resulting weight by
                $\mathcal W_{ij}^{(-g)}$. The bulk term is unchanged and still
                uses the complete axial-gauge numerator.

                Define the dimensionless, color-dressed boundary coefficient
                directly from that weight:

                $$
                B_{ij}^{(-g)}(x,\epsilon)
                =x(1-x)\mathcal W_{ij}^{(-g)}\!\left(
                x,\Lambda^2,\Lambda^2x(1-x)\right).
                $$

                The boundary part of the preceding integral is therefore

                $$
                \left.\mathcal I_{ij}^{R}\right|_{\partial,-g}
                =\int_0^1\mathrm dx\,
                \mathcal R_\epsilon(x)\,
                B_{ij}^{(-g)}(x,\epsilon)\,\sigma(j).
                $$

                The superscript $(-g)$ records one retained metric projector;
                one entry is shown for every such projector.

                The four metric surfaces simplify to

                $$
                B_{gq}^{(-g)}=T_R,\qquad
                B_{qg}^{(-g)}=B_{qq}^{(-g)}
                =\frac{C_F(d-2)}{2}=C_F(1-\epsilon),
                $$

                $$
                B_{gg}^{(-g,-g,-g)}=
                -\frac{3C_A(3-2\epsilon)}{4(1-\epsilon)}.
                $$

                For $D_{gg}$, ``metric only'' retains the metric term in each
                of its three gluon projectors before imposing the surface.

                What follows are the boundary coefficients
                $B_{ij}^{(-g)}$ and the integrated boundaries
                $\left.\mathcal I_{ij}^{R}\right|_{\partial,-g}$.
                """
            ),
            mo.ui.table(boundary_rows, pagination=False),
        ]
    )
    return


@app.cell
def _(colors, integrate_virtual_self_energy, kinematics, tensors):
    virtual_result = integrate_virtual_self_energy(tensors, kinematics, colors)
    assert virtual_result.numerator.residual == 0
    return (virtual_result,)


@app.cell
def _(Expression, assert_symbolic_equal, colors, epsilon, mo, virtual_result):
    compact_quark_virtual_expansion = colors.cf * (
        2 / epsilon**2
        + 3 / (2 * epsilon)
        + (7 - Expression.PI**2) / 2
    )
    assert_symbolic_equal(
        virtual_result.epsilon_expansion,
        compact_quark_virtual_expansion,
        "compact complete D_qq virtual coefficient",
    )
    mo.md(
        r"""
        ## 6. Integrated virtual contributions

        Continue the $\mathcal I_{ii}^{V}$ equality of Section 4 and
        define the color-dressed cut kernel by

        $$
        \mathcal P_i^{V}(x,\epsilon)
        =\frac{N_{ii}^{V,\mathrm{LP}}(x,p_1^2)}{2p_1^2}.
        $$

        With $K=|k_\perp|^2$, the $p_1^2$ delta and the remaining radial
        integral give the successive equalities

        $$
        \begin{aligned}
        \left.\mathcal I_{ii}^{V}\right|_{\mathrm{LP}}
        ={}&\frac{1}{2}
        \frac{e^{\gamma_E\epsilon}(\mu^2)^\epsilon}
        {\Gamma(1-\epsilon)}
        \int_0^1\mathrm dx\int_0^{\Lambda^2}\mathrm dp_1^2
        \int_0^\infty\mathrm dK\,K^{-\epsilon}
        \frac{N_{ii}^{V,\mathrm{LP}}(x,p_1^2)}
        {2x(1-x)(p_1^2)^2}\\
        &\hspace{2.0cm}\times
        \delta\!\left(p_1^2-\frac{K}{x(1-x)}\right)\sigma(i)\\
        ={}&\frac{1}{2}
        \frac{e^{\gamma_E\epsilon}(\mu^2)^\epsilon}
        {\Gamma(1-\epsilon)}
        \int_0^1\mathrm dx\,
        \mathcal P_i^V(x,\epsilon)
        \int_0^{\Lambda^2x(1-x)}\mathrm dK\,K^{-1-\epsilon}
        \sigma(i)\\
        ={}&-\frac{\sigma(i)}{2\epsilon}
        \int_0^1\mathrm dx\,
        \mathcal R_\epsilon(x)\,
        \mathcal P_i^V(x,\epsilon).
        \end{aligned}
        $$

        ### $D_{qq}$

        The two labels of the quark-gluon cut give

        $$
        \mathcal P_q^V(x,\epsilon)
        =P_{qq}^{\mathrm{CDR}}(x,\epsilon)
        +P_{gq}^{\mathrm{CDR}}(x,\epsilon).
        $$

        These are the two daughter labelings of the same quark-gluon cut, not
        two self-energy graphs.

        Since $\mathcal R_\epsilon(x)=\mathcal R_\epsilon(1-x)$ and
        $P_{gq}^{\mathrm{CDR}}(x,\epsilon)
        =P_{qq}^{\mathrm{CDR}}(1-x,\epsilon)$, the common equality becomes

        $$
        \begin{aligned}
        \left.\mathcal I_{qq}^{V}\right|_{\mathrm{LP}}
        ={}&-\frac{\sigma(q)}{2\epsilon}
        \int_0^1\mathrm dx\,\mathcal R_\epsilon(x)
        \left[P_{qq}^{\mathrm{CDR}}(x,\epsilon)
        +P_{gq}^{\mathrm{CDR}}(x,\epsilon)\right]\\
        ={}&-\frac{\sigma(q)}{\epsilon}
        \int_0^1\mathrm dx\,\mathcal R_\epsilon(x)
        P_{qq}^{\mathrm{CDR}}(x,\epsilon).
        \end{aligned}
        $$

        The Born factor has no $x$ dependence, so the $x$ integral is
        performed exactly. The equality continues as

        $$
        \begin{aligned}
        \left.\mathcal I_{qq}^{V}\right|_{\mathrm{LP}}
        ={}&-\left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}
        \frac{e^{\gamma_E\epsilon}}
        {\epsilon\Gamma(1-\epsilon)}C_F
        \Big[2\mathrm B(1-\epsilon,-\epsilon)
        -\mathrm B(1-\epsilon,1-\epsilon)\\
        &\hspace{4.2cm}
        -(1+\epsilon)\mathrm B(2-\epsilon,1-\epsilon)\Big]\sigma(q)\\
        ={}&\left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}C_F
        \left[\frac{2}{\epsilon^2}+\frac{3}{2\epsilon}
        +\frac{7-\pi^2}{2}+\mathcal O(\epsilon)\right]\sigma(q)\\
        \equiv{}&\left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}
        \mathcal V_q(\epsilon)\,\sigma(q).
        \end{aligned}
        $$
        """
    )
    return


@app.cell
def _(
    colors,
    gluon_virtual_self_energy_numerator,
    integrate_gluon_virtual_self_energy,
    kinematics,
    tensors,
):
    gluon_virtual_tensor_report = gluon_virtual_self_energy_numerator(
        tensors,
        kinematics,
    )
    assert gluon_virtual_tensor_report.gluon_residual == 0
    assert gluon_virtual_tensor_report.quark_residual == 0
    gluon_virtual_result = integrate_gluon_virtual_self_energy(
        tensors,
        kinematics,
        colors,
    )
    return gluon_virtual_result, gluon_virtual_tensor_report


@app.cell
def _(
    Expression,
    assert_symbolic_equal,
    colors,
    epsilon,
    gluon_virtual_result,
    mo,
):
    compact_gluon_virtual_expansion = (
        2 * colors.ca / epsilon**2
        + (11 * colors.ca - 4 * colors.tr * colors.nf)
        / (6 * epsilon)
        + colors.ca * (67 - 9 * Expression.PI**2) / 18
        - 10 * colors.tr * colors.nf / 9
    )
    assert_symbolic_equal(
        gluon_virtual_result.epsilon_expansion,
        compact_gluon_virtual_expansion,
        "compact complete D_gg virtual coefficient",
    )
    mo.md(
        r"""
        ### $D_{gg}$

        The gluon cut and the two quark-antiquark labelings for each flavor
        give

        $$
        \mathcal P_g^V(x,\epsilon)
        =P_{gg}^{\mathrm{CDR}}(x,\epsilon)
        +2n_fP_{qg}^{\mathrm{CDR}}(x,\epsilon).
        $$

        The factor $2n_f$ counts the quark and antiquark labelings for each of
        the $n_f$ flavors. The common factor $1/2$ in
        $\mathcal I_{gg}^{V}$ leaves the $n_fP_{qg}^{\mathrm{CDR}}$ term below.

        The common equality therefore specializes to

        $$
        \begin{aligned}
        \left.\mathcal I_{gg}^{V}\right|_{\mathrm{LP}}
        ={}&-\frac{\sigma(g)}{2\epsilon}
        \int_0^1\mathrm dx\,\mathcal R_\epsilon(x)
        \left[P_{gg}^{\mathrm{CDR}}(x,\epsilon)
        +2n_fP_{qg}^{\mathrm{CDR}}(x,\epsilon)\right]\\
        ={}&-\frac{\sigma(g)}{\epsilon}
        \int_0^1\mathrm dx\,\mathcal R_\epsilon(x)
        \left[\frac{P_{gg}^{\mathrm{CDR}}(x,\epsilon)}{2}
        +n_fP_{qg}^{\mathrm{CDR}}(x,\epsilon)\right].
        \end{aligned}
        $$

        Again $\sigma(g)$ factorizes, and the $x$ integral is exact. The
        equality continues as

        $$
        \begin{aligned}
        \left.\mathcal I_{gg}^{V}\right|_{\mathrm{LP}}
        ={}&-\left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}
        \frac{e^{\gamma_E\epsilon}}
        {\epsilon\Gamma(1-\epsilon)}
        \Bigg\{C_A\left[
        2\mathrm B(2-\epsilon,-\epsilon)
        +\mathrm B(2-\epsilon,2-\epsilon)\right]\\
        &\hspace{2.0cm}+\frac{n_fT_R}{1-\epsilon}\left[
        2\mathrm B(3-\epsilon,1-\epsilon)
        -\epsilon\mathrm B(1-\epsilon,1-\epsilon)\right]\Bigg\}\sigma(g)\\
        ={}&\left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}
        \left[\frac{2C_A}{\epsilon^2}
        +\frac{11C_A-4T_Rn_f}{6\epsilon}
        +\frac{C_A(67-9\pi^2)}{18}
        -\frac{10T_Rn_f}{9}+\mathcal O(\epsilon)\right]\sigma(g)\\
        \equiv{}&\left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}
        \mathcal V_g(\epsilon)\,\sigma(g).
        \end{aligned}
        $$

        Only now introduce an external convolution fraction $\xi$. Let
        $\sigma_i(\xi)$ denote the Born function evaluated with incoming
        fraction $\xi$, so that $\sigma_i(1)=\sigma(i)$. The diagonal virtual
        kernel is defined by

        $$
        \begin{aligned}
        \left.\mathcal I_{ii}^{V}\right|_{\mathrm{LP}}
        ={}&\left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}
        \mathcal V_i(\epsilon)\sigma_i(1)\\
        ={}&\int_0^1\mathrm d\xi\,
        \left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}
        \mathcal V_i(\epsilon)
        \delta(1-\xi)\sigma_i(\xi)\\
        \equiv{}&\int_0^1\mathrm d\xi\,
        D_{ii}^{V}(\xi)\sigma_i(\xi),
        \end{aligned}
        $$

        and hence

        $$
        D_{ii}^{V}(\xi)
        =\left(\frac{\Lambda^2}{\mu^2}\right)^{-\epsilon}
        \mathcal V_i(\epsilon)\delta(1-\xi).
        $$
        """
    )
    return


@app.cell
def _(
    assemble_nlo_counterterm,
    colors,
    gluon_virtual_result,
    kinematics,
    phase_space_results,
    virtual_result,
):
    final_assembly = assemble_nlo_counterterm(
        phase_space_results,
        virtual_result,
        gluon_virtual_result,
        kinematics,
        colors,
    )
    assert final_assembly.passed
    return (final_assembly,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. Assembled NLO counterterm

    The real and virtual terms already contain the common normalization
    $\mathcal C_\epsilon$ of Section 2 and the normalized radial weight
    $\mathcal R_\epsilon$ of Section 5. No factor is restored at this stage.
    Use $\bar\xi'=1-\xi'$. The state set contains the gluon and every separate
    quark and antiquark flavor,

    $$
    \mathfrak S_1=\{g,q_1,\bar q_1,\ldots,q_{n_f},\bar q_{n_f}\}.
    $$

    The color-stripped kernels in the compact counterterm use the same
    index order as $D_{\mathfrak q\mathfrak q'}$. Thus the results of
    Section 1 are inserted through

    $$
    \begin{aligned}
    c_{qq}P_{qq}^{(0)}&=P_{qq}^{\mathrm{CDR}},&
    c_{qg}P_{qg}^{(0)}&=P_{gq}^{\mathrm{CDR}},\\
    c_{gq}P_{gq}^{(0)}&=P_{qg}^{\mathrm{CDR}},&
    c_{gg}P_{gg}^{(0)}&=P_{gg}^{\mathrm{CDR}},
    \end{aligned}
    $$

    with

    $$
    c_{gq}=T_R,\qquad c_{qg}=c_{qq}=C_F,\qquad c_{gg}=C_A.
    $$

    The metric-projector boundaries of Section 5 give

    $$
    b_{\partial}^{gq}=1,\qquad
    b_{\partial}^{qg}=b_{\partial}^{qq}=1-\epsilon,\qquad
    b_{\partial}^{gg}=-\frac{3(3-2\epsilon)}{4(1-\epsilon)},
    $$

    because
    $c_{\mathfrak q\mathfrak a}b_{\partial}^{\mathfrak q\mathfrak a}
    =B_{\mathfrak q\mathfrak a}^{(-g)}$ for the first three channels and
    $c_{gg}b_{\partial}^{gg}=B_{gg}^{(-g,-g,-g)}$. The sum over $\mathfrak S_1$
    reproduces the two virtual results of Section 6: for a quark it gives
    $P_{qq}^{\mathrm{CDR}}+P_{gq}^{\mathrm{CDR}}$, while for a gluon it
    gives $P_{gg}^{\mathrm{CDR}}+2n_fP_{qg}^{\mathrm{CDR}}$.

    The splitting counterterm uses the convention

    $$
    D^{(1)}=-\mathcal I_{\mathrm{bulk}}^R
    +\mathcal I_{\partial}^R+\mathcal I^V.
    $$

    Thus the $-P/\epsilon$ produced by the raw real radial integral enters
    $D^{(1)}$ as $+P/\epsilon$, whereas the virtual self-energy retains the
    minus sign derived in Section 6. Combining the three terms gives

    $$
    \begin{aligned}
    D_{\mathfrak q\mathfrak q'}^{(1)}(\xi)
    &={}
    \left.
    \sum_{\mathfrak a\in\mathfrak S_1}\int_0^1\mathrm d\xi'\,
    \frac{c_{\mathfrak q\mathfrak a}}{\Gamma(1-\epsilon)}
    \Bigg\{
    \delta_{\mathfrak a\mathfrak q'}\delta(\xi-\xi')
    b_{\partial}^{\mathfrak q\mathfrak a}
        +
        \left[
    \delta_{\mathfrak a\mathfrak q'}\delta(\xi-\xi')
    -\frac{\delta_{\mathfrak q\mathfrak q'}\delta(1-\xi)}{2}
    \right]
    \frac{P_{\mathfrak q\mathfrak a}^{(0)}(\xi')}{\epsilon}
    \Bigg\}
    \left(
    \frac{\Lambda^2\xi'\bar\xi'}{e^{\gamma_E}\mu^2}
    \right)^{-\epsilon}
    \right|_{\epsilon^0}.
    \end{aligned}
    $$

    The finite-part operation is applied only after the regulated expression
    has been assembled.
    """)
    return


@app.cell
def _(final_assembly, mo):
    _assembly_rows = [
        {
            "Channel": _entry.channel,
            "Real residual": str(_entry.real_residual),
            "Virtual residual": str(_entry.virtual_residual),
            r"$\epsilon^{-2}$ action residual": str(
                _entry.distributional_check.residuals[0]
            ),
            r"$\epsilon^{-1}$ action residual": str(
                _entry.distributional_check.residuals[1]
            ),
            r"$\epsilon^0$ action residual": str(
                _entry.distributional_check.residuals[2]
            ),
        }
        for _entry in final_assembly.entries
    ]
    mo.vstack(
        [
            mo.md(
                "Each entry is applied to a generic polynomial test "
                "function. Symbolica performs the regulated unit-interval "
                "integral and compares the Laurent coefficients with the "
                "flavor-sum formula."
            ),
            mo.ui.table(_assembly_rows, pagination=False),
            mo.callout(
                "The explicit normalization and all distributional checks "
                f"pass: `{final_assembly.passed}`.",
                kind="success" if final_assembly.passed else "danger",
            ),
        ]
    )
    return


@app.cell
def _(
    Expression,
    channel_results,
    final_assembly,
    gluon_virtual_result,
    mo,
    phase_space_results,
    virtual_result,
):
    all_symbolica = all(
        isinstance(expression, Expression)
        for result in channel_results
        for expression in (
            result.spec.raw_numerator,
            result.spec.metric_numerator,
            result.spec.spin_factorization_factor,
            result.collinear_coefficient,
            result.factorized_numerator,
            result.virtuality_weight,
            result.boundary_virtuality_weight,
        )
    ) and all(
        isinstance(expression, Expression)
        for result in phase_space_results
        for expression in (
            result.bulk_density,
            result.bulk_coefficient,
            result.integrated_bulk,
            result.boundary_density,
            result.boundary_coefficient,
            result.integrated_boundary,
        )
    ) and all(
        isinstance(expression, Expression)
        for expression in (
            virtual_result.numerator.leading_coefficient,
            virtual_result.cut_transverse_result,
            virtual_result.x_integral,
            virtual_result.epsilon_expansion,
            virtual_result.full_counterterm,
        )
    ) and all(
        isinstance(expression, Expression)
        for expression in (
            gluon_virtual_result.numerator.gluon_loop_coefficient,
            gluon_virtual_result.numerator.quark_loop_coefficient,
            gluon_virtual_result.gluon_x_integral,
            gluon_virtual_result.quark_x_integral,
            gluon_virtual_result.epsilon_expansion,
            gluon_virtual_result.full_counterterm,
        )
    ) and all(
        isinstance(expression, Expression)
        for entry in final_assembly.entries
        for expression in (
            entry.derived_real_integrand,
            entry.formula_real_integrand,
            entry.real_residual,
            entry.derived_virtual_integrand,
            entry.formula_virtual_integrand,
            entry.virtual_residual,
            entry.derived_counterterm,
            entry.formula_counterterm,
            entry.formula_residual,
            entry.distributional_check.derived_action,
            entry.distributional_check.formula_action,
            *entry.distributional_check.derived_coefficients,
            *entry.distributional_check.formula_coefficients,
            *entry.distributional_check.residuals,
        )
    ) and all(
        isinstance(expression, Expression)
        for expression in (
            final_assembly.normalization.loop_measure,
            final_assembly.normalization.cut_delta_factors,
            final_assembly.normalization.virtuality_measure,
            final_assembly.normalization.coupling_per_as,
            final_assembly.normalization.transverse_solid_angle,
            final_assembly.normalization.msbar_scale,
            final_assembly.normalization.factorized_prefactor,
            final_assembly.normalization.normalized_prefactor,
            final_assembly.normalization.residual,
        )
    )
    mo.callout(
        mo.md(
            "**Backend check:** all mathematical intermediates are Symbolica "
            f"expressions: `{all_symbolica}`."
        ),
        kind="success" if all_symbolica else "danger",
    )
    return


if __name__ == "__main__":
    app.run()
