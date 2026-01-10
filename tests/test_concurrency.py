import unittest
import threading
import time
from UniversalGalTrans.core.text_processor import TextProcessor

class TestConcurrency(unittest.TestCase):
    def test_race_condition(self):
        """
        Simulate a race condition where two sentences are processed.
        Sentence A starts streaming, then Sentence B arrives.
        We ensure A's streaming chunks don't land in B's entry.
        """
        processor = TextProcessor()

        # 1. Start Sentence A
        index_A = processor.add_to_history("Sentence A", "")
        self.assertEqual(index_A, 0)

        # 2. Start Sentence B (user fast-forwarded)
        index_B = processor.add_to_history("Sentence B", "")
        self.assertEqual(index_B, 1)

        # 3. Stream chunk for A (should go to index 0)
        processor.update_latest_translation("Trans A", index=index_A)

        # 4. Stream chunk for B (should go to index 1)
        processor.update_latest_translation("Trans B", index=index_B)

        # 5. Verify Isolation
        history = processor.get_history()
        self.assertEqual(history[0]['translated'], "Trans A")
        self.assertEqual(history[1]['translated'], "Trans B")

        # 6. Verify incorrect usage (defaulting to latest) would have failed
        # If we used old method: processor.update_latest_translation("Wrong", index=None)
        # It would append to index 1 (latest)
        processor.update_latest_translation("Wrong", index=None)
        self.assertEqual(history[1]['translated'], "Trans BWrong")

if __name__ == "__main__":
    unittest.main()
