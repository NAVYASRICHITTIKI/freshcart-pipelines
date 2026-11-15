import pandas as pd
from sklearn.model_selection import train_test_split

try:
    if 'transformer' not in globals():
        from mage_ai.data_preparation.decorators import transformer
    if 'test' not in globals():
        from mage_ai.data_preparation.decorators import test
except ImportError:
    # Running outside Mage (e.g. in pytest): use no-op decorators
    def transformer(func):
        return func

    def test(func):
        return func


@transformer
def transform(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    train_idx, test_idx = train_test_split(
        df.index, test_size=0.2, random_state=42, stratify=df["target"]
    )
    df = df.copy()
    df["split"] = "train"
    df.loc[test_idx, "split"] = "test"
    return df


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert "split" in output.columns
