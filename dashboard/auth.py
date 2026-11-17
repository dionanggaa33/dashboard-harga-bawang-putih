"""Autentikasi sederhana berbasis session state Streamlit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import streamlit as st


@dataclass(frozen=True)
class User:
    """Representasi pengguna yang sedang masuk."""

    username: str
    role: str


def _load_users() -> dict[str, tuple[str, str]]:
    """Membaca kredensial pengguna dari ``st.secrets``.

    Kredensial TIDAK pernah ditulis di dalam kode, sehingga repo aman dipublikasikan
    dan perilaku lokal maupun Streamlit Cloud identik. Bila secrets belum diisi,
    aplikasi berhenti dengan pesan yang menjelaskan cara memperbaikinya.
    """

    try:
        configured = st.secrets["auth"]["users"]
    except Exception:  # noqa: BLE001 - secrets belum dibuat
        configured = None

    users: dict[str, tuple[str, str]] = {}
    if configured:
        for username, record in configured.items():
            try:
                users[str(username).strip().lower()] = (
                    str(record["password"]),
                    str(record["role"]),
                )
            except (KeyError, TypeError):
                continue

    if not users:
        raise RuntimeError(
            "Kredensial pengguna belum dikonfigurasi. "
            "Lokal: salin .streamlit/secrets.toml.example menjadi .streamlit/secrets.toml "
            "lalu isi password. Streamlit Cloud: isi pada Settings > Secrets."
        )
    return users


USERS: Final[dict[str, tuple[str, str]]] = _load_users()


def current_user() -> User | None:
    """Mengembalikan pengguna aktif, atau ``None`` jika belum login."""

    username = st.session_state.get("username")
    role = st.session_state.get("role")
    if not username or not role:
        return None
    return User(username=username, role=role)


def authenticate(username: str, password: str) -> User | None:
    """Memvalidasi kredensial demo dan mengembalikan objek pengguna."""

    record = USERS.get(username.strip().lower())
    if record is None or record[0] != password:
        return None
    return User(username=username.strip().lower(), role=record[1])


def login_form() -> None:
    """Merender halaman login dan menangani submit form."""

    from dashboard.components import render_login_page

    render_login_page()
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        submitted = st.form_submit_button("Masuk ke dashboard", width="stretch")

    if submitted:
        user = authenticate(username, password)
        if user is None:
            st.error("Username atau password belum sesuai.")
        else:
            st.session_state.username = user.username
            st.session_state.role = user.role
            st.session_state.page = "Ringkasan"
            st.rerun()


def logout() -> None:
    """Menghapus sesi pengguna aktif."""

    for key in ("username", "role", "page"):
        st.session_state.pop(key, None)
    st.rerun()
