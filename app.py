from flask import Flask, request, redirect, session, url_for, render_template
import dropbox
import os

app = Flask(__name__)
app.secret_key = "K3CZwH3D3X-WZ_t1NiMSSBHvLvQFUwWbAF5LUbWdexJPdyhW9wN65-_Jrd8Pjgg2_bvHBHf25hy-acJUAH27dMgSSZLsXNbEOoTkas_6jze39XCN1C2kO6n6a5J-Ah8ERZP1nTLG7mKZfm7_bh-vMxGh0soio12-E3dcAAe0cWus9hVYwze_UJccIh9jmfU_2sC1zrdgDDoMk5P1G2PbWDUF7PN3zK6-nquY63lkMGFkL9ji7rZjTveL9HYviiLWHCBBI3unApxHizAMn7BwRL_0qtZUxb0OFjUVjgWhRibyeEVOm5gLUcKhT9HarMs25Cr8a2pfSlGjdkA3OEjb6P91pDHtVE_HraAqFtvo1L4UdnB8xZxQg3wLJc1vr1dVryapw16o7jt7ud_I"  # Change this in production

DROPBOX_APP_KEY = ''
DROPBOX_APP_SECRET = ''
REDIRECT_URI = 'http://localhost:5000/oauth_callback'

@app.route('/')
def home():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))

    dbx = dropbox.Dropbox(access_token)
    files = dbx.files_list_folder("").entries
    return render_template('home.html', files=files)

@app.route('/login')
def login():
    authorize_url = (
        f"https://www.dropbox.com/oauth2/authorize"
        f"?client_id={DROPBOX_APP_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    )
    return redirect(authorize_url)

@app.route('/oauth_callback')
def oauth_callback():
    code = request.args.get('code')
    token_url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': DROPBOX_APP_KEY,
        'client_secret': DROPBOX_APP_SECRET,
        'redirect_uri': REDIRECT_URI,
    }

    res = requests.post(token_url, data=data)
    token = res.json().get('access_token')
    session['access_token'] = token
    return redirect(url_for('home'))

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    access_token = session.get('access_token')
    dbx = dropbox.Dropbox(access_token)
    dbx.files_upload(file.read(), f"/{file.filename}")
    return redirect(url_for('home'))

@app.route('/download/<path:filename>')
def download(filename):
    access_token = session.get('access_token')
    dbx = dropbox.Dropbox(access_token)
    metadata, res = dbx.files_download(f"/{filename}")
    return res.content

@app.route('/delete/<path:filename>')
def delete(filename):
    access_token = session.get('access_token')
    dbx = dropbox.Dropbox(access_token)
    dbx.files_delete_v2(f"/{filename}")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
