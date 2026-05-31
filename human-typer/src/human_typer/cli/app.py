from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Annotated

import typer

from human_typer.config import MIN_TRAINING_SAMPLES
from human_typer.control.hotkeys import HotkeyController
from human_typer.engine.typer import HumanTyper
from human_typer.engine.typo import TypoStrategy
from human_typer.io.pyautogui_backend import PyAutoGuiBackend
from human_typer.profiles.models import TypingProfile
from human_typer.profiles.repository import ProfileRepository
from human_typer.profiles.trainer import TypingTrainer

app = typer.Typer(no_args_is_help=True, add_completion=False)
profiles_app = typer.Typer(no_args_is_help=True, help="Gestión de perfiles de escritura.")
app.add_typer(profiles_app, name="profiles")


_repo = ProfileRepository()


# ── helpers ──────────────────────────────────────────────────────────────────


def _load_profile(name: str) -> TypingProfile:
    profile = _repo.load(name)
    if profile.training_samples == 0 and name != "default":
        print(f"[aviso] Perfil '{name}' no encontrado. Usando perfil por defecto.", file=sys.stderr)
        return TypingProfile(name=name)
    return profile


def _countdown(seconds: int, stopped: callable) -> bool:
    for i in range(seconds, 0, -1):
        if stopped():
            return True
        print(f"  Comenzando en {i} segundos...", end="\r")
        time.sleep(1)
    print(" " * 40, end="\r")
    return False


# ── type ─────────────────────────────────────────────────────────────────────


@app.command()
def type_text(
    text: Annotated[
        str | None, typer.Argument(help="Texto directo a escribir")
    ] = None,
    file: Annotated[
        Path | None, typer.Option("--file", "-f", help="Archivo .txt con el texto")
    ] = None,
    profile: Annotated[
        str, typer.Option("--profile", "-p", help="Nombre del perfil")
    ] = "default",
    stealth: Annotated[
        bool, typer.Option("--stealth", "-s", help="Modo evasivo: maxima evasion de deteccion")
    ] = False,
    delay: Annotated[
        int, typer.Option("--delay", "-d", help="Segundos antes de empezar")
    ] = 5,
    start: Annotated[
        int | None, typer.Option("--start", help="Indice de caracter inicial")
    ] = None,
    end: Annotated[
        int | None, typer.Option("--end", help="Indice de caracter final")
    ] = None,
    no_interactive: Annotated[
        bool, typer.Option("--no-interactive", help="Desactiva controles por teclado")
    ] = False,
    continuous: Annotated[
        bool, typer.Option("--continuous", "-c", help="Modo continuo: pegar mas texto tras escribir")
    ] = False,
    interactive_input: Annotated[
        bool, typer.Option("--interactive-input", "-i", help="Pegar texto linea por linea")
    ] = False,
    speed: Annotated[
        float, typer.Option("--speed", "-x", help="Multiplicador de velocidad (0.1=lento, 5.0=rapido)")
    ] = 1.0,
    ai: Annotated[
        bool, typer.Option("--ai", help="Procesa el archivo con IA local (Ollama) antes de tipear")
    ] = False,
    ai_model: Annotated[
        str, typer.Option("--ai-model", help="Modelo Ollama a usar (default: deepseek-r1:1.5b)")
    ] = "deepseek-r1:1.5b",
) -> None:
    if speed < 0.1 or speed > 5.0:
        print("[Error] --speed debe estar entre 0.1 y 5.0", file=sys.stderr)
        raise typer.Exit(code=1)
    if ai and file is None:
        print("[Error] --ai requiere --file", file=sys.stderr)
        raise typer.Exit(code=1)
    _run_typing(
        text=text,
        file=file,
        profile_name=profile,
        stealth=stealth,
        delay_start=delay,
        start_pos=start,
        end_pos=end,
        interactive=not no_interactive,
        continuous=continuous,
        interactive_input=interactive_input,
        speed=speed,
        ai=ai,
        ai_model=ai_model,
    )


def _run_typing(
    text: str | None,
    file: Path | None,
    profile_name: str,
    stealth: bool,
    delay_start: int,
    start_pos: int | None,
    end_pos: int | None,
    interactive: bool,
    continuous: bool,
    interactive_input: bool,
    speed: float,
    ai: bool,
    ai_model: str,
) -> None:
    if interactive_input:
        text = _read_interactive_text()

    if file is not None:
        if not file.exists():
            print(f"[Error] Archivo no encontrado: {file}", file=sys.stderr)
            raise typer.Exit(code=1)
        raw = file.read_text(encoding="utf-8")

        if ai:
            try:
                from human_typer.ai.client import check_ollama_health, query_ollama
            except ImportError as exc:
                print("[Error] No se pudo cargar el modulo AI interno", file=sys.stderr)
                raise typer.Exit(code=1) from exc

            if not check_ollama_health():
                print("[Error] Ollama no disponible. Verifica: ollama serve", file=sys.stderr)
                raise typer.Exit(code=1)

            print(f"[AI] Procesando archivo con {ai_model}...")
            try:
                text = query_ollama(raw, model=ai_model)
                print(f"[AI] Texto procesado ({len(text)} caracteres)")
            except (ConnectionError, ValueError) as exc:
                print(f"[Error] {exc}", file=sys.stderr)
                raise typer.Exit(code=1)
        else:
            text = raw

    if text is None and not continuous:
        print("[Error] Debes proporcionar texto, --file, --interactive-input o --continuous", file=sys.stderr)
        raise typer.Exit(code=1)

    profile = _load_profile(profile_name)

    def _execute(payload: str) -> None:
        _do_type(payload, profile, stealth, delay_start, start_pos, end_pos, interactive, speed)

    if continuous:
        print("Modo continuo. Despues de escribir, pega mas texto (o 'q' para salir).")
        current = text
        while True:
            if current is None:
                print("\nPega el texto a escribir (o 'q' + Enter para salir):")
                lines = []
                while True:
                    try:
                        line = input()
                    except (EOFError, KeyboardInterrupt):
                        return
                    if line.strip().lower() == "q":
                        return
                    if line == "":
                        break
                    lines.append(line)
                current = "\n".join(lines)
                if not current:
                    return
            _execute(current)
            current = None
    else:
        if text is None:
            print("[Error] Debes proporcionar texto.", file=sys.stderr)
            raise typer.Exit(code=1)
        _execute(text)


def _do_type(
    text: str,
    profile: TypingProfile,
    stealth: bool,
    delay_start: int,
    start_pos: int | None,
    end_pos: int | None,
    interactive: bool,
    speed: float,
) -> None:
    backend = PyAutoGuiBackend()
    typo = TypoStrategy(probability=profile.typo_probability)
    typer_engine = HumanTyper(backend, profile, typo_strategy=typo, stealth=stealth, speed_multiplier=speed)

    controller = None
    if interactive:
        controller = HotkeyController(typer_engine)
        controller.start()

    print(f"\n[HumanTyper] Perfil: '{profile.name}' (muestras: {profile.training_samples})")
    print(f"[HumanTyper] Stealth: {'SI' if stealth else 'NO'}  |  Velocidad: x{speed:.2f}")
    print(f"[HumanTyper] Preparando {len(text)} caracteres...")
    print("[HumanTyper] Coloca el cursor en el editor y espera...")

    if _countdown(delay_start, lambda: typer_engine.is_stopped):
        print("\n[HumanTyper] Escritura cancelada.")
        return

    if typer_engine.is_stopped:
        print("[HumanTyper] Escritura cancelada.")
        return

    print("[HumanTyper] \u270d\ufe0f  ESCRIBIENDO... (P: pausa, S: detener, Ctrl+O/L: velocidad)")

    typer_engine.type_text(text, start_pos=start_pos, end_pos=end_pos)

    if not typer_engine.is_stopped:
        print("\n[HumanTyper] \u2705 Escritura completada.")
    else:
        print("\n[HumanTyper] \u23f9\ufe0f  Escritura interrumpida.")


def _read_interactive_text() -> str:
    print("Modo interactivo. Pega el texto y presiona Enter (linea vacia + Enter = empezar):")
    lines = []
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            break
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    if not text:
        print("[Error] No se ingreso texto.", file=sys.stderr)
        raise typer.Exit(code=1)
    return text


# ── train ────────────────────────────────────────────────────────────────────


@app.command()
def train(
    profile: Annotated[
        str, typer.Option("--profile", "-p", help="Nombre del perfil a entrenar")
    ] = "default",
    duration: Annotated[
        int, typer.Option("--duration", "-d", help="Duracion en minutos")
    ] = 3,
) -> None:
    _run_training(profile_name=profile, duration_minutes=duration)


def _run_training(profile_name: str, duration_minutes: int) -> None:
    try:
        import keyboard
    except ImportError:
        print("[Error] Se necesita 'keyboard'. Instalalo con: pip install keyboard", file=sys.stderr)
        raise typer.Exit(code=1)

    profile = _repo.load(profile_name)
    profile.name = profile_name
    trainer = TypingTrainer(profile, repository=_repo)

    print("\n═══ MODO ENTRENAMIENTO ═══")
    print(f"Perfil objetivo: '{profile_name}'")
    print(f"Duracion: {duration_minutes} minuto(s)")
    print("\nInstrucciones:")
    print("  1. Coloca el cursor / enfoca la ventana donde escribiras NORMALMENTE.")
    print("  2. Escribe con total naturalidad durante el tiempo indicado.")
    print("  3. Presiona [Q] para terminar antes.")
    print("  4. Presiona [S] para salir (y descartar).")
    print("══════════════════════════════\n")

    stop_flag = {"value": False}
    save_flag = {"value": True}

    keyboard.add_hotkey("q", lambda: _signal_stop(stop_flag, True))
    keyboard.add_hotkey("s", lambda: _signal_stop(stop_flag, False, save_flag))

    for i in range(3, 0, -1):
        print(f"  Comienza a escribir en {i}...", end="\r")
        time.sleep(1)
    print(" " * 30, end="\r")
    print("¡YA! Escribe normalmente. (Q=terminar, S=salir)")

    start_time = time.time()
    duration_seconds = duration_minutes * 60

    last_key_time = time.time()
    current_pause_start: float | None = None

    def on_key_event(e: keyboard.KeyboardEvent) -> None:
        nonlocal last_key_time, current_pause_start
        now = time.time()

        if e.event_type == "down":
            if current_pause_start is not None:
                pause_dur = now - current_pause_start
                if pause_dur > 0.03:
                    trainer.on_pause(pause_dur)
                current_pause_start = None
            trainer.on_key_down()
            last_key_time = now
        elif e.event_type == "up":
            trainer.on_key_up()

    keyboard.hook(on_key_event)

    try:
        while not stop_flag["value"]:
            elapsed = time.time() - start_time
            remaining = duration_seconds - elapsed
            if remaining <= 0:
                break

            now = time.time()
            if now - last_key_time > 0.1 and current_pause_start is None:
                current_pause_start = now
                last_key_time = now

            mins, secs = divmod(int(remaining), 60)
            print(f"  Tiempo restante: {mins:02d}:{secs:02d}  (Q=terminar, S=salir)   ", end="\r")
            time.sleep(0.5)
    finally:
        keyboard.unhook_all()

    print("\n\n[Trainer] Procesando muestras...")
    try:
        result = trainer.finalize(save=save_flag["value"])
        print(f"[Trainer] Perfil '{result.name}' guardado ({result.training_samples} muestras).")
        print(f"  Intervalo entre teclas: media={result.char_interval_mean*1000:.0f}ms, "
              f"std={result.char_interval_std*1000:.0f}ms")
        if trainer._key_holds:
            kh = [x for x in trainer._key_holds if x > 0]
            if kh:
                print(f"  Duracion pulsacion: media={sum(kh)/len(kh)*1000:.0f}ms")
    except ValueError as exc:
        print(f"[Trainer] {exc}", file=sys.stderr)
        raise typer.Exit(code=1)


def _signal_stop(
    flag: dict,
    value: bool,
    save_flag: dict | None = None,
) -> None:
    flag["value"] = True
    if save_flag is not None:
        save_flag["value"] = value
    label = "Finalizando..." if value else "Saliendo sin guardar..."
    print(f"\n[Trainer] {label}")


# ── profiles ─────────────────────────────────────────────────────────────────


@profiles_app.command(name="list")
def list_profiles() -> None:
    profiles = _repo.list_profiles()
    if profiles:
        print("Perfiles disponibles:")
        for name in profiles:
            p = _repo.load(name)
            print(f"  {name} ({p.training_samples} muestras)")
    else:
        print("No hay perfiles guardados. Usa: human-typer train")


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    try:
        app()
    except KeyboardInterrupt:
        print("\n\n[HumanTyper] Interrumpido por el usuario.")
        raise typer.Exit(0)


if __name__ == "__main__":
    main()
