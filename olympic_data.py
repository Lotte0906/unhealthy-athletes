
from pathlib import Path

import pandas as pd


class OlympicData:
    """Load and prepare Olympic athlete data."""

    MEDAL_TYPES = ("Bronze", "Silver", "Gold")

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.raw_data = None
        self.data = None

    def load_data(self) -> None:
        """Load the CSV file into raw_data."""
        self.raw_data = pd.read_csv(self.filepath)

    def prepare_data(self) -> None:
        """Create binary medal columns and remove the original Medal column."""
        if self.raw_data is None:
            raise RuntimeError("Load the data first.")

        self.data = self.raw_data.copy()

        for medal_type in self.MEDAL_TYPES:
            self.data[medal_type] = (
                self.data["Medal"] == medal_type
            ).astype(int)
        
        self.data["medals"] = self.data["Gold"] + self.data["Silver"] + self.data["Bronze"]

        self.data = self.data.drop(columns="Medal")

    def load_and_prepare(self) -> None:
        """Load the CSV file and prepare the data."""
        self.load_data()
        self.prepare_data()

