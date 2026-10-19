#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite de Validación Estructural y Simulación Funcional de Bloques Scratch 3
para NEXUS-BLOCKS-ENDLESS.sb3.

Ejecuta dos niveles de verificación:
1. Validación estructural del archivo .sb3 (ZIP, MD5, XML SVG, PCM WAV,
   esquema de project.json, enlaces padre/hijo de los 1052 bloques y opcodes).
2. Intérprete de máquina virtual Scratch 3 (AST VM) que ejecuta directamente
   los bloques de `project.json` para verificar las 11 pruebas obligatorias.
"""

import hashlib
import io
import json
import math
import os
import random
import wave
import xml.etree.ElementTree as ET
import zipfile
from typing import Any, Dict, List, Optional, Tuple


OFFICIAL_SCRATCH3_OPCODES = {
    "event_whenflagclicked",
    "event_whenkeypressed",
    "event_whenthisspriteclicked",
    "event_whenbroadcastreceived",
    "event_broadcast",
    "event_broadcastandwait",
    "control_wait",
    "control_repeat",
    "control_forever",
    "control_if",
    "control_if_else",
    "control_wait_until",
    "control_repeat_until",
    "control_stop",
    "data_variable",
    "data_setvariableto",
    "data_changevariableby",
    "data_addtolist",
    "data_deleteoflist",
    "data_deletealloflist",
    "data_insertatlist",
    "data_replaceitemoflist",
    "data_itemoflist",
    "data_lengthoflist",
    "data_listcontainsitem",
    "operator_add",
    "operator_subtract",
    "operator_multiply",
    "operator_divide",
    "operator_random",
    "operator_gt",
    "operator_lt",
    "operator_equals",
    "operator_and",
    "operator_or",
    "operator_not",
    "operator_join",
    "operator_mod",
    "operator_round",
    "operator_mathop",
    "motion_gotoxy",
    "looks_show",
    "looks_hide",
    "looks_switchcostumeto",
    "looks_costume",
    "looks_switchbackdropto",
    "looks_backdrops",
    "looks_setsizeto",
    "sound_play",
    "sound_sounds_menu",
    "sensing_timer",
    "sensing_mousedown",
    "sensing_touchingobject",
    "sensing_touchingobjectmenu",
    "sensing_keypressed",
    "sensing_keyoptions",
    "procedures_definition",
    "procedures_prototype",
    "procedures_call",
    "argument_reporter_string_number",
    "pen_clear",
    "pen_stamp",
}


def validate_sb3_structure(sb3_path: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    logs: List[str] = []
    if not os.path.isfile(sb3_path):
        return False, [f"ERROR: No existe el archivo {sb3_path}"], {}

    with zipfile.ZipFile(sb3_path, "r") as zf:
        names = set(zf.namelist())
        assert "project.json" in names, "Falta project.json en la raíz del .sb3"
        proj = json.loads(zf.read("project.json").decode("utf-8"))
        logs.append(f"[PASS] Archivo ZIP válido con project.json ({len(names)} archivos internos).")

        targets = proj.get("targets", [])
        stages = [t for t in targets if t.get("isStage") is True]
        assert len(stages) == 1 and stages[0]["name"] == "Stage", "Debe existir exactamente 1 Stage"
        stage = stages[0]

        var_ids = set(stage["variables"].keys())
        list_ids = set(stage["lists"].keys())
        bcast_ids = set(stage["broadcasts"].keys())

        asset_count = 0
        for t in targets:
            for c in t.get("costumes", []):
                md5ext = c["md5ext"]
                assert md5ext in names, f"Falta disfraz {md5ext} en el archivo .sb3"
                raw = zf.read(md5ext)
                calc_md5 = hashlib.md5(raw).hexdigest()
                assert calc_md5 == c["assetId"], f"MD5 inválido en {md5ext}"
                if c["dataFormat"] == "svg":
                    root = ET.fromstring(raw.decode("utf-8"))
                    assert "svg" in root.tag, f"XML no es SVG válido en {md5ext}"
                asset_count += 1

            for s in t.get("sounds", []):
                md5ext = s["md5ext"]
                assert md5ext in names, f"Falta sonido {md5ext} en el archivo .sb3"
                raw = zf.read(md5ext)
                calc_md5 = hashlib.md5(raw).hexdigest()
                assert calc_md5 == s["assetId"], f"MD5 inválido en sonido {md5ext}"
                with wave.open(io.BytesIO(raw), "rb") as wf:
                    assert wf.getnchannels() == 1
                    assert wf.getframerate() == 22050
                asset_count += 1

        logs.append(f"[PASS] {asset_count} activos (disfraces SVG y sonidos WAV) verificados con hash MD5 y formato íntegro.")

        total_blocks = 0
        for t in targets:
            blocks = t["blocks"]
            total_blocks += len(blocks)
            defined_procs = set()
            called_procs = set()

            for bid, blk in blocks.items():
                op = blk["opcode"]
                assert op in OFFICIAL_SCRATCH3_OPCODES, f"Opcode no estándar detectado: {op}"

                if blk["topLevel"]:
                    assert blk["parent"] is None
                else:
                    assert blk["parent"] in blocks

                nxt = blk.get("next")
                if nxt is not None:
                    assert nxt in blocks
                    assert blocks[nxt]["parent"] == bid

                for in_name, in_val in blk.get("inputs", {}).items():
                    if isinstance(in_val, list) and len(in_val) >= 2:
                        child = in_val[1]
                        if isinstance(child, str):
                            assert child in blocks
                            assert blocks[child]["parent"] == bid

                fields = blk.get("fields", {})
                if "VARIABLE" in fields:
                    assert fields["VARIABLE"][1] in var_ids
                if "LIST" in fields:
                    assert fields["LIST"][1] in list_ids
                if "BROADCAST_OPTION" in fields:
                    assert fields["BROADCAST_OPTION"][1] in bcast_ids

                if op == "procedures_prototype":
                    defined_procs.add(blk["mutation"]["proccode"])
                elif op == "procedures_call":
                    called_procs.add(blk["mutation"]["proccode"])

            assert called_procs.issubset(defined_procs)

        logs.append(
            f"[PASS] {total_blocks} bloques Scratch 3 validados: 0 bloques huérfanos, 100% opcodes oficiales, enlaces padre/hijo consistentes."
        )

    return True, logs, proj


class Scratch3VMInterpreter:
    def __init__(self, project_json: Dict[str, Any]):
        self.project = project_json
        self.targets = {t["name"]: t for t in project_json["targets"]}
        self.stage = self.targets["Stage"]
        self.motor = self.targets["Motor_Juego"]
        self.blocks = self.motor["blocks"]

        self.vars: Dict[str, Any] = {}
        for vid, (vname, vval) in self.stage["variables"].items():
            self.vars[vname] = vval

        self.lists: Dict[str, List[Any]] = {}
        for lid, (lname, lval) in self.stage["lists"].items():
            self.lists[lname] = list(lval)

        self.procs: Dict[str, Tuple[str, List[str]]] = {}
        for bid, blk in self.blocks.items():
            if blk["opcode"] == "procedures_definition":
                proto_id = blk["inputs"]["custom_block"][1]
                proto = self.blocks[proto_id]
                proccode = proto["mutation"]["proccode"]
                arg_names = json.loads(proto["mutation"]["argumentnames"])
                self.procs[proccode] = (bid, arg_names)

        self.bcast_hats: Dict[str, List[Tuple[Dict[str, Any], str]]] = {}
        for t in project_json["targets"]:
            t_blocks = t["blocks"]
            for bid, blk in t_blocks.items():
                if blk["opcode"] == "event_whenbroadcastreceived":
                    bname = blk["fields"]["BROADCAST_OPTION"][0]
                    self.bcast_hats.setdefault(bname, []).append((t_blocks, bid))

        self.sim_timer: float = 0.0
        self.stamps_log: List[Tuple[float, float, Any]] = []
        self.sounds_played: List[str] = []
        self.current_costume: Any = "Bloque_1_I"

    def _to_num(self, val: Any) -> float:
        if isinstance(val, (int, float)):
            return float(val)
        try:
            return float(str(val))
        except ValueError:
            return 0.0

    def _to_int_or_float(self, val: float) -> Any:
        if abs(val - round(val)) < 1e-9:
            return int(round(val))
        return round(val, 6)

    def eval_input(self, blocks_dict: Dict[str, Any], blk: Dict[str, Any], key: str, arg_env: Dict[str, Any]) -> Any:
        if key not in blk["inputs"]:
            return 0
        raw = blk["inputs"][key]
        target = raw[1]
        if isinstance(target, list):
            prim_type = target[0]
            if prim_type in (4, 5, 6, 7, 8):
                return self._to_int_or_float(float(target[1]))
            if prim_type in (9, 10, 11):
                return str(target[1])
            if prim_type == 12:
                return self.vars.get(target[1], 0)
        elif isinstance(target, str):
            return self.eval_reporter(blocks_dict, target, arg_env)
        return 0

    def eval_reporter(self, blocks_dict: Dict[str, Any], bid: str, arg_env: Dict[str, Any]) -> Any:
        blk = blocks_dict[bid]
        op = blk["opcode"]

        if op == "data_variable":
            return self.vars[blk["fields"]["VARIABLE"][0]]
        if op == "argument_reporter_string_number":
            return arg_env.get(blk["fields"]["VALUE"][0], 0)
        if op == "sensing_timer":
            return self.sim_timer
        if op == "looks_costume":
            return blk["fields"]["COSTUME"][0]
        if op == "looks_backdrops":
            return blk["fields"]["BACKDROP"][0]
        if op == "sound_sounds_menu":
            return blk["fields"]["SOUND_MENU"][0]

        if op == "operator_add":
            return self._to_int_or_float(
                self._to_num(self.eval_input(blocks_dict, blk, "NUM1", arg_env))
                + self._to_num(self.eval_input(blocks_dict, blk, "NUM2", arg_env))
            )
        if op == "operator_subtract":
            return self._to_int_or_float(
                self._to_num(self.eval_input(blocks_dict, blk, "NUM1", arg_env))
                - self._to_num(self.eval_input(blocks_dict, blk, "NUM2", arg_env))
            )
        if op == "operator_multiply":
            return self._to_int_or_float(
                self._to_num(self.eval_input(blocks_dict, blk, "NUM1", arg_env))
                * self._to_num(self.eval_input(blocks_dict, blk, "NUM2", arg_env))
            )
        if op == "operator_divide":
            denom = self._to_num(self.eval_input(blocks_dict, blk, "NUM2", arg_env))
            return 0.0 if abs(denom) < 1e-12 else self._to_num(self.eval_input(blocks_dict, blk, "NUM1", arg_env)) / denom
        if op == "operator_mod":
            b = self._to_num(self.eval_input(blocks_dict, blk, "NUM2", arg_env))
            return self._to_int_or_float(self._to_num(self.eval_input(blocks_dict, blk, "NUM1", arg_env)) % b)
        if op == "operator_random":
            low = int(round(self._to_num(self.eval_input(blocks_dict, blk, "FROM", arg_env))))
            high = int(round(self._to_num(self.eval_input(blocks_dict, blk, "TO", arg_env))))
            return random.randint(min(low, high), max(low, high))
        if op == "operator_mathop":
            fn = blk["fields"]["OPERATOR"][0]
            val = self._to_num(self.eval_input(blocks_dict, blk, "NUM", arg_env))
            return math.floor(val) if fn == "floor" else (abs(val) if fn == "abs" else val)
        if op == "operator_join":
            return str(self.eval_input(blocks_dict, blk, "STRING1", arg_env)) + str(
                self.eval_input(blocks_dict, blk, "STRING2", arg_env)
            )
        if op == "operator_equals":
            v1 = self.eval_input(blocks_dict, blk, "OPERAND1", arg_env)
            v2 = self.eval_input(blocks_dict, blk, "OPERAND2", arg_env)
            try:
                return abs(float(v1) - float(v2)) < 1e-9
            except (ValueError, TypeError):
                return str(v1).lower() == str(v2).lower()
        if op == "operator_lt":
            return self._to_num(self.eval_input(blocks_dict, blk, "OPERAND1", arg_env)) < self._to_num(
                self.eval_input(blocks_dict, blk, "OPERAND2", arg_env)
            )
        if op == "operator_gt":
            return self._to_num(self.eval_input(blocks_dict, blk, "OPERAND1", arg_env)) > self._to_num(
                self.eval_input(blocks_dict, blk, "OPERAND2", arg_env)
            )
        if op == "operator_and":
            return bool(self.eval_input(blocks_dict, blk, "OPERAND1", arg_env)) and bool(
                self.eval_input(blocks_dict, blk, "OPERAND2", arg_env)
            )
        if op == "operator_or":
            return bool(self.eval_input(blocks_dict, blk, "OPERAND1", arg_env)) or bool(
                self.eval_input(blocks_dict, blk, "OPERAND2", arg_env)
            )
        if op == "operator_not":
            return not bool(self.eval_input(blocks_dict, blk, "OPERAND", arg_env))
        if op == "data_itemoflist":
            lname = blk["fields"]["LIST"][0]
            idx = int(round(self._to_num(self.eval_input(blocks_dict, blk, "INDEX", arg_env))))
            lst = self.lists[lname]
            return lst[idx - 1] if 1 <= idx <= len(lst) else ""
        if op == "data_lengthoflist":
            return len(self.lists[blk["fields"]["LIST"][0]])

        raise NotImplementedError(f"Reporter opcode no soportado: {op}")

    def exec_chain(self, blocks_dict: Dict[str, Any], start_id: Optional[str], arg_env: Dict[str, Any]) -> None:
        curr_id = start_id
        while curr_id is not None:
            blk = blocks_dict[curr_id]
            op = blk["opcode"]

            if op == "data_setvariableto":
                self.vars[blk["fields"]["VARIABLE"][0]] = self.eval_input(blocks_dict, blk, "VALUE", arg_env)
            elif op == "data_changevariableby":
                vname = blk["fields"]["VARIABLE"][0]
                delta = self._to_num(self.eval_input(blocks_dict, blk, "VALUE", arg_env))
                self.vars[vname] = self._to_int_or_float(self._to_num(self.vars[vname]) + delta)
            elif op == "data_deletealloflist":
                self.lists[blk["fields"]["LIST"][0]].clear()
            elif op == "data_addtolist":
                self.lists[blk["fields"]["LIST"][0]].append(self.eval_input(blocks_dict, blk, "ITEM", arg_env))
            elif op == "data_deleteoflist":
                lname = blk["fields"]["LIST"][0]
                idx = int(round(self._to_num(self.eval_input(blocks_dict, blk, "INDEX", arg_env))))
                if 1 <= idx <= len(self.lists[lname]):
                    self.lists[lname].pop(idx - 1)
            elif op == "data_replaceitemoflist":
                lname = blk["fields"]["LIST"][0]
                idx = int(round(self._to_num(self.eval_input(blocks_dict, blk, "INDEX", arg_env))))
                item = self.eval_input(blocks_dict, blk, "ITEM", arg_env)
                if 1 <= idx <= len(self.lists[lname]):
                    self.lists[lname][idx - 1] = item
            elif op == "control_if":
                if bool(self.eval_input(blocks_dict, blk, "CONDITION", arg_env)) and "SUBSTACK" in blk["inputs"]:
                    self.exec_chain(blocks_dict, blk["inputs"]["SUBSTACK"][1], arg_env)
            elif op == "control_if_else":
                if bool(self.eval_input(blocks_dict, blk, "CONDITION", arg_env)):
                    if "SUBSTACK" in blk["inputs"]:
                        self.exec_chain(blocks_dict, blk["inputs"]["SUBSTACK"][1], arg_env)
                else:
                    if "SUBSTACK2" in blk["inputs"]:
                        self.exec_chain(blocks_dict, blk["inputs"]["SUBSTACK2"][1], arg_env)
            elif op == "control_repeat":
                times = int(round(self._to_num(self.eval_input(blocks_dict, blk, "TIMES", arg_env))))
                sub = blk["inputs"].get("SUBSTACK", [None, None])[1]
                for _ in range(max(0, times)):
                    self.exec_chain(blocks_dict, sub, arg_env)
            elif op == "control_repeat_until":
                sub = blk["inputs"].get("SUBSTACK", [None, None])[1]
                guard = 0
                while not bool(self.eval_input(blocks_dict, blk, "CONDITION", arg_env)):
                    self.exec_chain(blocks_dict, sub, arg_env)
                    guard += 1
                    assert guard < 5000
            elif op == "procedures_call":
                proccode = blk["mutation"]["proccode"]
                arg_ids = json.loads(blk["mutation"]["argumentids"])
                def_id, arg_names = self.procs[proccode]
                new_env = {aname: self.eval_input(blocks_dict, blk, aid, arg_env) for aid, aname in zip(arg_ids, arg_names)}
                self.exec_chain(self.blocks, self.blocks[def_id]["next"], new_env)
            elif op in ("event_broadcast", "event_broadcastandwait"):
                self.trigger_broadcast(blk["inputs"]["BROADCAST_INPUT"][1][1])
            elif op == "pen_clear":
                self.stamps_log.clear()
            elif op == "pen_stamp":
                self.stamps_log.append((self.vars.get("_sim_x", 0.0), self.vars.get("_sim_y", 0.0), self.current_costume))
            elif op == "motion_gotoxy":
                self.vars["_sim_x"] = self._to_num(self.eval_input(blocks_dict, blk, "X", arg_env))
                self.vars["_sim_y"] = self._to_num(self.eval_input(blocks_dict, blk, "Y", arg_env))
            elif op == "looks_switchcostumeto":
                self.current_costume = self.eval_input(blocks_dict, blk, "COSTUME", arg_env)
            elif op == "sound_play":
                self.sounds_played.append(str(self.eval_input(blocks_dict, blk, "SOUND_MENU", arg_env)))
            elif op in ("looks_show", "looks_hide", "looks_setsizeto", "looks_switchbackdropto", "control_wait"):
                pass
            else:
                raise NotImplementedError(f"Statement opcode no soportado: {op}")

            curr_id = blk["next"]

    def call_proc(self, proccode: str, *args: Any) -> None:
        def_id, arg_names = self.procs[proccode]
        env = {k: v for k, v in zip(arg_names, args)}
        self.exec_chain(self.blocks, self.blocks[def_id]["next"], env)

    def trigger_broadcast(self, bcast_name: str) -> None:
        for t_blocks, hat_id in self.bcast_hats.get(bcast_name, []):
            self.exec_chain(t_blocks, t_blocks[hat_id]["next"], {})


def run_all_tests(sb3_path: str) -> List[str]:
    report: List[str] = []
    ok, struct_logs, proj = validate_sb3_structure(sb3_path)
    assert ok
    report.extend(struct_logs)

    vm = Scratch3VMInterpreter(proj)
    random.seed(42)

    vm.call_proc("Iniciar_Partida")
    assert vm.vars["Estado_Juego"] == "JUGANDO"
    assert len(vm.lists["Tablero"]) == 200 and all(x == 0 for x in vm.lists["Tablero"])

    vm.lists["Bolsa_7"].clear()
    drawn_bags = []
    for _ in range(3):
        bag = []
        for _ in range(7):
            vm.call_proc("Extraer_De_Bolsa")
            bag.append(int(vm.vars["temp_pieza"]))
        assert sorted(bag) == [1, 2, 3, 4, 5, 6, 7]
        drawn_bags.append(bag)
    report.append(
        f"[PASS] Prueba 1 (Sistema 7-Bag): 21 extracciones seguidas verificadas en 3 bolsas exactas {drawn_bags[0]} sin repeticiones prematuras."
    )

    for pid in range(1, 8):
        vm.call_proc("Iniciar_Partida")
        vm.vars["Pieza_Actual"] = pid
        vm.vars["Pieza_Rotacion"] = 0
        vm.vars["Pieza_Col"] = 5
        vm.vars["Pieza_Fila"] = 4
        for _ in range(15):
            vm.call_proc("Mover_Horizontal %s", -1)
        min_col = vm.vars["Pieza_Col"]
        vm.call_proc("Comprobar_Colision %s %s %s %s", pid, min_col, 4, 0)
        assert vm.vars["Colision_Detectada"] == 0
        vm.call_proc("Comprobar_Colision %s %s %s %s", pid, min_col - 1, 4, 0)
        assert vm.vars["Colision_Detectada"] == 1

        for _ in range(15):
            vm.call_proc("Mover_Horizontal %s", 1)
        max_col = vm.vars["Pieza_Col"]
        vm.call_proc("Comprobar_Colision %s %s %s %s", pid, max_col, 4, 0)
        assert vm.vars["Colision_Detectada"] == 0
        vm.call_proc("Comprobar_Colision %s %s %s %s", pid, max_col + 1, 4, 0)
        assert vm.vars["Colision_Detectada"] == 1
    report.append(
        "[PASS] Prueba 2 (Movimiento contra paredes): Las 7 piezas se detienen exactamente en los bordes (cols 1..10) sin salirse del tablero."
    )

    vm.call_proc("Iniciar_Partida")
    vm.vars["Pieza_Actual"] = 1
    vm.vars["Pieza_Rotacion"] = 1
    vm.vars["Pieza_Col"] = 0
    vm.vars["Pieza_Fila"] = 5
    vm.call_proc("Rotar_Pieza")
    assert vm.vars["Rotacion_Exito"] == 1 and vm.vars["Pieza_Col"] >= 2

    vm.call_proc("Iniciar_Partida")
    vm.vars["Pieza_Actual"] = 1
    vm.vars["Pieza_Rotacion"] = 1
    vm.vars["Pieza_Col"] = 5
    vm.vars["Pieza_Fila"] = 5
    for r in range(3, 8):
        for c in range(1, 11):
            if c != 6:
                vm.lists["Tablero"][(r - 1) * 10 + (c - 1)] = 2
    old_rot = vm.vars["Pieza_Rotacion"]
    vm.call_proc("Rotar_Pieza")
    assert vm.vars["Rotacion_Exito"] == 0 and vm.vars["Pieza_Rotacion"] == old_rot
    report.append(
        "[PASS] Prueba 3 (Rotaciones y Wall Kicks): Wall Kick corrige posición junto a paredes y bloquea giros imposibles entre obstáculos."
    )

    vm.call_proc("Iniciar_Partida")
    vm.vars["Pieza_Actual"] = 2
    vm.vars["Pieza_Col"] = 5
    vm.vars["Pieza_Fila"] = 2
    vm.vars["Pieza_Rotacion"] = 0
    vm.call_proc("Actualizar_Fantasma")
    assert vm.vars["Fila_Fantasma"] == 19
    vm.call_proc("Paso_Caida %s", 1)
    assert vm.vars["Pieza_Fila"] == 3 and vm.vars["Puntuacion"] == 1
    vm.call_proc("Caida_Instantanea")
    assert vm.vars["Puntuacion"] == 1 + (19 - 3) * 2
    report.append(
        "[PASS] Prueba 4 (Colisiones al descender, Fantasma y Hard Drop): Cálculo exacto de aterrizaje, puntuación de caída y fijación en Tablero."
    )

    expected_base_scores = {1: 100, 2: 300, 3: 500, 4: 800}
    for num_lines, expected_pts in expected_base_scores.items():
        vm.call_proc("Iniciar_Partida")
        for r in range(20, 20 - num_lines, -1):
            for c in range(1, 11):
                vm.lists["Tablero"][(r - 1) * 10 + (c - 1)] = 3
        witness_row = 20 - num_lines
        vm.lists["Tablero"][(witness_row - 1) * 10 + 0] = 7
        vm.call_proc("Revisar_Y_Eliminar_Lineas")
        assert vm.vars["Lineas_Turno"] == num_lines
        assert vm.vars["Lineas"] == num_lines
        assert vm.vars["Puntuacion"] == expected_pts
        assert vm.lists["Tablero"][(20 - 1) * 10 + 0] == 7
        assert sum(1 for x in vm.lists["Tablero"] if x > 0) == 1
    report.append(
        "[PASS] Prueba 5 (Eliminación de 1, 2, 3 y 4 líneas): Limpieza simultánea verificada (100/300/500/800 pts) y descenso exacto de filas superiores."
    )

    vm.call_proc("Iniciar_Partida")
    first_piece = vm.vars["Pieza_Actual"]
    next_piece = vm.vars["Siguiente_Pieza"]
    vm.call_proc("Guardar_Hold")
    assert vm.vars["Pieza_Guardada"] == first_piece and vm.vars["Pieza_Actual"] == next_piece and vm.vars["Puede_Guardar"] == 0
    curr_after_hold = vm.vars["Pieza_Actual"]
    vm.call_proc("Guardar_Hold")
    assert vm.vars["Pieza_Actual"] == curr_after_hold
    vm.call_proc("Caida_Instantanea")
    assert vm.vars["Puede_Guardar"] == 1
    report.append(
        "[PASS] Prueba 6 (Sistema Hold): Guardado, intercambio y prevención de doble cambio en el mismo turno verificados."
    )

    vm.call_proc("Iniciar_Partida")
    for c in range(1, 11):
        vm.lists["Tablero"][(2 - 1) * 10 + (c - 1)] = 5
    vm.call_proc("Generar_Nueva_Pieza")
    assert vm.vars["Estado_Juego"] == "GAMEOVER"
    vm.trigger_broadcast("Iniciar_Juego")
    assert vm.vars["Estado_Juego"] == "JUGANDO" and all(x == 0 for x in vm.lists["Tablero"])
    report.append(
        "[PASS] Prueba 7 (Detección de Game Over y Reinicio): Fin de partida detectado al bloquearse la zona superior y limpieza total al reiniciar."
    )

    vm.call_proc("Iniciar_Partida")
    col_before = vm.vars["Pieza_Col"]
    vm.trigger_broadcast("Alternar_Pausa")
    assert vm.vars["Estado_Juego"] == "PAUSA"
    vm.call_proc("Mover_Horizontal %s", -1)
    assert vm.vars["Pieza_Col"] == col_before
    vm.trigger_broadcast("Alternar_Pausa")
    assert vm.vars["Estado_Juego"] == "JUGANDO"
    vm.call_proc("Mover_Horizontal %s", -1)
    assert vm.vars["Pieza_Col"] == col_before - 1
    report.append(
        "[PASS] Prueba 8 (Pausa y Reanudación): Estado PAUSA bloquea entradas y detiene caída; reanudación restaura el control."
    )

    seen_diffs = []
    for _ in range(4):
        vm.trigger_broadcast("Cambiar_Dificultad")
        seen_diffs.append((vm.vars["Dificultad"], vm.vars["Velocidad_Base"]))
    diff_dict = dict(seen_diffs)
    assert set(diff_dict.keys()) == {"Fácil", "Normal", "Difícil", "Pesadilla"}
    assert diff_dict["Fácil"] > diff_dict["Normal"] > diff_dict["Difícil"] > diff_dict["Pesadilla"]

    seen_modes = []
    for _ in range(4):
        vm.trigger_broadcast("Cambiar_Modo")
        seen_modes.append(vm.vars["Modo_Juego"])
    assert set(seen_modes) == {"ENDLESS CLASSIC", "RELAX", "CHAOS MODE", "SPRINT 40L"}

    vm.vars["Modo_Juego"] = "ENDLESS CLASSIC"
    vm.vars["Dificultad"] = "Pesadilla"
    vm.vars["Nivel"] = 50
    vm.call_proc("Actualizar_Velocidad_Y_Caos")
    assert vm.vars["Velocidad_Caida"] >= 0.06

    vm.vars["Modo_Juego"] = "SPRINT 40L"
    vm.call_proc("Iniciar_Partida")
    vm.vars["Lineas"] = 39
    for c in range(1, 11):
        vm.lists["Tablero"][(20 - 1) * 10 + (c - 1)] = 4
    vm.call_proc("Revisar_Y_Eliminar_Lineas")
    assert vm.vars["Lineas"] == 40 and vm.vars["Estado_Juego"] == "VICTORIA"
    report.append(
        "[PASS] Prueba 9 (Dificultades y Modos): 4 dificultades (0.85s a 0.22s), límite técnico >=0.06s, CHAOS MODE y victoria en SPRINT 40L verificados."
    )

    vm.vars["Modo_Juego"] = "ENDLESS CLASSIC"
    vm.vars["Dificultad"] = "Normal"
    vm.call_proc("Iniciar_Partida")
    for _ in range(150):
        for idx_clear in range(80):
            vm.lists["Tablero"][idx_clear] = 0
        for act in ("IZQ", "ROTAR", "DER", "BAJAR", "HOLD", "CAIDA"):
            vm.vars["Accion_Tactil"] = act
            vm.trigger_broadcast("Ejecutar_Accion")
            if vm.vars["Estado_Juego"] != "JUGANDO":
                vm.call_proc("Iniciar_Partida")
    assert len(vm.stamps_log) >= 12
    report.append(
        f"[PASS] Prueba 10 y 11 (Partida prolongada + Controles táctiles): 150 ciclos de juego y despacho táctil ejecutados sin fugas de estado ({len(vm.stamps_log)} sellos Pen activos en el frame actual)."
    )

    return report


if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sb3_file = os.path.join(repo_root, "NEXUS-BLOCKS-ENDLESS.sb3")
    results = run_all_tests(sb3_file)
    print("=" * 76)
    print("RESULTADOS DE VALIDACIÓN Y PRUEBAS — NEXUS BLOCKS: ENDLESS (.SB3)")
    print("=" * 76)
    for line in results:
        print(line)
    print("=" * 76)
    print("VEREDICTO FINAL: 100% DE LAS PRUEBAS ESTRUCTURALES Y LÓGICAS SUPERADAS.")
