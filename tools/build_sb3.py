#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador programático del proyecto Scratch 3: NEXUS BLOCKS (.sb3)
Construye un archivo .sb3 100% compatible con el editor oficial de Scratch 3,
incluyendo activos vectoriales SVG originales, efectos de sonido WAV sintetizados
y toda la arquitectura de bloques para teclado físico, incluido iPad.
"""

import hashlib
import io
import json
import math
import os
import struct
import wave
import zipfile
from typing import Any, Dict, List, Optional, Tuple


# ==============================================================================
# 1. GENERADOR DE SONIDOS WAV ORIGINALES (SÍNTESIS PCM 16-BIT 22050 HZ)
# ==============================================================================

def synthesize_wav(notes: List[Tuple[float, float, str]], sample_rate: int = 22050) -> Tuple[bytes, int]:
    """
    Genera un archivo WAV mono de 16 bits con una secuencia de notas/efectos.
    Cada tupla en `notes` es (frecuencia_hz, duracion_seg, forma_onda).
    """
    buf = io.BytesIO()
    samples: List[int] = []
    for freq, duration, waveform in notes:
        n_samples = int(sample_rate * duration)
        for i in range(n_samples):
            t = i / sample_rate
            env = 1.0
            attack = min(0.01, duration * 0.15)
            release = min(0.04, duration * 0.35)
            if t < attack:
                env = t / max(attack, 1e-5)
            elif t > duration - release:
                env = max(0.0, (duration - t) / max(release, 1e-5))

            if freq <= 0:
                val = 0.0
            elif waveform == "sine":
                val = math.sin(2.0 * math.pi * freq * t)
            elif waveform == "square":
                val = 0.6 if math.sin(2.0 * math.pi * freq * t) >= 0 else -0.6
            elif waveform == "triangle":
                phase = (freq * t) % 1.0
                val = 4.0 * abs(phase - 0.5) - 1.0
            elif waveform == "sweep_down":
                inst_freq = freq * (1.0 - 0.55 * (t / max(duration, 1e-4)))
                val = math.sin(2.0 * math.pi * inst_freq * t)
            elif waveform == "sweep_up":
                inst_freq = freq * (1.0 + 0.65 * (t / max(duration, 1e-4)))
                val = math.sin(2.0 * math.pi * inst_freq * t)
            else:
                val = math.sin(2.0 * math.pi * freq * t)

            pcm = int(max(-32767, min(32767, val * env * 14000)))
            samples.append(pcm)

    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack("<" + "h" * len(samples), *samples))

    return buf.getvalue(), len(samples)


def build_sound_assets() -> Dict[str, Dict[str, Any]]:
    """Crea el catálogo de efectos de sonido arcade originales."""
    specs = {
        "Sonido_Mover": [(320.0, 0.035, "triangle")],
        "Sonido_Rotar": [(520.0, 0.045, "sweep_up"), (680.0, 0.045, "triangle")],
        "Sonido_Caida": [(260.0, 0.075, "sweep_down"), (140.0, 0.055, "square")],
        "Sonido_Linea": [
            (523.25, 0.06, "triangle"),
            (659.25, 0.06, "triangle"),
            (783.99, 0.07, "triangle"),
            (1046.50, 0.14, "sine"),
        ],
        "Sonido_Hold": [(440.0, 0.045, "sine"), (587.33, 0.055, "sine")],
        "Sonido_Caos": [(392.0, 0.07, "square"), (311.13, 0.07, "square"), (587.33, 0.11, "square")],
        "Sonido_NMWarning": [(196.0,0.07,"square"),(0,0.025,"sine"),(293.66,0.10,"triangle")],
        "Sonido_Armor": [(640.0,0.035,"square"),(320.0,0.085,"sweep_down")],
        "Sonido_GlitchFire": [(720.0,0.07,"sweep_down")],
        "Sonido_GlitchHit": [(180.0,0.10,"square"),(110.0,0.09,"sweep_down")],
        "Sonido_GlitchWin": [(440.0,0.07,"triangle"),(659.25,0.07,"triangle"),(880.0,0.13,"sine")],
        "Sonido_GameOver": [
            (440.0, 0.12, "triangle"),
            (392.0, 0.12, "triangle"),
            (349.23, 0.14, "triangle"),
            (261.63, 0.28, "sweep_down"),
        ],
    }
    assets: Dict[str, Dict[str, Any]] = {}
    for name, notes in specs.items():
        raw_bytes, sample_count = synthesize_wav(notes)
        md5 = hashlib.md5(raw_bytes).hexdigest()
        assets[name] = {
            "name": name,
            "bytes": raw_bytes,
            "assetId": md5,
            "md5ext": f"{md5}.wav",
            "dataFormat": "wav",
            "format": "",
            "rate": 22050,
            "sampleCount": sample_count,
        }
    return assets


# ==============================================================================
# 2. GENERADOR DE GRÁFICOS VECTORIALES SVG ORIGINALES (ESTILO ARCADE MODERNO)
# ==============================================================================

def register_svg_asset(name: str, svg_text: str, rot_x: float, rot_y: float) -> Dict[str, Any]:
    raw_bytes = svg_text.strip().encode("utf-8")
    md5 = hashlib.md5(raw_bytes).hexdigest()
    return {
        "name": name,
        "bytes": raw_bytes,
        "assetId": md5,
        "md5ext": f"{md5}.svg",
        "dataFormat": "svg",
        "bitmapResolution": 1,
        "rotationCenterX": rot_x,
        "rotationCenterY": rot_y,
    }


def make_stage_backdrop_svg(border_color="#31435A", subtitle="KEYBOARD ARCADE"):
    grid = ''.join(f'<path d="M{165+c*15} 30V330" stroke="#152033"/>' for c in range(1,10))
    grid += ''.join(f'<path d="M165 {30+r*15}H315" stroke="#152033"/>' for r in range(1,20))
    labels = [(80,60,"HOLD"),(80,160,"SCORE"),(400,60,"NEXT"),(400,160,"LEVEL"),(400,218,"LINES"),(400,276,"MODE")]
    text = ''.join(f'<text x="{x}" y="{y}" text-anchor="middle" fill="#8B9CB5" font-family="sans-serif" font-size="10" letter-spacing="2">{t}</text>' for x,y,t in labels)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#090F1B"/><rect x="163" y="28" width="154" height="304" rx="2" fill="#070B13" stroke="{border_color}"/>{grid}{text}<text x="240" y="18" text-anchor="middle" fill="#DDE7F5" font-family="sans-serif" font-size="11" letter-spacing="3">NEXUS BLOCKS</text><text x="240" y="350" text-anchor="middle" fill="#70829D" font-family="sans-serif" font-size="9">ARROWS MOVE / ROTATE · SPACE DROP · C HOLD · P PAUSE · R RESTART</text></svg>'''


def make_block_svg(fill_hex: str, highlight_hex: str, border_hex: str, size: int = 15) -> str:
    """Crea un disfraz SVG de bloque de tetrominó con bisel arcade."""
    inner = size - 4
    return f"""<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <rect x="0.5" y="0.5" width="{size - 1}" height="{size - 1}" rx="2.2" fill="{fill_hex}" stroke="{border_hex}" stroke-width="1"/>
  <rect x="2.2" y="2.2" width="{inner}" height="{inner * 0.45:.1f}" rx="1" fill="{highlight_hex}" fill-opacity="0.55"/>
  <rect x="2.8" y="2.8" width="{size - 5.6:.1f}" height="{size - 5.6:.1f}" rx="1" fill="none" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="0.8"/>
</svg>"""


def make_ghost_block_svg(size: int = 15) -> str:
    """Crea el disfraz de la pieza fantasma (contorno neón translúcido)."""
    return f"""<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <rect x="1.2" y="1.2" width="{size - 2.4:.1f}" height="{size - 2.4:.1f}" rx="2.2" fill="#00F0FF" fill-opacity="0.14" stroke="#00F0FF" stroke-width="1.4" stroke-dasharray="3,1.5"/>
</svg>"""



def make_modal_svg(title, line1, line2, line3, accent_hex):
    """Panel de estado informativo sin controles táctiles."""
    if title == "NEXUS BLOCKS":
        lines = [(55,"1 — NORMAL"),(74,"2 — HARD"),(93,"3 — CHAOS"),(112,"4 — NIGHTMARE / CHANGE TYPE"),(145,"PRESS ENTER TO START")]
    else:
        lines = [(68,line1),(94,line2),(135,line3)]
    texts = ''.join(f'<text x="118" y="{y}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#CFDBEA">{t}</text>' for y,t in lines)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="236" height="168"><rect x="1" y="1" width="234" height="166" rx="6" fill="#0B1320" stroke="#34455E"/><text x="118" y="31" text-anchor="middle" font-family="sans-serif" font-size="16" letter-spacing="1" fill="{accent_hex}">{title}</text>{texts}</svg>'''


def make_line_fx_svg(label: str, color_hex: str) -> str:
    """Crea un destello animado horizontal para celebrar líneas completadas."""
    w, h = 148, 34
    return f"""<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="8" fill="#071226" fill-opacity="0.92" stroke="{color_hex}" stroke-width="2.5"/>
  <text x="{w / 2.0}" y="22" font-family="sans-serif" font-size="13" font-weight="bold" fill="{color_hex}" text-anchor="middle">{label}</text>
</svg>"""


def make_nightmare_modal(title: str, lines: List[str]) -> str:
    text = ''.join(f'<text x="14" y="{70 + i*25}" fill="#F5F2E9" font-family="monospace" font-size="12">{line}</text>' for i, line in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="236" height="168"><rect x="1" y="1" width="234" height="166" fill="#101010" stroke="#FFBC32" stroke-width="2"/><path d="M12 41H224 M12 142H224" stroke="#FFBC32"/><text x="14" y="29" fill="#FFBC32" font-family="monospace" font-size="16" font-weight="bold">{title}</text>{text}</svg>'''


# ==============================================================================
# 3. CONSTRUCTOR DE BLOQUES SCRATCH 3 (AST -> PROJECT.JSON)
# ==============================================================================

class ScratchBlockBuilder:
    """Clase auxiliar para construir grafos de bloques de Scratch 3 sin errores de enlaces."""

    def __init__(self, prefix: str, var_map: Dict[str, str], list_map: Dict[str, str], bcast_map: Dict[str, str]):
        self.prefix = prefix
        self.var_map = var_map
        self.list_map = list_map
        self.bcast_map = bcast_map
        self.blocks: Dict[str, Dict[str, Any]] = {}
        self.comments: Dict[str, Dict[str, Any]] = {}
        self._counter = 0

    def new_id(self, tag: str = "b") -> str:
        self._counter += 1
        return f"{self.prefix}_{tag}_{self._counter}"

    def add_comment(self, block_id: Optional[str], text: str, x: int = 50, y: int = 50, w: int = 300, h: int = 120) -> str:
        cid = self.new_id("cmt")
        self.comments[cid] = {
            "blockId": block_id,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "minimized": False,
            "text": text,
        }
        return cid

    def add_block(
        self,
        opcode: str,
        inputs: Optional[Dict[str, Any]] = None,
        fields: Optional[Dict[str, Any]] = None,
        top_level: bool = False,
        shadow: bool = False,
        x: int = 0,
        y: int = 0,
        mutation: Optional[Dict[str, Any]] = None,
    ) -> str:
        bid = self.new_id("blk")
        node: Dict[str, Any] = {
            "opcode": opcode,
            "next": None,
            "parent": None,
            "inputs": inputs or {},
            "fields": fields or {},
            "shadow": shadow,
            "topLevel": top_level,
        }
        if top_level:
            node["x"] = x
            node["y"] = y
        if mutation is not None:
            node["mutation"] = mutation
        self.blocks[bid] = node
        return bid

    # --- Helpers para Inputs (Literales, Variables, Bloques Reporteros) ---

    def num_in(self, val: Any) -> List[Any]:
        return [1, [4, str(val)]]

    def int_in(self, val: int) -> List[Any]:
        return [1, [7, str(val)]]

    def txt_in(self, val: Any) -> List[Any]:
        return [1, [10, str(val)]]

    def var_in(self, parent_id: str, var_name: str, default_str: str = "0") -> List[Any]:
        vid = self.var_map[var_name]
        vblock = self.add_block(
            "data_variable",
            fields={"VARIABLE": [var_name, vid]},
        )
        self.blocks[vblock]["parent"] = parent_id
        return [3, vblock, [10, default_str]]

    def rep_in(self, parent_id: str, reporter_id: str, default_str: str = "0") -> List[Any]:
        self.blocks[reporter_id]["parent"] = parent_id
        return [3, reporter_id, [10, default_str]]

    def bool_in(self, parent_id: str, cond_id: str) -> List[Any]:
        self.blocks[cond_id]["parent"] = parent_id
        return [2, cond_id]

    def substack_in(self, parent_id: str, first_stmt_id: Optional[str]) -> Optional[List[Any]]:
        if not first_stmt_id:
            return None
        self.blocks[first_stmt_id]["parent"] = parent_id
        return [2, first_stmt_id]

    def bcast_in(self, bcast_name: str) -> List[Any]:
        bid = self.bcast_map[bcast_name]
        return [1, [11, bcast_name, bid]]

    # --- Constructores de Expresiones (Reporters y Booleanos) ---

    def expr_var(self, var_name: str) -> str:
        vid = self.var_map[var_name]
        return self.add_block("data_variable", fields={"VARIABLE": [var_name, vid]})

    def expr_arg(self, arg_name: str) -> str:
        return self.add_block("argument_reporter_string_number", fields={"VALUE": [arg_name, None]})

    def expr_timer(self) -> str:
        return self.add_block("sensing_timer")

    def expr_key_pressed(self, key_name: str) -> str:
        b = self.add_block("sensing_keypressed")
        menu = self.add_block(
            "sensing_keyoptions",
            fields={"KEY_OPTION": [key_name, None]},
            shadow=True,
        )
        self.blocks[menu]["parent"] = b
        self.blocks[b]["inputs"]["KEY_OPTION"] = [1, menu]
        return b

    def _attach_val(self, parent_id: str, input_key: str, val: Any) -> None:
        if isinstance(val, str):
            if val.startswith("$v:"):
                vname = val[3:]
                self.blocks[parent_id]["inputs"][input_key] = self.var_in(parent_id, vname)
                return
            if val.startswith("$a:"):
                aname = val[3:]
                ablock = self.expr_arg(aname)
                self.blocks[parent_id]["inputs"][input_key] = self.rep_in(parent_id, ablock)
                return
            if val.startswith("$b:"):
                rblock = val[3:]
                self.blocks[parent_id]["inputs"][input_key] = self.rep_in(parent_id, rblock)
                return
            self.blocks[parent_id]["inputs"][input_key] = self.txt_in(val)
        elif isinstance(val, (int, float)):
            self.blocks[parent_id]["inputs"][input_key] = self.num_in(val)
        else:
            self.blocks[parent_id]["inputs"][input_key] = self.txt_in(str(val))

    def op_add(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_add")
        self._attach_val(blk, "NUM1", a)
        self._attach_val(blk, "NUM2", b)
        return f"$b:{blk}"

    def op_sub(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_subtract")
        self._attach_val(blk, "NUM1", a)
        self._attach_val(blk, "NUM2", b)
        return f"$b:{blk}"

    def op_mul(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_multiply")
        self._attach_val(blk, "NUM1", a)
        self._attach_val(blk, "NUM2", b)
        return f"$b:{blk}"

    def op_div(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_divide")
        self._attach_val(blk, "NUM1", a)
        self._attach_val(blk, "NUM2", b)
        return f"$b:{blk}"

    def op_mod(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_mod")
        self._attach_val(blk, "NUM1", a)
        self._attach_val(blk, "NUM2", b)
        return f"$b:{blk}"

    def op_random(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_random")
        self._attach_val(blk, "FROM", a)
        self._attach_val(blk, "TO", b)
        return f"$b:{blk}"

    def op_math(self, func_name: str, num: Any) -> str:
        blk = self.add_block("operator_mathop", fields={"OPERATOR": [func_name, None]})
        self._attach_val(blk, "NUM", num)
        return f"$b:{blk}"

    def op_join(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_join")
        self._attach_val(blk, "STRING1", a)
        self._attach_val(blk, "STRING2", b)
        return f"$b:{blk}"

    def op_eq(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_equals")
        self._attach_val(blk, "OPERAND1", a)
        self._attach_val(blk, "OPERAND2", b)
        return blk

    def op_lt(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_lt")
        self._attach_val(blk, "OPERAND1", a)
        self._attach_val(blk, "OPERAND2", b)
        return blk

    def op_gt(self, a: Any, b: Any) -> str:
        blk = self.add_block("operator_gt")
        self._attach_val(blk, "OPERAND1", a)
        self._attach_val(blk, "OPERAND2", b)
        return blk

    def op_and(self, cond1_id: str, cond2_id: str) -> str:
        blk = self.add_block("operator_and")
        self.blocks[blk]["inputs"]["OPERAND1"] = self.bool_in(blk, cond1_id)
        self.blocks[blk]["inputs"]["OPERAND2"] = self.bool_in(blk, cond2_id)
        return blk

    def op_or(self, cond1_id: str, cond2_id: str) -> str:
        blk = self.add_block("operator_or")
        self.blocks[blk]["inputs"]["OPERAND1"] = self.bool_in(blk, cond1_id)
        self.blocks[blk]["inputs"]["OPERAND2"] = self.bool_in(blk, cond2_id)
        return blk

    def op_not(self, cond_id: str) -> str:
        blk = self.add_block("operator_not")
        self.blocks[blk]["inputs"]["OPERAND"] = self.bool_in(blk, cond_id)
        return blk

    def expr_list_item(self, list_name: str, index_val: Any) -> str:
        lid = self.list_map[list_name]
        blk = self.add_block("data_itemoflist", fields={"LIST": [list_name, lid]})
        self._attach_val(blk, "INDEX", index_val)
        return f"$b:{blk}"

    def expr_list_length(self, list_name: str) -> str:
        lid = self.list_map[list_name]
        blk = self.add_block("data_lengthoflist", fields={"LIST": [list_name, lid]})
        return f"$b:{blk}"

    # --- Constructores de Sentencias (Statements) ---

    def chain(self, stmt_ids: List[str]) -> Optional[str]:
        valid = [s for s in stmt_ids if s]
        if not valid:
            return None
        for i in range(len(valid) - 1):
            curr_id = valid[i]
            next_id = valid[i + 1]
            self.blocks[curr_id]["next"] = next_id
            self.blocks[next_id]["parent"] = curr_id
        return valid[0]

    def stmt_set_var(self, var_name: str, val: Any) -> str:
        vid = self.var_map[var_name]
        blk = self.add_block("data_setvariableto", fields={"VARIABLE": [var_name, vid]})
        self._attach_val(blk, "VALUE", val)
        return blk

    def stmt_change_var(self, var_name: str, val: Any) -> str:
        vid = self.var_map[var_name]
        blk = self.add_block("data_changevariableby", fields={"VARIABLE": [var_name, vid]})
        self._attach_val(blk, "VALUE", val)
        return blk

    def stmt_delete_all_list(self, list_name: str) -> str:
        lid = self.list_map[list_name]
        return self.add_block("data_deletealloflist", fields={"LIST": [list_name, lid]})

    def stmt_add_to_list(self, list_name: str, item_val: Any) -> str:
        lid = self.list_map[list_name]
        blk = self.add_block("data_addtolist", fields={"LIST": [list_name, lid]})
        self._attach_val(blk, "ITEM", item_val)
        return blk

    def stmt_delete_of_list(self, list_name: str, index_val: Any) -> str:
        lid = self.list_map[list_name]
        blk = self.add_block("data_deleteoflist", fields={"LIST": [list_name, lid]})
        self._attach_val(blk, "INDEX", index_val)
        return blk

    def stmt_replace_item_list(self, list_name: str, index_val: Any, item_val: Any) -> str:
        lid = self.list_map[list_name]
        blk = self.add_block("data_replaceitemoflist", fields={"LIST": [list_name, lid]})
        self._attach_val(blk, "INDEX", index_val)
        self._attach_val(blk, "ITEM", item_val)
        return blk

    def stmt_if(self, cond_id: str, substack_stmts: List[str]) -> str:
        blk = self.add_block("control_if")
        self.blocks[blk]["inputs"]["CONDITION"] = self.bool_in(blk, cond_id)
        first = self.chain(substack_stmts)
        if first:
            self.blocks[blk]["inputs"]["SUBSTACK"] = self.substack_in(blk, first)
        return blk

    def stmt_if_else(self, cond_id: str, then_stmts: List[str], else_stmts: List[str]) -> str:
        blk = self.add_block("control_if_else")
        self.blocks[blk]["inputs"]["CONDITION"] = self.bool_in(blk, cond_id)
        first_then = self.chain(then_stmts)
        if first_then:
            self.blocks[blk]["inputs"]["SUBSTACK"] = self.substack_in(blk, first_then)
        first_else = self.chain(else_stmts)
        if first_else:
            self.blocks[blk]["inputs"]["SUBSTACK2"] = self.substack_in(blk, first_else)
        return blk

    def stmt_repeat(self, times_val: Any, substack_stmts: List[str]) -> str:
        blk = self.add_block("control_repeat")
        self._attach_val(blk, "TIMES", times_val)
        first = self.chain(substack_stmts)
        if first:
            self.blocks[blk]["inputs"]["SUBSTACK"] = self.substack_in(blk, first)
        return blk

    def stmt_repeat_until(self, cond_id: str, substack_stmts: List[str]) -> str:
        blk = self.add_block("control_repeat_until")
        self.blocks[blk]["inputs"]["CONDITION"] = self.bool_in(blk, cond_id)
        first = self.chain(substack_stmts)
        if first:
            self.blocks[blk]["inputs"]["SUBSTACK"] = self.substack_in(blk, first)
        return blk

    def stmt_forever(self, substack_stmts: List[str]) -> str:
        blk = self.add_block("control_forever")
        first = self.chain(substack_stmts)
        if first:
            self.blocks[blk]["inputs"]["SUBSTACK"] = self.substack_in(blk, first)
        return blk

    def stmt_wait(self, duration_val: Any) -> str:
        blk = self.add_block("control_wait")
        self._attach_val(blk, "DURATION", duration_val)
        return blk

    def stmt_wait_until(self, cond_id: str) -> str:
        blk = self.add_block("control_wait_until")
        self.blocks[blk]["inputs"]["CONDITION"] = self.bool_in(blk, cond_id)
        return blk

    def stmt_broadcast(self, bcast_name: str, wait: bool = False) -> str:
        op = "event_broadcastandwait" if wait else "event_broadcast"
        return self.add_block(op, inputs={"BROADCAST_INPUT": self.bcast_in(bcast_name)})

    def stmt_play_sound(self, sound_name: str) -> str:
        blk = self.add_block("sound_play")
        menu = self.add_block("sound_sounds_menu", fields={"SOUND_MENU": [sound_name, None]}, shadow=True)
        self.blocks[menu]["parent"] = blk
        self.blocks[blk]["inputs"]["SOUND_MENU"] = [1, menu]
        return blk

    def stmt_switch_costume(self, costume_val: Any) -> str:
        blk = self.add_block("looks_switchcostumeto")
        if isinstance(costume_val, str) and not (
            costume_val.startswith("$v:") or costume_val.startswith("$a:") or costume_val.startswith("$b:")
        ):
            menu = self.add_block("looks_costume", fields={"COSTUME": [costume_val, None]}, shadow=True)
            self.blocks[menu]["parent"] = blk
            self.blocks[blk]["inputs"]["COSTUME"] = [1, menu]
        else:
            menu = self.add_block("looks_costume", fields={"COSTUME": ["Bloque_1_I", None]}, shadow=True)
            self.blocks[menu]["parent"] = blk
            if isinstance(costume_val, str) and costume_val.startswith("$v:"):
                vid = self.var_map[costume_val[3:]]
                vblk = self.add_block("data_variable", fields={"VARIABLE": [costume_val[3:], vid]})
                self.blocks[vblk]["parent"] = blk
                self.blocks[blk]["inputs"]["COSTUME"] = [3, vblk, menu]
            elif isinstance(costume_val, str) and costume_val.startswith("$b:"):
                rblk = costume_val[3:]
                self.blocks[rblk]["parent"] = blk
                self.blocks[blk]["inputs"]["COSTUME"] = [3, rblk, menu]
        return blk

    def stmt_switch_backdrop(self, backdrop_name: str) -> str:
        blk = self.add_block("looks_switchbackdropto")
        menu = self.add_block("looks_backdrops", fields={"BACKDROP": [backdrop_name, None]}, shadow=True)
        self.blocks[menu]["parent"] = blk
        self.blocks[blk]["inputs"]["BACKDROP"] = [1, menu]
        return blk

    def stmt_show(self) -> str:
        return self.add_block("looks_show")

    def stmt_hide(self) -> str:
        return self.add_block("looks_hide")

    def stmt_goto_xy(self, x_val: Any, y_val: Any) -> str:
        blk = self.add_block("motion_gotoxy")
        self._attach_val(blk, "X", x_val)
        self._attach_val(blk, "Y", y_val)
        return blk

    def stmt_set_size(self, size_val: Any) -> str:
        blk = self.add_block("looks_setsizeto")
        self._attach_val(blk, "SIZE", size_val)
        return blk

    def stmt_pen_clear(self) -> str:
        return self.add_block("pen_clear")

    def stmt_pen_stamp(self) -> str:
        return self.add_block("pen_stamp")

    # --- Constructores de Sombreros (Hats) y Procedimientos (My Blocks) ---

    def hat_green_flag(self, body_stmts: List[str], x: int = 40, y: int = 40) -> str:
        hat = self.add_block("event_whenflagclicked", top_level=True, x=x, y=y)
        first = self.chain(body_stmts)
        if first:
            self.blocks[hat]["next"] = first
            self.blocks[first]["parent"] = hat
        return hat

    def hat_broadcast(self, bcast_name: str, body_stmts: List[str], x: int = 40, y: int = 300) -> str:
        bid = self.bcast_map[bcast_name]
        hat = self.add_block(
            "event_whenbroadcastreceived",
            fields={"BROADCAST_OPTION": [bcast_name, bid]},
            top_level=True,
            x=x,
            y=y,
        )
        first = self.chain(body_stmts)
        if first:
            self.blocks[hat]["next"] = first
            self.blocks[first]["parent"] = hat
        return hat

    def define_proc(
        self,
        proccode: str,
        arg_ids: List[str],
        arg_names: List[str],
        warp: bool,
        body_stmts: List[str],
        x: int = 40,
        y: int = 40,
    ) -> str:
        def_id = self.add_block("procedures_definition", top_level=True, x=x, y=y)
        proto_inputs: Dict[str, Any] = {}
        for aid, aname in zip(arg_ids, arg_names):
            arg_rep = self.add_block(
                "argument_reporter_string_number",
                fields={"VALUE": [aname, None]},
                shadow=True,
            )
            proto_inputs[aid] = [1, arg_rep]

        mutation = {
            "tagName": "mutation",
            "children": [],
            "proccode": proccode,
            "argumentids": json.dumps(arg_ids),
            "argumentnames": json.dumps(arg_names),
            "argumentdefaults": json.dumps([""] * len(arg_ids)),
            "warp": "true" if warp else "false",
        }
        proto_id = self.add_block(
            "procedures_prototype",
            inputs=proto_inputs,
            shadow=True,
            mutation=mutation,
        )
        for aid in arg_ids:
            rep_id = proto_inputs[aid][1]
            self.blocks[rep_id]["parent"] = proto_id

        self.blocks[proto_id]["parent"] = def_id
        self.blocks[def_id]["inputs"]["custom_block"] = [1, proto_id]

        first = self.chain(body_stmts)
        if first:
            self.blocks[def_id]["next"] = first
            self.blocks[first]["parent"] = def_id
        return def_id

    def stmt_call_proc(
        self,
        proccode: str,
        arg_ids: List[str],
        arg_vals: List[Any],
        warp: bool = True,
    ) -> str:
        mutation = {
            "tagName": "mutation",
            "children": [],
            "proccode": proccode,
            "argumentids": json.dumps(arg_ids),
            "warp": "true" if warp else "false",
        }
        call_id = self.add_block("procedures_call", mutation=mutation)
        for aid, val in zip(arg_ids, arg_vals):
            self._attach_val(call_id, aid, val)
        return call_id


# ==============================================================================
# 4. TABLAS DE GEOMETRÍA DE TETROMINÓS (7 PIEZAS x 4 ROTACIONES x 4 BLOQUES)
# ==============================================================================

def get_tetromino_tables() -> Tuple[List[int], List[int], List[int], List[int]]:
    shapes = {
        # 1: I (Cian)
        1: [
            [(-1, 0), (0, 0), (1, 0), (2, 0)],
            [(1, -1), (1, 0), (1, 1), (1, 2)],
            [(-1, 1), (0, 1), (1, 1), (2, 1)],
            [(0, -1), (0, 0), (0, 1), (0, 2)],
        ],
        # 2: O (Amarillo)
        2: [
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
        ],
        # 3: T (Púrpura)
        3: [
            [(-1, 0), (0, 0), (1, 0), (0, -1)],
            [(0, -1), (0, 0), (1, 0), (0, 1)],
            [(-1, 0), (0, 0), (1, 0), (0, 1)],
            [(0, -1), (-1, 0), (0, 0), (0, 1)],
        ],
        # 4: S (Verde Neón)
        4: [
            [(-1, 0), (0, 0), (0, -1), (1, -1)],
            [(0, -1), (0, 0), (1, 0), (1, 1)],
            [(-1, 1), (0, 1), (0, 0), (1, 0)],
            [(-1, -1), (-1, 0), (0, 0), (0, 1)],
        ],
        # 5: Z (Rojo Coral)
        5: [
            [(-1, -1), (0, -1), (0, 0), (1, 0)],
            [(1, -1), (0, 0), (1, 0), (0, 1)],
            [(-1, 0), (0, 0), (0, 1), (1, 1)],
            [(0, -1), (-1, 0), (0, 0), (-1, 1)],
        ],
        # 6: J (Azul Eléctrico)
        6: [
            [(-1, -1), (-1, 0), (0, 0), (1, 0)],
            [(0, -1), (1, -1), (0, 0), (0, 1)],
            [(-1, 0), (0, 0), (1, 0), (1, 1)],
            [(0, -1), (0, 0), (-1, 1), (0, 1)],
        ],
        # 7: L (Naranja Solar)
        7: [
            [(-1, 0), (0, 0), (1, 0), (1, -1)],
            [(0, -1), (0, 0), (0, 1), (1, 1)],
            [(-1, 1), (-1, 0), (0, 0), (1, 0)],
            [(-1, -1), (0, -1), (0, 0), (0, 1)],
        ],
    }

    offset_x: List[int] = []
    offset_y: List[int] = []
    for piece_id in range(1, 8):
        for rot in range(4):
            for dx, dy in shapes[piece_id][rot]:
                offset_x.append(dx)
                offset_y.append(dy)

    kick_x = [0, -1, 1, 0, -2, 2]
    kick_y = [0, 0, 0, -1, 0, 0]
    return offset_x, offset_y, kick_x, kick_y


# ==============================================================================
# 5. CONSTRUCCIÓN COMPLETA DEL PROYECTO SCRATCH 3 (.SB3)
# ==============================================================================

def build_project(output_sb3_path: str) -> Dict[str, Any]:
    sound_assets = build_sound_assets()
    offset_x, offset_y, kick_x, kick_y = get_tetromino_tables()

    var_specs = {
        "Estado_Juego": ("var_estado", "MENU"),
        "Modo_Juego": ("var_modo", "NORMAL"),

        "Puntuacion": ("var_puntuacion", 0),
        "Nivel": ("var_nivel", 1),
        "Lineas": ("var_lineas", 0),
        "Combo": ("var_combo", -1),
        "Velocidad_Base": ("var_vel_base", 0.60),
        "Velocidad_Caida": ("var_vel_caida", 0.60),
        "Pieza_Actual": ("var_pieza_act", 1),
        "Pieza_Rotacion": ("var_pieza_rot", 0),
        "Pieza_Col": ("var_pieza_col", 5),
        "Pieza_Fila": ("var_pieza_fila", 2),
        "Fila_Fantasma": ("var_fila_fantasma", 20),
        "Siguiente_Pieza": ("var_sig_pieza", 2),
        "Pieza_Guardada": ("var_pieza_hold", 0),
        "Puede_Guardar": ("var_puede_hold", 1),
        "Colision_Detectada": ("var_colision", 0),
        "Rotacion_Exito": ("var_rot_exito", 0),
        "Lineas_Turno": ("var_lineas_turno", 0),
        "Multiplicador_Caos": ("var_mult_caos", 1),
        "Evento_Caos": ("var_evento_caos", "NONE"),
        "Reloj_Caida": ("var_reloj_caida", 0),


        "idx": ("var_idx", 1),
        "f": ("var_f", 1),
        "c": ("var_c", 1),
        "i": ("var_i", 1),
        "k": ("var_k", 1),
        "temp_pieza": ("var_temp_pieza", 1),
        "temp_azar": ("var_temp_azar", 1),
        "test_col": ("var_test_col", 5),
        "test_fila": ("var_test_fila", 2),
        "test_rot": ("var_test_rot", 0),
        "bloque_col": ("var_bloque_col", 5),
        "bloque_fila": ("var_bloque_fila", 2),
        "tabla_idx": ("var_tabla_idx", 1),
        "fila_completa": ("var_fila_completa", 1),
        "f_origen": ("var_f_origen", 20),
        "celda_val": ("var_celda_val", 0),
        "stamp_x": ("var_stamp_x", 0),
        "stamp_y": ("var_stamp_y", 0),
        "puntos_base": ("var_puntos_base", 0),
    }

    for name, value in {"Tiempo_Juego":0, "Ultimo_Tick":0, "Delta":0, "Bloqueo":-1,
                        "Evento_Fin":0, "Proximo_Evento":12, "Proximo_Ataque":25,
                        "Intervalo_Ataque":25, "Hueco":1, "Eventos":0, "hud_num":0, "hud_pos":0,
                        "Nightmare_Intro":0, "Pausa_Origen":"JUGANDO",
                        "NM_Event":"NONE", "NM_Warning":0, "NM_Rows":0,
                        "NM_Progress":0, "NM_Jam":0, "NM_Cooldown":0, "NM_Sequence":0, "NM_Cancelable":1,
                        "NM_Chain":0, "NM_EventStart":"NONE", "NM_Top":0, "NM_Scan":1, "NM_Delayed":0,
                        "Armor_Row":0, "Armor_Hit":0, "NM_Submode":"ENDLESS", "Trial_Wave":1,
                        "Trial_Count":0, "Trial_Event":0, "Trial_Goal":20, "Trial_Timer":0, "Trial_Required":1,
                        "Trial_GlitchDone":0, "G_Timer":0, "G_Time":0, "G_Phase":0, "G_PrevPhase":-1,
                        "G_Inner":0, "G_X":0, "G_Y":-45, "G_TargetX":0, "G_TargetY":0,
                        "G_HP":3, "G_Invuln":0, "G_Hit":0, "G_Pos":0, "G_Next":60, "G_Success":0, "G_Active":0, "G_Radius":0, "G_SoundedPhase":-1, "NM_Reduced":0}.items():
        var_specs[name] = ("v2_"+name, value)
    for key in ["left", "right", "down", "up", "space", "c", "p", "r", "m", "1", "2", "3", "4", "enter"]:
        var_specs["key_"+key] = ("v2_key_"+key, 0)
        var_specs["repeat_"+key] = ("v2_repeat_"+key, 0)
    var_map = {k: v[0] for k, v in var_specs.items()}
    stage_variables = {v[0]: [k, v[1]] for k, v in var_specs.items()}

    list_specs = {
        "Tablero": ("list_tablero", [0] * 200),
        "Bolsa_7": ("list_bolsa7", [1, 2, 3, 4, 5, 6, 7]),
        "Offset_X": ("list_offset_x", offset_x),
        "Offset_Y": ("list_offset_y", offset_y),
        "Kick_X": ("list_kick_x", kick_x),
        "Kick_Y": ("list_kick_y", kick_y),
    }
    list_map = {k: v[0] for k, v in list_specs.items()}
    stage_lists = {v[0]: [k, v[1]] for k, v in list_specs.items()}

    bcast_specs = {
        "Iniciar_Juego": "bcast_iniciar_juego",
        "Actualizar_UI": "bcast_actualizar_ui",
        "Alternar_Pausa": "bcast_alternar_pausa",
        "Animar_Linea": "bcast_animar_linea",
    }
    stage_broadcasts = {v: k for k, v in bcast_specs.items()}

    all_zip_files: Dict[str, bytes] = {}
    for snd in sound_assets.values():
        all_zip_files[snd["md5ext"]] = snd["bytes"]

    # --------------------------------------------------------------------------
    # TARGET 0: STAGE (ESCENARIO)
    # --------------------------------------------------------------------------
    bg_normal = register_svg_asset(
        "Fondo_Arcade",
        make_stage_backdrop_svg("#31435A", "NEXUS BLOCKS • IPAD Y TECLADO"),
        240,
        180,
    )
    bg_chaos = register_svg_asset(
        "Fondo_Caos",
        make_stage_backdrop_svg("#774254", "CHAOS MODE • EVENTO ESPECIAL ACTIVO"),
        240,
        180,
    )
    bg_nightmare = register_svg_asset("Fondo_Nightmare", '''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#101010"/><rect x="164" y="29" width="152" height="302" fill="#101010" stroke="#FFBC32" stroke-width="2"/><path d="M12 28H148 M332 28H468 M12 332H148 M332 332H468" stroke="#FFBC32"/><g fill="#F5F2E9" font-family="monospace" font-size="11" text-anchor="middle"><text x="80" y="60">HOLD</text><text x="80" y="160">SCORE</text><text x="400" y="60">NEXT</text><text x="400" y="160">LEVEL</text><text x="400" y="218">LINES</text><text x="400" y="276">MODE</text><text x="240" y="18">NEXUS BLOCKS / NIGHTMARE</text><text x="240" y="350">ARROWS MOVE / ROTATE   SPACE DROP   C HOLD   P PAUSE   R RESTART</text></g></svg>''', 240, 180)
    for asset in (bg_normal, bg_chaos, bg_nightmare):
        all_zip_files[asset["md5ext"]] = asset["bytes"]

    stage_b = ScratchBlockBuilder("stg", var_map, list_map, bcast_specs)
    stage_b.hat_broadcast(
        "Actualizar_UI",
        [
            stage_b.stmt_if_else(
                stage_b.op_eq("$v:Modo_Juego", "CHAOS"),
                [stage_b.stmt_switch_backdrop("Fondo_Caos")],
                [stage_b.stmt_if_else(stage_b.op_eq("$v:Modo_Juego", "NIGHTMARE"),
                    [stage_b.stmt_switch_backdrop("Fondo_Nightmare")],
                    [stage_b.stmt_switch_backdrop("Fondo_Arcade")])],
            )
        ],
        x=50,
        y=50,
    )
    stage_b.add_comment(
        None,
        "ESCENARIO PRINCIPAL (STAGE)\nContiene las variables globales, listas de geometría (Offset_X, Offset_Y, Kick_X, Kick_Y) y el estado del tablero de 10x20 celdas.",
        x=50,
        y=180,
    )

    stage_target = {
        "isStage": True,
        "name": "Stage",
        "variables": stage_variables,
        "lists": stage_lists,
        "broadcasts": stage_broadcasts,
        "blocks": stage_b.blocks,
        "comments": stage_b.comments,
        "currentCostume": 0,
        "costumes": [
            {k: v for k, v in bg_normal.items() if k != "bytes"},
            {k: v for k, v in bg_chaos.items() if k != "bytes"},
            {k: v for k, v in bg_nightmare.items() if k != "bytes"},
        ],
        "sounds": [],
        "volume": 100,
        "layerOrder": 0,
        "tempo": 120,
        "videoTransparency": 50,
        "videoState": "off",
        "textToSpeechLanguage": None,
    }

    # --------------------------------------------------------------------------
    # TARGET 1: MOTOR_JUEGO (MOTOR CENTRAL + RENDERIZADOR PEN)
    # --------------------------------------------------------------------------
    block_costumes_specs = [
        ("Bloque_1_I", make_block_svg("#00E5FF", "#B3F8FF", "#0088A3")),
        ("Bloque_2_O", make_block_svg("#FFD600", "#FFF399", "#B28900")),
        ("Bloque_3_T", make_block_svg("#AA00FF", "#E299FF", "#6A00A3")),
        ("Bloque_4_S", make_block_svg("#00E676", "#A6FFCE", "#008C44")),
        ("Bloque_5_Z", make_block_svg("#FF1744", "#FF99AC", "#A3001E")),
        ("Bloque_6_J", make_block_svg("#2979FF", "#99C2FF", "#0043B2")),
        ("Bloque_7_L", make_block_svg("#FF9100", "#FFD099", "#B25900")),
        ("Bloque_8_Flash", make_block_svg("#FFFFFF", "#FFFFCC", "#00F0FF")),
        ("Bloque_9_Armor", '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"><rect x=".5" y=".5" width="14" height="14" fill="#101010" stroke="#FFBC32"/><path d="M3 3H12V12H3Z M5 5H10V10H5Z" fill="none" stroke="#F5F2E9"/></svg>'),
        ("Bloque_10_Cracked", '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"><rect x=".5" y=".5" width="14" height="14" fill="#101010" stroke="#FFBC32"/><path d="M3 3H12V12H3Z M9 2L6 6 9 8 5 13" fill="none" stroke="#F5F2E9" stroke-width="1.3"/></svg>'),
        ("Bloque_Fantasma", make_ghost_block_svg(15)),
    ]
    motor_costumes = []
    for cname, csvg in block_costumes_specs:
        casset = register_svg_asset(cname, csvg, 7.5, 7.5)
        all_zip_files[casset["md5ext"]] = casset["bytes"]
        motor_costumes.append({k: v for k, v in casset.items() if k != "bytes"})

    # HUD vectorial: cifras y estados estampados, sin monitores de variables.
    for label in [str(n) for n in range(10)]+["NORMAL","HARD","CHAOS","NIGHTMARE","ENDLESS","TRIALS","WAVE","/","NONE","DIFFICULT PIECES","SPEED BURST","GARBAGE INCOMING","DOUBLE GARBAGE","HOLD JAM SOON","HOLD JAM","GARBAGE DEBT","ROWS","IN","LINES","CHAIN: DOUBLE > JAM","CHAIN: JAM > DEBT","DEBT SOON","PRESSURE DELAYED","ARMOR INCOMING","SIGNAL BEAM","TARGET MARKER","PULSE RING","SWEEP WALL","DATA FRAGMENTS","CHARGE","ACTIVE","CORE HP","MOTION LOW"]:
        safe_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        asset = register_svg_asset("HUD_"+label, f'<svg xmlns="http://www.w3.org/2000/svg" width="130" height="24"><text x="65" y="17" text-anchor="middle" font-family="sans-serif" font-size="{12 if len(label)>10 else 17}" fill="#E5EEF9">{safe_label}</text></svg>',65,12)
        all_zip_files[asset["md5ext"]]=asset["bytes"]
        motor_costumes.append({k:v for k,v in asset.items() if k!="bytes"})

    glitch_svgs = {
        "G_ARENA": '<svg xmlns="http://www.w3.org/2000/svg" width="130" height="130"><rect x="2" y="2" width="126" height="126" fill="#101010" stroke="#FFBC32" stroke-width="2"/><path d="M32 3V127 M65 3V127 M98 3V127 M3 32H127 M3 65H127 M3 98H127" stroke="#F5F2E9" stroke-opacity=".18"/></svg>',
        "G_CORE": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"><path d="M7 1L13 7 7 13 1 7Z" fill="#F5F2E9" stroke="#FFBC32"/></svg>',
        "G_CORE_HIT": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"><path d="M7 1L13 7 7 13 1 7Z" fill="#101010" stroke="#FFBC32" stroke-width="2"/></svg>',
        "G_BEAM_WARN": '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="12"><rect x="1" y="1" width="118" height="10" fill="none" stroke="#FFBC32" stroke-dasharray="5 3"/></svg>',
        "G_BEAM_FIRE": '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="12"><rect width="120" height="12" fill="#FFBC32"/><path d="M0 6H120" stroke="#101010"/></svg>',
        "G_TARGET": '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30"><rect x="2" y="2" width="26" height="26" fill="none" stroke="#FFBC32" stroke-width="2"/><path d="M15 0V30 M0 15H30" stroke="#F5F2E9"/></svg>',
        "G_TARGET_FIRE": '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30"><rect width="30" height="30" fill="#FFBC32"/><path d="M15 0V30 M0 15H30" stroke="#101010" stroke-width="2"/></svg>',
        "G_RING": '<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72"><circle cx="36" cy="36" r="30" fill="#FFBC32" fill-opacity=".28" stroke="#FFBC32" stroke-width="2"/></svg>',
        "G_RING_WARN": '<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72"><circle cx="36" cy="36" r="30" fill="#FFBC32" fill-opacity=".1" stroke="#FFBC32" stroke-width="2" stroke-dasharray="5 4"/></svg>',
        "G_FRAGMENT": '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30"><path d="M2 2H28V28H2Z M3 3L27 27" fill="none" stroke="#FFBC32" stroke-width="2"/></svg>',
        "G_WALL": '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="120"><path d="M1 0H29V43H1Z M1 77H29V120H1Z" fill="#FFBC32"/><path d="M1 46V74 M29 46V74" stroke="#F5F2E9" stroke-dasharray="3 2"/></svg>',
        "G_WALL_WARN": '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="120"><path d="M1 1H29V43H1Z M1 77H29V119H1Z" fill="none" stroke="#FFBC32" stroke-width="2" stroke-dasharray="5 3"/><path d="M1 46V74 M29 46V74" stroke="#F5F2E9" stroke-dasharray="3 2"/></svg>',
        "G_FRAGMENT_FIRE": '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30"><rect x="1" y="1" width="28" height="28" fill="#FFBC32"/><path d="M3 3L27 27" stroke="#101010" stroke-width="2"/></svg>',
    }
    for name, svg in glitch_svgs.items():
        size = {"G_ARENA":(65,65),"G_BEAM_WARN":(60,6),"G_BEAM_FIRE":(60,6),"G_TARGET":(15,15),"G_TARGET_FIRE":(15,15),"G_RING":(36,36),"G_RING_WARN":(36,36),"G_WALL":(15,60),"G_WALL_WARN":(15,60),"G_FRAGMENT":(15,15),"G_FRAGMENT_FIRE":(15,15)}.get(name,(7,7))
        asset = register_svg_asset(name,svg,*size); all_zip_files[asset["md5ext"]]=asset["bytes"]
        motor_costumes.append({k:v for k,v in asset.items() if k!="bytes"})

    motor_sounds = [
        {k: v for k, v in sound_assets[sname].items() if k != "bytes"}
        for sname in (
            "Sonido_Mover",
            "Sonido_Rotar",
            "Sonido_Caida",
            "Sonido_Linea",
            "Sonido_Hold",
            "Sonido_Caos",
            "Sonido_GameOver",
            "Sonido_NMWarning", "Sonido_Armor", "Sonido_GlitchFire", "Sonido_GlitchHit", "Sonido_GlitchWin",
        )
    ]

    mb = ScratchBlockBuilder("mot", var_map, list_map, bcast_specs)

    # --- PROCEDIMIENTO 1: Rellenar_Bolsa_7 (Sistema 7-Bag Randomizer) ---
    proc_bolsa_code = "Rellenar_Bolsa_7"
    mb.define_proc(
        proc_bolsa_code,
        [],
        [],
        True,
        [
            mb.stmt_if(
                mb.op_eq(mb.expr_list_length("Bolsa_7"), 0),
                [
                    mb.stmt_set_var("i", 1),
                    mb.stmt_repeat(
                        7,
                        [
                            mb.stmt_add_to_list("Bolsa_7", "$v:i"),
                            mb.stmt_change_var("i", 1),
                        ],
                    ),
                ],
            )
        ],
        x=40,
        y=40,
    )

    # --- PROCEDIMIENTO 2: Extraer_De_Bolsa ---
    proc_extraer_code = "Extraer_De_Bolsa"
    mb.define_proc(
        proc_extraer_code,
        [],
        [],
        True,
        [
            mb.stmt_call_proc(proc_bolsa_code, [], [], True),
            mb.stmt_set_var("temp_azar", mb.op_random(1, mb.expr_list_length("Bolsa_7"))),
            mb.stmt_set_var("temp_pieza", mb.expr_list_item("Bolsa_7", "$v:temp_azar")),
            mb.stmt_delete_of_list("Bolsa_7", "$v:temp_azar"),
            mb.stmt_call_proc(proc_bolsa_code, [], [], True),
        ],
        x=40,
        y=280,
    )

    # --- PROCEDIMIENTO 3: Comprobar_Colision (tipo) (col) (fila) (rot) ---
    proc_col_code = "Comprobar_Colision %s %s %s %s"
    proc_col_args = ["arg_tipo", "arg_col", "arg_fila", "arg_rot"]
    proc_col_names = ["tipo", "col", "fila", "rot"]

    calc_tabla_idx = mb.op_add(
        mb.op_add(
            mb.op_mul(mb.op_sub("$a:tipo", 1), 16),
            mb.op_mul("$a:rot", 4),
        ),
        "$v:i",
    )
    calc_board_idx = lambda: mb.op_add(
        mb.op_mul(mb.op_sub("$v:bloque_fila", 1), 10),
        "$v:bloque_col",
    )

    mb.define_proc(
        proc_col_code,
        proc_col_args,
        proc_col_names,
        True,
        [
            mb.stmt_set_var("Colision_Detectada", 0),
            mb.stmt_set_var("i", 1),
            mb.stmt_repeat(
                4,
                [
                    mb.stmt_set_var("tabla_idx", calc_tabla_idx),
                    mb.stmt_set_var(
                        "bloque_col",
                        mb.op_add("$a:col", mb.expr_list_item("Offset_X", "$v:tabla_idx")),
                    ),
                    mb.stmt_set_var(
                        "bloque_fila",
                        mb.op_add("$a:fila", mb.expr_list_item("Offset_Y", "$v:tabla_idx")),
                    ),
                    mb.stmt_if_else(
                        mb.op_or(
                            mb.op_or(
                                mb.op_lt("$v:bloque_col", 1),
                                mb.op_gt("$v:bloque_col", 10),
                            ),
                            mb.op_or(
                                mb.op_lt("$v:bloque_fila", 1),
                                mb.op_gt("$v:bloque_fila", 20),
                            ),
                        ),
                        [mb.stmt_set_var("Colision_Detectada", 1)],
                        [
                            mb.stmt_if(
                                mb.op_gt(
                                    mb.expr_list_item("Tablero", calc_board_idx()),
                                    0,
                                ),
                                [mb.stmt_set_var("Colision_Detectada", 1)],
                            )
                        ],
                    ),
                    mb.stmt_change_var("i", 1),
                ],
            ),
        ],
        x=40,
        y=520,
    )

    # --- PROCEDIMIENTO 4: Actualizar_Fantasma ---
    proc_ghost_code = "Actualizar_Fantasma"
    mb.define_proc(
        proc_ghost_code,
        [],
        [],
        True,
        [
            mb.stmt_set_var("Fila_Fantasma", "$v:Pieza_Fila"),
            mb.stmt_set_var("Colision_Detectada", 0),
            mb.stmt_repeat_until(
                mb.op_eq("$v:Colision_Detectada", 1),
                [
                    mb.stmt_call_proc(
                        proc_col_code,
                        proc_col_args,
                        [
                            "$v:Pieza_Actual",
                            "$v:Pieza_Col",
                            mb.op_add("$v:Fila_Fantasma", 1),
                            "$v:Pieza_Rotacion",
                        ],
                        True,
                    ),
                    mb.stmt_if(
                        mb.op_eq("$v:Colision_Detectada", 0),
                        [mb.stmt_change_var("Fila_Fantasma", 1)],
                    ),
                ],
            ),
            mb.stmt_set_var("Colision_Detectada", 0),
        ],
        x=40,
        y=980,
    )

    # Velocidad única, progresiva y limitada a 70 ms.
    proc_vel_code = "Actualizar_Velocidad_Y_Caos"
    mb.define_proc(proc_vel_code, [], [], True, [
        mb.stmt_set_var("Velocidad_Base", 0.65),
        mb.stmt_set_var("Delta", 0.045),
        mb.stmt_if(mb.op_eq("$v:Modo_Juego", "HARD"), [mb.stmt_set_var("Velocidad_Base",0.30),mb.stmt_set_var("Delta",0.055)]),
        mb.stmt_if(mb.op_or(mb.op_eq("$v:Modo_Juego", "CHAOS"),mb.op_eq("$v:Modo_Juego", "NIGHTMARE")), [mb.stmt_set_var("Velocidad_Base",0.23),mb.stmt_set_var("Delta",0.04)]),
        mb.stmt_set_var("Velocidad_Caida", mb.op_div("$v:Velocidad_Base",mb.op_add(1,mb.op_mul(mb.op_sub("$v:Nivel",1),"$v:Delta")))),
        mb.stmt_if(mb.op_or(mb.op_eq("$v:Modo_Juego", "CHAOS"),mb.op_eq("$v:Modo_Juego", "NIGHTMARE")), [
            mb.stmt_set_var("Velocidad_Caida",mb.op_div("$v:Velocidad_Caida",mb.op_add(1,mb.op_div("$v:Tiempo_Juego",180)))),
            mb.stmt_if(mb.op_eq("$v:Evento_Caos","SPEED BURST"),[mb.stmt_set_var("Velocidad_Caida",mb.op_mul("$v:Velocidad_Caida",0.5))])]),
        mb.stmt_if(mb.op_lt("$v:Velocidad_Caida",0.07),[mb.stmt_set_var("Velocidad_Caida",0.07)])])

    mb.define_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["n","x","y"],True,[
        mb.stmt_set_var("hud_num","$a:n"),mb.stmt_set_var("hud_pos","$a:x"),
        mb.stmt_repeat_until(mb.op_lt("$v:hud_num",10),[
            mb.stmt_switch_costume(mb.op_join("HUD_",mb.op_mod("$v:hud_num",10))),
            mb.stmt_goto_xy("$v:hud_pos","$a:y"),mb.stmt_pen_stamp(),
            mb.stmt_set_var("hud_num",mb.op_math("floor",mb.op_div("$v:hud_num",10))),mb.stmt_change_var("hud_pos",-11)]),
        mb.stmt_switch_costume(mb.op_join("HUD_","$v:hud_num")),mb.stmt_goto_xy("$v:hud_pos","$a:y"),mb.stmt_pen_stamp()])

    # --- PROCEDIMIENTO 6: Renderizar_Todo (Run without screen refresh) ---
    proc_render_code = "Renderizar_Todo"
    board_x_expr = lambda col_var: mb.op_add(-82.5, mb.op_mul(col_var, 15))
    board_y_expr = lambda fila_var: mb.op_sub(157.5, mb.op_mul(fila_var, 15))
    piece_idx_expr = lambda p_var, r_var: mb.op_add(
        mb.op_add(
            mb.op_mul(mb.op_sub(p_var, 1), 16),
            mb.op_mul(r_var, 4),
        ),
        "$v:i",
    )

    mb.define_proc(
        proc_render_code,
        [],
        [],
        True,
        [
            mb.stmt_pen_clear(),
            mb.stmt_show(),
            mb.stmt_set_size(100),
            mb.stmt_set_var("f", 1),
            mb.stmt_repeat(
                20,
                [
                    mb.stmt_set_var("c", 1),
                    mb.stmt_repeat(
                        10,
                        [
                            mb.stmt_set_var(
                                "idx",
                                mb.op_add(mb.op_mul(mb.op_sub("$v:f", 1), 10), "$v:c"),
                            ),
                            mb.stmt_set_var("celda_val", mb.expr_list_item("Tablero", "$v:idx")),
                            mb.stmt_if(
                                mb.op_gt("$v:celda_val", 0),
                                [
                                    mb.stmt_switch_costume("$v:celda_val"),
                                    mb.stmt_goto_xy(board_x_expr("$v:c"), board_y_expr("$v:f")),
                                    mb.stmt_pen_stamp(),
                                ],
                            ),
                            mb.stmt_change_var("c", 1),
                        ],
                    ),
                    mb.stmt_change_var("f", 1),
                ],
            ),
            mb.stmt_if(
                mb.op_or(
                    mb.op_eq("$v:Estado_Juego", "JUGANDO"),
                    mb.op_eq("$v:Estado_Juego", "PAUSA"),
                ),
                [
                    mb.stmt_switch_costume("Bloque_Fantasma"),
                    mb.stmt_set_var("i", 1),
                    mb.stmt_repeat(
                        4,
                        [
                            mb.stmt_set_var("tabla_idx", piece_idx_expr("$v:Pieza_Actual", "$v:Pieza_Rotacion")),
                            mb.stmt_set_var(
                                "bloque_col",
                                mb.op_add("$v:Pieza_Col", mb.expr_list_item("Offset_X", "$v:tabla_idx")),
                            ),
                            mb.stmt_set_var(
                                "bloque_fila",
                                mb.op_add("$v:Fila_Fantasma", mb.expr_list_item("Offset_Y", "$v:tabla_idx")),
                            ),
                            mb.stmt_goto_xy(board_x_expr("$v:bloque_col"), board_y_expr("$v:bloque_fila")),
                            mb.stmt_pen_stamp(),
                            mb.stmt_change_var("i", 1),
                        ],
                    ),
                    mb.stmt_switch_costume("$v:Pieza_Actual"),
                    mb.stmt_set_var("i", 1),
                    mb.stmt_repeat(
                        4,
                        [
                            mb.stmt_set_var("tabla_idx", piece_idx_expr("$v:Pieza_Actual", "$v:Pieza_Rotacion")),
                            mb.stmt_set_var(
                                "bloque_col",
                                mb.op_add("$v:Pieza_Col", mb.expr_list_item("Offset_X", "$v:tabla_idx")),
                            ),
                            mb.stmt_set_var(
                                "bloque_fila",
                                mb.op_add("$v:Pieza_Fila", mb.expr_list_item("Offset_Y", "$v:tabla_idx")),
                            ),
                            mb.stmt_goto_xy(board_x_expr("$v:bloque_col"), board_y_expr("$v:bloque_fila")),
                            mb.stmt_pen_stamp(),
                            mb.stmt_change_var("i", 1),
                        ],
                    ),
                    mb.stmt_set_size(80),
                    mb.stmt_switch_costume("$v:Siguiente_Pieza"),
                    mb.stmt_set_var("i", 1),
                    mb.stmt_repeat(
                        4,
                        [
                            mb.stmt_set_var("tabla_idx", piece_idx_expr("$v:Siguiente_Pieza", 0)),
                            mb.stmt_set_var(
                                "stamp_x",
                                mb.op_add(156, mb.op_mul(mb.expr_list_item("Offset_X", "$v:tabla_idx"), 12)),
                            ),
                            mb.stmt_set_var(
                                "stamp_y",
                                mb.op_sub(82, mb.op_mul(mb.expr_list_item("Offset_Y", "$v:tabla_idx"), 12)),
                            ),
                            mb.stmt_goto_xy("$v:stamp_x", "$v:stamp_y"),
                            mb.stmt_pen_stamp(),
                            mb.stmt_change_var("i", 1),
                        ],
                    ),
                    mb.stmt_if(
                        mb.op_gt("$v:Pieza_Guardada", 0),
                        [
                            mb.stmt_switch_costume("$v:Pieza_Guardada"),
                            mb.stmt_set_var("i", 1),
                            mb.stmt_repeat(
                                4,
                                [
                                    mb.stmt_set_var("tabla_idx", piece_idx_expr("$v:Pieza_Guardada", 0)),
                                    mb.stmt_set_var(
                                        "stamp_x",
                                        mb.op_add(
                                            -164,
                                            mb.op_mul(mb.expr_list_item("Offset_X", "$v:tabla_idx"), 12),
                                        ),
                                    ),
                                    mb.stmt_set_var(
                                        "stamp_y",
                                        mb.op_sub(
                                            82,
                                            mb.op_mul(mb.expr_list_item("Offset_Y", "$v:tabla_idx"), 12),
                                        ),
                                    ),
                                    mb.stmt_goto_xy("$v:stamp_x", "$v:stamp_y"),
                                    mb.stmt_pen_stamp(),
                                    mb.stmt_change_var("i", 1),
                                ],
                            ),
                        ],
                    ),
                    mb.stmt_set_size(100),
                ],
            ),
            mb.stmt_set_size(100),
            mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:Puntuacion",-140,0],True),
            mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:Nivel",165,0],True),
            mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:Lineas",165,-58],True),
            mb.stmt_switch_costume(mb.op_join("HUD_","$v:Modo_Juego")),mb.stmt_goto_xy(160,-116),mb.stmt_pen_stamp(),
            mb.stmt_if(mb.op_not(mb.op_eq("$v:Evento_Caos","NONE")),[mb.stmt_switch_costume(mb.op_join("HUD_","$v:Evento_Caos")),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp()]),
            mb.stmt_if(mb.op_eq("$v:Modo_Juego","NIGHTMARE"),[
                # Compact Nightmare HUD: fixed sizes keep labels and numbers inside
                # their columns even when the game is displayed on a 480x360 stage.
                mb.stmt_set_size(70),
                mb.stmt_switch_costume(mb.op_join("HUD_","$v:NM_Submode")),mb.stmt_goto_xy(160,-130),mb.stmt_pen_stamp(),
                mb.stmt_if(mb.op_and(mb.op_eq("$v:NM_Submode","TRIALS"),mb.op_not(mb.op_eq("$v:Estado_Juego","MENU"))),[
                    mb.stmt_switch_costume("HUD_WAVE"),mb.stmt_goto_xy(112,-146),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:Trial_Wave",138,-146],True),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:Trial_Count",176,-146],True),
                    mb.stmt_switch_costume("HUD_/"),mb.stmt_goto_xy(188,-146),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:Trial_Goal",216,-146],True)]),
                mb.stmt_if(mb.op_eq("$v:NM_Event","DOUBLE"),[
                    mb.stmt_switch_costume("HUD_DOUBLE GARBAGE"),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp(),
                    mb.stmt_switch_costume("HUD_ROWS"),mb.stmt_goto_xy(-194,-87),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Rows",-168,-87],True),
                    mb.stmt_switch_costume("HUD_IN"),mb.stmt_goto_xy(-142,-87),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Warning",-120,-87],True),
                    mb.stmt_if(mb.op_eq("$v:NM_Cancelable",1),[
                        mb.stmt_switch_costume("HUD_LINES"),mb.stmt_goto_xy(-180,-108),mb.stmt_pen_stamp(),
                        mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Progress",-140,-108],True)])]),
                mb.stmt_if(mb.op_eq("$v:NM_Event","JAM_WARNING"),[
                    mb.stmt_switch_costume("HUD_HOLD JAM SOON"),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Warning",-160,-87],True)]),
                mb.stmt_if(mb.op_eq("$v:NM_Event","CHAIN_JAM"),[
                    mb.stmt_switch_costume("HUD_HOLD JAM SOON"),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Warning",-160,-87],True)]),
                mb.stmt_if(mb.op_eq("$v:NM_Event","CHAIN_DEBT"),[
                    mb.stmt_switch_costume("HUD_DEBT SOON"),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Warning",-160,-87],True)]),
                mb.stmt_if(mb.op_eq("$v:NM_Event","ARMOR_WARNING"),[
                    mb.stmt_switch_costume("HUD_ARMOR INCOMING"),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Warning",-160,-87],True)]),
                mb.stmt_if(mb.op_eq("$v:NM_Event","DEBT"),[
                    mb.stmt_switch_costume("HUD_GARBAGE DEBT"),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp(),
                    mb.stmt_switch_costume("HUD_ROWS"),mb.stmt_goto_xy(-194,-87),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Rows",-168,-87],True),
                    mb.stmt_switch_costume("HUD_IN"),mb.stmt_goto_xy(-142,-87),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Warning",-120,-87],True),
                    mb.stmt_switch_costume("HUD_LINES"),mb.stmt_goto_xy(-180,-108),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Progress",-140,-108],True)]),
                mb.stmt_if(mb.op_gt("$v:NM_Jam",0),[
                    mb.stmt_switch_costume("HUD_HOLD JAM"),mb.stmt_goto_xy(-178,40),mb.stmt_pen_stamp(),
                    mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:NM_Jam",-127,40],True)]),
                mb.stmt_if(mb.op_eq("$v:NM_Chain",1),[mb.stmt_switch_costume("HUD_CHAIN: DOUBLE > JAM"),mb.stmt_goto_xy(-160,-145),mb.stmt_pen_stamp()]),
                mb.stmt_if(mb.op_eq("$v:NM_Chain",2),[mb.stmt_switch_costume("HUD_CHAIN: JAM > DEBT"),mb.stmt_goto_xy(-160,-145),mb.stmt_pen_stamp()]),
                mb.stmt_if(mb.op_eq("$v:NM_Delayed",1),[mb.stmt_switch_costume("HUD_PRESSURE DELAYED"),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp()]),
                mb.stmt_if(mb.op_and(mb.op_eq("$v:NM_Reduced",1),mb.op_and(mb.op_eq("$v:NM_Event","NONE"),mb.op_and(mb.op_eq("$v:NM_Jam",0),mb.op_eq("$v:NM_Delayed",0)))),
                    [mb.stmt_switch_costume("HUD_MOTION LOW"),mb.stmt_goto_xy(-160,-65),mb.stmt_pen_stamp()]),
                mb.stmt_set_size(100)]),
            mb.stmt_hide(),
        ],
        x=560,
        y=40,
    )

    # --- PROCEDIMIENTO 7: Generar_Nueva_Pieza ---
    proc_spawn_code = "Generar_Nueva_Pieza"
    mb.define_proc(
        proc_spawn_code,
        [],
        [],
        True,
        [
            mb.stmt_set_var("Pieza_Actual", "$v:Siguiente_Pieza"),
            mb.stmt_call_proc(proc_extraer_code, [], [], True),
            mb.stmt_if(mb.op_eq("$v:Evento_Caos","DIFFICULT PIECES"),[
                mb.stmt_if(mb.op_lt(mb.op_random(1,100),66),[mb.stmt_set_var("temp_pieza",mb.op_random(4,5))])]),
            mb.stmt_set_var("Siguiente_Pieza", "$v:temp_pieza"),
            mb.stmt_set_var("Pieza_Col", 5),
            mb.stmt_set_var("Pieza_Fila", 2),
            mb.stmt_set_var("Pieza_Rotacion", 0),
            mb.stmt_set_var("Puede_Guardar", 1),
            mb.stmt_set_var("Bloqueo", -1),
            mb.stmt_call_proc(
                proc_col_code,
                proc_col_args,
                ["$v:Pieza_Actual", "$v:Pieza_Col", "$v:Pieza_Fila", "$v:Pieza_Rotacion"],
                True,
            ),
            mb.stmt_if_else(
                mb.op_eq("$v:Colision_Detectada", 1),
                [
                    mb.stmt_set_var("Estado_Juego", "GAMEOVER"),
                    mb.stmt_play_sound("Sonido_GameOver"),
                    mb.stmt_broadcast("Actualizar_UI"),
                ],
                [
                    mb.stmt_call_proc(proc_ghost_code, [], [], True),
                    mb.stmt_set_var("Reloj_Caida", "$v:Tiempo_Juego"),
                ],
            ),
        ],
        x=560,
        y=920,
    )

    # --- PROCEDIMIENTO 8: Revisar_Y_Eliminar_Lineas ---
    proc_lines_code = "Revisar_Y_Eliminar_Lineas"
    mb.define_proc(
        proc_lines_code,
        [],
        [],
        True,
        [
            mb.stmt_set_var("Lineas_Turno", 0),
            mb.stmt_set_var("Armor_Hit", 0),
            mb.stmt_set_var("f", 20),
            mb.stmt_repeat_until(
                mb.op_lt("$v:f", 1),
                [
                    mb.stmt_set_var("fila_completa", 1),
                    mb.stmt_set_var("Armor_Row", 0),
                    mb.stmt_set_var("c", 1),
                    mb.stmt_repeat(
                        10,
                        [
                            mb.stmt_set_var(
                                "idx",
                                mb.op_add(mb.op_mul(mb.op_sub("$v:f", 1), 10), "$v:c"),
                            ),
                            mb.stmt_if(
                                mb.op_eq(mb.expr_list_item("Tablero", "$v:idx"), 0),
                                [mb.stmt_set_var("fila_completa", 0)],
                            ),
                            mb.stmt_if(mb.op_and(mb.op_eq("$v:Modo_Juego","NIGHTMARE"),mb.op_eq(mb.expr_list_item("Tablero","$v:idx"),9)),[mb.stmt_set_var("Armor_Row",1)]),
                            mb.stmt_change_var("c", 1),
                        ],
                    ),
                    # Una fila completa intacta se agrieta una sola vez por revisión.
                    # Su resolución automática ocurre al fijar la próxima pieza.
                    mb.stmt_if(mb.op_and(mb.op_eq("$v:fila_completa",1),mb.op_eq("$v:Armor_Row",1)),[
                        mb.stmt_set_var("c",1),
                        mb.stmt_repeat(10,[
                            mb.stmt_set_var("idx",mb.op_add(mb.op_mul(mb.op_sub("$v:f",1),10),"$v:c")),
                            mb.stmt_if(mb.op_eq(mb.expr_list_item("Tablero","$v:idx"),9),[mb.stmt_replace_item_list("Tablero","$v:idx",10)]),
                            mb.stmt_change_var("c",1)]),
                        mb.stmt_change_var("Armor_Hit",1),mb.stmt_set_var("fila_completa",0)]),
                    mb.stmt_if_else(
                        mb.op_eq("$v:fila_completa", 1),
                        [
                            mb.stmt_change_var("Lineas_Turno", 1),
                            mb.stmt_set_var("f_origen", "$v:f"),
                            mb.stmt_repeat_until(
                                mb.op_lt("$v:f_origen", 2),
                                [
                                    mb.stmt_set_var("c", 1),
                                    mb.stmt_repeat(
                                        10,
                                        [
                                            mb.stmt_set_var(
                                                "celda_val",
                                                mb.expr_list_item(
                                                    "Tablero",
                                                    mb.op_add(
                                                        mb.op_mul(mb.op_sub("$v:f_origen", 2), 10),
                                                        "$v:c",
                                                    ),
                                                ),
                                            ),
                                            mb.stmt_replace_item_list(
                                                "Tablero",
                                                mb.op_add(
                                                    mb.op_mul(mb.op_sub("$v:f_origen", 1), 10),
                                                    "$v:c",
                                                ),
                                                "$v:celda_val",
                                            ),
                                            mb.stmt_change_var("c", 1),
                                        ],
                                    ),
                                    mb.stmt_change_var("f_origen", -1),
                                ],
                            ),
                            mb.stmt_set_var("c", 1),
                            mb.stmt_repeat(
                                10,
                                [
                                    mb.stmt_replace_item_list("Tablero", "$v:c", 0),
                                    mb.stmt_change_var("c", 1),
                                ],
                            ),
                        ],
                        [
                            mb.stmt_change_var("f", -1),
                        ],
                    ),
                ],
            ),
            mb.stmt_if(mb.op_gt("$v:Armor_Hit",0),[mb.stmt_play_sound("Sonido_Armor")]),
            mb.stmt_if_else(
                mb.op_gt("$v:Lineas_Turno", 0),
                [
                    mb.stmt_play_sound("Sonido_Linea"),
                    mb.stmt_broadcast("Animar_Linea"),
                    mb.stmt_change_var("Lineas", "$v:Lineas_Turno"),
                    mb.stmt_change_var("Combo", 1),
                    mb.stmt_if_else(
                        mb.op_eq("$v:Lineas_Turno", 1),
                        [mb.stmt_set_var("puntos_base", 100)],
                        [
                            mb.stmt_if_else(
                                mb.op_eq("$v:Lineas_Turno", 2),
                                [mb.stmt_set_var("puntos_base", 300)],
                                [
                                    mb.stmt_if_else(
                                        mb.op_eq("$v:Lineas_Turno", 3),
                                        [mb.stmt_set_var("puntos_base", 500)],
                                        [mb.stmt_set_var("puntos_base", 800)],
                                    )
                                ],
                            )
                        ],
                    ),
                    mb.stmt_change_var(
                        "Puntuacion",
                        mb.op_mul(
                            mb.op_mul("$v:puntos_base", "$v:Nivel"),
                            "$v:Multiplicador_Caos",
                        ),
                    ),
                    mb.stmt_if(
                        mb.op_gt("$v:Combo", 0),
                        [
                            mb.stmt_change_var(
                                "Puntuacion",
                                mb.op_mul(mb.op_mul(50, "$v:Combo"), "$v:Nivel"),
                            )
                        ],
                    ),
                ],
                [
                    mb.stmt_set_var("Combo", -1),
                ],
            ),
        ],
        x=560,
        y=1300,
    )

    # --- PROCEDIMIENTO 9: Fijar_Y_Procesar_Pieza ---
    proc_lock_code = "Fijar_Y_Procesar_Pieza"
    mb.define_proc(
        proc_lock_code,
        [],
        [],
        True,
        [
            mb.stmt_set_var("i", 1),
            mb.stmt_repeat(
                4,
                [
                    mb.stmt_set_var("tabla_idx", piece_idx_expr("$v:Pieza_Actual", "$v:Pieza_Rotacion")),
                    mb.stmt_set_var(
                        "bloque_col",
                        mb.op_add("$v:Pieza_Col", mb.expr_list_item("Offset_X", "$v:tabla_idx")),
                    ),
                    mb.stmt_set_var(
                        "bloque_fila",
                        mb.op_add("$v:Pieza_Fila", mb.expr_list_item("Offset_Y", "$v:tabla_idx")),
                    ),
                    mb.stmt_if(
                        mb.op_and(
                            mb.op_and(
                                mb.op_gt("$v:bloque_col", 0),
                                mb.op_lt("$v:bloque_col", 11),
                            ),
                            mb.op_and(
                                mb.op_gt("$v:bloque_fila", 0),
                                mb.op_lt("$v:bloque_fila", 21),
                            ),
                        ),
                        [
                            mb.stmt_replace_item_list(
                                "Tablero",
                                calc_board_idx(),
                                "$v:Pieza_Actual",
                            )
                        ],
                    ),
                    mb.stmt_change_var("i", 1),
                ],
            ),
            mb.stmt_call_proc(proc_lines_code, [], [], True),
            mb.stmt_if(
                mb.op_eq("$v:Estado_Juego", "JUGANDO"),
                [mb.stmt_call_proc(proc_spawn_code, [], [], True)],
            ),
            mb.stmt_if(mb.op_and(mb.op_eq("$v:Modo_Juego","NIGHTMARE"),mb.op_eq("$v:Estado_Juego","JUGANDO")),
                [mb.stmt_call_proc("Nightmare_OnLock", [], [], True),
                 mb.stmt_if(mb.op_and(mb.op_eq("$v:NM_Submode","TRIALS"),mb.op_eq("$v:Estado_Juego","JUGANDO")),[mb.stmt_call_proc("Trial_OnLock", [], [], True)]),
                 mb.stmt_if(mb.op_and(mb.op_and(mb.op_eq("$v:Estado_Juego","JUGANDO"),mb.op_and(mb.op_eq("$v:NM_Event","NONE"),mb.op_eq("$v:NM_Jam",0))),
                    mb.op_or(mb.op_and(mb.op_eq("$v:NM_Submode","ENDLESS"),mb.op_gt("$v:Tiempo_Juego","$v:G_Next")),
                        mb.op_and(mb.op_and(mb.op_eq("$v:NM_Submode","TRIALS"),mb.op_eq("$v:Trial_Wave",5)),mb.op_and(mb.op_gt("$v:Trial_Count",35),mb.op_eq("$v:Trial_GlitchDone",0))))),
                    [mb.stmt_call_proc("Glitch_Begin",[],[],True)])]),
            mb.stmt_call_proc(proc_render_code, [], [], True),
        ],
        x=1100,
        y=40,
    )

    # --- PROCEDIMIENTO 10: Mover_Horizontal (delta_col) ---
    proc_move_code = "Mover_Horizontal %s"
    proc_move_args = ["arg_delta_col"]
    mb.define_proc(
        proc_move_code,
        proc_move_args,
        ["delta_col"],
        True,
        [
            mb.stmt_if(
                mb.op_eq("$v:Estado_Juego", "JUGANDO"),
                [
                    mb.stmt_call_proc(
                        proc_col_code,
                        proc_col_args,
                        [
                            "$v:Pieza_Actual",
                            mb.op_add("$v:Pieza_Col", "$a:delta_col"),
                            "$v:Pieza_Fila",
                            "$v:Pieza_Rotacion",
                        ],
                        True,
                    ),
                    mb.stmt_if(
                        mb.op_eq("$v:Colision_Detectada", 0),
                        [
                            mb.stmt_change_var("Pieza_Col", "$a:delta_col"),
                            mb.stmt_play_sound("Sonido_Mover"),
                            mb.stmt_call_proc(proc_ghost_code, [], [], True),
                            mb.stmt_call_proc(proc_render_code, [], [], True),
                        ],
                    ),
                ],
            )
        ],
        x=1100,
        y=520,
    )

    # --- PROCEDIMIENTO 11: Rotar_Pieza (con Wall Kicks) ---
    proc_rot_code = "Rotar_Pieza"
    mb.define_proc(
        proc_rot_code,
        [],
        [],
        True,
        [
            mb.stmt_if(
                mb.op_eq("$v:Estado_Juego", "JUGANDO"),
                [
                    mb.stmt_set_var("test_rot", mb.op_mod(mb.op_add("$v:Pieza_Rotacion", 1), 4)),
                    mb.stmt_set_var("Rotacion_Exito", 0),
                    mb.stmt_set_var("k", 1),
                    mb.stmt_repeat(
                        6,
                        [
                            mb.stmt_if(
                                mb.op_eq("$v:Rotacion_Exito", 0),
                                [
                                    mb.stmt_set_var(
                                        "test_col",
                                        mb.op_add("$v:Pieza_Col", mb.expr_list_item("Kick_X", "$v:k")),
                                    ),
                                    mb.stmt_set_var(
                                        "test_fila",
                                        mb.op_add("$v:Pieza_Fila", mb.expr_list_item("Kick_Y", "$v:k")),
                                    ),
                                    mb.stmt_call_proc(
                                        proc_col_code,
                                        proc_col_args,
                                        ["$v:Pieza_Actual", "$v:test_col", "$v:test_fila", "$v:test_rot"],
                                        True,
                                    ),
                                    mb.stmt_if(
                                        mb.op_eq("$v:Colision_Detectada", 0),
                                        [
                                            mb.stmt_set_var("Pieza_Col", "$v:test_col"),
                                            mb.stmt_set_var("Pieza_Fila", "$v:test_fila"),
                                            mb.stmt_set_var("Pieza_Rotacion", "$v:test_rot"),
                                            mb.stmt_set_var("Rotacion_Exito", 1),
                                            mb.stmt_play_sound("Sonido_Rotar"),
                                            mb.stmt_call_proc(proc_ghost_code, [], [], True),
                                            mb.stmt_call_proc(proc_render_code, [], [], True),
                                        ],
                                    ),
                                ],
                            ),
                            mb.stmt_change_var("k", 1),
                        ],
                    ),
                ],
            )
        ],
        x=1100,
        y=860,
    )

    # --- PROCEDIMIENTO 12: Paso_Caida (es_suave) ---
    proc_step_code = "Paso_Caida %s"
    proc_step_args = ["arg_es_suave"]
    mb.define_proc(
        proc_step_code,
        proc_step_args,
        ["es_suave"],
        True,
        [
            mb.stmt_if(
                mb.op_eq("$v:Estado_Juego", "JUGANDO"),
                [
                    mb.stmt_call_proc(
                        proc_col_code,
                        proc_col_args,
                        [
                            "$v:Pieza_Actual",
                            "$v:Pieza_Col",
                            mb.op_add("$v:Pieza_Fila", 1),
                            "$v:Pieza_Rotacion",
                        ],
                        True,
                    ),
                    mb.stmt_if_else(
                        mb.op_eq("$v:Colision_Detectada", 0),
                        [
                            mb.stmt_change_var("Pieza_Fila", 1),
                            mb.stmt_if(
                                mb.op_eq("$a:es_suave", 1),
                                [mb.stmt_change_var("Puntuacion", "$v:Multiplicador_Caos")],
                            ),
                            mb.stmt_set_var("Reloj_Caida", "$v:Tiempo_Juego"),
                            mb.stmt_call_proc(proc_render_code, [], [], True),
                        ],
                        [
                            mb.stmt_if(mb.op_lt("$v:Bloqueo",0),[mb.stmt_set_var("Bloqueo","$v:Tiempo_Juego")]),
                        ],
                    ),
                ],
            )
        ],
        x=1100,
        y=1340,
    )

    # --- PROCEDIMIENTO 13: Caida_Instantanea (Hard Drop) ---
    proc_hard_code = "Caida_Instantanea"
    mb.define_proc(
        proc_hard_code,
        [],
        [],
        True,
        [
            mb.stmt_if(
                mb.op_eq("$v:Estado_Juego", "JUGANDO"),
                [
                    mb.stmt_change_var(
                        "Puntuacion",
                        mb.op_mul(
                            mb.op_mul(mb.op_sub("$v:Fila_Fantasma", "$v:Pieza_Fila"), 2),
                            "$v:Multiplicador_Caos",
                        ),
                    ),
                    mb.stmt_set_var("Pieza_Fila", "$v:Fila_Fantasma"),
                    mb.stmt_play_sound("Sonido_Caida"),
                    mb.stmt_call_proc(proc_lock_code, [], [], True),
                ],
            )
        ],
        x=1620,
        y=40,
    )

    # --- PROCEDIMIENTO 14: Guardar_Hold ---
    proc_hold_code = "Guardar_Hold"
    mb.define_proc(
        proc_hold_code,
        [],
        [],
        True,
        [
            mb.stmt_if(
                mb.op_and(
                    mb.op_eq("$v:Estado_Juego", "JUGANDO"),
                    mb.op_and(mb.op_eq("$v:Puede_Guardar", 1),mb.op_or(mb.op_not(mb.op_eq("$v:Modo_Juego","NIGHTMARE")),mb.op_eq("$v:NM_Jam",0))),
                ),
                [
                    mb.stmt_play_sound("Sonido_Hold"),
                    mb.stmt_if_else(
                        mb.op_eq("$v:Pieza_Guardada", 0),
                        [
                            mb.stmt_set_var("Pieza_Guardada", "$v:Pieza_Actual"),
                            mb.stmt_call_proc(proc_spawn_code, [], [], True),
                            mb.stmt_set_var("Puede_Guardar", 0),
                            mb.stmt_set_var("Bloqueo", -1),
                        ],
                        [
                            mb.stmt_set_var("temp_pieza", "$v:Pieza_Actual"),
                            mb.stmt_set_var("Pieza_Actual", "$v:Pieza_Guardada"),
                            mb.stmt_set_var("Pieza_Guardada", "$v:temp_pieza"),
                            mb.stmt_set_var("Pieza_Col", 5),
                            mb.stmt_set_var("Pieza_Fila", 2),
                            mb.stmt_set_var("Pieza_Rotacion", 0),
                            mb.stmt_set_var("Puede_Guardar", 0),
                            mb.stmt_set_var("Bloqueo", -1),
                            mb.stmt_call_proc(proc_ghost_code, [], [], True),
                        ],
                    ),
                    mb.stmt_call_proc(proc_col_code,proc_col_args,["$v:Pieza_Actual","$v:Pieza_Col","$v:Pieza_Fila","$v:Pieza_Rotacion"],True),
                    mb.stmt_if(mb.op_eq("$v:Colision_Detectada",1),[mb.stmt_set_var("Estado_Juego","GAMEOVER"),mb.stmt_play_sound("Sonido_GameOver"),mb.stmt_broadcast("Actualizar_UI")]),
                    mb.stmt_call_proc(proc_render_code, [], [], True),
                ],
            )
        ],
        x=1620,
        y=420,
    )

    # --- PROCEDIMIENTO 15: Iniciar_Partida ---
    proc_start_code = "Iniciar_Partida"
    mb.define_proc(
        proc_start_code,
        [],
        [],
        True,
        [
            mb.stmt_delete_all_list("Tablero"),
            mb.stmt_repeat(200, [mb.stmt_add_to_list("Tablero", 0)]),
            mb.stmt_delete_all_list("Bolsa_7"),
            mb.stmt_call_proc(proc_bolsa_code, [], [], True),
            mb.stmt_set_var("Puntuacion", 0),
            mb.stmt_set_var("Nivel", 1),
            mb.stmt_set_var("Lineas", 0),
            mb.stmt_set_var("Combo", -1),
            mb.stmt_set_var("Pieza_Guardada", 0),
            mb.stmt_set_var("Puede_Guardar", 1),
            mb.stmt_set_var("Evento_Caos", "NONE"),
            mb.stmt_set_var("Multiplicador_Caos", 1),
            mb.stmt_set_var("Tiempo_Juego", 0),
            mb.stmt_set_var("Ultimo_Tick", "$b:" + mb.expr_timer()),
            mb.stmt_set_var("Proximo_Evento", 12),
            mb.stmt_set_var("Proximo_Ataque", 25),
            mb.stmt_set_var("Evento_Fin", 0),
            mb.stmt_set_var("Eventos", 0),
            mb.stmt_set_var("Nightmare_Intro", 0),
            mb.stmt_set_var("Pausa_Origen", "JUGANDO"),
            mb.stmt_set_var("NM_Event", "NONE"),mb.stmt_set_var("NM_Warning", 0),
            mb.stmt_set_var("NM_Rows",0),mb.stmt_set_var("NM_Progress",0),
            mb.stmt_set_var("NM_Jam",0),mb.stmt_set_var("NM_Cooldown",0),mb.stmt_set_var("NM_Sequence",0),mb.stmt_set_var("NM_Cancelable",1),mb.stmt_set_var("NM_Chain",0),mb.stmt_set_var("NM_EventStart","NONE"),mb.stmt_set_var("NM_Delayed",0),mb.stmt_set_var("Armor_Hit",0),
            mb.stmt_set_var("Trial_Wave",1),mb.stmt_set_var("Trial_Count",0),mb.stmt_set_var("Trial_Event",0),mb.stmt_set_var("Trial_Goal",20),mb.stmt_set_var("Trial_Timer",0),mb.stmt_set_var("Trial_Required",1),mb.stmt_set_var("Trial_GlitchDone",0),mb.stmt_set_var("G_Next",60),
            mb.stmt_set_var("G_Timer",0),mb.stmt_set_var("G_Time",0),mb.stmt_set_var("G_Phase",0),mb.stmt_set_var("G_PrevPhase",-1),mb.stmt_set_var("G_Inner",0),
            mb.stmt_set_var("G_X",0),mb.stmt_set_var("G_Y",-45),mb.stmt_set_var("G_TargetX",0),mb.stmt_set_var("G_TargetY",0),mb.stmt_set_var("G_HP",3),
            mb.stmt_set_var("G_Invuln",0),mb.stmt_set_var("G_Hit",0),mb.stmt_set_var("G_Pos",0),mb.stmt_set_var("G_Success",0),mb.stmt_set_var("G_Active",0),mb.stmt_set_var("G_Radius",0),mb.stmt_set_var("G_SoundedPhase",-1),
            mb.stmt_set_var("Bloqueo", -1),
            mb.stmt_call_proc(proc_vel_code, [], [], True),
            mb.stmt_call_proc(proc_extraer_code, [], [], True),
            mb.stmt_if(mb.op_eq("$v:Evento_Caos","DIFFICULT PIECES"),[
                mb.stmt_if(mb.op_lt(mb.op_random(1,100),66),[mb.stmt_set_var("temp_pieza",mb.op_random(4,5))])]),
            mb.stmt_set_var("Siguiente_Pieza", "$v:temp_pieza"),
            mb.stmt_set_var("Estado_Juego", "JUGANDO"),
            mb.stmt_call_proc(proc_spawn_code, [], [], True),
            mb.stmt_broadcast("Actualizar_UI"),
            mb.stmt_call_proc(proc_render_code, [], [], True),
        ],
        x=1620,
        y=880,
    )

    # Un único hilo muta el estado: evita carreras entre teclado, gravedad y render.
    call = lambda code, args=[], vals=[]: mb.stmt_call_proc(code,args,vals,True)
    col_below = lambda: call(proc_col_code,proc_col_args,["$v:Pieza_Actual","$v:Pieza_Col",mb.op_add("$v:Pieza_Fila",1),"$v:Pieza_Rotacion"])
    mb.define_proc("Garbage_Attack",[],[],True,[
        mb.stmt_set_var("Hueco",mb.op_random(1,10)),
        mb.stmt_set_var("idx",1),
        mb.stmt_repeat(10,[mb.stmt_if(mb.op_gt(mb.expr_list_item("Tablero","$v:idx"),0),[mb.stmt_set_var("Estado_Juego","GAMEOVER")]),mb.stmt_change_var("idx",1)]),
        mb.stmt_repeat(190,[mb.stmt_replace_item_list("Tablero",mb.op_sub("$v:idx",10),mb.expr_list_item("Tablero","$v:idx")),mb.stmt_change_var("idx",1)]),
        mb.stmt_set_var("c",1),
        mb.stmt_repeat(10,[mb.stmt_replace_item_list("Tablero",mb.op_add(190,"$v:c"),8),mb.stmt_if(mb.op_eq("$v:c","$v:Hueco"),[mb.stmt_replace_item_list("Tablero",mb.op_add(190,"$v:c"),0)]),mb.stmt_change_var("c",1)]),
        call(proc_col_code,proc_col_args,["$v:Pieza_Actual","$v:Pieza_Col","$v:Pieza_Fila","$v:Pieza_Rotacion"]),
        mb.stmt_if(mb.op_eq("$v:Colision_Detectada",1),[
            mb.stmt_change_var("Pieza_Fila",-1),
            call(proc_col_code,proc_col_args,["$v:Pieza_Actual","$v:Pieza_Col","$v:Pieza_Fila","$v:Pieza_Rotacion"]) ]),
        mb.stmt_if(mb.op_eq("$v:Colision_Detectada",1),[mb.stmt_set_var("Estado_Juego","GAMEOVER")]),
        mb.stmt_set_var("Bloqueo",-1),call(proc_ghost_code),mb.stmt_broadcast("Actualizar_UI")])
    mb.define_proc("Nightmare_ArmorAttack",[],[],True,[
        call("Garbage_Attack"),
        mb.stmt_set_var("NM_Scan",191),
        mb.stmt_repeat(10,[
            mb.stmt_if(mb.op_eq(mb.expr_list_item("Tablero","$v:NM_Scan"),8),[
                mb.stmt_replace_item_list("Tablero","$v:NM_Scan",9)]),
            mb.stmt_change_var("NM_Scan",1)])])
    # Glitch Protocol: todos los peligros son secuenciales; el reloj del
    # tablero permanece congelado mientras se actualiza este estado.
    abs_g = lambda value: mb.op_math("abs",value)
    g_dist = lambda x,y: mb.op_add(mb.op_mul(x,x),mb.op_mul(y,y))
    g_stamp = lambda name,x,y: [mb.stmt_switch_costume(name),mb.stmt_goto_xy(x,y),mb.stmt_pen_stamp()]
    mb.define_proc("Glitch_Render",[],[],True,[
        mb.stmt_pen_clear(),mb.stmt_show(),mb.stmt_set_size(100),*g_stamp("G_ARENA",0,0),
        mb.stmt_if(mb.op_eq("$v:G_Phase",0),[
            mb.stmt_if_else(mb.op_eq("$v:G_Active",0),g_stamp("G_BEAM_WARN",0,0),g_stamp("G_BEAM_FIRE",0,0))]),
        mb.stmt_if(mb.op_eq("$v:G_Phase",1),[mb.stmt_if_else(mb.op_eq("$v:G_Active",0),g_stamp("G_TARGET","$v:G_TargetX","$v:G_TargetY"),g_stamp("G_TARGET_FIRE","$v:G_TargetX","$v:G_TargetY"))]),
        mb.stmt_if(mb.op_eq("$v:G_Phase",2),[mb.stmt_if_else(mb.op_eq("$v:G_Active",0),g_stamp("G_RING_WARN",0,0),
            [mb.stmt_set_size(mb.op_mul(mb.op_div("$v:G_Radius",30),100)),*g_stamp("G_RING",0,0),mb.stmt_set_size(100)])]),
        mb.stmt_if(mb.op_eq("$v:G_Phase",3),[mb.stmt_if_else(mb.op_eq("$v:G_Active",0),g_stamp("G_WALL_WARN","$v:G_Pos",0),g_stamp("G_WALL","$v:G_Pos",0))]),
        mb.stmt_if(mb.op_eq("$v:G_Phase",4),[mb.stmt_if_else(mb.op_eq("$v:G_Active",0),
            g_stamp("G_FRAGMENT","$v:G_Pos",25)+g_stamp("G_FRAGMENT",mb.op_sub(0,"$v:G_Pos"),-25),
            g_stamp("G_FRAGMENT_FIRE","$v:G_Pos",25)+g_stamp("G_FRAGMENT_FIRE",mb.op_sub(0,"$v:G_Pos"),-25))]),
        mb.stmt_if_else(mb.op_gt("$v:G_Invuln",0),g_stamp("G_CORE_HIT","$v:G_X","$v:G_Y"),g_stamp("G_CORE","$v:G_X","$v:G_Y")),
        *g_stamp("HUD_CORE HP",-160,0),
        mb.stmt_call_proc("Dibujar_Numero %s %s %s",["hud_n","hud_x","hud_y"],["$v:G_HP",-160,-25],True),
        *[mb.stmt_if(mb.op_eq("$v:G_Phase",i),g_stamp("HUD_"+name,160,0)) for i,name in enumerate(["SIGNAL BEAM","TARGET MARKER","PULSE RING","SWEEP WALL","DATA FRAGMENTS"])],
        mb.stmt_if_else(mb.op_eq("$v:G_Active",0),g_stamp("HUD_CHARGE",160,-25),g_stamp("HUD_ACTIVE",160,-25)),
        mb.stmt_hide()])
    mb.define_proc("Glitch_Begin",[],[],True,[
        mb.stmt_set_var("Estado_Juego","GLITCH_INTRO"),mb.stmt_set_var("G_Timer",0),mb.stmt_set_var("G_Time",0),
        mb.stmt_set_var("G_Phase",0),mb.stmt_set_var("G_PrevPhase",-1),mb.stmt_set_var("G_X",0),mb.stmt_set_var("G_Y",-45),
        mb.stmt_set_var("G_HP",3),mb.stmt_set_var("G_Invuln",0),mb.stmt_set_var("G_Active",0),mb.stmt_set_var("G_SoundedPhase",-1),mb.stmt_set_var("G_Next",mb.op_add("$v:Tiempo_Juego",45)),
        mb.stmt_play_sound("Sonido_NMWarning"),mb.stmt_broadcast("Actualizar_UI")])
    mb.define_proc("Glitch_Advance",[],[],True,[
        mb.stmt_change_var("G_Time","$v:Delta"),
        mb.stmt_if(mb.op_gt("$v:G_Invuln",0),[mb.stmt_change_var("G_Invuln",mb.op_sub(0,"$v:Delta"))]),
        mb.stmt_if_else(mb.op_lt("$v:G_Time",5),[
            mb.stmt_set_var("G_Phase",mb.op_math("floor","$v:G_Time")),
            mb.stmt_set_var("G_Inner",mb.op_sub("$v:G_Time","$v:G_Phase")),
            mb.stmt_if(mb.op_not(mb.op_eq("$v:G_Phase","$v:G_PrevPhase")),[
                mb.stmt_set_var("G_PrevPhase","$v:G_Phase"),
                mb.stmt_if(mb.op_eq("$v:G_Phase",1),[mb.stmt_set_var("G_TargetX","$v:G_X"),mb.stmt_set_var("G_TargetY","$v:G_Y")])]),
            mb.stmt_set_var("G_Active",0),mb.stmt_set_var("G_Hit",0),mb.stmt_set_var("G_Pos",-55),
            mb.stmt_if(mb.op_gt("$v:G_Inner",0.6),[
                mb.stmt_set_var("G_Active",1),mb.stmt_set_var("G_Pos",mb.op_add(-55,mb.op_mul(mb.op_sub("$v:G_Inner",0.6),275))),
                mb.stmt_if(mb.op_not(mb.op_eq("$v:G_SoundedPhase","$v:G_Phase")),[
                    mb.stmt_set_var("G_SoundedPhase","$v:G_Phase"),mb.stmt_play_sound("Sonido_GlitchFire")]),
                mb.stmt_set_var("G_Radius",mb.op_mul(mb.op_sub("$v:G_Inner",0.6),75)),
                mb.stmt_if(mb.op_and(mb.op_eq("$v:G_Phase",0),mb.op_lt(abs_g("$v:G_Y"),6)),[mb.stmt_set_var("G_Hit",1)]),
                mb.stmt_if(mb.op_and(mb.op_eq("$v:G_Phase",1),mb.op_and(mb.op_lt(abs_g(mb.op_sub("$v:G_X","$v:G_TargetX")),15),mb.op_lt(abs_g(mb.op_sub("$v:G_Y","$v:G_TargetY")),15))),[mb.stmt_set_var("G_Hit",1)]),
                mb.stmt_if(mb.op_and(mb.op_eq("$v:G_Phase",2),mb.op_lt(g_dist("$v:G_X","$v:G_Y"),mb.op_mul("$v:G_Radius","$v:G_Radius"))),[mb.stmt_set_var("G_Hit",1)]),
                mb.stmt_if(mb.op_and(mb.op_eq("$v:G_Phase",3),mb.op_and(mb.op_lt(abs_g(mb.op_sub("$v:G_X","$v:G_Pos")),15),mb.op_gt(abs_g("$v:G_Y"),17))),[mb.stmt_set_var("G_Hit",1)]),
                mb.stmt_if(mb.op_and(mb.op_eq("$v:G_Phase",4),mb.op_or(
                    mb.op_and(mb.op_lt(abs_g(mb.op_sub("$v:G_X","$v:G_Pos")),15),mb.op_lt(abs_g(mb.op_sub("$v:G_Y",25)),15)),
                    mb.op_and(mb.op_lt(abs_g(mb.op_add("$v:G_X","$v:G_Pos")),15),mb.op_lt(abs_g(mb.op_add("$v:G_Y",25)),15)))),[mb.stmt_set_var("G_Hit",1)])]),
            mb.stmt_if(mb.op_and(mb.op_eq("$v:G_Hit",1),mb.op_lt("$v:G_Invuln",0.001)),[
                mb.stmt_change_var("G_HP",-1),mb.stmt_set_var("G_Invuln",0.45),mb.stmt_play_sound("Sonido_GlitchHit")]),
            mb.stmt_if_else(mb.op_lt("$v:G_HP",1),[
                mb.stmt_set_var("G_Success",0),mb.stmt_set_var("Estado_Juego","GLITCH_RESULT"),mb.stmt_set_var("G_Timer",0),mb.stmt_set_var("Delta",0),mb.stmt_broadcast("Actualizar_UI")],
                [call("Glitch_Render")])],
            [mb.stmt_set_var("G_Success",1),mb.stmt_set_var("Estado_Juego","GLITCH_RESULT"),mb.stmt_set_var("G_Timer",0),mb.stmt_set_var("Delta",0),mb.stmt_broadcast("Actualizar_UI")])])
    # Un solo evento comprometido. Las cuentas avanzan únicamente al fijar pieza.
    mb.define_proc("Nightmare_OnLock",[],[],True,[
        mb.stmt_set_var("NM_EventStart","$v:NM_Event"),
        mb.stmt_if(mb.op_gt("$v:NM_Jam",0),[mb.stmt_change_var("NM_Jam",-1)]),
        mb.stmt_if_else(mb.op_eq("$v:NM_Event","NONE"),[
            mb.stmt_if(mb.op_and(mb.op_eq("$v:NM_Jam",0),mb.op_eq("$v:NM_Submode","ENDLESS")),[
                mb.stmt_change_var("NM_Cooldown",1),
                mb.stmt_set_var("NM_Top",0),mb.stmt_set_var("NM_Scan",1),
                mb.stmt_repeat(40,[mb.stmt_if(mb.op_gt(mb.expr_list_item("Tablero","$v:NM_Scan"),0),[mb.stmt_change_var("NM_Top",1)]),mb.stmt_change_var("NM_Scan",1)]),
                mb.stmt_if(mb.op_and(mb.op_and(mb.op_gt("$v:NM_Cooldown",5),mb.op_gt("$v:Tiempo_Juego",20)),mb.op_gt("$v:NM_Top",7)),[mb.stmt_set_var("NM_Delayed",1)]),
                mb.stmt_if(mb.op_and(mb.op_and(mb.op_gt("$v:NM_Cooldown",5),mb.op_gt("$v:Tiempo_Juego",20)),mb.op_lt("$v:NM_Top",8)),[
                    mb.stmt_set_var("NM_Delayed",0),
                    mb.stmt_set_var("NM_Cooldown",0),
                    mb.stmt_if_else(mb.op_eq(mb.op_mod("$v:NM_Sequence",3),0),[
                        mb.stmt_set_var("NM_Event","DOUBLE"),mb.stmt_set_var("NM_Warning",4),
                        mb.stmt_set_var("NM_Rows",2),mb.stmt_set_var("NM_Progress",0),mb.stmt_set_var("NM_Cancelable",1)],
                        [mb.stmt_if_else(mb.op_and(mb.op_eq(mb.op_mod("$v:NM_Sequence",3),2),mb.op_gt("$v:Tiempo_Juego",60)),[
                            mb.stmt_set_var("NM_Event","DEBT"),mb.stmt_set_var("NM_Warning",12),
                            mb.stmt_set_var("NM_Rows",2),mb.stmt_set_var("NM_Progress",0)],
                            [mb.stmt_set_var("NM_Event","JAM_WARNING"),mb.stmt_set_var("NM_Warning",2)])]),
                    mb.stmt_if(mb.op_and(mb.op_gt("$v:Tiempo_Juego",120),mb.op_eq(mb.op_mod("$v:NM_Sequence",4),3)),[
                        mb.stmt_if_else(mb.op_eq(mb.op_mod("$v:NM_Sequence",8),3),[
                            mb.stmt_set_var("NM_Chain",1),mb.stmt_set_var("NM_Event","DOUBLE"),
                            mb.stmt_set_var("NM_Warning",4),mb.stmt_set_var("NM_Rows",2),mb.stmt_set_var("NM_Progress",0),mb.stmt_set_var("NM_Cancelable",1)],
                            [mb.stmt_set_var("NM_Chain",2),mb.stmt_set_var("NM_Event","JAM_WARNING"),mb.stmt_set_var("NM_Warning",2)])]),
                    mb.stmt_if(mb.op_and(mb.op_gt("$v:Tiempo_Juego",180),mb.op_eq(mb.op_mod("$v:NM_Sequence",4),2)),[
                        mb.stmt_set_var("NM_Event","ARMOR_WARNING"),mb.stmt_set_var("NM_Warning",4)]),
                    mb.stmt_change_var("NM_Sequence",1),mb.stmt_play_sound("Sonido_NMWarning")])])],
            [mb.stmt_if(mb.op_eq("$v:NM_EventStart","DOUBLE"),[
                mb.stmt_if(mb.op_eq("$v:NM_Cancelable",1),[
                    mb.stmt_change_var("NM_Progress","$v:Lineas_Turno"),
                    mb.stmt_repeat(2,[mb.stmt_if(mb.op_and(mb.op_gt("$v:NM_Progress",1),mb.op_gt("$v:NM_Rows",0)),[
                        mb.stmt_change_var("NM_Progress",-2),mb.stmt_change_var("NM_Rows",-1)])])]),
                mb.stmt_change_var("NM_Warning",-1),
                mb.stmt_if(mb.op_eq("$v:NM_Warning",0),[
                    mb.stmt_repeat("$v:NM_Rows",[mb.stmt_if(mb.op_eq("$v:Estado_Juego","JUGANDO"),[call("Garbage_Attack")])]),
                    mb.stmt_set_var("NM_Rows",0),mb.stmt_set_var("NM_Event","NONE"),
                    mb.stmt_if(mb.op_and(mb.op_eq("$v:NM_Chain",1),mb.op_eq("$v:Estado_Juego","JUGANDO")),[
                        mb.stmt_set_var("NM_Event","CHAIN_JAM"),mb.stmt_set_var("NM_Warning",2)])])]),
             mb.stmt_if(mb.op_eq("$v:NM_EventStart","JAM_WARNING"),[
                mb.stmt_change_var("NM_Warning",-1),
                mb.stmt_if(mb.op_eq("$v:NM_Warning",0),[
                    mb.stmt_set_var("NM_Jam",7),mb.stmt_set_var("NM_Event","NONE"),
                    mb.stmt_if(mb.op_eq("$v:NM_Chain",2),[
                        mb.stmt_set_var("NM_Event","CHAIN_DEBT"),mb.stmt_set_var("NM_Warning",2)])])]),
             mb.stmt_if(mb.op_eq("$v:NM_EventStart","CHAIN_JAM"),[
                mb.stmt_change_var("NM_Warning",-1),
                mb.stmt_if(mb.op_eq("$v:NM_Warning",0),[
                    mb.stmt_set_var("NM_Jam",7),mb.stmt_set_var("NM_Event","NONE"),mb.stmt_set_var("NM_Chain",0)])]),
             mb.stmt_if(mb.op_eq("$v:NM_EventStart","CHAIN_DEBT"),[
                mb.stmt_change_var("NM_Warning",-1),
                mb.stmt_if(mb.op_eq("$v:NM_Warning",0),[
                    mb.stmt_set_var("NM_Event","DEBT"),mb.stmt_set_var("NM_Warning",12),mb.stmt_set_var("NM_Rows",2),
                    mb.stmt_set_var("NM_Progress",0),mb.stmt_set_var("NM_Chain",0)])]),
             mb.stmt_if(mb.op_eq("$v:NM_EventStart","ARMOR_WARNING"),[
                mb.stmt_change_var("NM_Warning",-1),
                mb.stmt_if(mb.op_eq("$v:NM_Warning",0),[
                    call("Nightmare_ArmorAttack"),mb.stmt_set_var("NM_Event","NONE")])]),
             mb.stmt_if(mb.op_eq("$v:NM_EventStart","DEBT"),[
                mb.stmt_change_var("NM_Progress","$v:Lineas_Turno"),
                mb.stmt_repeat(2,[mb.stmt_if(mb.op_and(mb.op_gt("$v:NM_Progress",1),mb.op_gt("$v:NM_Rows",0)),[
                    mb.stmt_change_var("NM_Progress",-2),mb.stmt_change_var("NM_Rows",-1)])]),
                mb.stmt_change_var("NM_Warning",-1),
                mb.stmt_if_else(mb.op_eq("$v:NM_Rows",0),[mb.stmt_set_var("NM_Event","NONE")],
                    [mb.stmt_if(mb.op_eq("$v:NM_Warning",0),[
                        mb.stmt_set_var("NM_Event","DOUBLE"),mb.stmt_set_var("NM_Warning",2),mb.stmt_set_var("NM_Progress",0),mb.stmt_set_var("NM_Cancelable",0)])])])])])
    # Guion por fijaciones. Un hito espera si otra amenaza sigue activa.
    def trial_trigger(wave, index, threshold, actions):
        return mb.stmt_if(mb.op_and(
            mb.op_and(mb.op_eq("$v:Trial_Wave",wave),mb.op_eq("$v:Trial_Event",index)),
            mb.op_and(mb.op_gt("$v:Trial_Count",threshold-1),
                mb.op_and(mb.op_eq("$v:NM_Event","NONE"),mb.op_eq("$v:NM_Jam",0)))),
            actions+[mb.stmt_change_var("Trial_Event",1),mb.stmt_play_sound("Sonido_NMWarning")])
    def trial_double():
        return [mb.stmt_set_var("NM_Event","DOUBLE"),mb.stmt_set_var("NM_Warning",4),mb.stmt_set_var("NM_Rows",2),mb.stmt_set_var("NM_Progress",0),mb.stmt_set_var("NM_Cancelable",1)]
    def trial_jam():
        return [mb.stmt_set_var("NM_Event","JAM_WARNING"),mb.stmt_set_var("NM_Warning",2)]
    def trial_debt():
        return [mb.stmt_set_var("NM_Event","DEBT"),mb.stmt_set_var("NM_Warning",12),mb.stmt_set_var("NM_Rows",2),mb.stmt_set_var("NM_Progress",0)]
    def trial_chain(kind):
        return [mb.stmt_set_var("NM_Chain",kind)] + (trial_double() if kind == 1 else trial_jam())
    trial_script = [(1,0,10,trial_double),(2,0,6,trial_jam),(2,1,18,trial_jam),
                    (3,0,6,trial_debt),(3,1,18,trial_debt),
                    (4,0,6,lambda:[mb.stmt_set_var("NM_Event","ARMOR_WARNING"),mb.stmt_set_var("NM_Warning",4)]),
                    (4,1,17,lambda:trial_chain(1)),(4,2,28,lambda:trial_chain(2)),
                    (5,0,7,trial_double),(5,1,19,lambda:trial_chain(2)),(5,2,30,lambda:trial_chain(1))]
    mb.define_proc("Trial_OnLock",[],[],True,[
        mb.stmt_change_var("Trial_Count",1),
        *[trial_trigger(wave,index,threshold,make()) for wave,index,threshold,make in trial_script],
        mb.stmt_if(mb.op_and(mb.op_and(mb.op_and(mb.op_gt("$v:Trial_Count",mb.op_sub("$v:Trial_Goal",1)),
            mb.op_eq("$v:Trial_Event","$v:Trial_Required")),
            mb.op_and(mb.op_eq("$v:NM_Event","NONE"),mb.op_eq("$v:NM_Jam",0))),
            mb.op_or(mb.op_not(mb.op_eq("$v:Trial_Wave",5)),mb.op_eq("$v:Trial_GlitchDone",1))),[
            mb.stmt_if_else(mb.op_eq("$v:Trial_Wave",5),[
                mb.stmt_set_var("Estado_Juego","TRIAL_CLEAR"),mb.stmt_broadcast("Actualizar_UI")],
                [mb.stmt_set_var("Estado_Juego","TRIAL_INTERMISSION"),mb.stmt_set_var("Trial_Timer",0),mb.stmt_broadcast("Actualizar_UI")])])])
    mb.define_proc("Glitch_Move %s %s",["gm_x","gm_y"],["dx","dy"],True,[
        mb.stmt_if(mb.op_eq("$v:Estado_Juego","GLITCH_PLAY"),[
            mb.stmt_change_var("G_X","$a:dx"),mb.stmt_change_var("G_Y","$a:dy"),
            mb.stmt_if(mb.op_gt("$v:G_X",55),[mb.stmt_set_var("G_X",55)]),mb.stmt_if(mb.op_lt("$v:G_X",-55),[mb.stmt_set_var("G_X",-55)]),
            mb.stmt_if(mb.op_gt("$v:G_Y",55),[mb.stmt_set_var("G_Y",55)]),mb.stmt_if(mb.op_lt("$v:G_Y",-55),[mb.stmt_set_var("G_Y",-55)]),
            call("Glitch_Render")])])
    mb.define_proc("Alternar_Pausa",[],[],True,[
        mb.stmt_if_else(mb.op_or(mb.op_or(mb.op_eq("$v:Estado_Juego","JUGANDO"),mb.op_eq("$v:Estado_Juego","NIGHTMARE_INTRO")),
            mb.op_or(mb.op_eq("$v:Estado_Juego","TRIAL_INTERMISSION"),mb.op_or(mb.op_eq("$v:Estado_Juego","GLITCH_INTRO"),mb.op_or(mb.op_eq("$v:Estado_Juego","GLITCH_PLAY"),mb.op_eq("$v:Estado_Juego","GLITCH_RESULT"))))),
            [mb.stmt_set_var("Pausa_Origen","$v:Estado_Juego"),mb.stmt_set_var("Estado_Juego","PAUSA")],
            [mb.stmt_if(mb.op_eq("$v:Estado_Juego","PAUSA"),[mb.stmt_set_var("Estado_Juego","$v:Pausa_Origen")])]),
        mb.stmt_set_var("Ultimo_Tick","$b:"+mb.expr_timer()),mb.stmt_broadcast("Actualizar_UI")])
    mb.define_proc("Comenzar_Modo",[],[],True,[
        call(proc_start_code),
        mb.stmt_if(mb.op_eq("$v:Modo_Juego","NIGHTMARE"),[
            mb.stmt_set_var("Estado_Juego","NIGHTMARE_INTRO"),mb.stmt_set_var("Nightmare_Intro",0),mb.stmt_broadcast("Actualizar_UI")])])
    key_actions = {
        "left": ("left arrow",lambda:[mb.stmt_if_else(mb.op_eq("$v:Estado_Juego","GLITCH_PLAY"),[call("Glitch_Move %s %s",["gm_x","gm_y"],[-6,0])],[call(proc_move_code,proc_move_args,[-1])])],True),
        "right": ("right arrow",lambda:[mb.stmt_if_else(mb.op_eq("$v:Estado_Juego","GLITCH_PLAY"),[call("Glitch_Move %s %s",["gm_x","gm_y"],[6,0])],[call(proc_move_code,proc_move_args,[1])])],True),
        "down": ("down arrow",lambda:[mb.stmt_if_else(mb.op_eq("$v:Estado_Juego","GLITCH_PLAY"),[mb.stmt_if(mb.op_not(mb.op_or(mb.expr_key_pressed("left arrow"),mb.expr_key_pressed("right arrow"))),[call("Glitch_Move %s %s",["gm_x","gm_y"],[0,-6])])],[call(proc_step_code,proc_step_args,[1])])],True),
        "up": ("up arrow",lambda:[mb.stmt_if_else(mb.op_eq("$v:Estado_Juego","GLITCH_PLAY"),[mb.stmt_if(mb.op_not(mb.op_or(mb.expr_key_pressed("left arrow"),mb.expr_key_pressed("right arrow"))),[call("Glitch_Move %s %s",["gm_x","gm_y"],[0,6])])],[call(proc_rot_code)])],True),
        "space": ("space",lambda:[call(proc_hard_code)],False),
        "c": ("c",lambda:[call(proc_hold_code)],False),
        "p": ("p",lambda:[call("Alternar_Pausa")],False),
        "m": ("m",lambda:[mb.stmt_if(mb.op_eq("$v:Modo_Juego","NIGHTMARE"),[
            mb.stmt_if_else(mb.op_eq("$v:NM_Reduced",0),[mb.stmt_set_var("NM_Reduced",1)],[mb.stmt_set_var("NM_Reduced",0)]),
            mb.stmt_if(mb.op_eq("$v:Estado_Juego","JUGANDO"),[call(proc_render_code)])])],False),
        "r": ("r",lambda:[call("Comenzar_Modo")],False),
        "enter": ("enter",lambda:[mb.stmt_if(mb.op_or(mb.op_or(mb.op_eq("$v:Estado_Juego","MENU"),mb.op_eq("$v:Estado_Juego","GAMEOVER")),mb.op_eq("$v:Estado_Juego","TRIAL_CLEAR")),[call("Comenzar_Modo")])],False)}
    for key,mode in [("1","NORMAL"),("2","HARD"),("3","CHAOS")]:
        key_actions[key]=(key,lambda mode=mode:[mb.stmt_if(mb.op_not(mb.op_eq("$v:Estado_Juego","JUGANDO")),[mb.stmt_set_var("Modo_Juego",mode),call(proc_start_code),mb.stmt_set_var("Estado_Juego","MENU"),call(proc_render_code),mb.stmt_broadcast("Actualizar_UI")])],False)
    key_actions["4"]=("4",lambda:[mb.stmt_if(mb.op_not(mb.op_eq("$v:Estado_Juego","JUGANDO")),[
        mb.stmt_if_else(mb.op_and(mb.op_eq("$v:Modo_Juego","NIGHTMARE"),mb.op_eq("$v:Estado_Juego","MENU")),[
            mb.stmt_if_else(mb.op_eq("$v:NM_Submode","ENDLESS"),[mb.stmt_set_var("NM_Submode","TRIALS")],[mb.stmt_set_var("NM_Submode","ENDLESS")])],
            [mb.stmt_set_var("NM_Submode","ENDLESS")]),
        mb.stmt_set_var("Modo_Juego","NIGHTMARE"),call(proc_start_code),mb.stmt_set_var("Estado_Juego","MENU"),call(proc_render_code),mb.stmt_broadcast("Actualizar_UI")])],False)
    inputs=[]
    for key,(scratch_key,actions,repeats) in key_actions.items():
        repeat_actions = actions()+[mb.stmt_set_var("repeat_"+key,mb.op_add("$b:"+mb.expr_timer(),0.05))] if repeats else []
        if key == "up":
            repeat_actions = [mb.stmt_if(mb.op_eq("$v:Estado_Juego","GLITCH_PLAY"),repeat_actions)]
        body=[mb.stmt_if_else(mb.op_eq("$v:key_"+key,0),actions()+[mb.stmt_set_var("repeat_"+key,mb.op_add("$b:"+mb.expr_timer(),0.16 if key!="down" else 0.05))],
            [mb.stmt_if(mb.op_gt("$b:"+mb.expr_timer(),"$v:repeat_"+key),repeat_actions)] if repeats else []),mb.stmt_set_var("key_"+key,1)]
        inputs.append(mb.stmt_if_else(mb.expr_key_pressed(scratch_key),body,[mb.stmt_set_var("key_"+key,0)]))
    mb.define_proc("Leer_Teclado",[],[],True,inputs)
    mb.define_proc("Tick",[],[],True,[
        mb.stmt_set_var("Delta",mb.op_sub("$b:"+mb.expr_timer(),"$v:Ultimo_Tick")),
        mb.stmt_set_var("Ultimo_Tick","$b:"+mb.expr_timer()),
        mb.stmt_if(mb.op_gt("$v:Delta",0.1),[mb.stmt_set_var("Delta",0.1)]),
        mb.stmt_if(mb.op_eq("$v:Estado_Juego","NIGHTMARE_INTRO"),[
            mb.stmt_change_var("Nightmare_Intro","$v:Delta"),
            mb.stmt_if(mb.op_gt("$v:Nightmare_Intro",0.8),[
                mb.stmt_set_var("Estado_Juego","NIGHTMARE_READY"),mb.stmt_broadcast("Actualizar_UI")])]),
        mb.stmt_if(mb.op_eq("$v:Estado_Juego","NIGHTMARE_READY"),[
            mb.stmt_set_var("Estado_Juego","JUGANDO"),mb.stmt_set_var("Delta",0)]),
        mb.stmt_if(mb.op_eq("$v:Estado_Juego","TRIAL_INTERMISSION"),[
            mb.stmt_change_var("Trial_Timer","$v:Delta"),
            mb.stmt_if(mb.op_gt("$v:Trial_Timer",3),[
                mb.stmt_change_var("Trial_Wave",1),mb.stmt_set_var("Trial_Count",0),mb.stmt_set_var("Trial_Event",0),
                mb.stmt_set_var("Trial_Goal",mb.op_add(15,mb.op_mul(5,"$v:Trial_Wave"))),mb.stmt_set_var("Trial_Required",2),
                mb.stmt_if(mb.op_gt("$v:Trial_Wave",3),[mb.stmt_set_var("Trial_Required",3)]),
                mb.stmt_set_var("Estado_Juego","JUGANDO"),mb.stmt_set_var("Delta",0),mb.stmt_broadcast("Actualizar_UI")])]),
        mb.stmt_if(mb.op_eq("$v:Estado_Juego","GLITCH_INTRO"),[
            mb.stmt_change_var("G_Timer","$v:Delta"),
            mb.stmt_if(mb.op_gt("$v:G_Timer",0.8),[
                mb.stmt_set_var("Estado_Juego","GLITCH_PLAY"),mb.stmt_set_var("Delta",0),call("Glitch_Render"),mb.stmt_broadcast("Actualizar_UI")])]),
        mb.stmt_if(mb.op_eq("$v:Estado_Juego","GLITCH_PLAY"),[call("Glitch_Advance")]),
        mb.stmt_if(mb.op_eq("$v:Estado_Juego","GLITCH_RESULT"),[
            mb.stmt_change_var("G_Timer","$v:Delta"),
            mb.stmt_if(mb.op_gt("$v:G_Timer",0.65),[
                mb.stmt_if_else(mb.op_eq("$v:G_Success",1),[mb.stmt_change_var("Puntuacion",100),mb.stmt_play_sound("Sonido_GlitchWin")],
                    [mb.stmt_set_var("NM_Event","DOUBLE"),mb.stmt_set_var("NM_Warning",2),mb.stmt_set_var("NM_Rows",2),mb.stmt_set_var("NM_Progress",0),mb.stmt_set_var("NM_Cancelable",0)]),
                mb.stmt_if(mb.op_and(mb.op_eq("$v:NM_Submode","TRIALS"),mb.op_eq("$v:Trial_Wave",5)),[mb.stmt_set_var("Trial_GlitchDone",1)]),
                mb.stmt_set_var("repeat_left",mb.op_add("$b:"+mb.expr_timer(),0.16)),mb.stmt_set_var("repeat_right",mb.op_add("$b:"+mb.expr_timer(),0.16)),mb.stmt_set_var("repeat_down",mb.op_add("$b:"+mb.expr_timer(),0.16)),
                mb.stmt_set_var("Estado_Juego","JUGANDO"),mb.stmt_set_var("Delta",0),mb.stmt_broadcast("Actualizar_UI"),call(proc_render_code)])]),
        mb.stmt_if(mb.op_eq("$v:Estado_Juego","JUGANDO"),[
            mb.stmt_change_var("Tiempo_Juego","$v:Delta"),
            mb.stmt_if(mb.op_eq("$v:Modo_Juego","CHAOS"),[
                mb.stmt_set_var("Intervalo_Ataque",mb.op_sub(25,mb.op_div("$v:Tiempo_Juego",30))),
                mb.stmt_if(mb.op_lt("$v:Intervalo_Ataque",10),[mb.stmt_set_var("Intervalo_Ataque",10)]),
                mb.stmt_if(mb.op_gt("$v:Tiempo_Juego","$v:Evento_Fin"),[mb.stmt_set_var("Evento_Caos","NONE")]),
                mb.stmt_if(mb.op_gt("$v:Tiempo_Juego","$v:Proximo_Evento"),[
                    mb.stmt_change_var("Eventos",1),mb.stmt_set_var("Evento_Caos","DIFFICULT PIECES"),
                    mb.stmt_if(mb.op_eq(mb.op_mod("$v:Eventos",2),0),[mb.stmt_set_var("Evento_Caos","SPEED BURST")]),
                    mb.stmt_set_var("Evento_Fin",mb.op_add("$v:Tiempo_Juego",7)),
                    mb.stmt_set_var("Proximo_Evento",mb.op_add("$v:Tiempo_Juego",mb.op_mul("$v:Intervalo_Ataque",0.6))),mb.stmt_play_sound("Sonido_Caos")]),
                mb.stmt_if(mb.op_gt("$v:Tiempo_Juego",mb.op_sub("$v:Proximo_Ataque",2)),[mb.stmt_set_var("Evento_Caos","GARBAGE INCOMING")]),
                mb.stmt_if(mb.op_gt("$v:Tiempo_Juego","$v:Proximo_Ataque"),[call("Garbage_Attack"),mb.stmt_set_var("Proximo_Ataque",mb.op_add("$v:Tiempo_Juego","$v:Intervalo_Ataque")),mb.stmt_set_var("Evento_Caos","NONE")])]),
            call(proc_vel_code),
            mb.stmt_if(mb.op_gt(mb.op_sub("$v:Tiempo_Juego","$v:Reloj_Caida"),"$v:Velocidad_Caida"),[call(proc_step_code,proc_step_args,[0]),mb.stmt_set_var("Reloj_Caida","$v:Tiempo_Juego")]),
            col_below(),mb.stmt_if_else(mb.op_eq("$v:Colision_Detectada",1),[
                mb.stmt_if(mb.op_lt("$v:Bloqueo",0),[mb.stmt_set_var("Bloqueo","$v:Tiempo_Juego")]),
                mb.stmt_if(mb.op_gt(mb.op_sub("$v:Tiempo_Juego","$v:Bloqueo"),0.35),[mb.stmt_play_sound("Sonido_Caida"),call(proc_lock_code)])],[mb.stmt_set_var("Bloqueo",-1)]),
            call(proc_render_code)])])
    mb.hat_green_flag([mb.stmt_hide(),mb.stmt_pen_clear(),mb.stmt_set_var("Estado_Juego","MENU"),mb.stmt_set_var("Modo_Juego","NORMAL"),mb.stmt_set_var("NM_Submode","ENDLESS"),call(proc_start_code),mb.stmt_set_var("Estado_Juego","MENU"),mb.stmt_broadcast("Actualizar_UI"),call(proc_render_code),mb.stmt_forever([call("Tick"),call("Leer_Teclado"),mb.stmt_wait(0.01)])])
    mb.hat_broadcast("Iniciar_Juego",[call(proc_start_code)])
    mb.hat_broadcast("Alternar_Pausa",[call("Alternar_Pausa")])

    mb.add_comment(
        None,
        "MOTOR_JUEGO: Arquitectura modular en bloques personalizados ('Sin actualizar la pantalla'):\n- Rellenar_Bolsa_7 / Extraer_De_Bolsa (7-Bag)\n- Comprobar_Colision (Paredes + Bloques)\n- Rotar_Pieza (con 6 pruebas Wall Kick)\n- Actualizar_Fantasma (Pieza guía)\n- Revisar_Y_Eliminar_Lineas (1 a 4 líneas + Combo)\n- Renderizar_Todo (Extensión Lápiz libre de límites de clones)",
        x=40,
        y=1820,
    )

    motor_target = {
        "isStage": False,
        "name": "Motor_Juego",
        "variables": {},
        "lists": {},
        "broadcasts": {},
        "blocks": mb.blocks,
        "comments": mb.comments,
        "currentCostume": 0,
        "costumes": motor_costumes,
        "sounds": motor_sounds,
        "volume": 100,
        "layerOrder": 1,
        "visible": False,
        "x": 0,
        "y": 0,
        "size": 100,
        "direction": 90,
        "draggable": False,
        "rotationStyle": "all around",
    }

    # --------------------------------------------------------------------------
    # TARGET 2: EFECTO_LINEA (ANIMACIÓN NO BLOQUEANTE AL COMPLETAR 1-4 LÍNEAS)
    # --------------------------------------------------------------------------
    fx_1 = register_svg_asset("Linea_1", make_line_fx_svg("SINGLE", "#00F0FF"), 74, 17)
    fx_2 = register_svg_asset("Linea_2", make_line_fx_svg("DOUBLE", "#00FF66"), 74, 17)
    fx_3 = register_svg_asset("Linea_3", make_line_fx_svg("TRIPLE", "#FFE600"), 74, 17)
    fx_4 = register_svg_asset("Linea_4", make_line_fx_svg("NEXUS x4", "#FF2A85"), 74, 17)
    for fx_a in (fx_1, fx_2, fx_3, fx_4):
        all_zip_files[fx_a["md5ext"]] = fx_a["bytes"]

    fxb = ScratchBlockBuilder("fxl", var_map, list_map, bcast_specs)
    fxb.hat_green_flag([fxb.stmt_hide(), fxb.stmt_goto_xy(0, 95)], x=40, y=40)
    fxb.hat_broadcast(
        "Animar_Linea",
        [
            fxb.stmt_goto_xy(0, 95),
            fxb.stmt_if_else(
                fxb.op_eq("$v:Lineas_Turno", 1),
                [fxb.stmt_switch_costume("Linea_1")],
                [
                    fxb.stmt_if_else(
                        fxb.op_eq("$v:Lineas_Turno", 2),
                        [fxb.stmt_switch_costume("Linea_2")],
                        [
                            fxb.stmt_if_else(
                                fxb.op_eq("$v:Lineas_Turno", 3),
                                [fxb.stmt_switch_costume("Linea_3")],
                                [fxb.stmt_switch_costume("Linea_4")],
                            )
                        ],
                    )
                ],
            ),
            fxb.stmt_set_size(90),
            fxb.stmt_show(),
            fxb.stmt_repeat(
                5,
                [
                    fxb.stmt_set_size(105),
                    fxb.stmt_wait(0.05),
                ],
            ),
            fxb.stmt_hide(),
        ],
        x=40,
        y=180,
    )

    fx_target = {
        "isStage": False,
        "name": "Efecto_Linea",
        "variables": {},
        "lists": {},
        "broadcasts": {},
        "blocks": fxb.blocks,
        "comments": fxb.comments,
        "currentCostume": 0,
        "costumes": [
            {k: v for k, v in fx_1.items() if k != "bytes"},
            {k: v for k, v in fx_2.items() if k != "bytes"},
            {k: v for k, v in fx_3.items() if k != "bytes"},
            {k: v for k, v in fx_4.items() if k != "bytes"},
        ],
        "sounds": [],
        "volume": 100,
        "layerOrder": 12,
        "visible": False,
        "x": 0,
        "y": 95,
        "size": 100,
        "direction": 90,
        "draggable": False,
        "rotationStyle": "all around",
    }

    # --------------------------------------------------------------------------
    # TARGET 3: PANTALLA_ESTADO (MENÚ PRINCIPAL, PAUSA, GAME OVER)
    # --------------------------------------------------------------------------
    modal_menu = register_svg_asset(
        "Menu_Principal",
        make_modal_svg(
            "NEXUS BLOCKS",
            "1 NORMAL   2 HARD   3 CHAOS",
            "Select mode with number keys",
            "PRESS ENTER TO START",
            "#00F0FF",
        ),
        118,
        84,
    )
    modal_pausa = register_svg_asset(
        "Pausa_Modal",
        make_modal_svg(
            "PAUSED",
            "Take a breath",
            "P TO RESUME",
            "R TO RESTART",
            "#FFE600",
        ),
        118,
        84,
    )
    modal_gameover = register_svg_asset(
        "GameOver_Modal",
        make_modal_svg(
            "GAME OVER",
            "The stack reached the top",
            "Ready for another round?",
            "ENTER TO PLAY AGAIN",
            "#FF2A55",
        ),
        118,
        84,
    )
    modal_nightmare = register_svg_asset("Nightmare_Intro", '''<svg xmlns="http://www.w3.org/2000/svg" width="236" height="168"><rect x="1" y="1" width="234" height="166" fill="#101010" stroke="#FFBC32" stroke-width="2"/><path d="M12 41H224 M12 126H224" stroke="#FFBC32"/><text x="14" y="29" fill="#FFBC32" font-family="monospace" font-size="18" font-weight="bold">NIGHTMARE</text><text x="14" y="75" fill="#F5F2E9" font-family="monospace" font-size="12">INITIALIZING</text><text x="14" y="148" fill="#F5F2E9" font-family="monospace" font-size="11">SURVIVE THE PRESSURE</text></svg>''',118,84)
    modal_trial = register_svg_asset("Trial_Intermission", make_nightmare_modal("WAVE CLEAR",["BOARD PRESERVED","NEXT WAVE INCOMING","PREPARE TO SURVIVE"]),118,84)
    modal_core = register_svg_asset("Trial_Core", make_nightmare_modal("NIGHTMARE CORE",["FINAL WAVE","COMBINED THREATS","SURVIVE 40 LOCKS"]),118,84)
    modal_victory = register_svg_asset("Trial_Clear", make_nightmare_modal("TRIAL CLEARED",["NIGHTMARE CORE","FIVE WAVES SURVIVED","ENTER TO PLAY AGAIN"]),118,84)
    modal_glitch = register_svg_asset("Glitch_Intro", make_nightmare_modal("GLITCH PROTOCOL",["ARROWS MOVE CORE","SURVIVE THE SIGNAL","NO DIAGONAL MOVEMENT"]),118,84)
    modal_glitch_win = register_svg_asset("Glitch_Win", make_nightmare_modal("CORE STABLE",["SURVIVED","BONUS: 100","RETURNING TO BOARD"]),118,84)
    modal_glitch_loss = register_svg_asset("Glitch_Loss", make_nightmare_modal("CORE UNSTABLE",["PROTOCOL FAILED","2 GARBAGE IN 2 LOCKS","RETURNING TO BOARD"]),118,84)
    for m_asset in (modal_menu, modal_pausa, modal_gameover, modal_nightmare, modal_trial, modal_core, modal_victory, modal_glitch, modal_glitch_win, modal_glitch_loss):
        all_zip_files[m_asset["md5ext"]] = m_asset["bytes"]

    pb = ScratchBlockBuilder("pan", var_map, list_map, bcast_specs)
    pb.hat_green_flag(
        [
            pb.stmt_goto_xy(0, 6),
            pb.stmt_switch_costume("Menu_Principal"),
            pb.stmt_show(),
            # Capa visual únicamente: interpola con el reloj lógico de intro.
            pb.stmt_forever([
                pb.stmt_if_else(pb.op_and(pb.op_eq("$v:Estado_Juego","NIGHTMARE_INTRO"),pb.op_eq("$v:NM_Reduced",0)),[
                    pb.stmt_goto_xy(pb.op_add(-20,pb.op_mul("$v:Nightmare_Intro",25)),6),
                    pb.stmt_set_size(pb.op_add(90,pb.op_mul("$v:Nightmare_Intro",12.5)))],
                    [pb.stmt_if_else(pb.op_and(pb.op_eq("$v:Estado_Juego","GLITCH_INTRO"),pb.op_eq("$v:NM_Reduced",0)),[
                        pb.stmt_goto_xy(pb.op_add(-20,pb.op_mul("$v:G_Timer",25)),6),
                        pb.stmt_set_size(pb.op_add(90,pb.op_mul("$v:G_Timer",12.5)))],
                        [pb.stmt_if_else(pb.op_and(pb.op_eq("$v:NM_Reduced",0),pb.op_and(pb.op_eq("$v:Estado_Juego","TRIAL_INTERMISSION"),pb.op_lt("$v:Trial_Timer",0.8))),[
                            pb.stmt_goto_xy(pb.op_add(20,pb.op_mul("$v:Trial_Timer",-25)),6),
                            pb.stmt_set_size(pb.op_add(90,pb.op_mul("$v:Trial_Timer",12.5)))],
                            [pb.stmt_if(pb.op_not(pb.op_eq("$v:Estado_Juego","PAUSA")),[
                                pb.stmt_set_size(100),pb.stmt_goto_xy(0,6)])])])]),
                pb.stmt_wait(0.05)])
        ],
        x=40,
        y=40,
    )
    pb.hat_broadcast(
        "Actualizar_UI",
        [
            pb.stmt_goto_xy(0, 6),
            pb.stmt_if_else(
                pb.op_or(pb.op_eq("$v:Estado_Juego", "JUGANDO"),pb.op_eq("$v:Estado_Juego", "GLITCH_PLAY")),
                [pb.stmt_hide()],
                [
                    pb.stmt_show(),
                    pb.stmt_if(
                        pb.op_eq("$v:Estado_Juego", "MENU"),
                        [pb.stmt_switch_costume("Menu_Principal")],
                    ),
                    pb.stmt_if(
                        pb.op_eq("$v:Estado_Juego", "PAUSA"),
                        [pb.stmt_switch_costume("Pausa_Modal")],
                    ),
                    pb.stmt_if(
                        pb.op_eq("$v:Estado_Juego", "GAMEOVER"),
                        [pb.stmt_switch_costume("GameOver_Modal")],
                    ),
                    pb.stmt_if(pb.op_eq("$v:Estado_Juego", "NIGHTMARE_INTRO"),
                        [pb.stmt_switch_costume("Nightmare_Intro")]),
                    pb.stmt_if(pb.op_eq("$v:Estado_Juego", "TRIAL_INTERMISSION"),[
                        pb.stmt_if_else(pb.op_eq("$v:Trial_Wave",4),[pb.stmt_switch_costume("Trial_Core")],[pb.stmt_switch_costume("Trial_Intermission")])]),
                    pb.stmt_if(pb.op_eq("$v:Estado_Juego", "TRIAL_CLEAR"),[pb.stmt_switch_costume("Trial_Clear")]),
                    pb.stmt_if(pb.op_eq("$v:Estado_Juego", "GLITCH_INTRO"),[pb.stmt_switch_costume("Glitch_Intro")]),
                    pb.stmt_if(pb.op_eq("$v:Estado_Juego", "GLITCH_RESULT"),[
                        pb.stmt_if_else(pb.op_eq("$v:G_Success",1),[pb.stmt_switch_costume("Glitch_Win")],[pb.stmt_switch_costume("Glitch_Loss")])]),
                ],
            ),
        ],
        x=40,
        y=220,
    )

    pantalla_target = {
        "isStage": False,
        "name": "Pantalla_Estado",
        "variables": {},
        "lists": {},
        "broadcasts": {},
        "blocks": pb.blocks,
        "comments": pb.comments,
        "currentCostume": 0,
        "costumes": [
            {k: v for k, v in modal_menu.items() if k != "bytes"},
            {k: v for k, v in modal_pausa.items() if k != "bytes"},
            {k: v for k, v in modal_gameover.items() if k != "bytes"},
            {k: v for k, v in modal_nightmare.items() if k != "bytes"},
            {k: v for k, v in modal_trial.items() if k != "bytes"},
            {k: v for k, v in modal_core.items() if k != "bytes"},
            {k: v for k, v in modal_victory.items() if k != "bytes"},
            {k: v for k, v in modal_glitch.items() if k != "bytes"},
            {k: v for k, v in modal_glitch_win.items() if k != "bytes"},
            {k: v for k, v in modal_glitch_loss.items() if k != "bytes"},
        ],
        "sounds": [],
        "volume": 100,
        "layerOrder": 13,
        "visible": True,
        "x": 0,
        "y": 6,
        "size": 100,
        "direction": 90,
        "draggable": False,
        "rotationStyle": "all around",
    }

    monitors = []

    project_json = {
        "targets": [stage_target, motor_target, fx_target, pantalla_target],
        "monitors": monitors,
        "extensions": ["pen"],
        "meta": {
            "semver": "3.0.0",
            "vm": "0.2.0",
            "agent": "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) Scratch3-Generator/1.0",
        },
    }

    project_json_bytes = json.dumps(project_json, ensure_ascii=False, indent=2).encode("utf-8")

    os.makedirs(os.path.dirname(os.path.abspath(output_sb3_path)), exist_ok=True)
    with zipfile.ZipFile(output_sb3_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(zipfile.ZipInfo("project.json", (2026, 10, 19, 0, 0, 0)), project_json_bytes, compress_type=zipfile.ZIP_DEFLATED)
        for fname, fbytes in sorted(all_zip_files.items()):
            zf.writestr(zipfile.ZipInfo(fname, (2026, 10, 19, 0, 0, 0)), fbytes, compress_type=zipfile.ZIP_DEFLATED)

    return project_json


if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_file = os.path.join(repo_root, "NEXUS-BLOCKS-ENDLESS.sb3")
    proj = build_project(out_file)
    total_blocks = sum(len(t["blocks"]) for t in proj["targets"])
    print(f"[OK] Generado: {out_file}")
    print(f"     Targets (Stage + Sprites): {len(proj['targets'])}")
    print(f"     Total de bloques Scratch 3: {total_blocks}")
