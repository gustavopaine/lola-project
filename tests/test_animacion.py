import subprocess

import pytest

from src.animacion import (
    SadTalkerGenerationError,
    _find_output_video,
    _snapshot_results_dirs,
    create_ai_influencer,
)


def test_snapshot_results_dirs_returns_only_dir_names(tmp_path):
    (tmp_path / "20260101_120000").mkdir()
    (tmp_path / "20260101_130000").mkdir()
    (tmp_path / "not_a_dir.txt").write_text("x")

    assert _snapshot_results_dirs(str(tmp_path)) == {
        "20260101_120000",
        "20260101_130000",
    }


def test_snapshot_results_dirs_missing_dir_is_empty(tmp_path):
    missing = tmp_path / "does_not_exist"

    assert _snapshot_results_dirs(str(missing)) == set()


def test_find_output_video_success(tmp_path):
    before = _snapshot_results_dirs(str(tmp_path))

    run_dir = tmp_path / "20260101_140000"
    run_dir.mkdir()
    video = run_dir / "20260101_140000.mp4"
    video.write_bytes(b"not-really-a-video-but-not-empty")

    result = _find_output_video(before, str(tmp_path))

    assert result == str(video)


def test_find_output_video_no_new_folder(tmp_path):
    (tmp_path / "20260101_120000").mkdir()
    before = _snapshot_results_dirs(str(tmp_path))

    with pytest.raises(SadTalkerGenerationError, match="no se creó ninguna carpeta"):
        _find_output_video(before, str(tmp_path))


def test_find_output_video_only_first_frame_dir(tmp_path):
    before = _snapshot_results_dirs(str(tmp_path))

    run_dir = tmp_path / "20260101_150000"
    run_dir.mkdir()
    (run_dir / "first_frame_dir").mkdir()
    (run_dir / "first_frame_dir" / "00000.png").write_bytes(b"fake-frame")

    with pytest.raises(SadTalkerGenerationError, match="no contiene ningún"):
        _find_output_video(before, str(tmp_path))


def test_find_output_video_zero_byte_mp4(tmp_path):
    before = _snapshot_results_dirs(str(tmp_path))

    run_dir = tmp_path / "20260101_160000"
    run_dir.mkdir()
    (run_dir / "20260101_160000.mp4").write_bytes(b"")

    with pytest.raises(SadTalkerGenerationError, match="0 bytes"):
        _find_output_video(before, str(tmp_path))


@pytest.fixture(autouse=True)
def _sin_gpu(monkeypatch):
    """Ninguno de estos tests debe tocar hardware real."""
    monkeypatch.setattr("src.animacion.liberar_gpu", lambda: None)


def _completed(returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=["inference.py"], returncode=returncode, stdout="", stderr=stderr)


def test_create_ai_influencer_success_on_first_attempt(tmp_path, monkeypatch):
    calls = []

    def fake_run(cmd, capture_output, text):
        calls.append(cmd)
        run_dir = tmp_path / "run_1"
        run_dir.mkdir()
        (run_dir / "run_1.mp4").write_bytes(b"video-real")
        return _completed()

    monkeypatch.setattr("src.animacion.subprocess.run", fake_run)

    result = create_ai_influencer(
        "img.png", "audio.wav", result_dir=str(tmp_path), max_retries=1
    )

    assert result == str(tmp_path / "run_1" / "run_1.mp4")
    assert len(calls) == 1


def test_create_ai_influencer_succeeds_on_retry(tmp_path, monkeypatch):
    calls = []

    def fake_run(cmd, capture_output, text):
        calls.append(cmd)
        if len(calls) == 1:
            # primer intento: el proceso se corta a mitad de camino,
            # no crea ninguna carpeta nueva.
            return _completed(returncode=1, stderr="se cortó a mitad de camino")
        run_dir = tmp_path / "run_2"
        run_dir.mkdir()
        (run_dir / "run_2.mp4").write_bytes(b"video-real")
        return _completed()

    monkeypatch.setattr("src.animacion.subprocess.run", fake_run)

    result = create_ai_influencer(
        "img.png", "audio.wav", result_dir=str(tmp_path), max_retries=1
    )

    assert result == str(tmp_path / "run_2" / "run_2.mp4")
    assert len(calls) == 2


def test_create_ai_influencer_raises_after_exhausting_retries(tmp_path, monkeypatch):
    calls = []

    def fake_run(cmd, capture_output, text):
        calls.append(cmd)
        return _completed(returncode=1, stderr="fallo persistente")

    monkeypatch.setattr("src.animacion.subprocess.run", fake_run)

    with pytest.raises(SadTalkerGenerationError):
        create_ai_influencer("img.png", "audio.wav", result_dir=str(tmp_path), max_retries=1)

    assert len(calls) == 2  # intento inicial + 1 reintento
