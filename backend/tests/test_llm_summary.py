from unittest.mock import MagicMock, patch

HEADERS = {'x-api-key': 'test-key'}

@patch("app.routes.llm_summary_routes.report_to_markdown")
@patch("app.routes.llm_summary_routes.generate_ai_summary")

def test_summary_returns_cached_results(
    mock_generate, mock_markdown, client, mock_db
):  

    mock_summary = MagicMock()
    mock_summary.summary = {"overview": "cached_summary"}
    mock_summary.provider = 'gemini'
    mock_summary.llm_latency = 2
    mock_summary.summary_type = 'full'

    mock_db.query.return_value.filter.return_value.first.return_value = mock_summary
    
    mock_markdown.return_value = "# Cached Report"

    response = client.get(
        "/batch/job/1/summary", headers=HEADERS
    )

    assert response.status_code == 200

    data = response.json()

    assert data["cached"] is True
    assert data["summary"]=={"overview": "cached_summary"}
    assert data["converted_report"] == "# Cached Report"
    assert data["provider"] == "gemini"
    assert data["latency"] == 2
    assert data["summary_type"] == 'full'

    mock_generate.assert_not_called()

@patch('app.routes.llm_summary_routes.generate_ai_summary')
@patch('app.routes.llm_summary_routes.report_to_markdown')
@patch("app.routes.llm_summary_routes.get_top")

def test_generate_ai_summary(
    mock_get_top, mock_markdown, mock_generate, client, mock_db
):

    mock_generate.return_value = {
        "summary": {"overview": "summary"},
        "provider": "gemini",
        "latency": 10,
        "summary_type": "full",
        "fallback_used": False,
        "estimated_tokens": 100,
        "input_tokens": 50,
        "output_tokens": 50,
        "total_tokens": 100,
        "thoughts_tokens": 0,
        "prompt_version": "v1",
        "error": None
    }

    fake_dataset_context = MagicMock()
    fake_dataset_context.filename = 'reviews.csv'
    fake_dataset_context.no_of_columns = 5
    fake_dataset_context.text_column = 'reviews'
    fake_dataset_context.total_rows = 10000
    fake_dataset_context.model_name = "RoBERTa Transformer"

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        None, fake_dataset_context
    ]

    fake_row = MagicMock()
    fake_row.sentiment = "2"
    fake_row.countings = 100

    mock_db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = [
        fake_row
    ]

    mock_get_top.return_value = [("Amazing", "2", 0.95)]

    mock_markdown.return_value = "# New Summary"

    response = client.get(
        "/batch/job/1/summary", headers=HEADERS
    )

    assert response.status_code == 200

    data = response.json()

    assert data["cached"] is False
    assert data["summary"] == {"overview": "summary"}
    assert data["provider"] == "gemini"
    assert data["latency"] == 10
    assert data["summary_type"] == "full"
    assert data["converted_report"] == "# New Summary"

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_generate.assert_called_once()