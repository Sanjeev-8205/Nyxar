import pytest

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_empty_string_returns_400(client, prediction_payload, auth_headers, model):
    response = client.post("/predict", json=prediction_payload("", model), headers=auth_headers)
    assert response.status_code==400

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_whitespace_only_returns_400(client, prediction_payload, auth_headers, model):
    response = client.post("/predict", json=prediction_payload("      ", model), headers=auth_headers)
    assert response.status_code==400

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_single_character_input(client, prediction_payload, auth_headers, model):
    response = client.post("/predict", json=prediction_payload("a", model), headers=auth_headers)
    assert response.status_code==200

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_very_long_input_10000_chars(client, prediction_payload, auth_headers, model):
    text = ("The quick brown fox jumps over the lazy dog. " * 223)[:10000]
    response = client.post("/predict", json=prediction_payload(text, model), headers=auth_headers)
    assert response.status_code==200

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_unicode_input(client, prediction_payload, auth_headers, model):
    if model=="Bi-LSTM":
        response = client.post("/predict", json=prediction_payload("こんにちは", model), headers=auth_headers)
        assert response.status_code==400
    else:
        response = client.post("/predict", json=prediction_payload("こんにちは", model), headers=auth_headers)
        assert response.status_code==200
    

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_emoji_only_input(client, prediction_payload, auth_headers, model):
    if model=="Bi-LSTM":
        response = client.post("/predict", json=prediction_payload("😎😎😎😎😎😎😎", model), headers=auth_headers)
        assert response.status_code==400
    else:
        response = client.post("/predict", json=prediction_payload("😎😎😎😎😎😎😎", model), headers=auth_headers)
        assert response.status_code==200

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_numbers_only_input(client, prediction_payload, auth_headers, model):
    response = client.post("/predict", json=prediction_payload("990011226688173638 628349349 38298048207422", model), headers=auth_headers)
    assert response.status_code==200

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_special_characters_only_input(client, prediction_payload, auth_headers, model):
    if model=="Bi-LSTM":
        response = client.post("/predict", json=prediction_payload("-=['/.,;@(!*#&( (@&( @* (!@*( @@@#:< >)[']", model), headers=auth_headers)
        assert response.status_code==400
    else:
        response = client.post("/predict", json=prediction_payload("-=['/.,;@(!*#&( (@&( @* (!@*( @@@#:< >)[']", model), headers=auth_headers)
        assert response.status_code==200

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_mixed_languages_input(client, prediction_payload, auth_headers, model):
    response = client.post("/predict", json=prediction_payload("こんにちは Awesome नमस्ते 你好", model), headers=auth_headers)
    assert response.status_code==200

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_newlines_and_tabs_input(client, prediction_payload, auth_headers, model):
    response = client.post("/predict", json=prediction_payload("First line.\nSecond line.\tIndented text.", model), headers=auth_headers)
    assert response.status_code==200