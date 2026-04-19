#!/usr/bin/env python3
"""
Dimensionamento de viga protendida — NBR 6118
Cordoalha CP 190 RB 12,70 (Belgo) — engraxada e plastificada
"""

import math
import os

os.system("clear")


# ---------------------------------------------------------------------------
# Entrada de dados
# ---------------------------------------------------------------------------

def _float(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if raw == "" and default is not None:
            return float(default)
        try:
            return float(raw)
        except ValueError:
            print("  Valor inválido. Digite um número.")


def _int(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if raw == "" and default is not None:
            return int(default)
        try:
            return int(raw)
        except ValueError:
            print("  Valor inválido. Digite um inteiro.")


def _choice(prompt, options, default=None):
    opts_str = "/".join(options)
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt} ({opts_str}){suffix}: ").strip().lower()
        if raw == "" and default is not None:
            return default
        if raw in options:
            return raw
        print(f"  Escolha entre: {opts_str}")


print("=" * 60)
print("  DIMENSIONAMENTO DE VIGA PROTENDIDA — NBR 6118")
print("=" * 60)

print("\n--- Tipo de protensão ---")
z_str = _choice("Tipo (pos=pós-tração, pre=pré-tração)", ["pos", "pre"], default="pos")
z = 0 if z_str == "pos" else 1

print("\n--- Concreto ---")
fck  = _float("fck (MPa)", default=35)
fckj = _float("fckj (MPa)", default=fck)
gamma_c = _float("γc", default=1.4)

print("\n--- Cordoalha CP 190 RB ---")
phi_original = _float("Diâmetro nominal da cordoalha (mm)", default=12.7)
fptk = _float("fptk (MPa)", default=1900)
fpyk = _float("fpyk (MPa)", default=1710)

print("\n--- Coeficientes ---")
gamma_f  = _float("γf", default=1.4)
gamma_s  = _float("γs", default=1.15)

print("\n--- Perdas ---")
perdas_iniciais = _float("Perdas iniciais (fração, ex: 0.05)", default=0.05)
perdas_finais   = _float("Perdas finais (fração, ex: 0.25)",   default=0.25)

print("\n--- Cargas (KN/m) e vão ---")
vao = _float("Vão (m)", default=8)
g1  = _float("g1 — peso próprio (KN/m)", default=3.5)
g2  = _float("g2 — laje alveolar (KN/m)", default=0)
g3  = _float("g3 — capa (KN/m)", default=0)
g4  = _float("g4 — alvenaria (KN/m)", default=1.3)
g5  = _float("g5 — revestimento (KN/m)", default=0)
q   = _float("q  — acidental (KN/m)", default=1.5)

print("\n--- Seção transversal (m) ---")
bf = _float("bf — largura da mesa (m)", default=0.40)
bw = _float("bw — largura da alma (m)", default=0.40)
h  = _float("h  — altura total (m)", default=0.30)
hw = _float("hw — altura da alma abaixo da laje (m)", default=0.0)

print("\n--- Cobrimento ---")
d_linha = _float("d' — cobrimento até centroide da armadura (m)", default=0.05)


# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("  RESULTADOS")
print("=" * 60)

# Geometria da cordoalha
phi_calc = phi_original - 1.5           # desconta capa plástica
area_phi = math.pi * ((phi_calc / 10) ** 2) / 4   # cm²
print(f"\nÁrea da cordoalha: {area_phi:.4f} cm²")

# Momentos
Mkmax_g1 = g1 * vao**2 / 8
Mkmax_g2 = g2 * vao**2 / 8
Mkmax_g3 = g3 * vao**2 / 8
Mkmax_g4 = g4 * vao**2 / 8
Mkmax_g5 = g5 * vao**2 / 8
Mkmax_q  = q  * vao**2 / 8

Mk = Mkmax_g1 + Mkmax_g2 + Mkmax_g3 + Mkmax_g4 + Mkmax_g5 + Mkmax_q
Md = gamma_f * Mk
print(f"Mk = {Mk:.2f} KNm")
print(f"Md = {Md:.2f} KNm")

# Seção em T
hf       = h - hw
hf_linha = 0.0          # trapezoidal não utilizado aqui
yi       = h / 2
ys       = h - yi
Ac       = bw * hw + hf * bf
Ic       = (bw * h**3) / 12

# Módulos resistentes
Wi = Ic / yi
Ws = Ic / ys

# Wsimples só é válido quando hw > 0
if hw > 0:
    Wsimples = bw * hw**2 / 6
else:
    Wsimples = None

print(f"\nyi = {yi:.4f} m | ys = {ys:.4f} m")
print(f"Ac = {Ac:.4f} m² | Ic = {Ic:.6f} m⁴")
print(f"Wi = {Wi:.6f} m³ | Ws = {Ws:.6f} m³")
if Wsimples is not None:
    print(f"Wsimples = {Wsimples:.6f} m³")
else:
    print("Wsimples: N/A (hw = 0 — seção retangular pura)")

# Altura útil
d = h - d_linha
print(f"\nd = {d:.4f} m")

# KMD e tabela KX/KZ
KMD = Md / (bf * d**2 * (fck * 1000 / gamma_c))
print(f"KMD = {KMD:.6f}")

# Tabela KX / KZ / Es (Montoya)
tabela = [
    (0.01,  0.0148, 0.9941, 10.000),
    (0.02,  0.0298, 0.9881, 10.000),
    (0.03,  0.0449, 0.9820, 10.000),
    (0.04,  0.0603, 0.9759, 10.000),   # corrigido: era 0.00603
    (0.05,  0.0758, 0.9697, 10.000),
    (0.055, 0.0836, 0.9665, 10.000),
    (0.06,  0.0916, 0.9634, 10.000),
    (0.065, 0.0995, 0.9602, 10.000),
    (0.07,  0.1076, 0.9570, 10.000),
    (0.075, 0.1156, 0.9537, 10.000),
    (0.08,  0.1238, 0.9505, 10.000),
    (0.085, 0.1320, 0.9472, 10.000),
    (0.09,  0.1403, 0.9439, 10.000),
    (0.095, 0.1485, 0.9406, 10.000),   # corrigido: KZ era 0.9606
    (0.100, 0.1569, 0.9372, 10.000),
    (0.105, 0.1654, 0.9339, 10.000),
    (0.110, 0.1739, 0.9305, 10.000),
    (0.115, 0.1824, 0.9270, 10.000),
    (0.120, 0.1911, 0.9236, 10.000),
    (0.125, 0.1998, 0.9201, 10.000),
    (0.130, 0.2086, 0.9166, 10.000),
    (0.135, 0.2175, 0.9130, 10.000),
    (0.140, 0.2264, 0.9094, 10.000),
    (0.145, 0.2354, 0.9058, 10.000),
    (0.150, 0.2445, 0.9022, 10.000),
    (0.155, 0.2536, 0.8985, 10.000),
    (0.160, 0.2630, 0.8948,  9.8104),
    (0.165, 0.2723, 0.8911,  9.3531),
    (0.170, 0.2818, 0.8873,  8.9222),
    (0.175, 0.2912, 0.8835,  8.5154),  # corrigido: KX era repetido (0.2723)
]

KX = KZ = Es = None
for kmd_lim, kx, kz, es in tabela:
    if KMD <= kmd_lim:
        KX, KZ, Es = kx, kz, es
        break

if KX is None:
    print("AVISO: KMD fora da tabela (> 0.175). Seção insuficiente.")
    exit(1)

print(f"KX = {KX} | KZ = {KZ} | Es = {Es} ‰")

# Verificação da LN na mesa
x = KX * d
print(f"\nx (LN) = {x:.4f} m | hf = {hf:.4f} m")
if x <= hf:
    print("✓ LN está na mesa — hipótese válida.")
else:
    print("⚠ LN não está na mesa. Recalcule para seção T completa.")

# Tensão inicial de protensão
deltap_i = min(0.80 * fptk, 0.88 * fpyk)
print(f"\nδp,i = {deltap_i:.1f} MPa")

deltap_t_inf = deltap_i * (1 - perdas_finais)
print(f"δp,∞ (estimado) = {deltap_t_inf:.1f} MPa")

# Diagrama de Vasconcelos — deformação plástica Ep
vasconcelos = [
    (1025, 5.25),
    (1314, 6.794),
    (1411, 7.438),
    (1459, 8.167),
    (1482, 9.000),
    (1486, 9.962),
    # faixa >1486 e <=1486 removida (impossível)
    (1496, 12.50),
    (1507, 15.00),
    (1517, 17.50),
    (1527, 20.00),
    (1538, 22.50),
    (1548, 25.00),
    (1559, 27.50),
    (1569, 30.00),
    (1579, 32.50),
    (1590, 35.00),
    (1600, 37.50),
    (1611, 40.00),
]

Ep_vasc = next((ep for lim, ep in vasconcelos if deltap_t_inf <= lim), None)
if Ep_vasc is None:
    print("AVISO: δp,∞ fora da tabela de Vasconcelos.")
    exit(1)

Et = Ep_vasc + Es
print(f"Ep (Vasconcelos) = {Ep_vasc} ‰ | Es = {Es} ‰ | Et = {Et} ‰")

# Tensão de serviço final (tabela inversa)
deltap_final = next((lim for lim, ep in vasconcelos if Et <= ep), None)
if deltap_final is None:
    # Et maior que todos os Ep — usar o maior limite
    deltap_final = vasconcelos[-1][0]

print(f"δp,∞ final = {deltap_final} MPa")

# Área de aço necessária
Ap_final = (gamma_f * Mk) / (KZ * d * deltap_final * 1000)
print(f"\nAp necessária = {Ap_final * 10000:.4f} cm²")

# Número de cordoalhas
Ncord = math.ceil(Ap_final * 10000 / area_phi)
print(f"Número de cordoalhas = {Ncord} unidades")

# Verificação no tempo t = 0
deltap_t_zero = deltap_final * (1 - perdas_iniciais)
print(f"\nδp,t=0 = {deltap_t_zero:.2f} MPa")

Np_t_zero = z * Ncord * area_phi * 0.0001 * deltap_t_zero * 1000
print(f"Np,t=0 = {Np_t_zero:.2f} kN  ({'pós-tração: verificação em fase de uso' if z == 0 else 'pré-tração'})")

# Limites de tensão — ELS
deltac_lim =  0.7 * fckj
deltat_lim = -1.2 * 0.3 * fckj ** (2 / 3)
print(f"\nLimites: {deltat_lim:.3f} MPa ≤ σ ≤ {deltac_lim:.1f} MPa")

# Verificação de tensões no meio do vão (apenas quando hw > 0)
if hw > 0 and Wsimples is not None:
    e = hw / 2 - d_linha      # excentricidade
    delta_1 = Np_t_zero / Ac
    delta_2 = Np_t_zero * e / Wsimples
    delta_3 = Mkmax_g1 / Wsimples

    sigma_sup = delta_1 - delta_2 + delta_3
    sigma_inf = delta_1 + delta_2 - delta_3

    print(f"\n--- Verificação de tensões no meio do vão (t=0) ---")
    print(f"Np/Ac         = {delta_1:.2f} KN/m²")
    print(f"Np·e/Wsimples = {delta_2:.2f} KN/m²")
    print(f"Mg1/Wsimples  = {delta_3:.2f} KN/m²")
    print(f"σ_sup = {sigma_sup:.2f} KN/m²")
    print(f"σ_inf = {sigma_inf:.2f} KN/m²")

    ok_sup = deltat_lim * 1000 <= sigma_sup <= deltac_lim * 1000
    ok_inf = deltat_lim * 1000 <= sigma_inf <= deltac_lim * 1000
    print(f"Borda superior: {'✓ OK' if ok_sup else '⚠ FORA DO LIMITE'}")
    print(f"Borda inferior: {'✓ OK' if ok_inf else '⚠ FORA DO LIMITE'}")
else:
    print("\nVerificação de tensões no t=0: indisponível para seção retangular pura (hw=0).")
    print("Use hw > 0 para ativar esta verificação.")

print("\n" + "=" * 60)
