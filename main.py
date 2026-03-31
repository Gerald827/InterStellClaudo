"""
InterSellclaudo — Simulation de Relativité Générale
Inspiré du film Interstellar

Modules :
    1. Visualisation du trou noir de Kerr (disque d'accrétion, sphère de photons, jets)
    2. Dilatation temporelle gravitationnelle (f_obs = f_em × √(1 − rs/r))
    3. Lentille gravitationnelle (α = 4GM / c²b)
    4. Effet Doppler relativiste (f_obs/f_em = √((1+β)/(1−β)) / γ)

Dépendances : pip install pygame numpy
"""

import sys
import math
import random
import pygame
import numpy as np

# ─────────────────────────────────────────────
#  Constantes physiques
# ─────────────────────────────────────────────
G_SI  = 6.674e-11      # m³ kg⁻¹ s⁻²
C_SI  = 2.998e8        # m/s
M_SOL = 1.989e30       # kg  (masse solaire)


def schwarzschild_radius(M_kg: float) -> float:
    """rs = 2GM / c²"""
    return 2 * G_SI * M_kg / C_SI**2


def gravitational_time_dilation(r_over_rs: float) -> float:
    """τ/t = √(1 − rs/r)   (métrique de Schwarzschild)"""
    if r_over_rs <= 1.0:
        return 0.0
    return math.sqrt(max(0.0, 1.0 - 1.0 / r_over_rs))


def lensing_deflection_angle(b_over_rs: float) -> float:
    """α = 4GM/c²b = 2rs/b  (déflexion en radians, champ faible)"""
    if b_over_rs <= 0:
        return math.pi
    return 2.0 / b_over_rs


def relativistic_doppler(beta: float) -> float:
    """f_obs/f_em = √((1+β)/(1−β))   (β = v_r / c)"""
    beta = max(-0.9999, min(0.9999, beta))
    return math.sqrt((1.0 + beta) / (1.0 - beta))


# ─────────────────────────────────────────────
#  Palette & thème
# ─────────────────────────────────────────────
BG        = (4,   4,  14)
PANEL_BG  = (10,  12,  28)
ACCENT    = (255, 200,  60)
ACCENT2   = (100, 160, 255)
WHITE     = (240, 240, 255)
GRAY      = (130, 130, 160)
TAB_ACT   = ( 30,  50, 100)
TAB_IDLE  = ( 14,  18,  40)
BORDER    = ( 60,  80, 130)


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ─────────────────────────────────────────────
#  Simulation
# ─────────────────────────────────────────────
class InterSellclaudo:

    TABS = ["Trou Noir de Kerr", "Dilatation Temporelle",
            "Lentille Gravitationnelle", "Effet Doppler"]

    def __init__(self):
        pygame.init()
        self.W, self.H = 1280, 760
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("InterSellclaudo — Relativité Générale")
        self.clock = pygame.time.Clock()

        self._init_fonts()

        # ── Paramètres physiques (modifiables via sliders) ──
        self.mass_solar = 15.0        # M☉
        self.spin       = 0.85        # paramètre a/M  ∈ [0, 1)
        self.dist_rs    = 5.0         # distance observateur en rs

        # ── État ──
        self.time    = 0.0
        self.paused  = False
        self.tab     = 0

        # ── Particules du disque d'accrétion ──
        self.particles = self._init_particles()

        # ── Étoiles de fond (fixes) ──
        rng = random.Random(2024)
        self.stars = [(rng.randint(0, self.W), rng.randint(0, self.H - 220),
                       rng.randint(40, 200)) for _ in range(300)]

        # ── Sliders ──
        slider_cx = self.W // 2
        self.slider_defs = [
            {"key": "mass_solar", "label": "Masse (M☉)",  "min": 1.0,  "max": 60.0, "cx": slider_cx - 320},
            {"key": "spin",       "label": "Spin  (a/M)", "min": 0.0,  "max": 0.998,"cx": slider_cx},
            {"key": "dist_rs",    "label": "Distance (rs)","min": 1.5, "max": 25.0, "cx": slider_cx + 320},
        ]
        self.slider_w = 160
        self.slider_y = self.H - 60
        self.dragging = None

    # ── Fonts ──────────────────────────────────
    def _init_fonts(self):
        pygame.font.init()
        try:
            self.fnt_big   = pygame.font.SysFont("DejaVuSans", 22, bold=True)
            self.fnt_med   = pygame.font.SysFont("DejaVuSans", 17)
            self.fnt_small = pygame.font.SysFont("DejaVuSansMono", 13)
            self.fnt_title = pygame.font.SysFont("DejaVuSans", 26, bold=True)
        except Exception:
            self.fnt_big   = pygame.font.Font(None, 24)
            self.fnt_med   = pygame.font.Font(None, 19)
            self.fnt_small = pygame.font.Font(None, 15)
            self.fnt_title = pygame.font.Font(None, 28)

    # ── Particules ─────────────────────────────
    def _init_particles(self):
        rng = random.Random(42)
        particles = []
        for _ in range(300):
            r      = rng.uniform(1.4, 7.0)
            angle  = rng.uniform(0, 2 * math.pi)
            # vitesse orbitale keplerienne simplifiée
            speed  = 0.012 / math.sqrt(r) * (1 + 0.4 * self.spin)
            bright = rng.uniform(0.4, 1.0)
            size   = rng.choice([1, 1, 1, 2, 2, 3])
            particles.append({"r": r, "a": angle, "speed": speed,
                               "bright": bright, "size": size})
        return particles

    # ── Propriétés physiques dérivées ──────────
    @property
    def M_kg(self):
        return self.mass_solar * M_SOL

    @property
    def rs(self):
        return schwarzschild_radius(self.M_kg)

    @property
    def kerr_a(self):
        return self.spin * G_SI * self.M_kg / C_SI**2

    @property
    def td_factor(self):
        return gravitational_time_dilation(self.dist_rs)

    # ── Boucle principale ──────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            if not self.paused:
                self.time += dt
                self._update_particles(dt)
            self._draw()
            pygame.display.flip()

    def _handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif ev.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif ev.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.tab = ev.key - pygame.K_1
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self._click(ev.pos)
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                self.dragging = None
            elif ev.type == pygame.MOUSEMOTION and self.dragging is not None:
                self._drag(ev.pos)

    def _click(self, pos):
        mx, my = pos
        # onglets
        tw = self.W // len(self.TABS)
        if self.H - 220 <= my <= self.H - 192:
            self.tab = min(mx // tw, len(self.TABS) - 1)
            return
        # sliders
        for sd in self.slider_defs:
            sx = sd["cx"] - self.slider_w // 2
            sy = self.slider_y
            if sx - 8 <= mx <= sx + self.slider_w + 8 and sy - 8 <= my <= sy + 24:
                self.dragging = sd
                self._apply_slider(sd, mx)
                return

    def _drag(self, pos):
        if self.dragging:
            self._apply_slider(self.dragging, pos[0])

    def _apply_slider(self, sd, mx):
        sx = sd["cx"] - self.slider_w // 2
        t  = max(0.0, min(1.0, (mx - sx) / self.slider_w))
        val = sd["min"] + t * (sd["max"] - sd["min"])
        setattr(self, sd["key"], val)
        # Réinitialiser les particules si le spin change
        if sd["key"] in ("mass_solar", "spin"):
            self.particles = self._init_particles()

    def _update_particles(self, dt):
        for p in self.particles:
            p["a"] += p["speed"] * (1 + 0.4 * self.spin) * dt * 60

    # ── Rendu ──────────────────────────────────
    def _draw(self):
        self.screen.fill(BG)
        # étoiles
        for sx, sy, sb in self.stars:
            self.screen.set_at((sx, sy), (sb, sb, sb))

        # panneau principal
        content_rect = pygame.Rect(0, 0, self.W, self.H - 220)
        if self.tab == 0:
            self._draw_black_hole(content_rect)
        elif self.tab == 1:
            self._draw_time_dilation(content_rect)
        elif self.tab == 2:
            self._draw_lensing(content_rect)
        elif self.tab == 3:
            self._draw_doppler(content_rect)

        self._draw_ui()

    # ────────────────────────────────────────────
    #  TAB 0 — Trou Noir de Kerr
    # ────────────────────────────────────────────
    def _draw_black_hole(self, rect):
        cx = self.W // 2
        cy = rect.height // 2 - 10
        scale = min(rect.width, rect.height) // 9  # 1 rs = scale px

        # ── Disque d'accrétion (partie arrière) ──
        self._draw_disk(cx, cy, scale, front=False)

        # ── Horizon des événements ──
        eh_r = int(scale * 0.92)
        pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), eh_r)

        # ── Ergosphère (Kerr) ──
        ergo_r = scale * (1 + math.sqrt(max(0, 1 - self.spin**2)))
        pygame.draw.ellipse(self.screen, (80, 40, 150),
                            (int(cx - ergo_r), int(cy - ergo_r * 0.35),
                             int(ergo_r * 2), int(ergo_r * 0.7)), 1)

        # ── Sphère de photons (r = 1.5 rs) ──
        ph_r = int(scale * 1.5)
        pygame.draw.circle(self.screen, (255, 200, 50), (cx, cy), ph_r, 1)

        # ── Disque d'accrétion (partie avant) ──
        self._draw_disk(cx, cy, scale, front=True)

        # ── Jets relativistes (axe rotation) ──
        for sign in (+1, -1):
            for i, alpha in enumerate(np.linspace(0, 1, 30)):
                jx = cx + int(alpha * 8 * math.sin(self.time * 0.3 + i * 0.2))
                jy = cy + sign * int(scale * 0.9 + alpha * scale * 2.5)
                r_j = max(0, int(200 * (1 - alpha)))
                g_j = max(0, int(100 * (1 - alpha)))
                b_j = min(255, int(255 * (1 - alpha * 0.5)))
                pygame.draw.circle(self.screen, (r_j, g_j, b_j), (jx, jy), max(1, int(3 * (1 - alpha))))

        # ── Étiquettes ──
        infos = [
            f"Masse  : {self.mass_solar:.1f} M☉  =  {self.M_kg:.2e} kg",
            f"rs     : {self.rs:.3e} m",
            f"Spin   : a = {self.spin:.3f}  →  a_kerr = {self.kerr_a:.2e} m",
            f"Ergo-  sphère visible en violet",
            f"Sphère photons  r = 1.5 rs  (jaune)",
        ]
        for i, txt in enumerate(infos):
            s = self.fnt_small.render(txt, True, GRAY)
            self.screen.blit(s, (12, 12 + i * 18))

        title = self.fnt_title.render("Trou Noir de Kerr", True, ACCENT)
        self.screen.blit(title, (self.W - title.get_width() - 12, 12))

        eq = self.fnt_small.render("ds² = −(1−rs·r/ρ²)c²dt² − 2rs·r·a·sin²θ/ρ²·c·dt·dφ + …", True, ACCENT2)
        self.screen.blit(eq, (self.W // 2 - eq.get_width() // 2, rect.height - 30))

    def _draw_disk(self, cx, cy, scale, front: bool):
        for r_factor in np.arange(1.1, 7.5, 0.12):
            rx = r_factor * scale
            ry = r_factor * scale * 0.28

            # Température : plus chaud vers l'intérieur
            t  = 1.0 / r_factor
            rc = min(255, int(80 + 200 * t**0.6))
            gc = min(255, int(30 + 130 * t**1.2))
            bc = min(255, int(10 + 240 * t**2.5))
            color = (rc, gc, bc)

            pts = []
            half = np.linspace(0, math.pi, 40)
            for a in (half if front else (half + math.pi)):
                pts.append((int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a))))
            if len(pts) > 1:
                pygame.draw.lines(self.screen, color, False, pts, 1)

        # Particules
        for p in self.particles:
            px = cx + p["r"] * scale * math.cos(p["a"])
            py = cy + p["r"] * scale * 0.28 * math.sin(p["a"])
            is_front = math.sin(p["a"]) > 0
            if is_front != front:
                continue
            if p["r"] * scale < scale * 0.92:
                continue  # derrière l'horizon

            # Couleur Doppler (approche = bleu, éloignement = rouge)
            beta_r = math.cos(p["a"]) * p["speed"] * 20
            if beta_r > 0:
                col = lerp_color((255, 120, 30), (160, 200, 255), beta_r * 5)
            else:
                col = lerp_color((160, 200, 255), (255, 120, 30), -beta_r * 5)
            col = tuple(int(c * p["bright"]) for c in col)
            pygame.draw.circle(self.screen, col, (int(px), int(py)), p["size"])

    # ────────────────────────────────────────────
    #  TAB 1 — Dilatation temporelle
    # ────────────────────────────────────────────
    def _draw_time_dilation(self, rect):
        cx = self.W // 2
        tdf = self.td_factor

        # Titre & formule
        title = self.fnt_title.render("Dilatation Temporelle Gravitationnelle", True, ACCENT)
        self.screen.blit(title, (cx - title.get_width() // 2, 18))
        eq = self.fnt_med.render("f_obs = f_em × √(1 − rs / r)", True, ACCENT2)
        self.screen.blit(eq, (cx - eq.get_width() // 2, 52))

        # Deux horloges
        cy_clk = rect.height // 2 + 10
        self._draw_clock(self.W // 4, cy_clk, 110,
                         self.time * tdf,
                         "Proche du trou noir",
                         f"r = {self.dist_rs:.2f} rs",
                         f"τ = {tdf:.4f} × t",
                         (255, 110, 90))
        self._draw_clock(3 * self.W // 4, cy_clk, 110,
                         self.time,
                         "Loin du trou noir",
                         "r → ∞",
                         "τ = 1.0000 × t",
                         (90, 210, 130))

        # Ligne de connexion animée
        lx1, lx2 = self.W // 4 + 115, 3 * self.W // 4 - 115
        n_seg = 30
        for i in range(n_seg):
            x1 = int(lx1 + (lx2 - lx1) * i / n_seg)
            x2 = int(lx1 + (lx2 - lx1) * (i + 1) / n_seg)
            wave = int(6 * math.sin(i * 0.6 - self.time * 3))
            pygame.draw.line(self.screen, BORDER, (x1, cy_clk + wave), (x2, cy_clk + wave), 1)

        # Résumé
        if tdf > 0:
            ratio = 1.0 / tdf
            summary = (f"1 heure proche du trou noir  ↔  {ratio:.2f} heure(s) au loin"
                       if ratio < 100 else
                       f"1 heure proche du trou noir  ↔  {ratio:.0f} heures au loin  (comme dans Interstellar !)")
        else:
            summary = "À l'horizon des événements — le temps s'arrête !"

        s = self.fnt_big.render(summary, True, ACCENT)
        self.screen.blit(s, (cx - s.get_width() // 2, rect.height - 55))

        # Facteur numérique
        fac = self.fnt_med.render(f"Facteur dilatation  =  {tdf:.6f}      Distance  =  {self.dist_rs:.2f} rs", True, GRAY)
        self.screen.blit(fac, (cx - fac.get_width() // 2, rect.height - 28))

    def _draw_clock(self, cx, cy, r, time, label, sub, tau, color):
        # Fond
        pygame.draw.circle(self.screen, PANEL_BG, (cx, cy), r)
        pygame.draw.circle(self.screen, color, (cx, cy), r, 2)
        # Graduations
        for i in range(60):
            a    = i * math.pi / 30
            rout = r - 2
            rin  = r - (8 if i % 5 == 0 else 4)
            pygame.draw.line(self.screen,
                             (180, 180, 200) if i % 5 == 0 else (70, 70, 100),
                             (cx + int(rout * math.sin(a)), cy - int(rout * math.cos(a))),
                             (cx + int(rin  * math.sin(a)), cy - int(rin  * math.cos(a))), 1)
        # Aiguilles
        sec  = time % (2 * math.pi)
        minu = (time / 60) % (2 * math.pi)
        hr   = (time / 3600) % (2 * math.pi)
        self._hand(cx, cy, sec,  r - 10, 1, (200, 200, 255))
        self._hand(cx, cy, minu, r - 22, 2, WHITE)
        self._hand(cx, cy, hr,   r - 38, 3, GRAY)
        # Centre
        pygame.draw.circle(self.screen, color, (cx, cy), 4)
        # Textes
        for j, (txt, col) in enumerate([(label, color), (sub, GRAY), (tau, ACCENT)]):
            s = self.fnt_small.render(txt, True, col)
            self.screen.blit(s, (cx - s.get_width() // 2, cy + r + 8 + j * 16))

    def _hand(self, cx, cy, angle, length, width, color):
        ex = cx + int(length * math.sin(angle))
        ey = cy - int(length * math.cos(angle))
        pygame.draw.line(self.screen, color, (cx, cy), (ex, ey), width)

    # ────────────────────────────────────────────
    #  TAB 2 — Lentille gravitationnelle
    # ────────────────────────────────────────────
    def _draw_lensing(self, rect):
        cx   = self.W // 2
        cy   = rect.height // 2
        sc   = 38  # px / rs

        title = self.fnt_title.render("Lentille Gravitationnelle", True, ACCENT)
        self.screen.blit(title, (cx - title.get_width() // 2, 18))
        eq = self.fnt_med.render("α̂ = 4GM / (c² b)  =  2 rs / b", True, ACCENT2)
        self.screen.blit(eq, (cx - eq.get_width() // 2, 52))

        # Tracé des rayons lumineux
        for b_rs in np.arange(1.7, 9.0, 0.45):
            path = self._trace_ray(cx, cy, sc, b_rs)
            if len(path) > 1:
                intensity = max(60, int(255 - b_rs * 22))
                pygame.draw.lines(self.screen, (intensity, intensity, 100), False, path, 1)

        # Étoile source (à droite)
        star_x = cx + int(10 * sc)
        pygame.draw.circle(self.screen, ACCENT, (star_x, cy), 10)
        s = self.fnt_small.render("Étoile source", True, ACCENT)
        self.screen.blit(s, (star_x - s.get_width() // 2, cy + 14))

        # Trou noir
        pygame.draw.circle(self.screen, (0, 0, 0),        (cx, cy), int(sc))
        pygame.draw.circle(self.screen, ACCENT,            (cx, cy), int(sc * 1.5), 1)
        pygame.draw.circle(self.screen, (80, 40, 160),     (cx, cy), int(sc * 2.0), 1)

        s = self.fnt_small.render("r = 1.5 rs  (sphère photons)", True, ACCENT)
        self.screen.blit(s, (cx + int(sc * 1.5) + 4, cy - 9))
        s2 = self.fnt_small.render("r = 2 rs  (orbite circulaire)", True, (80, 40, 160))
        self.screen.blit(s2, (cx + int(sc * 2.0) + 4, cy + 9))

        # Déflexion pour b=3 rs
        b_ex  = 3.0
        alpha = lensing_deflection_angle(b_ex)
        note  = self.fnt_med.render(
            f"Exemple  b = {b_ex} rs  →  α = {math.degrees(alpha):.1f}°  ({alpha:.4f} rad)",
            True, (150, 230, 150))
        self.screen.blit(note, (cx - note.get_width() // 2, rect.height - 32))

    def _trace_ray(self, cx, cy, sc, b_rs):
        """Intégration numérique simplifiée du chemin d'un photon."""
        path = []
        x_phys =  -self.W / (2 * sc)
        y_phys = b_rs
        vx, vy = 1.0, 0.0

        steps = 600
        ds    = self.W / (sc * steps)

        for _ in range(steps):
            r2 = x_phys**2 + y_phys**2
            r  = math.sqrt(r2)
            if r < 0.95:
                break
            # Force gravitationnelle effective sur le photon
            ax = -2.0 * x_phys / (r2 * r)
            ay = -2.0 * y_phys / (r2 * r)

            vx += ax * ds * 0.5
            vy += ay * ds * 0.5
            norm = math.sqrt(vx**2 + vy**2) + 1e-12
            vx /= norm; vy /= norm

            x_phys += vx * ds
            y_phys += vy * ds

            sx = int(cx + x_phys * sc)
            sy = int(cy - y_phys * sc)
            if 0 <= sx < self.W and 0 <= sy < self.H:
                path.append((sx, sy))

        return path

    # ────────────────────────────────────────────
    #  TAB 3 — Effet Doppler relativiste
    # ────────────────────────────────────────────
    def _draw_doppler(self, rect):
        cx = self.W // 2
        cy = rect.height // 2

        title = self.fnt_title.render("Effet Doppler Relativiste", True, ACCENT)
        self.screen.blit(title, (cx - title.get_width() // 2, 18))
        eq = self.fnt_med.render("f_obs / f_em = √( (1+β) / (1−β) ) / γ", True, ACCENT2)
        self.screen.blit(eq, (cx - eq.get_width() // 2, 52))

        orb_rx = 230
        orb_ry = int(orb_rx * 0.3)

        # Orbite
        for a in np.linspace(0, 2 * math.pi, 120):
            ox = cx + int(orb_rx * math.cos(a))
            oy = cy + int(orb_ry * math.sin(a))
            pygame.draw.circle(self.screen, (40, 50, 90), (ox, oy), 1)

        # Position de la source orbitante
        ang = self.time * 0.9
        sx  = cx + int(orb_rx * math.cos(ang))
        sy  = cy + int(orb_ry * math.sin(ang))

        # Vitesse orbitale en fraction de c (simplifiée)
        v_orb = 0.3 * self.spin + 0.1
        # composante radiale (par rapport à l'observateur à gauche)
        beta_r = v_orb * math.sin(ang)    # >0 = s'éloigne, <0 = approche
        f_ratio = relativistic_doppler(-beta_r)

        # Couleur selon décalage
        if f_ratio >= 1.0:
            t_col = (f_ratio - 1.0) / 0.5
            col   = lerp_color((240, 240, 255), (80, 120, 255), min(1.0, t_col))
            label_shift = f"Bleuté (approche)  f_obs/f_em = {f_ratio:.3f}"
        else:
            t_col = (1.0 - f_ratio) / 0.5
            col   = lerp_color((240, 240, 255), (255, 80, 50), min(1.0, t_col))
            label_shift = f"Rougi (éloignement)  f_obs/f_em = {f_ratio:.3f}"

        # Source
        pygame.draw.circle(self.screen, col, (sx, sy), 10)
        pygame.draw.circle(self.screen, WHITE, (sx, sy), 10, 1)

        # Flèche de vitesse
        vdir_x = -math.sin(ang) * 35
        vdir_y =  math.cos(ang) * orb_ry / orb_rx * 35
        pygame.draw.line(self.screen, WHITE, (sx, sy),
                         (sx + int(vdir_x), sy + int(vdir_y)), 2)

        # Trou noir
        pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), 28)
        pygame.draw.circle(self.screen, ACCENT, (cx, cy), 42, 1)

        # Observateur à gauche
        obs_x = 60
        obs_y = cy
        pygame.draw.rect(self.screen, ACCENT2,
                         (obs_x - 12, obs_y - 18, 24, 36), 2)
        obs_lbl = self.fnt_small.render("Obs.", True, ACCENT2)
        self.screen.blit(obs_lbl, (obs_x - obs_lbl.get_width() // 2, obs_y + 22))

        # Ligne de visée
        pygame.draw.line(self.screen, (40, 50, 80), (obs_x + 12, obs_y), (sx, sy), 1)

        # Infos
        info_y = rect.height - 80
        for txt, col_t in [
            (label_shift,                             col),
            (f"β = v/c ≈ {abs(beta_r):.4f}",         GRAY),
            (f"Approche → bleuissement   Éloignement → rougissement", GRAY),
        ]:
            s = self.fnt_med.render(txt, True, col_t)
            self.screen.blit(s, (cx - s.get_width() // 2, info_y))
            info_y += 22

        # Barre de spectre
        self._draw_spectrum_bar(cx, rect.height - 22, 400, f_ratio)

    def _draw_spectrum_bar(self, cx, y, bw, f_ratio):
        bx = cx - bw // 2
        # Gradient rouge → blanc → bleu
        for i in range(bw):
            t = i / bw
            if t < 0.5:
                col = lerp_color((255, 60, 30), (240, 240, 255), t * 2)
            else:
                col = lerp_color((240, 240, 255), (60, 100, 255), (t - 0.5) * 2)
            pygame.draw.line(self.screen, col, (bx + i, y - 10), (bx + i, y + 8))

        # Curseur
        pos = int(max(0, min(bw - 1, (f_ratio - 0.5) / 1.5 * bw)))
        pygame.draw.line(self.screen, WHITE, (bx + pos, y - 14), (bx + pos, y + 12), 2)

        for txt, xx in [("Rouge (éloignement)", bx), ("Bleu (approche)", bx + bw)]:
            s = self.fnt_small.render(txt, True, GRAY)
            self.screen.blit(s, (xx - (0 if "Rouge" in txt else s.get_width()), y + 10))

    # ────────────────────────────────────────────
    #  Barre de contrôle en bas
    # ────────────────────────────────────────────
    def _draw_ui(self):
        ui_y = self.H - 220
        pygame.draw.rect(self.screen, PANEL_BG, (0, ui_y, self.W, 220))
        pygame.draw.line(self.screen, BORDER, (0, ui_y), (self.W, ui_y), 1)

        # Onglets
        tw = self.W // len(self.TABS)
        for i, name in enumerate(self.TABS):
            col = TAB_ACT if i == self.tab else TAB_IDLE
            pygame.draw.rect(self.screen, col, (i * tw, ui_y, tw, 28))
            pygame.draw.rect(self.screen, BORDER, (i * tw, ui_y, tw, 28), 1)
            s = self.fnt_small.render(f"[{i+1}] {name}", True, WHITE if i == self.tab else GRAY)
            self.screen.blit(s, (i * tw + tw // 2 - s.get_width() // 2, ui_y + 7))

        # Sliders
        for sd in self.slider_defs:
            val  = getattr(self, sd["key"])
            t    = (val - sd["min"]) / (sd["max"] - sd["min"])
            sx   = sd["cx"] - self.slider_w // 2
            sy   = self.slider_y

            lbl  = self.fnt_small.render(f'{sd["label"]}  {val:.3f}', True, GRAY)
            self.screen.blit(lbl, (sd["cx"] - lbl.get_width() // 2, sy - 18))

            pygame.draw.rect(self.screen, (30, 35, 60), (sx, sy + 4, self.slider_w, 8), border_radius=4)
            fw = int(t * self.slider_w)
            pygame.draw.rect(self.screen, ACCENT2, (sx, sy + 4, fw, 8), border_radius=4)
            pygame.draw.circle(self.screen, WHITE, (sx + fw, sy + 8), 7)

        # Bouton pause / play
        btn_col = (30, 80, 40) if not self.paused else (80, 30, 30)
        btn_txt = "  ▐▐  Pause [ESPACE]" if not self.paused else "  ▶  Reprendre [ESPACE]"
        pygame.draw.rect(self.screen, btn_col, (self.W - 195, ui_y + 35, 185, 30), border_radius=5)
        pygame.draw.rect(self.screen, BORDER, (self.W - 195, ui_y + 35, 185, 30), border_radius=5, width=1)
        s = self.fnt_small.render(btn_txt, True, WHITE)
        self.screen.blit(s, (self.W - 192, ui_y + 43))

        # Raccourcis
        hints = self.fnt_small.render("ESC: quitter   ESPACE: pause   1-4: onglets   Glisser: sliders", True, (60, 65, 100))
        self.screen.blit(hints, (10, self.H - 20))

        # FPS
        fps_s = self.fnt_small.render(f"FPS {int(self.clock.get_fps())}", True, (50, 55, 90))
        self.screen.blit(fps_s, (self.W - fps_s.get_width() - 6, self.H - 18))


# ─────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("InterSellclaudo — Simulation de Relativité Générale")
    print("Dépendances : pip install pygame numpy")
    print("Lancement de la simulation…\n")
    sim = InterSellclaudo()
    sim.run()