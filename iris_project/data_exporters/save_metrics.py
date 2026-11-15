if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_exporter
def export_metrics(df, *args, **kwargs):
    df.to_csv('iris_metrics.csv', index=False)
    print('Saved metrics to iris_metrics.csv')


@test
def test_metrics_file(*args, **kwargs):
    import pandas as pd
    m = pd.read_csv('iris_metrics.csv')
    assert len(m) == 4, 'expected 4 metrics'
    assert m['value'].between(0, 1).all(), 'metric outside 0-1'
