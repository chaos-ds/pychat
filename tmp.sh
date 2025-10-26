# 1) 専用ユーザー作成（ログイン不要）
sudo useradd --system --no-create-home --shell /sbin/nologin pychat

# 2) /opt にリポジトリをクローン
sudo git clone <REPO_URL> /opt/pychat

# 3) 所有権を専用ユーザーに変更
sudo chown -R pychat:pychat /opt/pychat

# 4) 仮想環境作成と依存インストール（pychat ユーザーになって実行する）
sudo -u pychat bash -c 'python3 -m venv /opt/pychat/.venv && \
  /opt/pychat/.venv/bin/pip install --upgrade pip && \
  /opt/pychat/.venv/bin/pip install -r /opt/pychat/server/requirements.txt'