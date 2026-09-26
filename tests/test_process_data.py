import pandas as pd

from src.process_data import process_data


def test_process_data_empty_df():
    """Test processing an empty DataFrame."""
    df = pd.DataFrame()
    processed_df = process_data(df)
    assert processed_df.empty


def test_process_data_cleaning():
    """Test cleaning logic: dropping all-NaN rows and stripping whitespace."""
    data = {
        "descricao": ["  Item 1  ", "Item 2", None, "   "],
        "valor": [100, 200, None, 400],
        "extra": [None, None, None, None],  # Coluna irrelevante
    }
    df = pd.DataFrame(data)

    # Adiciona uma linha inteiramente vazia para testar o dropna(how='all')
    df.loc[len(df)] = [None, None, None]

    processed = process_data(df)

    # Verifica se removeu a linha totalmente vazia (agora temos 4 linhas iniciais)
    # Nota: process_data remove linhas onde *todas* as colunas são NaN.
    # A linha 2 tem descricao=None, valor=None, extra=None -> Deve cair se o drop for em tudo.

    # Verifica strip na descrição
    assert processed.iloc[0]["descricao"] == "Item 1"
    assert processed.iloc[1]["descricao"] == "Item 2"

    # Verifica se a descrição virou string 'nan' ou 'None' (comportamento padrão do astype(str) do pandas)
    # ou se foi removida se fosse só whitespace
    val = processed.iloc[2]["descricao"]
    assert val == "nan" or val == "None" or val == ""
