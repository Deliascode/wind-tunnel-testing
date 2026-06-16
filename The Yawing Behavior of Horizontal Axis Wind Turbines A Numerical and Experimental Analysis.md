# The Yawing Behavior of Horizontal-Axis Wind Turbines: A Numerical and Experimental Analysis

> Markdown transcription generated from the uploaded PDF. Text is copied from all 15 PDF pages using embedded PDF text extraction. Figures/graphs are represented by their original captions plus technical descriptions where the graphic itself cannot be copied directly into a single Markdown file.

---

## Page 1

machines
Article
The Yawing Behavior of Horizontal-Axis Wind
Turbines: A Numerical and Experimental Analysis
Francesco Castellani *,†
, Davide Astolfi†, Francesco Natili † and Francesco Mari †
Department of Engineering, University of Perugia, Via G. Duranti 93, 06125 Perugia, Italy;
davide.astolfi@unipg.it (D.A.); francesco.natili@yahoo.it (F.N.); francesco.mari.max@gmail.com (F.M.)
* Correspondence: francesco.castellani@unipg.it; Tel.: +39-075-585-3709
† These authors contributed equally to this work.
Received: 21 December 2018; Accepted: 4 February 2019; Published: 8 February 2019


Abstract: The yawing of horizontal-axis wind turbines (HAWT) is a major topic in the comprehension
of the dynamical behavior of these kinds of devices. It is important for the study of mechanical
loads to which wind turbines are subjected and it is important for the optimization of wind farms
because the yaw active control can steer the wakes between nearby wind turbines. On these grounds,
this work is devoted to the numerical and experimental analysis of the yawing behavior of a HAWT.
The experimental tests have been performed at the wind tunnel of the University of Perugia on a
three-bladed small HAWT prototype, having two meters of rotor diameter. Two numerical set ups
have been selected: a proprietary code based on the Blade Element Momentum theory (BEM) and
the aeroelastic simulation software FAST, developed at the National Renewable Energy Laboratory
(NREL) in Golden, CO, USA. The behavior of the test wind turbine up to ±45◦of yaw offset is
studied. The performances (power coefficient CP) and the mechanical behavior (thrust coefficient
CT) are studied and the predictions of the numerical models are compared against the wind tunnel
measurements. The results for CT inspire a subsequent study: its behavior as a function of the
azimuth angle is studied and the periodic component equal to the blade passing frequency 3P is
observed. The fluctuation intensity decreases with the yaw angle because the distance between tower
and blade increases. Consequently, the tower interference is studied through the comparison of
measurements and simulations as regards the fore-aft vibration spectrum and the force on top of
the tower.
Keywords: wind energy; wind turbines; blade element momentum theory; aeroelasticity; control
and optimization; vibration
1. Introduction
The yawing behavior of wind turbines has attracted a considerable amount of interest in the
scientific literature about wind energy. On one hand, excessive yaw rates and yaw loads can severely
impact on the reliability of a wind turbine (Hansen [1], Ekelund [2], Micallef [3]): for example,
in Bakshi [4], the effects of yaw error on the reliability of blades is estimated by performing load and
stress analysis for various yaw errors. On the other hand, yaw error can impact impressively on the
power output production: for example, in Wan [5], an equivalent wind speed model and a yaw error
model are employed for simulating the impact of yaw misalignment on the power production of
a multi-megawatt wind turbine. It arises that, approaching rated power, an average misalignment
of 10◦can decrease the power production up to 10%: for this reason, interest is growing as regards
yaw misalignment diagnosis through lidar (Mikkelsen [6], Fleming [7], Pedersen [8]) and-or nacelle
anemometer data mining (Astolfi[9], Pei [10]).
Machines 2019, 7, 15; doi:10.3390/machines7010015
www.mdpi.com/journal/machines

---

## Page 2

Machines 2019, 7, 15
2 of 15
The yaw control has recently become a key aspect of wind farm optimization, in particular as
regards the management of wakes between nearby wind turbines. For example, in Schottler [11],
Trujillo [12], Schottler [13], Bromm [14], the wake deviation is studied in relation to yaw misalignment.
In Schottler [13], results are reported of wind tunnel experiments on turbines in yaw and the wake
flow is observed to be slightly asymmetric with respect to 0◦of yaw. The study in Bromm [14] deals
instead with field tests aimed at demonstrating the applicability of yaw control for deflecting wind
turbine wakes: yaw misalignment up to 20◦with respect to the inflow direction is investigated. Wind
tunnel tests of wake control strategies for power optimization and loads reduction are addressed
also in Campagnolo [15].
First field tests of yaw control for wake steering are presented in
Fleming [16]: an array of wind turbines operating in China has been modified according to a novel
yaw control strategy. The control has been designed based on wind farm models developed at the
National Renewable Energy Laboratory (NREL) in Golden, CO, USA: it includes a Computational
Fluid-Dynamics (CFD) model named SOWFA (Simulator fOr Wind Farm Applications, Fleming [17],
Fleming [18], Fleming [19], Gebraad [20], Gebraad [21]) for the characterization of wakes and an
engineering model named FLORIS (FLOw Redirection and Induction in Steady State) for the yaw
management. The results indicate that the control is indeed capable of improving the power capture in
the wind farm. In Zalkind [22], the increase of fatigue loads experienced by wind turbines using yaw
control to redirect wakes is studied. In Urbàn [23], the focus is on the yaw control of the downstream
wake-affected wind turbines for reducing the blade root flapwise fatigue loading: the main result is
that modest wind turbine lifetime increases can be achieved for low wind speeds and high turbulence
levels, but considerable improvements (up to the order of 20%) can be achieved when the wind speed
is moderate and the turbulence intensity is low. In Kragh [24], the objective is alleviating through yaw
misalignment the blade load variations induced by the wind shear: the main result is that the potential
blade fatigue load reductions depend on the turbulence level and are smaller at high turbulence.
The performance of wind turbines in yaw has been studied in Dai [25] through the formulation of
a yaw index that has been put in relation to the power curve of the wind turbine through operation
data analysis. Some proposals have been formulated for diminishing the yaw error and improving the
energy conversion efficiency of wind turbines: in Kragh [26], the potential of increased power output
with improved yaw alignment is investigated by assessing also the performance of the yaw control
system. In Song [27], a new control structure is proposed: it is based on a wind direction predictive
model and a new yaw control; it is shown that this method can diminish the yaw error and therefore
increase the wind turbine performances.
An inspiring study for the purposes of this work is Schulz [28]: it deals with the CFD simulation
of the influence of yawed inflow conditions on the performance of a wind turbine; a cosine law for the
relation between yaw angle and power output reduction is proposed.
On the grounds of this discussion, the objective of this work is the numerical and experimental
characterization of the behavior of a horizontal-axis wind turbine in yaw. The test case is a three-bladed
horizontal-axis wind turbine HAWT having two meters of rotor diameter: this prototype has been
selected because it has been possible to employ it for full-scale tests in the wind tunnel of the University
of Perugia. Furthermore, previous studies had been conducted about the dynamical behavior of
this wind turbine, especially as regards vibrations and control (Scappaticci [29], Castellani [30],
Castellani [31], Castellani [32]). Sideways, the study of the control and of the performance of small
HAWT technology has recently been attracting attention in the scientific literature, especially as regards
the interaction with complex ambient conditions (as, for example, urban environment: see Battisti [33],
Balduzzi [34], Bianchi [35], Balduzzi [36]). The numerical methods employed in this work for the
simulations are the Fatigue, Aerodynamic, Structures and Turbulence (FAST) software v8, developed
at the NREL in Golden, Colorado, and a Blade Element Momentum (BEM) theory code developed
for the scientific purposes of this study. The performance and the mechanical behavior predicted
by the numerical models are compared to the experimental measurements: particular attention is
devoted to the power coefficient CP and the thrust coefficient CT. The results for the thrust coefficient

---

## Page 3

Machines 2019, 7, 15
3 of 15
inspire a subsequent discussion about the tower interference in relation to the yaw condition: this
part of the study is based on the comparison of the fore-aft measured vibration spectrum against the
FAST simulation.
The manuscript is organized as follows: in Section 2, the numerical and experimental facilities
are presented: respectively, the prototype wind turbine, the wind tunnel, the FAST model, and the
BEM code. Section 3 is devoted to the discussion of the results and, finally, in Section 4 conclusions are
drawn and further directions of this work are indicated.
2. Methods and Facilities
2.1. Experimental Set Up: The Wind Turbine and the Wind Tunnel
The HAWT prototype selected for this work has these main features:
•
the mass of the nacelle is 40 kg;
•
the rotor diameter is 2 m, the hub height is 1.2 m and the hub radius is 0.13 m;
•
the minimum chord of the profile is 5 cm and the maximum is 15 cm;
•
the minimum angle of attack for the profile is 1.7◦and the maximum is 32◦;
•
the prototype is three-bladed and the blades are in polymer reinforced with glass fibers;
•
the blades have fixed pitch angle;
•
in operation, the rotational speed of the rotor goes from more or less 200 to 700 revolutions
per minute;
•
the maximum producible power is 3 kW;
•
the wind turbine control is fully electric and is based on the optimal rotor revolutions per minute
(rpm)–power curve tracking, where the optimal curve has been measured in previous wind
tunnel tests.
In Figure 1, the configuration of the prototype in the wind tunnel is reported.
Figure 1. The small HAWT in the wind tunnel open test section.

> Technical description: Photograph of the three-bladed horizontal-axis wind turbine prototype mounted in the open test section of the University of Perugia wind tunnel. The rotor is positioned upstream of the support tower/nacelle assembly, with the wind-tunnel walls and test-section floor visible as the constrained experimental domain.


---

## Page 4

Machines 2019, 7, 15
4 of 15
The prototype has been tested in the wind tunnel at the Department of Engineering, University
of Perugia, Italy. The wind tunnel is an open test chamber section, whose section is 2.2 m × 2.2 m;
the recovery section is 2.7 m × 2.7 m. The maximum obtainable wind speed is 45 m/s through a
375 kW electric motor. The turbulence intensity in the wind tunnel has been measured and it results
to be quite low: less than 0.4%. The wind speed is measured by a Pitot tube and a cup anemometer
placed at the inlet section. In Figure 2, a scheme of the wind tunnel is reported.
Figure 2. A sketch of the wind tunnel.

> Technical description: Schematic side/top layout of the wind tunnel, showing the inlet, open test chamber, recovery section, and the position of the HAWT model. The sketch documents the test-section geometry used for blockage-correction considerations.

In the wind tunnel experiments, a relevant factor affecting measurements can be wall boundaries
interference. As the wind turbine is placed in a constrained domain, there could be a change in
velocity and pressure fields that surround the stream tube compared to the far upstream. In this work,
the measured power and thrust coefficient were corrected using the equations for blockage correction
by Kinsey and Dumas [37], where the blockage factor BF is defined as:
BF = U
U′ ,
(1)
where U is the free stream wind speed in the wind tunnel with the rotor and U′ is the velocity
without the presence of the rotor. Using BF, it is possible to correct the CP and the CT using the
following equations:
C′
P = CP ·
U
U′
3
= CP · BF3,
(2)
C′
T = CT ·
U
U′
2
= CT · BF2,
(3)
where C′
P and C′
T are the corrected power and thrust coefficient. The blockage factor for the wind tunnel
of the University of Perugia has been studied numerically and experimentally also in Eltayesh [38] and
the results of that work have been employed for the purposes of this study to correctly estimate the
reference free wind speed. On these grounds, for a reliable comparison against numerical simulations,
it should be intended that in Section 3 the experimental reported CP and CT are the corrected ones.
The HAWT has been subjected to steady wind time series having duration of 60 s. During each
time series, the wind turbine has a fixed yaw angle. The tested yaw angles are:
•
0◦,
•
±22.5◦,
•
±45◦.
The selected wind intensity is 10 m/s and some tests have been performed at 8 m/s too.
2.2. The FAST Model
FAST is an open source software, developed at the NREL (National Renewable Energy Laboratory)
in Golden, CO, USA and it is used to set up aeroelastic analysis of horizontal-axis wind turbines.
The versatility of FAST consists of the possibility of customizing the modeling of turbine
components. Electric generator, yaw controller, pitch controller and shaft brake can be modeled

---

## Page 5

Machines 2019, 7, 15
5 of 15
in many ways; the most used includes the use of subroutines, look up tables and the interface with
external software environments.
The number of input files depends on the characteristics of the simulation.
In this test,
the employed input files are:
•
Primary: is the main file that includes simulation settings and the link to the other files.
•
InflowWind: this file contains input wind characteristics, as the intensity and horizontal or vertical
components. In addition, data about computational spatial resolution grid have to be included.
•
AeroDyn: it includes environment air condition, links to the table of blade airfoils polars,
and tower aerodynamic properties.
•
ElastoDyn: in this file, the wind turbine mechanical design (pre-cone, tilt angle, masses and
inertia) is described. Links to blades and tower shape modes are also included.
•
ServoDyn: it manages the behavior of the controllers. Through this file, it is possible to implement
generator, pitch, yaw and braking models.
The main steps of the simulation are summarized in the flowchart of Figure 3.
Figure 3. A flowchart of the FAST simulation.

> Technical description: FAST simulation workflow diagram. The process links the primary FAST input file with InflowWind, AeroDyn, ElastoDyn, and ServoDyn modules, then advances the aeroelastic simulation to compute turbine response variables such as power, thrust, and structural loads.

The HAWT selected for this study doesn’t have active pitch or yaw control as shaft brake: as
discussed, for example, in Scappaticci [29], this is quite common for devices having this size because
they can be cheaper in order to meet market requests. For this reason, therefore, only the electric
generator is modeled. Among the many alternatives that FAST offers for generator modeling, a look-up
table has been considered a good solution for this purpose. Actually, the “simple generator model”
(as named in the ServoDyn file) is appropriate for modelling large HAWTs, but is not adequate for
simulating small wind turbine generators. On the other hand, modeling the generator through the call
to environments that are external to FAST, is practical when Proportional, Integral, Derivative (PID)
controllers have to be implemented: this happens most likely in unsteady conditions. In this study,
instead, all the experimental and numerical tests are executed in steady conditions, and therefore the
look-up table has been preferred.
The function of the electric generator is applying a torque to the shaft, depending on the rotational
speed: the resulting power output is the product of torque and speed.
The relationship between shaft rotational speed and electric power is implemented in the model
through the look-up table obtained from wind tunnel steady-state tests on the real turbine to ensure
that, for a given rotational speed, the generator model supplies the effective power.
The experimental rpm–power table has been obtained subjecting the turbine to a constant wind
speed and varying the electrical load until the turbine didn’t produce the maximum power, according
to the MPPT (Maximum Power Point Tracking) theory. Repeating this procedure with different wind
speeds, the rpm–power table has been redacted and implemented in FAST.
Five simulations have been performed with nominal wind speed of 10 m/s. For each wind
intensity regime, yaw angles of -45◦, -22.5◦, 0◦, 22.5◦and 45◦have been selected, as is done in the
wind tunnel tests.
In the FAST simulations, the yaw angle is taken into account in the ElastoDyn file, where it is
possible to impose a custom value to the angle between the wind flow and the normal to the blade
rotational plane. Every simulation has been carried out for a run time of ten seconds: considering that
the initial conditions have been set to minimize the computational time, this duration guarantees the
complete convergence of the results at the end of each cycle.

---

## Page 6

Machines 2019, 7, 15
6 of 15
2.3. The BEM Code
The mechanical loads in yawing conditions have been computed also using the Blade Element
Momentum (BEM) theory. The code has been developed in the Matlab environment for the scientific
purposes of this work.
The formulation of the BEM equations can be found in several textbooks (as for example,
Burton [39]). In the following, some of them are recalled.
The aerodynamic features of the blades are encoded in the drag and lift coefficients, defined as
Cli f t =
2L
ρAre f U2∞
,
(4)
Cdrag =
2D
ρAre f U2∞
,
(5)
where D and L are drag and lift forces, ρ is the air density, Are f is the rotor area and U∞is the
undisturbed wind speed.
The crucial point in the BEM theory is the computation of the axial and tangential induction
factors a and a′.
The axial induction factor is defined as
a = U∞-Ud
U∞
,
(6)
where Ud is the velocity at disk and U∞is the free-stream velocity.
The tangential inflow factor a′ is introduced in the theory because the disk imparts rotation to the
flow downstream. a′ is defined in Equation (7):
a′ = ω
2Ω,
(7)
where ω is the angular velocity imparted to the wake and Ωis the angular velocity of the rotor disk.
The axial and tangential velocities can be written as
Vx = U∞(1 -a),
Vy = ΩR(1 + a).
(8)
The lift and drag coefficients for each angle of attack of each blade section are obtained from polars
that are calculated with the Xfoil airfoil tool. Computing Cx and Cy as:
Cx = Cl cos(φ) + Cd sin(φ),
Cy = Cl sin(φ) + Cd cos(φ),
(9)
it is possible to write tip and hub loss coefficients as (Ning [40]):
ftip = B
2
(R -r)
|sinφ| ,
Ftip = 2
π acos(e-ftip),
(10)
fhub = B
2
(r -Rhub)
Rhub|sinφ|,
Fhub = 2
π acos(e-fhub),
(11)
where Ftip is the tip loss correction, B is blade number, R is the rotor radius, r is the distance to the root
blade section, Fhub is the hub loss correction, and Rhub is hub radius.
If one defines the solidity σ as
σ = Bc
2πr,
(12)

---

## Page 7

Machines 2019, 7, 15
7 of 15
where c is the chord length, one can write
k =
σCx
4 sin φ sin φF,
k′ =
σCx
4 sin φ cos φF,
(13)
where F = f 2
tip. Different equations for a are obtained depending on the solution region (Ning [40]):
If φ > 0 and k > 2/3, the following equations are obtained:
γ1 = 2Fk -(10
9 -F)
γ2 = 2Fk -F(4
3 -F)
γ2 = 2Fk -(25
9 -2F).
(14)
With Equation (14), it is possible to write:
a = γ1 -√γ2
γ3
.
(15)
If φ < 0 and k > 1, the axial induction factor has the following formulation:
a =
k
k -1.
(16)
Instead, if φ > 0 and k < 2/3, one obtains
a =
k
k + 1.
(17)
For a′, a unique formulation is obtained:
a′ =
k′
k′ + 1.
(18)
With Equations (8) to (18), the induction inflow factors are computed, setting as outputs one of the
equations for a, depending on the solution region, and Equation (18) for a′.
The axial induction factor a has to be corrected for yawed wind turbines. Actually, the BEM
equations above recalled are adequate for the simplest case of wind turbines with vanishing yaw angle.
In this work, the following formulation for the yaw correction has been selected:
ayaw = a(1 + K r
R sin(ψ)),
(19)
where ψ is the azimuth angle and K (Shen [41]) is
K = 15
32π tan χ
2 .
(20)
χ is the skew angle and can be computed using
χ = (0.6a + 1)γ,
(21)
where γ is the yaw angle.
In the literature, there are several formulations of the coefficient for correcting the induction factor
with the dependency on the yaw angle (Micallef [3]). For Coleman [42]:
K = tan(χ
2 ),
(22)
For White and Blake [43]:
K =
√
2 tan(χ),
(23)

---

## Page 8

Machines 2019, 7, 15
8 of 15
For Shen [41]:
ayaw = a
"
1 + 15π
32
s
1 -cosγ
1 + cosγ
r
RKsinψ
#
.
(24)
Other formulations have been proposed, for example, by Ackerman [44] and Bianchi [35].
It should be noticed that the above cited different formulations of the induction factor have
been compared and it results that the selection impacts on the CP and CT estimate less than 1%.
Discriminating between these formulations is not the objective of the present work.
3. Results
3.1. Power and Thrust Analysis
In the following, the results from the wind tunnel tests and the numerical simulations are
presented. In Figure 4, the numerical and experimental results are reported for the power coefficient
CP, defined as
CP =
P
1
2ρAU3∞
,
(25)
where P is the produced power, ρ is the air density, A is the blade swept area and U∞is the free-stream
wind intensity. The power coefficient CP is basically the ratio of the produced power to the wind
power and has a theoretical limit according to the Betz [45] law.
The thrust coefficient CT is defined to model the axial force on the wind turbine as:
CT =
F
1
2ρAU2∞
= 4a(1 -a),
(26)
where F = 1
2ρA
U2
∞-U2
w

is the thrust force.
In Figure 5, the numerical and experimental results are reported for the thrust coefficient CT:
it arises that it is considerably dependent on the yaw angle.
-40
-20
0
20
40
γ(∘)
0.1
0.2
0.3
0.4
0.5
Cp
numerical (FAST)
experimental
BEM code
Figure 4. Power coefficients at 10 m/s: experimental vs. numerical results.

> Technical description: Scatter/line comparison of power coefficient C_P versus yaw angle γ at U = 10 m/s. The horizontal axis is γ in degrees, spanning approximately −45° to +45°. The vertical axis is C_P, spanning roughly 0.10 to 0.45. Experimental values, FAST predictions, and BEM-code predictions are plotted. All data series show maximum power coefficient near γ = 0° and decreasing C_P magnitude as |γ| increases; numerical and experimental values are close, with small deviations.


---

## Page 9

Machines 2019, 7, 15
9 of 15
-40
-20
0
20
40
γ(∘)
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9
Ct
numerical∘(FAST)
experimen al
BEM∘code
Figure 5. Thrust coefficients at 10 m/s: experimental vs. numerical results.

> Technical description: Scatter/line comparison of thrust coefficient C_T versus yaw angle γ at U = 10 m/s. The horizontal axis is γ in degrees, spanning approximately −45° to +45°. The vertical axis is C_T, spanning roughly 0.1 to 0.9. Experimental, FAST, and BEM-code results are plotted. C_T is highest near aligned inflow and decreases under yawed inflow; both numerical approaches overpredict measured C_T across yaw angles.

It arises that both numerical models fairly reproduce the power coefficient, while the thrust is
largely overestimated. The maximum percentage error as regards the CP is the order of 5% for the
BEM code and 8% for FAST and, as regards the CT, it is 25% for the BEM code and 20% for FAST.
It should be noticed that, in the numerical simulations, a 95% of generator efficiency has been
supposed. This has been considered a reliable estimate of the generator efficiency of a small HAWT.
Furthermore, this choice is supported by the fact that, for a vanishing yaw angle, the numerical
simulations fairly reproduce the experimental CP coefficient.
The considerable numerical overestimation of the thrust coefficient can be interpreted as partly
due to small error of measurement (i.e., load cell misalignment), but more considerably due to the effect
of blade deformation. As will be discussed in Section 3.3, blade deformations and yaw configurations
modify the distance between the blades and the tower. Every time the distance is reduced, an increasing
effect of tower blockage has to be taken into account, as it reflects in diminishing thrust.
The slight asymmetry with respect to 0◦of both experimental CP and CT curves is explained by
the wind tunnel layout: when the yaw angle is positive, the rotor is closer to right side wall of the
test section than it is to the left side wall when the yaw is negative. For this reason, a slightly higher
blockage effect is expected for positive yaw angles. The asymmetry of the experimental results has
been quantifies as a maximum of 3% for the thrust coefficient and of 8% for the power coefficient.
3.2. Cyclic Variation of the Thrust
Another interesting analysis regards the rotor cyclic variation. The thrust has been averaged on
azimuth angle intervals, as shown in Figure 6: from the Figure, it is possible to notice the presence
of a periodic component equal to the first blade passing frequency 3P. This phenomenon is well
known and can be explained as the interaction between the tower and airflow, causing cyclic decrease
of aerodynamic forces. In correspondence of higher yaw angles, the fluctuation intensity tends to
decrease, as the distance between tower and blades, with respect to the wind direction, increases.
In Figure 7, the thrust curves are scaled with respect to the corresponding mean value. As the
curves tend to overlap, it can be argued that the amplitudes of the oscillations caused by the tower
inference are proportional to the thrust mean value and that this relationship doesn’t depend on the
yaw angle.

---

## Page 10

Machines 2019, 7, 15
10 of 15
0
50
100
150
200
250
300
350
Azimuth ( ∘)
-20
-10
0
10
20
Rotor Thrust Variation (N)
Experimental∘0 ∘∘(10∘m/s)
Experimental∘-45 ∘∘(10∘m/s)
Experimental∘+45 ∘∘(10∘m/s)
Figure 6. The rotor thrust variation, with respect to the average value, as a function of the azimuth angle.

> Technical description: Rotor thrust variation relative to the mean value plotted against blade azimuth angle ψ from 0° to 360°. Multiple curves are plotted for yaw cases including 0°, −22.5°, +22.5°, −45°, and +45° at U = 10 m/s. The curves exhibit periodic thrust oscillations with a 3P blade-passing component. The amplitude is largest for aligned/low-yaw operation and decreases as yaw magnitude increases because blade–tower proximity effects are reduced.

0
50
100
150
200
250
300
350
Azimuth ( ∘)
-30
-20
-10
0
10
20
30
Normalized Thrust Variation (%)
Experimental∘0 ∘∘(10∘m/s)
Experimental∘-45 ∘∘(10∘m/s)
Experimental∘+45 ∘∘(10∘m/s)
Figure 7. The rotor thrust relative variation, with respect to the average value, as a function of the

> Technical description: Experimental rotor thrust relative variation plotted versus azimuth angle ψ from 0° to 360° for yaw cases 0°, −45°, and +45° at U = 10 m/s. The graph emphasizes the cyclic tower-interference signature and shows reduced normalized thrust fluctuation under ±45° yaw compared with the non-yawed case.

azimuth angle.
The tower interference can only be introduced in the FAST numerical model (and, at now, not in
the BEM code) but it can be very hard to correctly estimate the thrust fluctuations. The experimental
measurements revealed a very large oscillation amplitude due to the tower and this can partly be
explained by the high flexibility of the blades.
The effects of the blade deflection has been also investigated with another experiment with a
lower wind speed (8 m/s). In this case, only a zero yaw condition has been analyzed, in order to focus
on the effect of blade deflection on the tower dam (thrust cyclic fluctuations).
In Figure 8, the two plots of the cyclic variation of the thrust coefficient for 8 and 10 m/s of wind
intensity are compared. It is quite clear that the CT fluctuations are more then doubled in the case of
10 m/s with respect to the case of 8 m/s.
For wind speeds lower than 8 m/s, it is possible to argue that the tower interference induced by
blade deflection can be considered negligible. This information is valuable because one can conclude
that the turbine can be modeled disregarding the blade flexibility in a reliable way only at low wind
speed regimes. The speed of 10 m/s can be considered critical from this point of view and it is indeed
interesting to notice how big the effect of a small blade deflection on thrust oscillation is In previous
measuring campaigns, the blade deflection at tip has been measured to be around 7% with a wind
speed of 32 m/s. As a consequence, it is expected that the blade deflection at tip with 10 m/s is of the
order of 1% of the rotor radius and it is remarkable that this small value can induce such a large tower
interaction effect.

---

## Page 11

Machines 2019, 7, 15
11 of 15
These considerations have been corroborated by a preliminary study that will be the object of
further work because it deals with unsteadiness: the wind turbine has been subjected to a ramp wind
intensity time series (from 6 to 10 m/s spanned in 120 s) and the same has been simulated using FAST.
It arises that the mismatch between measurements and simulations, as regards the thrust coefficient,
almost triples at the end of the ramp (approaching 10 m/s) with respect to the beginning (moving from
6 m/s). This is a further hint of the fact that neglecting a small blade deflection can have a considerable
impact on the reliability of low-fidelity models.
0
50
100
150
200
250
300
350
Azimuth ( ∘)
-0.15
-0.10
-0.05
0.00
0.05
0.10
0.15
Rotor Thrust Coefficient variation
Experimental∘0 ∘∘(8∘m/s)
Experimental∘0 ∘∘(10∘m/s)
Figure 8. The rotor thrust coefficient cyclic variation in different wind tunnel tests with a wind speed

> Technical description: Rotor thrust coefficient cyclic variation plotted for wind-tunnel tests at U = 8 m/s and U = 10 m/s. The graph compares repeated cyclic C_T fluctuation patterns under different wind speeds, highlighting repeatability of the blade-passing/tower-interference component and the dependence of oscillation amplitude on operating condition.

of 8 m/s and 10 m/s.
3.3. Acceleration Analysis and Tower Interference
As discussed above, the tower interference produces non-negligible experimental phenomena.
In addition, the FAST numerical model is capable of accounting for the effect of the tower, which is
strictly related to the minimum amplitude of the gap between the blade surface and the tower: if this
gap is quite low, cyclic components with a frequency equal to the number of blades multiplied by the
rotor speed can be observed. The gap can also affect somehow the global rotor thrust and this effect
should be strongly linked to the actual blade deformation that unfortunately is not modeled in the
numerical set up of FAST. Anyway, this is a meaningful hint about the observed mismatch between
experimental and numerical rotor thrust coefficient.
Even without including the blade deformations, the numerical model can give an interesting
insight about the influence of the yaw angle on the vibration spectrum. During the experiments, a
triaxial accelerometer has been used to collect vibration data on the top of the tower. The forces
have been measured too, using a load cell.
Comparing the amplitudes in the order spectrum
(Figures 9 and 10), it is quite clear that the 3P component is much weaker when the turbine is yawed.
From Figures 9 and 10, the different dynamic performance of the two measuring equipment also arises:
accelerometers are much more sensible in observing how the dynamic loads components change
when the turbine is yawed, even if they could be affected by noise arising also from electromechanical
couplings (Castellani [31]).

---

## Page 12

Machines 2019, 7, 15
12 of 15
2
4
6
8
10
Order
0.0
0.2
0.4
0.6
0.8
1.0
1.2
1.4
Amplitude (m/s2)
0∘
∘45∘
Figure 9. Experimental normalized order spectrum of the acceleration (fore-aft component normalized

> Technical description: Experimental normalized order spectrum of the fore-aft acceleration component, normalized by rotational speed. The abscissa is order/frequency normalized to rotor speed, with labeled harmonics including 1P and 3P. The spectrum shows dominant periodic content at the blade-passing frequency 3P, associated with the three-bladed rotor and tower-interference effects.

on the amplitude of the 3P component with zero yaw).
2
4
6
8
10
Order
0.0
0.2
0.4
0.6
0.8
1.0
1.2
1.4
Amplitude (N)
0∘
∘45∘
Figure 10. Experimental normalized order spectrum of the forces (fore-aft component normalized on

> Technical description: Experimental normalized order spectrum of the fore-aft force component, normalized by rotational speed. The spectrum displays harmonic peaks, especially at 3P, indicating cyclic aerodynamic/structural loading induced by blade passage in front of the tower and modulated by yaw configuration.

the amplitude of the 3P component with zero yaw).
The error in the amplitude of the experimental and numerical accelerations is biased mainly
by the effect of the electromechanical coupling (that is actually not correctly reproduced in FAST as
discussed, for example, in Castellani [31]). Consequently, the effect of the yaw has been discussed in
Figure 9 using a normalized amplitude. Anyway, it is meaningful to notice the different amplitude
of the 3P component for vanishing yaw angle, with respect to the yawed cases. This is induced by
the different effect of the tower due to the higher gap between the tower and the blade surface in
the yawed cases. Sideways, this phenomenon is a reasonable explanation of the numerical thrust
overestimation (noticed in Section 3.1), which increases when the yaw angle vanishes and the tower
interference is maximum.
4. Conclusions
This work has been devoted to a topic that has been attracting recently a certain amount of
attention in wind energy literature, mainly because of the interest in wind farm cooperative control and
wake steering, but is still overlooked by several points of view: the yawing behavior of horizontal-axis
wind turbines.
A full-scale three-bladed HAWT having 2 m of rotor diameter has been selected as a test case
for this work, also on the ground of previous studies (Scappaticci [29], Castellani [31], Castellani [32])
characterizing its design, control and vibration behavior under steady and unsteady conditions.

---

## Page 13

Machines 2019, 7, 15
13 of 15
A measurement campaign has been conducted in the wind tunnel of the University of Perugia and
the experimental conditions have been replicated using two simulation frameworks: the aeroelastic
software FAST, developed at the NREL, and an ad hoc developed code based on Blade Element
Momentum Theory. The wind turbine has been subjected in the wind tunnel to steady wind time
series at different yaw angles with respect to the wind flow: ±45◦, ±22.5◦, and 0◦. The response
of the wind turbine has been analyzed by the point of view of the power coefficient CP and of the
thrust coefficient CT. The experimental measurements have been compared to the predictions from the
numerical simulations. It arises that the two numerical models quite reliably reproduce the CP and
how it varies depending on the yaw angle.
A meaningful overestimation of the numerical thrust coefficient with respect to the measurements
is observed. This has inspired further analysis about the tower interference for vanishing and
non-vanishing yaw angles. The analysis of the thrust coefficient as a function of the azimuth angle
indicates that, as expected, a periodic component equal to the first blade passing frequency 3P is
clearly visible. This is due to the interaction between the tower and the wind flow, causing the cyclic
decrease of aerodynamic forces. The amplitude of the absolute oscillation caused by the tower inference
decreases with the yaw angle because the distance between tower and blade increases. The tower
interference has been analyzed also through the comparison of the measured and simulated (with
FAST) fore-aft vibration spectra and force at the top of the tower: the amplitude of the 3P component
for vanishing yaw angle results being different with respect to the yawed cases. This is explained
by the higher distance between the tower and the blade surface in the yawed cases. Sideways,
since the tower interference is difficult to model in FAST for small HAWTs (as discussed, for example,
in Castellani [31]), this possibly explains why the discrepancy between simulated and measured CT is
higher when the yaw angle vanishes and the tower interference is maximum.
A valuable result for the present work is the increase of knowledge about the steady behaviour
of the HAWT in different yaw conditions and about the limits of low-fidelity models in reproducing
reliably the dynamical behavior of the HAWT. A further outlook of this work is to use these data for
developing new yaw control strategies and reliably modeling it dynamically. An ongoing development
of the present work is an in-depth analysis about the influence between the blade tip and the solid
wind tunnel walls and about how this effect impacts the reliability of the numerical simulations in
reproducing the real experimental set-up. Finally, on the grounds of the discussion in Section 3.3,
it would be particularly valuable to include the modeling of the blade flexibility in the numerical
simulations and to validate it against devoted experimental campaigns.
Author Contributions: Conceptualization, F.C., D.A. and F.N.; methodology, F.C.; software, F.C., F.N. and F.M.;
validation, F.C., D.A. and F.N.; formal analysis, F.C., D.A. and F.N.; investigation, F.C., D.A. and F.N.; resources,
F.C.; data curation, F.C. and F.N., writing—original draft preparation, D.A. and F.N.; writing—review and editing,
F.C., D.A. and F.N.; supervision, F.C.
Funding: This research received no external funding.
Acknowledgments: The authors thank Filippo Campagnolo, Matteo Becchetti and Francesco Berno for the useful
contributions in the development of the analysis. D.A. acknowledges the Italian funding source Progetto di
Ricerca di Interesse Nazionale (PRIN) for the support, in the context of the project entitled SOFTWIND (Smart
Optimized Fault Tolerant WIND turbines.
Conflicts of Interest: The authors declare no conflict of interest.
References
1.
Hansen, A.C. Yaw Dynamics of Horizontal Axis Wind Turbines; NREL/TP-442-4822, National Renewable
Energy Lab.: Golden, CO, USA, 1992.
2.
Ekelund, T. Yaw control for reduction of structural dynamic loads in wind turbines. J. Wind Eng. Ind. Aerodyn.
2000, 85, 241–262. [CrossRef]
3.
Micallef, D.; Sant, T. A review of wind turbine yaw aerodynamics. In Wind Turbines-Design, Control and
Applications; InTech: London, UK, 2016.

---

## Page 14

Machines 2019, 7, 15
14 of 15
4.
Bakhshi, R.; Sandborn, P. The effect of yaw error on the reliability of wind turbine blades. In Proceedings of
the ASME 2016 10th International Conference on Energy Sustainability, Charlotte, NC, USA, 26–30 June 2016;
pp. V001T14A001–V001T14A007.
5.
Wan, S.; Cheng, L.; Sheng, X. Effects of yaw error on wind turbine running characteristics based on the
equivalent wind speed model. Energies 2015, 8, 6286–6301. [CrossRef]
6.
Mikkelsen, T.; Angelou, N.; Hansen, K.; Sjöholm, M.; Harris, M.; Slinger, C.; Hadley, P.; Scullion, R.; Ellis, G.;
Vives, G. A spinner-integrated wind lidar for enhanced wind turbine control. Wind Energy 2013, 16, 625–643.
[CrossRef]
7.
Fleming, P.; Scholbrock, A.; Jehu, A.; Davoust, S.; Osler, E.; Wright, A.D.; Clifton, A. Field-test results using a
nacelle-mounted lidar for improving wind turbine power capture by reducing yaw misalignment. J. Phys.
Conf. Ser. 2014, 524, 012002. [CrossRef]
8.
Pedersen, T.F.; Demurtas, G.; Zahle, F.
Calibration of a spinner anemometer for yaw misalignment
measurements. Wind Energy 2015, 18, 1933–1952. [CrossRef]
9.
Astolfi, D.; Castellani, F.; Scappaticci, L.; Terzi, L. Diagnosis of wind turbine misalignment through SCADA
data. Diagnostyka 2017, 18, 17–24 .
10.
Pei, Y.; Qian, Z.; Jing, B.; Kang, D.; Zhang, L. Data-Driven Method for Wind Turbine Yaw Angle Sensor
Zero-Point Shifting Fault Detection. Energies 2018, 11, 553. [CrossRef]
11.
Schottler, J.; Hölling, A.; Peinke, J.; Hölling, M. Wind tunnel tests on controllable model wind turbines in
yaw. In Proceedings of the 34th Wind Energy Symposium, San Diego, CA, USA, 4–8 January 2016; p. 1523.
12.
Trujillo, J.J.; Seifert, J.K.; Würth, I.; Schlipf, D.; Kühn, M. Full-field assessment of wind turbine near-wake
deviation in relation to yaw misalignment. Wind Energy Sci. 2016, 1, 41–53. [CrossRef]
13.
Schottler, J.; Bartl, J.; Mühle, F.; Sætran, L.; Peinke, J.; Hölling, M. Wind tunnel experiments on wind turbine
wakes in yaw: Redefining the wake width. Wind Energy Sci. 2018, 3, 257. [CrossRef]
14.
Bromm, M.; Rott, A.; Beck, H.; Vollmer, L.; Steinfeld, G.; Kühn, M. Field investigation on the influence of
yaw misalignment on the propagation of wind turbine wakes. Wind Energy 2018, 21, 1011–1028. [CrossRef]
15.
Campagnolo, F.; Petrovi´c, V.; Bottasso, C.L.; Croce, A. Wind tunnel testing of wake control strategies.
In Proceedings of the American Control Conference (ACC), Boston, MA, USA, 6–8 July 2016; pp. 513–518.
16.
Fleming, P.; Annoni, J.; Shah, J.J.; Wang, L.; Ananthan, S.; Zhang, Z.; Hutchings, K.; Wang, P.; Chen, W.;
Chen, L. Field test of wake steering at an offshore wind farm. Wind Energy Sci. 2017, 2, 229–239. [CrossRef]
17.
Fleming, P.A.; Gebraad, P.M.; Lee, S.; van Wingerden, J.W.; Johnson, K.; Churchfield, M.; Michalakes, J.;
Spalart, P.; Moriarty, P. Evaluating techniques for redirecting turbine wakes using SOWFA. Renew. Energy
2014, 70, 211–218. [CrossRef]
18.
Fleming, P.A.; Ning, A.; Gebraad, P.M.; Dykes, K. Wind plant system engineering through optimization of
layout and yaw control. Wind Energy 2016, 19, 329–344. [CrossRef]
19.
Fleming, P.; Churchfield, M.; Scholbrock, A.; Clifton, A.; Schreck, S.; Johnson, K.; Wright, A.; Gebraad, P.;
Annoni, J.; Naughton, B.; et al. Detailed field test of yaw-based wake steering. J. Phys. Conf. Ser. 2016,
753, 052003. [CrossRef]
20.
Gebraad, P.; Teeuwisse, F.; Van Wingerden, J.; Fleming, P.A.; Ruben, S.; Marden, J.; Pao, L. Wind plant power
optimization through yaw control using a parametric model for wake effects—A CFD simulation study.
Wind Energy 2016, 19, 95–114. [CrossRef]
21.
Gebraad, P.; Thomas, J.J.; Ning, A.; Fleming, P.; Dykes, K. Maximization of the annual energy production of
wind power plants by optimization of layout and yaw-based wake control. Wind Energy 2017, 20, 97–107.
[CrossRef]
22.
Zalkind, D.S.; Pao, L.Y. The fatigue loading effects of yaw control for wind plants. In Proceedings of the
American Control Conference (ACC), Boston, MA, USA, 6–8 July 2016; pp. 537–542.
23.
Urbán, A.M.; Larsen, T.J.; Larsen, G.C.; Held, D.P.; Dellwik, E.; Verelst, D. Optimal yaw strategy for
optimized power and load in various wake situations. J. Phys. Conf. Ser. 2018, 1102, 012019. [CrossRef]
24.
Kragh, K.A.; Hansen, M.H. Load alleviation of wind turbines by yaw misalignment. Wind Energy 2014,
17, 971–982. [CrossRef]
25.
Dai, J.; Yang, X.; Hu, W.; Wen, L.; Tan, Y. Effect investigation of yaw on wind turbine performance based on
SCADA data. Energy 2018, 149, 684–696. [CrossRef]
26.
Kragh, K.A.; Hansen, M.H. Potential of power gain with improved yaw alignment. Wind Energy 2015,
18, 979–989. [CrossRef]

---

## Page 15

Machines 2019, 7, 15
15 of 15
27.
Song, D.; Yang, J.; Fan, X.; Liu, Y.; Liu, A.; Chen, G.; Joo, Y.H. Maximum power extraction for wind turbines
through a novel yaw control solution using predicted wind directions.
Energy Convers. Manag. 2018,
157, 587–599. [CrossRef]
28.
Schulz, C.; Letzgus, P.; Lutz, T.; Krämer, E. CFD study on the impact of yawed inflow on loads, power and
near wake of a generic wind turbine. Wind Energy 2017, 20, 253–268. [CrossRef]
29.
Scappatici, L.; Bartolini, N.; Castellani, F.; Astolfi, D.; Garinei, A.; Pennicchi, M. Optimizing the design
of horizontal-axis small wind turbines: From the laboratory to market. J. Wind Eng. Ind. Aerodyn. 2016,
154, 58–68. [CrossRef]
30.
Castellani, F.; Becchetti, M.; Astolfi, D.; Cianetti, F. Dynamic Experimental and Numerical Analysis of Loads
for a Horizontal Axis Micro Wind Turbine. In Green Energy and Technology; Springer: Berlin, Germany, 2017,
pp. 79–90.
31.
Castellani, F.; Astolfi, D.; Becchetti, M.; Berno, F.; Cianetti, F.; Cetrini, A. Experimental and Numerical
Vibrational Analysis of a Horizontal-Axis Micro-Wind Turbine. Energies 2018, 11, 456. [CrossRef]
32.
Castellani, F.; Astolfi, D.; Becchetti, M.; Berno, F. Experimental and Numerical Analysis of the Dynamical
Behavior of a Small Horizontal-Axis Wind Turbine under Unsteady Conditions: Part I. Machines 2018, 6, 52.
[CrossRef]
33.
Battisti, L.; Benini, E.; Brighenti, A.; Dell’Anna, S.; Castelli, M.R. Small wind turbine effectiveness in the
urban environment. Renew. Energy 2018, 129, 102–113. [CrossRef]
34.
Balduzzi, F.; Bianchini, A.; Ferrari, L. Microeolic turbines in the built environment: Influence of the
installation site on the potential energy yield. Renew. Energy 2012, 45, 163–174. [CrossRef]
35.
Bianchi, S.; Bianchini, A.; Ferrara, G.; Ferrari, L. Small wind turbines in the built environment: Influence of
flow inclination on the potential energy yield. J. Turbomach. 2014, 136, 041013. [CrossRef]
36.
Balduzzi, F.; Bigalli, S.; Bianchini, A. A hybrid BEM-CFD model for effective numerical siting analyses of
wind turbines in the urban environment. J. Phys. Conf. Ser. 2018, 1037, 072029. [CrossRef]
37.
Kinsey, T.; Dumas, G. Impact of channel blockage on the performance of axial and cross-flow hydrokinetic
turbines. Renew. Energy 2016, 103, 239–254. [CrossRef]
38.
Eltayesh, A.; Burlando, M.; Castellani, F.; Becchetti, M. Experimental and numerical study of the wind tunnel
blockage effects on the behaviour of a horizontal axis wind turbine. Lect. Notes Civ. Eng. 2019, in press.
39.
Burton, T.; Jenkins, N.; Sharpe, D.; Bossanyi, E. Wind Energy Handbook; John Wiley & Sons: Hoboken, NJ,
USA, 2011.
40.
Ning, A.; Hayman, G.; Damiani, R.; Jonkman, J.M. Development and Validation of a New Blade Element
Momentum Skewed-Wake Model within AeroDyn. In Proceedings of the 33rd Wind Energy Symposium,
Kissimmee, FL, USA, 5–9 January 2015; p. 0215.
41.
Shen, W.Z.; Zhu, W.J.; Sørensen, J.N. Actuator line/Navier–Stokes computations for the MEXICO rotor:
Comparison with detailed measurements. Wind Energy 2012, 15, 811–825. [CrossRef]
42.
Coleman, R.P.; Feingold, A.M.; Stempin, C.W. Evaluation of the Induced-Velocity Field of an Idealized Helicoptor
Rotor; NACA-WR-L-126; National Aeronautics and Space Administration Hampton Va Langley Research
Center: Washington, DC, USA, 1945.
43.
White, F.; Blake, B.B. Improved Method Predicting Helicopter Control Response and Gust Sensitivity.
American Helicopter Society. 1979. Available online: https://vtol.org/store/product/improved-method-of-
predicting-helicopter-control-response-and-gust-sensitivity-2286.cfm (accessed on 8 February 2019).
44.
Ackerman, M. Yaw modelling of small wind turbines. J. Wind Eng. Ind. Aerodyn. 1992, 39, 1–9. [CrossRef]
45.
Betz, A. Introduction to the Theory of Flow Machines; Pergamon Press: Oxford, UK, 1966.
c⃝2019 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access
article distributed under the terms and conditions of the Creative Commons Attribution
(CC BY) license (http://creativecommons.org/licenses/by/4.0/).

---

## Figure and graph descriptions index

**Figure 1.** Technical description: Photograph of the three-bladed horizontal-axis wind turbine prototype mounted in the open test section of the University of Perugia wind tunnel. The rotor is positioned upstream of the support tower/nacelle assembly, with the wind-tunnel walls and test-section floor visible as the constrained experimental domain.

**Figure 2.** Technical description: Schematic side/top layout of the wind tunnel, showing the inlet, open test chamber, recovery section, and the position of the HAWT model. The sketch documents the test-section geometry used for blockage-correction considerations.

**Figure 3.** Technical description: FAST simulation workflow diagram. The process links the primary FAST input file with InflowWind, AeroDyn, ElastoDyn, and ServoDyn modules, then advances the aeroelastic simulation to compute turbine response variables such as power, thrust, and structural loads.

**Figure 4.** Technical description: Scatter/line comparison of power coefficient C_P versus yaw angle γ at U = 10 m/s. The horizontal axis is γ in degrees, spanning approximately −45° to +45°. The vertical axis is C_P, spanning roughly 0.10 to 0.45. Experimental values, FAST predictions, and BEM-code predictions are plotted. All data series show maximum power coefficient near γ = 0° and decreasing C_P magnitude as |γ| increases; numerical and experimental values are close, with small deviations.

**Figure 5.** Technical description: Scatter/line comparison of thrust coefficient C_T versus yaw angle γ at U = 10 m/s. The horizontal axis is γ in degrees, spanning approximately −45° to +45°. The vertical axis is C_T, spanning roughly 0.1 to 0.9. Experimental, FAST, and BEM-code results are plotted. C_T is highest near aligned inflow and decreases under yawed inflow; both numerical approaches overpredict measured C_T across yaw angles.

**Figure 6.** Technical description: Rotor thrust variation relative to the mean value plotted against blade azimuth angle ψ from 0° to 360°. Multiple curves are plotted for yaw cases including 0°, −22.5°, +22.5°, −45°, and +45° at U = 10 m/s. The curves exhibit periodic thrust oscillations with a 3P blade-passing component. The amplitude is largest for aligned/low-yaw operation and decreases as yaw magnitude increases because blade–tower proximity effects are reduced.

**Figure 7.** Technical description: Experimental rotor thrust relative variation plotted versus azimuth angle ψ from 0° to 360° for yaw cases 0°, −45°, and +45° at U = 10 m/s. The graph emphasizes the cyclic tower-interference signature and shows reduced normalized thrust fluctuation under ±45° yaw compared with the non-yawed case.

**Figure 8.** Technical description: Rotor thrust coefficient cyclic variation plotted for wind-tunnel tests at U = 8 m/s and U = 10 m/s. The graph compares repeated cyclic C_T fluctuation patterns under different wind speeds, highlighting repeatability of the blade-passing/tower-interference component and the dependence of oscillation amplitude on operating condition.

**Figure 9.** Technical description: Experimental normalized order spectrum of the fore-aft acceleration component, normalized by rotational speed. The abscissa is order/frequency normalized to rotor speed, with labeled harmonics including 1P and 3P. The spectrum shows dominant periodic content at the blade-passing frequency 3P, associated with the three-bladed rotor and tower-interference effects.

**Figure 10.** Technical description: Experimental normalized order spectrum of the fore-aft force component, normalized by rotational speed. The spectrum displays harmonic peaks, especially at 3P, indicating cyclic aerodynamic/structural loading induced by blade passage in front of the tower and modulated by yaw configuration.
