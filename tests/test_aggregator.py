from app.pipelines.aggregator import MetricsAggregator
from app.models.metrics import PostureMetrics, GestureMetrics, FaceMetrics, SpeechMetrics, FillerMetrics
from app.llm.engine import FeedbackEngine


def test_aggregator_empty():
    agg = MetricsAggregator()
    result = agg.aggregate()

    assert result.posture.score == 1.0
    assert result.speech.fillers.count == 0


def test_aggregator_with_data():
    agg = MetricsAggregator()

    agg.push_video({
        "posture": PostureMetrics(score=0.5, issues=["hombros desnivelados"]),
        "gestures": GestureMetrics(movement_level="normal"),
        "face": FaceMetrics(eye_contact_pct=0.3, nervousness_score=0.2),
    })
    agg.push_video({
        "posture": PostureMetrics(score=0.7, issues=[]),
        "gestures": GestureMetrics(movement_level="normal"),
        "face": FaceMetrics(eye_contact_pct=0.5, nervousness_score=0.4),
    })

    result = agg.aggregate()

    assert result.posture.score == 0.6
    assert result.face.eye_contact_pct == 0.4


def test_feedback_bad_posture():
    engine = FeedbackEngine()
    from app.models.metrics import AggregatedMetrics

    metrics = AggregatedMetrics(
        posture=PostureMetrics(score=0.3, issues=["torso inclinado"]),
        face=FaceMetrics(eye_contact_pct=0.8),
        speech=SpeechMetrics(),
    )

    feedbacks = engine.generate(metrics)
    categories = [f.category for f in feedbacks]

    assert "postura" in categories


def test_feedback_too_many_fillers():
    engine = FeedbackEngine()
    from app.models.metrics import AggregatedMetrics

    metrics = AggregatedMetrics(
        speech=SpeechMetrics(
            pace_wpm=140,
            fillers=FillerMetrics(count=20, per_minute=5.0, words={"este": 10, "o sea": 7, "bueno": 3}),
        ),
    )

    feedbacks = engine.generate(metrics)
    categories = [f.category for f in feedbacks]

    assert "fillers" in categories


def test_feedback_all_good():
    engine = FeedbackEngine()
    from app.models.metrics import AggregatedMetrics

    metrics = AggregatedMetrics(
        posture=PostureMetrics(score=0.9),
        face=FaceMetrics(eye_contact_pct=0.8, nervousness_score=0.1),
        speech=SpeechMetrics(pace_wpm=130, fillers=FillerMetrics(count=1, per_minute=0.5)),
        gestures=GestureMetrics(movement_level="normal"),
    )

    feedbacks = engine.generate(metrics)

    assert len(feedbacks) == 1
    assert feedbacks[0].category == "general"