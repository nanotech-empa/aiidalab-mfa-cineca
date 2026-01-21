__version__ = "v2026.0001"

import subprocess
import time
import re
import requests
import os
import datetime
import ipywidgets as ipw
from IPython.display import display
from threading import Thread, Event, Lock

# ============================================================
# Low-level helpers
# ============================================================

def run_cmd(cmd, input=None):
    res = subprocess.run(
        cmd,
        input=input,
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip())
    return res.stdout.strip()


def step_bootstrap_cineca():
    step_dir = os.path.expanduser("~/.step")
    if os.path.isdir(step_dir):
        subprocess.run(["rm", "-rf", step_dir], check=False)

    run_cmd([
        "step", "ca", "bootstrap",
        "--ca-url=https://sshproxy.hpc.cineca.it",
        "--fingerprint=2ae1543202304d3f434bdc1a2c92eff2cd2b02110206ef06317e70c1c1735ecd"
    ])

def get_ssh_expiry(email):
    if not email.strip():
        return None, "Enter email to check SSH validity"

    try:
        raw = run_cmd(["step", "ssh", "list", "--raw", email])
        if not raw:
            return None, "No active SSH login"

        info = run_cmd(["step", "ssh", "inspect"], input=raw)

        m = re.search(r"Valid:\s+from\s+\S+\s+to\s+(\S+)", info)
        if not m:
            return None, "Cannot parse SSH validity"

        expiry = datetime.datetime.fromisoformat(m.group(1))
        return expiry, None

    except Exception:
        return None, "No active SSH login"


def format_expiry(expiry):
    delta = expiry - datetime.datetime.utcnow()
    if delta.total_seconds() <= 0:
        return "❌ SSH session expired"

    minutes = int(delta.total_seconds() // 60)
    h, m = divmod(minutes, 60)

    if h > 0:
        return f"⏳ SSH will expire in {h}h {m}m"
    return f"⏳ SSH will expire in {m}m"

def step_login(email, password, otp):
    env = os.environ.copy()
    env["BROWSER"] = "echo"

    proc = subprocess.Popen(
        ["step", "ssh", "login", email, "--provisioner", "cineca-hpc"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )
    auth_url = None
    start = time.time()

    while time.time() - start < 30:
        line = proc.stdout.readline()
        if not line:
            break

        if "requires the" in line:
            proc.kill()
            step_bootstrap_cineca()
            return step_login(email, password, otp)

        m = re.search(r"https://sso\.hpc\.cineca\.it/\S+", line)
        if m:
            auth_url = m.group(0)
            break

    if not auth_url:
        proc.kill()
        raise RuntimeError("Could not obtain CINECA login URL")

    session = requests.Session()
    html = session.get(auth_url).text

    m = re.search(r'id="kc-form-login".*?action="([^"]+)"', html)
    if not m:
        raise RuntimeError("Login form not found")

    action = m.group(1).replace("&amp;", "&")
    if action.startswith("/"):
        action = "https://sso.hpc.cineca.it" + action

    html = session.post(action, data={
        "username": email,
        "password": password,
        "login": "Sign In"
    }).text

    m = re.search(r'id="kc-otp-login-form".*?action="([^"]+)"', html)
    if not m:
        raise RuntimeError("OTP form not found")

    action = m.group(1).replace("&amp;", "&")
    if action.startswith("/"):
        action = "https://sso.hpc.cineca.it" + action

    r = session.post(action, data={"otp": otp}, allow_redirects=False)
    if "Location" not in r.headers:
        raise RuntimeError("OTP failed")

    run_cmd(["curl", "-s", r.headers["Location"]])
    proc.wait(timeout=10)


class CinecaMfaWidget(ipw.VBox):
    
    def __init__(self, appbase):

        # ============================================================
        # UI + state
        # ============================================================
        logo = ipw.HTML(
            f"""
            <div style="text-align:left; margin-bottom:20px;">
                <img src="{appbase}/cineca_logo.png" style="width:320px; height:auto;">
            </div>
            """
        )

        self.email_w = ipw.Text(description="Email")
        self.pwd_w   = ipw.Password(description="Password")
        self.otp_w   = ipw.Text(description="OTP")
        login_b = ipw.Button(description="Login to CINECA", button_style="success")
        login_b.on_click(self.on_login)


        self.status = ipw.HTML("<b>Status:</b> Enter email to check SSH validity")

        children = [
            logo,
            self.email_w,
            self.pwd_w,
            self.otp_w,
            login_b,
            self.status
        ]

        # ============================================================
        # State control (THIS FIXES EVERYTHING)
        # ============================================================

        self.stop_event = Event()
        self.login_lock = Lock()
        
        Thread(target=self.status_updater, daemon=True).start()
        
        super().__init__(children=children)


    # ============================================================
    # Login via step ssh login
    # ============================================================




    def refresh_status(self):
        expiry, msg = get_ssh_expiry(self.email_w.value)
        if expiry:
            self.status.value = f"<b>Status:</b> logged in<br>{format_expiry(expiry)}"
        else:
            self.status.value = f"<b>Status:</b> {msg}"

    def status_updater(self):
        while not self.stop_event.is_set():
            if not self.login_lock.locked():
                self.refresh_status()
            self.stop_event.wait(30)


    # ============================================================
    # Login button
    # ============================================================

    def on_login(self, _):
        with self.login_lock:
            self.status.value = "<b>Status:</b> checking existing login…"

            expiry, _ = get_ssh_expiry(self.email_w.value)
            if expiry:
                self.refresh_status()
                return

            self.status.value = "<b>Status:</b> logging in…"
            try:
                step_login(self.email_w.value, self.pwd_w.value, self.otp_w.value)
            except Exception as e:
                self.status.value = f"<b>Status:</b> ❌ {e}"
                return

            self.refresh_status()




def get_start_widget(appbase, jupbase, notebase):
    return CinecaMfaWidget(appbase=appbase)
