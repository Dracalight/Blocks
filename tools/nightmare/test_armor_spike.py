"""Pruebas del modelo aislado; no acreditan el comportamiento Scratch."""
import unittest
from armor_spike import DAMAGED, INTACT, empty, insert_armor, resolve


class ArmorSpikeTests(unittest.TestCase):
    def test_damage_and_second_clear(self):
        board = empty(); board[-1] = [INTACT] * 9 + [3]
        board, lines, cracks = resolve(board)
        self.assertEqual((lines, cracks), (0, 1))
        self.assertEqual(board[-1], [DAMAGED] * 9 + [0])
        board[-1][-1] = 2
        board, lines, cracks = resolve(board)
        self.assertEqual((lines, cracks), (1, 0))
        self.assertEqual(board, empty())

    def test_multiple_rows_and_simultaneous_compaction(self):
        board = empty(); board[-3] = [INTACT] * 9 + [2]
        board[-2] = [1] * 10; board[-1] = [INTACT] * 9 + [3]
        board[-4][0] = 7
        result, lines, cracks = resolve(board)
        self.assertEqual((lines, cracks), (1, 2))
        self.assertEqual(result[-3][0], 7)
        self.assertEqual(result[-2:], [[DAMAGED] * 9 + [0], [DAMAGED] * 9 + [0]])
        self.assertEqual(sum(bool(x) for r in result for x in r), 19)

    def test_t_spin_shape_with_a_normal_and_armored_row(self):
        board = empty(); board[-2] = [INTACT] * 10; board[-1] = [1] * 10
        board[-2][3:6] = [0, 0, 0]; board[-1][4] = 0; board[-3][3] = 8
        # Rotación 2 de la T: tres celdas en la fila 19 y una en la 20.
        for y, x in ((18,3), (18,4), (18,5), (19,4)): board[y][x] = 3
        board, lines, cracks = resolve(board)
        self.assertEqual((lines, cracks), (1, 1))
        self.assertEqual(board[-1], [DAMAGED] * 3 + [0, 3, 3] + [DAMAGED] * 4)
        self.assertEqual(sum(bool(x) for r in board for x in r), 10)

    def test_garbage_topout_and_reset(self):
        board, topout = insert_armor(empty(), 4)
        self.assertFalse(topout); self.assertEqual(board[-1].count(INTACT), 9)
        self.assertEqual(board[-1][4], 0)
        board[0][0] = 7
        saved = [r[:] for r in board]
        board, topout = insert_armor(board, 3)
        self.assertTrue(topout); self.assertEqual(board, saved)
        self.assertEqual(empty(), [[0] * 10 for _ in range(20)])

    def test_full_armor_without_normal_cell_is_rejected(self):
        board = empty(); board[-1] = [INTACT] * 10
        with self.assertRaises(ValueError): resolve(board)


if __name__ == '__main__':
    unittest.main()
