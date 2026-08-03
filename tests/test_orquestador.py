import pytest

from src.orquestador import init_lola


def _fail(*args, **kwargs):
    raise AssertionError("no debería haberse llamado a esta etapa")


def test_init_lola_skips_generation_when_video_already_exists(tmp_path, monkeypatch):
    existing_video = tmp_path / "dia_1.mp4"
    existing_video.write_bytes(b"video-ya-generado")

    monkeypatch.setattr("src.orquestador.generate_avatar_image", _fail)
    monkeypatch.setattr("src.orquestador.resize_for_sadtalker", _fail)
    monkeypatch.setattr("src.orquestador.generate_voiceover", _fail)
    monkeypatch.setattr("src.orquestador.create_ai_influencer", _fail)

    result = init_lola(
        "hola",
        guion_id="dia_1",
        reusar_imagen="ancla.png",
        result_dir=str(tmp_path),
    )

    assert result == str(existing_video)


def test_init_lola_generates_and_copies_to_guion_id_path(tmp_path, monkeypatch):
    generated_video = tmp_path / "sadtalker_run" / "output.mp4"
    generated_video.parent.mkdir()
    generated_video.write_bytes(b"video-recien-generado")

    calls = {}

    def fake_generate_voiceover(script_text):
        calls["audio_script"] = script_text
        return "audio.wav"

    def fake_create_ai_influencer(image_path, audio_path, pose_style=0, result_dir="./results", max_retries=1):
        calls["create_ai_influencer"] = {
            "image_path": image_path,
            "audio_path": audio_path,
            "result_dir": result_dir,
            "max_retries": max_retries,
        }
        return str(generated_video)

    monkeypatch.setattr("src.orquestador.generate_avatar_image", _fail)
    monkeypatch.setattr("src.orquestador.resize_for_sadtalker", _fail)
    monkeypatch.setattr("src.orquestador.generate_voiceover", fake_generate_voiceover)
    monkeypatch.setattr("src.orquestador.create_ai_influencer", fake_create_ai_influencer)

    result = init_lola(
        "hola",
        guion_id="dia_1",
        reusar_imagen="ancla.png",
        result_dir=str(tmp_path),
    )

    expected_final_path = tmp_path / "dia_1.mp4"
    assert result == str(expected_final_path)
    assert expected_final_path.read_bytes() == b"video-recien-generado"
    assert calls["audio_script"] == "hola"
    assert calls["create_ai_influencer"]["image_path"] == "ancla.png"
    assert calls["create_ai_influencer"]["result_dir"] == str(tmp_path)


def test_init_lola_without_guion_id_returns_raw_path(tmp_path, monkeypatch):
    monkeypatch.setattr("src.orquestador.generate_avatar_image", _fail)
    monkeypatch.setattr("src.orquestador.resize_for_sadtalker", _fail)
    monkeypatch.setattr("src.orquestador.generate_voiceover", lambda script_text: "audio.wav")
    monkeypatch.setattr(
        "src.orquestador.create_ai_influencer",
        lambda image_path, audio_path, pose_style=0, result_dir="./results", max_retries=1: "raw/run/video.mp4",
    )

    result = init_lola("hola", reusar_imagen="ancla.png", result_dir=str(tmp_path))

    assert result == "raw/run/video.mp4"
