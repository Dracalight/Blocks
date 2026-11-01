import json
import unittest
import zipfile
from pathlib import Path
from simulate_board import SB3

QA = Path(__file__).resolve().parents[2]/'qa-output/NEXUS-BLOCKS-NIGHTMARE-QA-ONLY.sb3'

class QAIsolation(unittest.TestCase):
    def test_player_build_has_no_qa_input_variables(self):
        with zipfile.ZipFile(SB3) as z:
            project=json.loads(z.read('project.json'))
        names={v[0] for v in project['targets'][0]['variables'].values()}
        self.assertFalse({'key_5','key_6','key_7'} & names)

    def test_qa_fixture_is_separate_and_has_inputs(self):
        self.assertNotEqual(QA,SB3)
        with zipfile.ZipFile(QA) as z:
            project=json.loads(z.read('project.json'))
        names={v[0] for v in project['targets'][0]['variables'].values()}
        self.assertTrue({'key_5','key_6','key_7'} <= names)

if __name__=='__main__':unittest.main()
