from app.pipelines.audio import AudioPipeline


def test_detect_fillers():
    pipeline = AudioPipeline()

    result = pipeline.process_transcript(
        "este bueno yo creo que o sea la defensa este fue bien"
    )

    assert result.fillers.count == 4  # "este" x2, "bueno" x1, "o sea" x1
    assert result.fillers.words["este"] == 2
    assert result.fillers.words["bueno"] == 1
    assert result.fillers.words["o sea"] == 1
    assert result.pace_wpm > 0


def test_no_fillers():
    pipeline = AudioPipeline()

    result = pipeline.process_transcript("la investigación demuestra resultados positivos")

    assert result.fillers.count == 0
    assert result.pace_wpm > 0